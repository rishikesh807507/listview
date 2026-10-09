import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional

from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, root_mean_squared_error
from sklearn.preprocessing import StandardScaler

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from backend.ml.feature_engineering import calculate_technical_features

logger = logging.getLogger("StockPredictor")

FEATURE_COLS = [
    'rsi_14', 'macd', 'macd_signal', 'macd_hist',
    'bb_position', 'return_1d', 'return_5d',
    'volatility_20', 'volume_ratio'
]

class StockPredictor:
    """
    Open-Source ML Pipeline for Stock Direction and Return Range Estimation.
    Uses TimeSeriesSplit walk-forward validation to eliminate lookahead bias.
    Zero paid AI API dependency.
    """
    def __init__(self, model_type: str = "RandomForest"):
        self.model_type = model_type if (model_type != "XGBoost" or HAS_XGBOOST) else "RandomForest"
        self.scaler = StandardScaler()

    def train_and_predict(self, price_records: list[dict]) -> Dict[str, Any]:
        """
        Takes raw chronological price dictionaries: [{timestamp, open, high, low, close, volume}, ...]
        Returns comprehensive statistical forecast with metrics and audit trail.
        """
        if len(price_records) < 60:
            return {
                "error": "Insufficient historical data for time-series modeling (minimum 60 trading days required)."
            }

        df = pd.DataFrame(price_records)
        df_feat = calculate_technical_features(df)
        
        # Drop rows with NaN in features
        valid_df = df_feat.dropna(subset=FEATURE_COLS).copy()
        if len(valid_df) < 50:
            return {"error": "Insufficient samples after feature calculation."}

        # Last row is for live inference (where forward targets are unknown)
        inference_row = valid_df.iloc[-1:][FEATURE_COLS]
        
        # Training dataset: exclude the last 5 rows to allow forward target completion
        train_df = valid_df.iloc[:-5].dropna(subset=['target_dir_1d', 'target_return_5d'])
        if len(train_df) < 40:
            train_df = valid_df.iloc[:-1].dropna(subset=['target_dir_1d', 'target_return_1d'])
        
        X = train_df[FEATURE_COLS].values
        y_dir = train_df['target_dir_1d'].values
        y_ret = train_df['target_return_5d'].values if 'target_return_5d' in train_df else train_df['target_return_1d'].values

        # TimeSeriesSplit Walk-Forward Validation (3 splits)
        n_splits = min(3, max(2, len(train_df) // 30))
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        acc_scores, prec_scores, rec_scores, f1_scores = [], [], [], []
        mae_scores = []
        
        # Classifier for direction
        if self.model_type == "XGBoost" and HAS_XGBOOST:
            clf = xgb.XGBClassifier(n_estimators=60, max_depth=3, learning_rate=0.05, eval_metric="logloss", random_state=42)
            reg = xgb.XGBRegressor(n_estimators=60, max_depth=3, learning_rate=0.05, random_state=42)
        else:
            clf = RandomForestClassifier(n_estimators=80, max_depth=4, min_samples_split=6, random_state=42)
            reg = GradientBoostingRegressor(n_estimators=60, max_depth=3, learning_rate=0.05, random_state=42)

        # Walk-forward validation
        for train_idx, test_idx in tscv.split(X):
            X_tr, X_te = X[train_idx], X[test_idx]
            y_dir_tr, y_dir_te = y_dir[train_idx], y_dir[test_idx]
            y_ret_tr, y_ret_te = y_ret[train_idx], y_ret[test_idx]
            
            clf.fit(X_tr, y_dir_tr)
            preds_dir = clf.predict(X_te)
            acc_scores.append(accuracy_score(y_dir_te, preds_dir))
            prec_scores.append(precision_score(y_dir_te, preds_dir, zero_division=0))
            rec_scores.append(recall_score(y_dir_te, preds_dir, zero_division=0))
            f1_scores.append(f1_score(y_dir_te, preds_dir, zero_division=0))
            
            reg.fit(X_tr, y_ret_tr)
            preds_ret = reg.predict(X_te)
            mae_scores.append(mean_absolute_error(y_ret_te, preds_ret))

        # Final fit on full training set
        clf.fit(X, y_dir)
        reg.fit(X, y_ret)
        
        # Live Inference
        live_prob = float(clf.predict_proba(inference_row.values)[0][1]) * 100.0  # Positive movement prob
        live_expected_ret = float(reg.predict(inference_row.values)[0]) * 100.0
        
        # Volatility estimation for confidence band
        current_vol = float(valid_df.iloc[-1]['volatility_20']) if 'volatility_20' in valid_df else 0.18
        band_spread = max(1.5, round(current_vol * 15, 2))
        ret_min = round(live_expected_ret - band_spread, 2)
        ret_max = round(live_expected_ret + band_spread, 2)
        
        confidence = "High" if (live_prob > 65 or live_prob < 35) and np.mean(acc_scores) > 0.58 else ("Medium" if np.mean(acc_scores) > 0.50 else "Low")
        
        avg_acc = round(float(np.mean(acc_scores) * 100), 2)
        avg_prec = round(float(np.mean(prec_scores) * 100), 2)
        avg_rec = round(float(np.mean(rec_scores) * 100), 2)
        avg_f1 = round(float(np.mean(f1_scores) * 100), 2)
        avg_mae = round(float(np.mean(mae_scores) * 100), 2)
        
        return {
            "model_name": self.model_type,
            "target_timeframe": "Next 1 to 5 Trading Days",
            "positive_prob": round(live_prob, 1),
            "expected_return_min": ret_min,
            "expected_return_max": ret_max,
            "expected_return_mid": round(live_expected_ret, 2),
            "volatility_annualized": round(current_vol * 100, 2),
            "confidence": confidence,
            "features_used": FEATURE_COLS,
            "metrics": {
                "walk_forward_accuracy": f"{avg_acc}%",
                "precision": f"{avg_prec}%",
                "recall": f"{avg_rec}%",
                "f1_score": f"{avg_f1}%",
                "mae": f"{avg_mae}%",
                "splits_tested": n_splits
            },
            "validation_method": "TimeSeriesSplit Walk-Forward (Strict No-Lookahead)",
            "training_period": f"Past {len(train_df)} daily trading records",
            "prediction_timestamp": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
            "disclaimer": "Predictions are probabilistic estimates based on historical statistical patterns. Never treated as guaranteed return or financial advice."
        }

stock_predictor = StockPredictor()
