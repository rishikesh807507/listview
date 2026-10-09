import numpy as np
import pandas as pd
from typing import Tuple, List

def calculate_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes time-series technical indicators without future lookahead bias.
    df must be sorted chronologically by timestamp.
    """
    data = df.copy()
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data = data.sort_values('timestamp').reset_index(drop=True)
    
    # 1. Simple Moving Averages
    data['sma_5'] = data['close'].rolling(window=5, min_periods=5).mean()
    data['sma_20'] = data['close'].rolling(window=20, min_periods=20).mean()
    data['sma_50'] = data['close'].rolling(window=50, min_periods=50).mean()
    
    # 2. Exponential Moving Averages
    data['ema_12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['ema_26'] = data['close'].ewm(span=26, adjust=False).mean()
    
    # 3. MACD
    data['macd'] = data['ema_12'] - data['ema_26']
    data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
    data['macd_hist'] = data['macd'] - data['macd_signal']
    
    # 4. RSI (Relative Strength Index - 14 period)
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss.replace(0, np.nan))
    data['rsi_14'] = 100 - (100 / (1 + rs))
    data['rsi_14'] = data['rsi_14'].fillna(50)
    
    # 5. Bollinger Bands (20, 2)
    bb_mean = data['close'].rolling(window=20).mean()
    bb_std = data['close'].rolling(window=20).std()
    data['bb_upper'] = bb_mean + 2 * bb_std
    data['bb_lower'] = bb_mean - 2 * bb_std
    data['bb_position'] = (data['close'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'] + 1e-8)
    
    # 6. Returns & Volatility
    data['return_1d'] = data['close'].pct_change(1)
    data['return_5d'] = data['close'].pct_change(5)
    data['volatility_20'] = data['return_1d'].rolling(window=20).std() * np.sqrt(252)
    
    # 7. Volume dynamics
    data['vol_sma_20'] = data['volume'].rolling(window=20).mean()
    data['volume_ratio'] = data['volume'] / (data['vol_sma_20'] + 1e-8)
    
    # Forward Targets (shift backwards to strictly prevent look-ahead bias during test)
    data['target_return_1d'] = data['close'].pct_change(1).shift(-1)
    data['target_return_5d'] = data['close'].pct_change(5).shift(-5)
    data['target_return_20d'] = data['close'].pct_change(20).shift(-20)
    
    data['target_dir_1d'] = (data['target_return_1d'] > 0).astype(int)
    data['target_dir_5d'] = (data['target_return_5d'] > 0).astype(int)
    
    return data
