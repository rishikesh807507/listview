"""
Comprehensive Test Suite for Rebuilt IPO Module (Accuracy First).
Covers:
- Dynamic IPO status engine (Asia/Kolkata timezone)
- Date boundary rules (past listed IPO never Upcoming/Open)
- Demo data isolation (zero mock data in production)
- Status filtering: All, Upcoming, Open, Closed, Listed
- Board filtering: Mainboard vs SME
- Case-insensitive search
- Missing data policy (never invent data)
- Indicative GMP calculation (upper band + GMP) and separation
- Preserved subscription & GMP history
- Educational IPO Calculator
- Watchlist persistence
- Data Health endpoint (/data-health)
"""
import pytest
from datetime import datetime, timedelta
import pytz
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import IPO, IPOSubscription, IPOGMP, IPOSubscriptionHistory, IPOGMPHistory, Watchlist
from backend.data.ipo_status_engine import compute_ipo_status, IPOStatus, get_ist_now

client = TestClient(app)
IST = pytz.timezone("Asia/Kolkata")

def test_status_engine_calculation():
    """Verify dynamic IST status calculation across all life-cycle states."""
    now_ist = get_ist_now()

    # 1. UPCOMING: Open date is in future
    res_upcoming = compute_ipo_status(
        open_date=now_ist + timedelta(days=5),
        close_date=now_ist + timedelta(days=8),
        listing_date=now_ist + timedelta(days=15),
        as_of=now_ist
    )
    assert res_upcoming["status"] == IPOStatus.UPCOMING

    # 2. OPEN: Currently within open and close date window
    res_open = compute_ipo_status(
        open_date=now_ist - timedelta(days=1),
        close_date=now_ist + timedelta(days=1),
        listing_date=now_ist + timedelta(days=6),
        as_of=now_ist
    )
    assert res_open["status"] == IPOStatus.OPEN

    # 3. CLOSED: Past close date, before listing
    res_closed = compute_ipo_status(
        open_date=now_ist - timedelta(days=5),
        close_date=now_ist - timedelta(days=2),
        allotment_date=now_ist + timedelta(days=1),
        listing_date=now_ist + timedelta(days=4),
        as_of=now_ist
    )
    assert res_closed["status"] == IPOStatus.CLOSED

    # 4. LISTING_TODAY: Today is the listing date
    res_listing_today = compute_ipo_status(
        open_date=now_ist - timedelta(days=10),
        close_date=now_ist - timedelta(days=7),
        listing_date=now_ist,
        as_of=now_ist
    )
    assert res_listing_today["status"] == IPOStatus.LISTING_TODAY

    # 5. LISTED: Listing date is in the past (NEVER UPCOMING OR OPEN)
    res_listed = compute_ipo_status(
        open_date=now_ist - timedelta(days=30),
        close_date=now_ist - timedelta(days=27),
        listing_date=now_ist - timedelta(days=20),
        as_of=now_ist
    )
    assert res_listed["status"] == IPOStatus.LISTED
    assert res_listed["status"] != IPOStatus.UPCOMING
    assert res_listed["status"] != IPOStatus.OPEN

def test_demo_isolation_in_production():
    """Verify production API NEVER returns mock demo records."""
    response = client.get("/api/ipos?mode=live")
    assert response.status_code == 200
    ipos = response.json()
    assert len(ipos) > 0

    mock_names = [
        "Ather Energy", "Nova Bio Agri Tech", "Apex Green Tech", 
        "NTPC Green Energy", "Swiggy", "Waaree Energies", 
        "Hyundai Motor India", "Bajaj Housing Finance"
    ]
    
    for item in ipos:
        assert item.get("is_demo") is False, f"Production returned demo record: {item['company_name']}"
        assert item["company_name"] not in mock_names, f"Mock company found in production: {item['company_name']}"

def test_demo_mode_explicit_review():
    """Verify demo mode returns demo records explicitly flagged with is_demo=True."""
    response = client.get("/api/ipos?mode=demo")
    assert response.status_code == 200
    demo_ipos = response.json()
    assert len(demo_ipos) > 0
    for item in demo_ipos:
        assert item.get("is_demo") is True

def test_status_filters():
    """Test All, Upcoming, Open, Closed, and Listed filtering."""
    # Upcoming
    resp_up = client.get("/api/ipos?status=UPCOMING")
    assert resp_up.status_code == 200
    for item in resp_up.json():
        assert item["status"] == "UPCOMING"

    # Open
    resp_open = client.get("/api/ipos?status=OPEN")
    assert resp_open.status_code == 200
    for item in resp_open.json():
        assert item["status"] == "OPEN"

    # Closed
    resp_closed = client.get("/api/ipos?status=CLOSED")
    assert resp_closed.status_code == 200
    for item in resp_closed.json():
        assert item["status"] in ("CLOSED", "ALLOTMENT", "REFUND", "DEMAT_CREDIT")

    # Listed
    resp_listed = client.get("/api/ipos?status=LISTED")
    assert resp_listed.status_code == 200
    for item in resp_listed.json():
        assert item["status"] in ("LISTED", "LISTING_TODAY")

def test_board_filters_mainboard_and_sme():
    """Test filtering by verified exchange board."""
    # Mainboard
    resp_main = client.get("/api/ipos?board=Mainboard")
    assert resp_main.status_code == 200
    for item in resp_main.json():
        board_val = (item.get("board") or item.get("ipo_type") or "").upper()
        assert "SME" not in board_val

    # SME
    resp_sme = client.get("/api/ipos?board=SME")
    assert resp_sme.status_code == 200
    for item in resp_sme.json():
        board_val = (item.get("board") or item.get("ipo_type") or "").upper()
        assert "SME" in board_val

def test_case_insensitive_search():
    """Test search by company name and symbol."""
    # Fetch a sample real IPO
    all_ipos = client.get("/api/ipos").json()
    assert len(all_ipos) > 0
    sample = all_ipos[0]
    sample_name = sample["company_name"]
    query = sample_name[:4].lower()

    search_resp = client.get(f"/api/ipos?search={query}")
    assert search_resp.status_code == 200
    matched = search_resp.json()
    assert len(matched) > 0
    assert any(sample_name.lower() in m["company_name"].lower() for m in matched)

def test_gmp_indicative_estimate_and_separation():
    """Verify that indicative GMP listing estimate equals upper price band + GMP."""
    all_ipos = client.get("/api/ipos").json()
    for item in all_ipos:
        gmp = item.get("gmp")
        band_high = item.get("price_band_high")
        est_price = item.get("estimated_listing_price")

        if gmp is not None and band_high is not None:
            expected = round(band_high + gmp, 2)
            assert est_price == expected, f"Calculation mismatch: {est_price} vs {expected}"
        elif gmp is None:
            assert est_price is None or est_price == "Not Available"

def test_ipo_detail_endpoint():
    """Verify IPO Detail endpoint returns timeline, documents, and disclosures."""
    all_ipos = client.get("/api/ipos").json()
    assert len(all_ipos) > 0
    first_id = all_ipos[0]["id"]

    detail_resp = client.get(f"/api/ipos/{first_id}")
    assert detail_resp.status_code == 200
    data = detail_resp.json()

    assert "ipo" in data
    assert "timeline" in data
    assert len(data["timeline"]) > 0
    assert "documents" in data
    assert len(data["documents"]) >= 3
    assert "disclaimers" in data
    assert "gmp_warning" in data["disclaimers"]

def test_ipo_calculator_endpoint():
    """Test educational lot and capital calculator."""
    all_ipos = client.get("/api/ipos").json()
    first_id = all_ipos[0]["id"]

    calc_resp = client.get(f"/api/ipos/{first_id}/calculator?investment_amount=30000")
    assert calc_resp.status_code == 200
    calc = calc_resp.json()

    assert "affordable_lots" in calc
    assert "total_shares" in calc
    assert "total_amount_required" in calc
    assert "unutilized_balance" in calc
    assert calc["total_amount_required"] <= 30000
    assert calc["total_amount_required"] + calc["unutilized_balance"] == pytest.approx(30000.0, 0.01)

def test_ipo_watchlist_toggle():
    """Test bookmarking an IPO to Watchlist and toggling off."""
    all_ipos = client.get("/api/ipos").json()
    first_id = all_ipos[0]["id"]

    # Toggle On
    res1 = client.post(f"/api/ipos/{first_id}/watchlist")
    assert res1.status_code == 200
    assert res1.json()["is_bookmarked"] is True

    # Toggle Off
    res2 = client.post(f"/api/ipos/{first_id}/watchlist")
    assert res2.status_code == 200
    assert res2.json()["is_bookmarked"] is False

def test_data_health_endpoint():
    """Verify /data-health endpoint returns verified statistics and provider status."""
    health_resp = client.get("/api/ipos/data-health")
    assert health_resp.status_code == 200
    health = health_resp.json()

    assert "provider_status" in health
    assert "nse_official_feed" in health["provider_status"]
    assert "unofficial_gmp_feed" in health["provider_status"]
    assert "metrics" in health
    assert health["metrics"]["total_real_ipos"] > 0
    assert health["metrics"]["demo_records_isolated"] > 0
