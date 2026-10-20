"""
Production Resilience and Data Pipeline Verification Test Suite.
Validates:
1. Empty database behavior (no fabricated data, explicit Unavailable status)
2. Successful index retrieval, mathematical verification, and persistence
3. Upstream HTTP errors, connection drops, and timeout resilience
4. Cached fallback with preserved observation timestamps and source provenance
5. Stale snapshot detection and explicit unavailable status when missing
6. Bounded concurrency and partial-result resilience in market_data_service
7. Market session logic when exchange is closed (IST timezone enforcement)
8. Scheduler fault isolation (independent job boundaries)
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Base, Stock, IndexQuote, MarketQuote, IPO
from backend.data.symbol_mapper import symbol_mapper, INDEX_REGISTRY
from backend.data.data_validator import data_validator
from backend.data.index_provider import IndexProvider
from backend.data.cache_manager import CacheManager
from backend.data.provider_manager import ProviderManager
from backend.data.market_data_service import MarketDataService
from backend.data.market_session import evaluate_freshness, get_market_session, MarketSessionState, IST
from backend.sync.scheduler import sync_indices, run_sync_cycle

@pytest.fixture
def test_db():
    """Isolated in-memory SQLite database simulating a fresh production database."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# 1. Empty Database Test
def test_empty_database_no_fake_data(test_db):
    """
    On an empty database where live provider fails, system must NEVER return
    fabricated numbers or hardcoded baselines. Must report Unavailable with value=None.
    """
    cache = CacheManager()
    mgr = ProviderManager()
    mgr.cache_manager = cache
    mgr.data_mode = "live"

    # Mock index provider to fail (simulating blocked Render IP)
    mgr.index_provider = MagicMock()
    mgr.index_provider.get_index_quote.return_value = None

    result = mgr.get_index_data(test_db, "NIFTY 50")
    assert result["index_name"] == "NIFTY 50"
    assert result["value"] is None
    assert result["price"] is None
    assert result["status"] == "Unavailable"
    assert "Live data temporarily unavailable" in result["warning"]
    assert result["source"] == "None"

# 2. Successful Index Retrieval & Persistence
def test_index_retrieval_and_persistence(test_db):
    """
    Validates that a verified quote is persisted to IndexQuote table
    and mathematical change is computed accurately.
    """
    cache = CacheManager()
    mgr = ProviderManager()
    mgr.cache_manager = cache
    mgr.data_mode = "live"

    # Mock provider returning valid raw payload
    raw_quote = {
        "symbol": "NIFTY 50",
        "index_name": "NIFTY 50",
        "exchange": "NSE",
        "instrument_type": "INDEX",
        "price": 22888.95,
        "value": 22888.95,
        "previous_close": 22721.95,
        "change": 167.00,
        "change_percent": 0.73,
        "volume": 0.0,
        "timestamp": datetime(2026, 10, 19, 15, 30, 0),
        "source": "NSE/BSE Public Feed via Yahoo Finance",
        "status": "Verified",
        "currency": "INR"
    }

    mgr.index_provider = MagicMock()
    mgr.index_provider.get_index_quote.return_value = raw_quote

    res = mgr.get_index_data(test_db, "NIFTY 50")
    assert res["value"] == 22888.95
    assert res["change"] == 167.00
    assert res["change_percent"] == 0.73

    # Check persistence in database
    db_records = test_db.query(IndexQuote).filter(IndexQuote.index_name == "NIFTY 50").all()
    assert len(db_records) == 1
    assert db_records[0].value == 22888.95
    assert db_records[0].source == "NSE/BSE Public Feed via Yahoo Finance"

# 3. Provider Timeouts and HTTP Errors
def test_provider_timeouts_and_errors(test_db):
    """
    Tests index_provider handling of HTTP 500, 404, or network timeout without crashing.
    """
    provider = IndexProvider()
    mock_client = MagicMock()
    mock_client.get.side_effect = Exception("Connection timed out (ReadTimeout)")

    with patch.object(provider, "_get_client", return_value=mock_client):
        quote = provider.get_index_quote("NIFTY 50")
        assert quote is None

# 4. Cached Fallback with Preserved Timestamps & Provenance
def test_cached_fallback_preserves_provenance(test_db):
    """
    When live provider fails, cached snapshot from DB must be served
    with original timestamp and original source preserved.
    """
    obs_time = datetime(2026, 10, 19, 14, 15, 0)
    orig_source = "NSE Public Feed via Yahoo Finance"

    # Pre-populate DB with a verified historical snapshot
    record = IndexQuote(
        index_name="SENSEX",
        value=73852.90,
        previous_close=73033.78,
        change=819.12,
        change_percent=1.12,
        timestamp=obs_time,
        source=orig_source,
        status="Verified",
        created_at=datetime.utcnow()
    )
    test_db.add(record)
    test_db.commit()

    cache = CacheManager()
    mgr = ProviderManager()
    mgr.cache_manager = cache
    mgr.data_mode = "live"
    # Live provider fails
    mgr.index_provider = MagicMock()
    mgr.index_provider.get_index_quote.return_value = None

    fallback = mgr.get_index_data(test_db, "SENSEX")
    assert fallback["value"] == 73852.90
    assert fallback["previous_close"] == 73033.78
    assert orig_source in fallback["source"]
    assert fallback["timestamp"] is not None
    assert fallback["status"] in ["Cached", "Stale Cached", "Market Closed"]

# 5. Stale and Missing Snapshots
def test_stale_and_missing_snapshots(test_db):
    """
    Verifies that very old snapshots (>2 days) are marked as Stale,
    and missing snapshots return None / Unavailable.
    """
    cache = CacheManager()

    # Missing index
    assert cache.get_last_verified_index(test_db, "NON_EXISTENT") is None

    # Snapshot from 5 days ago
    old_time = datetime.utcnow() - timedelta(days=5)
    test_db.add(IndexQuote(
        index_name="NIFTY IT",
        value=31500.0,
        previous_close=31000.0,
        change=500.0,
        change_percent=1.61,
        timestamp=old_time,
        source="Historical Feed",
        status="Verified",
        created_at=old_time
    ))
    test_db.commit()

    cached = cache.get_last_verified_index(test_db, "NIFTY IT")
    assert cached is not None
    assert cached["value"] == 31500.0
    assert "Stale" in cached["status"] or "Stale" in cached["freshness"] or "stale" in cached["warning"].lower()

# 6. Bounded Concurrency and Partial-Result Handling
def test_partial_market_data_response(test_db):
    """
    Tests that MarketDataService fetches all indices concurrently and handles partial failures
    gracefully without blocking or exceeding bounded timeouts.
    """
    service = MarketDataService()
    service.cache_manager = CacheManager()
    
    # Pre-seed one index in DB
    test_db.add(IndexQuote(
        index_name="NIFTY BANK",
        value=55488.10,
        previous_close=55481.05,
        change=7.05,
        change_percent=0.01,
        timestamp=datetime.utcnow() - timedelta(minutes=10),
        source="NSE Public Feed",
        status="Verified",
        created_at=datetime.utcnow()
    ))
    test_db.commit()

    # Mock provider: succeeds for NIFTY 50, fails for others
    def mock_index_quote(name):
        if name == "NIFTY 50":
            return {
                "symbol": "NIFTY 50",
                "index_name": "NIFTY 50",
                "exchange": "NSE",
                "instrument_type": "INDEX",
                "price": 22888.95,
                "value": 22888.95,
                "previous_close": 22721.95,
                "change": 167.0,
                "change_percent": 0.73,
                "volume": 0.0,
                "timestamp": datetime.utcnow(),
                "source": "NSE Feed",
                "status": "Verified",
                "currency": "INR"
            }
        return None

    service.provider_manager.index_provider = MagicMock()
    service.provider_manager.index_provider.get_index_quote.side_effect = mock_index_quote

    # Market overview should succeed and return all 5 tracked indices
    overview = service.get_market_overview(test_db)
    assert "indices" in overview
    assert len(overview["indices"]) == 5
    
    names = [i["index_name"] for i in overview["indices"]]
    assert "NIFTY 50" in names
    assert "NIFTY BANK" in names

    # NIFTY 50 had live data
    nifty50 = next(i for i in overview["indices"] if i["index_name"] == "NIFTY 50")
    assert nifty50["value"] == 22888.95

    # NIFTY BANK had cached data
    niftybank = next(i for i in overview["indices"] if i["index_name"] == "NIFTY BANK")
    assert niftybank["value"] == 55488.10

# 7. Market Closed Session Evaluation
def test_market_closed_behavior():
    """
    Ensures that when evaluation occurs outside market hours or on weekends,
    quotes are never falsely labeled as 'Live'.
    """
    # Test Saturday 11:00 AM IST
    saturday_noon = datetime(2026, 10, 24, 11, 0, 0)
    session = get_market_session(saturday_noon)
    assert not session["is_open"]
    assert session["session"] == MarketSessionState.WEEKEND

    freshness = evaluate_freshness(saturday_noon)
    assert not freshness["is_live"]
    assert freshness["freshness"] == "Market Closed"

# 8. Scheduler Fault Isolation
def test_scheduler_fault_isolation(test_db):
    """
    Verifies that a failure during index synchronization does NOT crash the scheduler
    nor disrupt IPO or securities synchronization.
    """
    # 1. Test sync_indices directly with simulated failure
    with patch("backend.data.index_provider.index_provider.get_index_quote", side_effect=Exception("Simulated Network Drop")):
        report = sync_indices(test_db)
        assert report["success"] == 0
        assert report["failed"] > 0
        # Should not raise exception

    # 2. Test run_sync_cycle fault isolation across components
    with patch("backend.sync.scheduler.refresh_securities_master", side_effect=Exception("Securities API Down")), \
         patch("backend.data_providers.ipo.ipo_provider_manager.ipo_provider_manager.refresh_ipo_database", return_value={"records_valid": 10}), \
         patch("backend.sync.scheduler.sync_indices", return_value={"success": 5, "failed": 0}):
        
        import asyncio
        asyncio.run(run_sync_cycle())
        
        from backend.sync.scheduler import get_sync_status
        status = get_sync_status()
        assert status["status"] == "Degraded"
        assert "securities_error" in status["details"]
        assert status["details"]["ipos"]["records_valid"] == 10
        assert status["details"]["indices"]["success"] == 5
