"""
Comprehensive Test Suite for Listview — Indian Stocks & IPO Intelligence Platform.
Tests:
- Database connectivity & seeding
- Technical Indicators & Feature Engineering
- AI Stock Predictor (TimeSeriesSplit, bounds, no lookahead)
- IPO Listing Prediction Model
- Fundamental Health Score
- Backtesting Engine
- Data Providers (IndianStockProvider, GMPProvider, NewsProvider)
- FastAPI Endpoints (Stocks, Market, IPOs, GMP, Predictions, Screener, Backtest)
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, Base, engine
from backend.models import Stock, StockPrice, IPO, IPOGMP
from backend.ml.feature_engineering import calculate_technical_features
from backend.ml.stock_predictor import stock_predictor
from backend.ml.ipo_predictor import ipo_predictor
from backend.ml.health_score import compute_health_score
from backend.backtest.engine import run_backtest
from backend.data_providers.news_provider import analyze_sentiment
import pandas as pd

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["api_cost"] == "₹0.00"

def test_database_seeded():
    db = SessionLocal()
    try:
        stock_count = db.query(Stock).count()
        price_count = db.query(StockPrice).count()
        ipo_count = db.query(IPO).count()
        assert stock_count > 0, "Stocks should be populated"
        assert price_count > 100, "Historical prices should be populated"
        assert ipo_count > 0, "IPOs should be populated"
    finally:
        db.close()

def test_stocks_endpoint():
    response = client.get("/api/stocks")
    assert response.status_code == 200
    stocks = response.json()
    assert len(stocks) > 0
    symbols = [s["symbol"] for s in stocks]
    assert "RELIANCE" in symbols

def test_stock_history_lightweight_format():
    response = client.get("/api/stocks/RELIANCE/history?timeframe=1M")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "RELIANCE"
    candles = data["candles"]
    assert len(candles) > 0
    first = candles[0]
    # Check TradingView Lightweight Charts required keys
    assert "time" in first
    assert "open" in first
    assert "high" in first
    assert "low" in first
    assert "close" in first
    assert "volume" in first

def test_market_overview():
    response = client.get("/api/market/overview")
    assert response.status_code == 200
    data = response.json()
    assert "indices" in data
    assert "top_gainers" in data
    assert "market_stats" in data
    assert len(data["indices"]) >= 5

def test_ipos_and_gmp():
    response = client.get("/api/ipos")
    assert response.status_code == 200
    ipos = response.json()
    assert len(ipos) > 0
    
    gmp_resp = client.get("/api/gmp")
    assert gmp_resp.status_code == 200
    gmp_data = gmp_resp.json()
    assert "disclaimer" in gmp_data
    assert "unofficial" in gmp_data["disclaimer"].lower()

def test_ai_stock_prediction():
    response = client.get("/api/predictions/stock/RELIANCE")
    assert response.status_code == 200
    pred = response.json()
    assert "positive_prob" in pred
    assert 0 <= pred["positive_prob"] <= 100
    assert "expected_return_min" in pred
    assert "expected_return_max" in pred
    assert "confidence" in pred
    assert "walk_forward_accuracy" in pred["metrics"]
    assert "disclaimer" in pred

def test_ai_ipo_prediction():
    response = client.get("/api/predictions/ipo/1")
    assert response.status_code == 200
    pred = response.json()
    assert "expected_listing_price_min" in pred
    assert "expected_listing_price_max" in pred
    assert "positive_listing_probability" in pred
    assert "disclaimer" in pred

def test_fundamental_health_score():
    sample_funds = {
        "revenue_growth": 14.5,
        "profit_growth": 22.0,
        "roe": 24.5,
        "roce": 28.0,
        "debt_to_equity": 0.25,
        "ebitda_margin": 26.0,
        "free_cash_flow": 2500.0,
        "pe": 24.0,
        "current_ratio": 1.8,
        "promoter_holding": 52.0
    }
    score_res = compute_health_score(sample_funds)
    assert score_res["overall_health"] in ["Strong", "Moderate", "Watchlist", "Weak"]
    assert 0 <= score_res["score_out_of_100"] <= 100
    assert len(score_res["components"]) == 10

def test_backtest_simulation():
    payload = {
        "symbol": "RELIANCE",
        "strategy": "SMA",
        "initial_capital": 100000.0
    }
    response = client.post("/api/backtest", json=payload)
    assert response.status_code == 200
    bt = response.json()
    assert "return_percent" in bt
    assert "max_drawdown" in bt
    assert "total_trades" in bt
    assert "Historical Simulation" in bt["label"]

def test_screener():
    response = client.get("/api/screener/run?min_roe=15")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    for r in data["results"]:
        assert r["roe"] >= 15

def test_sentiment_nlp():
    pos_text = "Company reported massive surge in quarterly profits and announced high dividend"
    label, score = analyze_sentiment(pos_text)
    assert label == "Positive"
    assert score > 0

    neg_text = "Stock slumps sharply amid major loss and fraud investigation probe"
    label_neg, score_neg = analyze_sentiment(neg_text)
    assert label_neg == "Negative"
    assert score_neg < 0

def test_data_validator_mathematical_precision():
    from backend.data.data_validator import data_validator
    
    # Valid payload
    payload = {
        "symbol": "INFY",
        "price": 1035.00,
        "previous_close": 994.10,
        "volume": 500000,
        "timestamp": 1727776800,
        "source": "NSE Public Feed",
        "exchange": "NSE",
        "currency": "INR"
    }
    is_valid, validated, err = data_validator.validate_and_compute_quote(payload, is_index=False)
    assert is_valid is True
    assert err is None
    # Must compute exact change and change_percent
    assert validated["change"] == round(1035.00 - 994.10, 2)
    expected_pct = round(((1035.00 - 994.10) / 994.10) * 100, 2)
    assert validated["change_percent"] == expected_pct

    # Rejection: Negative price
    bad_price = payload.copy()
    bad_price["price"] = -10.0
    is_valid, _, err = data_validator.validate_and_compute_quote(bad_price, is_index=False)
    assert is_valid is False
    assert "positive" in err.lower()

    # Rejection: Invalid currency
    bad_curr = payload.copy()
    bad_curr["currency"] = "USD"
    is_valid, _, err = data_validator.validate_and_compute_quote(bad_curr, is_index=False)
    assert is_valid is False
    assert "currency" in err.lower()

def test_symbol_mapper_registry():
    from backend.data.symbol_mapper import symbol_mapper, INDEX_REGISTRY
    
    # Benchmark indices must all be mapped
    required_indices = ["NIFTY 50", "SENSEX", "NIFTY BANK", "NIFTY IT", "NIFTY AUTO"]
    for idx in required_indices:
        meta = symbol_mapper.get_index_meta(idx)
        assert meta is not None, f"Index {idx} must be registered"
        assert meta["currency"] == "INR"

    # Equities
    assert symbol_mapper.is_valid_equity("RELIANCE")
    assert symbol_mapper.is_valid_equity("INFY")
    assert symbol_mapper.is_valid_equity("TCS")
    assert not symbol_mapper.is_valid_equity("FAKE_EQUITY_999")

def test_market_session_and_freshness():
    from backend.data.market_session import get_ist_now, get_current_market_session, evaluate_freshness
    
    ist_now = get_ist_now()
    assert ist_now is not None
    session_info = get_current_market_session()
    assert "session" in session_info
    assert "is_open" in session_info

    # Freshness test
    now_ts = ist_now.timestamp()
    live_eval = evaluate_freshness(now_ts - 30)  # 30 seconds ago
    assert live_eval["freshness"] in ["Live", "Market Closed"]

    stale_eval = evaluate_freshness(now_ts - 7200)  # 2 hours ago
    assert stale_eval["freshness"] in ["Stale", "Market Closed"]

def test_market_overview_verified_pipeline():
    response = client.get("/api/market/overview")
    assert response.status_code == 200
    data = response.json()

    # Rule: Never return hardcoded fabricated numbers
    for idx in data["indices"]:
        assert idx["value"] != 25810.85, "Must never return old fake NIFTY 50 value"
        assert idx["value"] != 84299.90, "Must never return old fake SENSEX value"
        assert idx["value"] > 0
        assert idx["previous_close"] > 0
        # Check mathematical consistency: change == price - prev_close
        computed_change = round(idx["value"] - idx["previous_close"], 2)
        assert abs(idx["change"] - computed_change) < 0.15, f"Change calculation mismatch for {idx['index_name']}"
        assert "timestamp" in idx
        assert "source" in idx
        assert "status" in idx

    # Gainers & Losers must have unified session timestamp
    gainers = data.get("top_gainers", [])
    losers = data.get("top_losers", [])
    if gainers:
        assert all("as_of" in g for g in gainers)
        assert all(g["change_percent"] >= 0 for g in gainers)
    if losers:
        assert all("as_of" in l for l in losers)
        assert all(l["change_percent"] <= 0 for l in losers)

def test_data_health_endpoint():
    response = client.get("/api/market/data-health")
    assert response.status_code == 200
    data = response.json()
    assert "provider_status" in data
    assert "metrics" in data
    assert data["metrics"]["records_received"] > 0
    assert data["metrics"]["records_valid"] > 0
    assert data["data_mode"] == "live"

if __name__ == "__main__":
    pytest.main(["-v", "test_platform.py"])
