"""
Script to generate rich, realistic offline demo data for Indian Stock Market & IPO Platform.
Creates all required CSV and JSON files in demo-data/ directory.
"""
import os
import json
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent / "demo-data"
DEMO_DIR.mkdir(parents=True, exist_ok=True)

# 1. STOCKS DATA
STOCKS = [
    {
        "symbol": "RELIANCE",
        "name": "Reliance Industries Ltd",
        "exchange": "NSE",
        "sector": "Energy",
        "industry": "Oil & Gas Refining & Marketing",
        "current_price": 2980.50,
        "change": 24.15,
        "change_percent": 0.82,
        "market_cap": 2016500.0,
        "pe_ratio": 28.4,
        "pb_ratio": 2.35,
        "roe": 9.8,
        "roce": 11.2,
        "dividend_yield": 0.34,
        "debt_to_equity": 0.38,
        "high_52w": 3217.90,
        "low_52w": 2221.05,
        "volume": 6842100
    },
    {
        "symbol": "TCS",
        "name": "Tata Consultancy Services Ltd",
        "exchange": "NSE",
        "sector": "IT",
        "industry": "IT Consulting & Software",
        "current_price": 4210.75,
        "change": -15.40,
        "change_percent": -0.36,
        "market_cap": 1523400.0,
        "pe_ratio": 32.1,
        "pb_ratio": 14.8,
        "roe": 48.2,
        "roce": 59.1,
        "dividend_yield": 1.25,
        "debt_to_equity": 0.05,
        "high_52w": 4585.90,
        "low_52w": 3313.00,
        "volume": 2154300
    },
    {
        "symbol": "HDFCBANK",
        "name": "HDFC Bank Ltd",
        "exchange": "NSE",
        "sector": "Banking",
        "industry": "Private Sector Bank",
        "current_price": 1682.30,
        "change": 12.80,
        "change_percent": 0.77,
        "market_cap": 1284500.0,
        "pe_ratio": 19.4,
        "pb_ratio": 2.75,
        "roe": 16.5,
        "roce": 14.8,
        "dividend_yield": 1.16,
        "debt_to_equity": 0.92,
        "high_52w": 1794.00,
        "low_52w": 1363.45,
        "volume": 14205000
    },
    {
        "symbol": "INFY",
        "name": "Infosys Ltd",
        "exchange": "NSE",
        "sector": "IT",
        "industry": "IT Consulting & Software",
        "current_price": 1915.20,
        "change": 31.45,
        "change_percent": 1.67,
        "market_cap": 795400.0,
        "pe_ratio": 29.8,
        "pb_ratio": 8.9,
        "roe": 31.8,
        "roce": 40.5,
        "dividend_yield": 2.1,
        "debt_to_equity": 0.08,
        "high_52w": 1991.45,
        "low_52w": 1358.35,
        "volume": 5840200
    },
    {
        "symbol": "ICICIBANK",
        "name": "ICICI Bank Ltd",
        "exchange": "NSE",
        "sector": "Banking",
        "industry": "Private Sector Bank",
        "current_price": 1245.60,
        "change": 8.90,
        "change_percent": 0.72,
        "market_cap": 876300.0,
        "pe_ratio": 18.2,
        "pb_ratio": 3.1,
        "roe": 18.4,
        "roce": 16.9,
        "dividend_yield": 0.85,
        "debt_to_equity": 0.86,
        "high_52w": 1318.00,
        "low_52w": 913.40,
        "volume": 9482000
    },
    {
        "symbol": "BHARTIARTL",
        "name": "Bharti Airtel Ltd",
        "exchange": "NSE",
        "sector": "Telecom",
        "industry": "Telecom Services",
        "current_price": 1690.40,
        "change": 22.10,
        "change_percent": 1.32,
        "market_cap": 962100.0,
        "pe_ratio": 64.2,
        "pb_ratio": 9.4,
        "roe": 15.8,
        "roce": 13.9,
        "dividend_yield": 0.48,
        "debt_to_equity": 1.74,
        "high_52w": 1779.00,
        "low_52w": 912.10,
        "volume": 4120300
    },
    {
        "symbol": "TATAMOTORS",
        "name": "Tata Motors Ltd",
        "exchange": "NSE",
        "sector": "Automobile",
        "industry": "Commercial & Passenger Vehicles",
        "current_price": 985.25,
        "change": -8.60,
        "change_percent": -0.87,
        "market_cap": 362400.0,
        "pe_ratio": 11.4,
        "pb_ratio": 3.9,
        "roe": 34.6,
        "roce": 21.8,
        "dividend_yield": 0.61,
        "debt_to_equity": 0.78,
        "high_52w": 1179.00,
        "low_52w": 621.50,
        "volume": 7654000
    },
    {
        "symbol": "SUNPHARMA",
        "name": "Sun Pharmaceutical Industries Ltd",
        "exchange": "NSE",
        "sector": "Pharma",
        "industry": "Pharmaceuticals",
        "current_price": 1910.80,
        "change": 14.50,
        "change_percent": 0.76,
        "market_cap": 458300.0,
        "pe_ratio": 38.5,
        "pb_ratio": 6.2,
        "roe": 16.7,
        "roce": 18.2,
        "dividend_yield": 0.72,
        "debt_to_equity": 0.05,
        "high_52w": 1960.00,
        "low_52w": 1110.00,
        "volume": 2490000
    },
    {
        "symbol": "ITC",
        "name": "ITC Ltd",
        "exchange": "NSE",
        "sector": "FMCG",
        "industry": "Diversified FMCG",
        "current_price": 508.15,
        "change": 3.40,
        "change_percent": 0.67,
        "market_cap": 634800.0,
        "pe_ratio": 29.8,
        "pb_ratio": 8.7,
        "roe": 29.4,
        "roce": 37.1,
        "dividend_yield": 2.72,
        "debt_to_equity": 0.01,
        "high_52w": 528.50,
        "low_52w": 399.30,
        "volume": 12840000
    },
    {
        "symbol": "LT",
        "name": "Larsen & Toubro Ltd",
        "exchange": "NSE",
        "sector": "Infrastructure",
        "industry": "Engineering & Construction",
        "current_price": 3645.00,
        "change": -22.50,
        "change_percent": -0.61,
        "market_cap": 501200.0,
        "pe_ratio": 37.8,
        "pb_ratio": 5.1,
        "roe": 15.3,
        "roce": 14.2,
        "dividend_yield": 0.94,
        "debt_to_equity": 1.25,
        "high_52w": 3919.90,
        "low_52w": 2965.00,
        "volume": 1980000
    }
]

# Write stocks.csv
with open(DEMO_DIR / "stocks.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(STOCKS[0].keys()))
    writer.writeheader()
    writer.writerows(STOCKS)

print(f"Generated {len(STOCKS)} stocks into stocks.csv")

# 2. HISTORICAL OHLCV PRICES (Daily for past ~250 trading days)
random.seed(42)
historical_rows = []
end_date = datetime.now()
days_count = 250

for stock in STOCKS:
    sym = stock["symbol"]
    curr = stock["current_price"]
    price = curr * 0.75  # Start from ~25% lower 250 days ago
    
    current_dt = end_date - timedelta(days=int(days_count * 1.45))
    day_idx = 0
    while day_idx < days_count:
        current_dt += timedelta(days=1)
        # skip weekends
        if current_dt.weekday() >= 5:
            continue
        
        # Daily drift towards current_price
        target_step = (curr - price) / (days_count - day_idx + 1)
        pct_change = random.gauss(0.0008, 0.016)
        day_open = round(price * (1 + random.gauss(0, 0.005)), 2)
        day_close = round(day_open * (1 + pct_change) + target_step, 2)
        day_high = round(max(day_open, day_close) * (1 + abs(random.gauss(0.004, 0.006))), 2)
        day_low = round(min(day_open, day_close) * (1 - abs(random.gauss(0.004, 0.006))), 2)
        volume = int(stock["volume"] * random.uniform(0.6, 1.6))
        
        price = day_close
        day_idx += 1
        
        historical_rows.append({
            "symbol": sym,
            "exchange": "NSE",
            "timestamp": current_dt.strftime("%Y-%m-%d"),
            "open": day_open,
            "high": day_high,
            "low": day_low,
            "close": day_close,
            "volume": volume,
            "source": "demo_bundled"
        })

with open(DEMO_DIR / "historical_prices.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(historical_rows[0].keys()))
    writer.writeheader()
    writer.writerows(historical_rows)

print(f"Generated {len(historical_rows)} historical price rows into historical_prices.csv")

# 3. FUNDAMENTALS
FUNDAMENTALS = [
    {
        "symbol": "RELIANCE", "revenue": 997450.0, "revenue_growth": 11.2, "ebitda": 178200.0,
        "ebitda_margin": 17.8, "net_profit": 69620.0, "profit_growth": 7.4, "eps": 102.8,
        "pe": 28.4, "pb": 2.35, "roe": 9.8, "roce": 11.2, "debt": 312000.0,
        "debt_to_equity": 0.38, "current_ratio": 1.15, "dividend_yield": 0.34,
        "free_cash_flow": 38400.0, "promoter_holding": 50.3, "market_cap": 2016500.0,
        "enterprise_value": 2290100.0, "period": "FY2025-26"
    },
    {
        "symbol": "TCS", "revenue": 240890.0, "revenue_growth": 6.8, "ebitda": 65120.0,
        "ebitda_margin": 27.0, "net_profit": 46580.0, "profit_growth": 9.1, "eps": 128.4,
        "pe": 32.1, "pb": 14.8, "roe": 48.2, "roce": 59.1, "debt": 8400.0,
        "debt_to_equity": 0.05, "current_ratio": 2.45, "dividend_yield": 1.25,
        "free_cash_flow": 41200.0, "promoter_holding": 71.8, "market_cap": 1523400.0,
        "enterprise_value": 1495000.0, "period": "FY2025-26"
    },
    {
        "symbol": "HDFCBANK", "revenue": 348200.0, "revenue_growth": 28.5, "ebitda": 94100.0,
        "ebitda_margin": 27.0, "net_profit": 64060.0, "profit_growth": 37.1, "eps": 84.5,
        "pe": 19.4, "pb": 2.75, "roe": 16.5, "roce": 14.8, "debt": 415000.0,
        "debt_to_equity": 0.92, "current_ratio": 1.20, "dividend_yield": 1.16,
        "free_cash_flow": 48000.0, "promoter_holding": 25.6, "market_cap": 1284500.0,
        "enterprise_value": 1650000.0, "period": "FY2025-26"
    },
    {
        "symbol": "INFY", "revenue": 153670.0, "revenue_growth": 4.7, "ebitda": 36890.0,
        "ebitda_margin": 24.0, "net_profit": 26230.0, "profit_growth": 8.9, "eps": 63.8,
        "pe": 29.8, "pb": 8.9, "roe": 31.8, "roce": 40.5, "debt": 7100.0,
        "debt_to_equity": 0.08, "current_ratio": 2.10, "dividend_yield": 2.1,
        "free_cash_flow": 22400.0, "promoter_holding": 14.6, "market_cap": 795400.0,
        "enterprise_value": 782000.0, "period": "FY2025-26"
    },
    {
        "symbol": "ICICIBANK", "revenue": 218900.0, "revenue_growth": 24.1, "ebitda": 71200.0,
        "ebitda_margin": 32.5, "net_profit": 44380.0, "profit_growth": 28.5, "eps": 63.2,
        "pe": 18.2, "pb": 3.1, "roe": 18.4, "roce": 16.9, "debt": 295000.0,
        "debt_to_equity": 0.86, "current_ratio": 1.18, "dividend_yield": 0.85,
        "free_cash_flow": 36500.0, "promoter_holding": 0.0, "market_cap": 876300.0,
        "enterprise_value": 1120000.0, "period": "FY2025-26"
    },
    {
        "symbol": "BHARTIARTL", "revenue": 149980.0, "revenue_growth": 7.8, "ebitda": 79840.0,
        "ebitda_margin": 53.2, "net_profit": 14600.0, "profit_growth": 78.4, "eps": 25.4,
        "pe": 64.2, "pb": 9.4, "roe": 15.8, "roce": 13.9, "debt": 152000.0,
        "debt_to_equity": 1.74, "current_ratio": 0.65, "dividend_yield": 0.48,
        "free_cash_flow": 31200.0, "promoter_holding": 53.1, "market_cap": 962100.0,
        "enterprise_value": 1098000.0, "period": "FY2025-26"
    },
    {
        "symbol": "TATAMOTORS", "revenue": 437930.0, "revenue_growth": 26.6, "ebitda": 62800.0,
        "ebitda_margin": 14.3, "net_profit": 31810.0, "profit_growth": 140.2, "eps": 82.6,
        "pe": 11.4, "pb": 3.9, "roe": 34.6, "roce": 21.8, "debt": 74500.0,
        "debt_to_equity": 0.78, "current_ratio": 0.98, "dividend_yield": 0.61,
        "free_cash_flow": 26900.0, "promoter_holding": 46.4, "market_cap": 362400.0,
        "enterprise_value": 412000.0, "period": "FY2025-26"
    },
    {
        "symbol": "SUNPHARMA", "revenue": 48490.0, "revenue_growth": 10.4, "ebitda": 13450.0,
        "ebitda_margin": 27.7, "net_profit": 10230.0, "profit_growth": 17.8, "eps": 42.6,
        "pe": 38.5, "pb": 6.2, "roe": 16.7, "roce": 18.2, "debt": 3400.0,
        "debt_to_equity": 0.05, "current_ratio": 2.30, "dividend_yield": 0.72,
        "free_cash_flow": 9800.0, "promoter_holding": 54.5, "market_cap": 458300.0,
        "enterprise_value": 452000.0, "period": "FY2025-26"
    },
    {
        "symbol": "ITC", "revenue": 76840.0, "revenue_growth": 6.5, "ebitda": 26400.0,
        "ebitda_margin": 34.3, "net_profit": 20420.0, "profit_growth": 7.9, "eps": 16.4,
        "pe": 29.8, "pb": 8.7, "roe": 29.4, "roce": 37.1, "debt": 380.0,
        "debt_to_equity": 0.01, "current_ratio": 2.85, "dividend_yield": 2.72,
        "free_cash_flow": 17500.0, "promoter_holding": 0.0, "market_cap": 634800.0,
        "enterprise_value": 618000.0, "period": "FY2025-26"
    },
    {
        "symbol": "LT", "revenue": 221110.0, "revenue_growth": 20.6, "ebitda": 23490.0,
        "ebitda_margin": 10.6, "net_profit": 13060.0, "profit_growth": 24.7, "eps": 95.1,
        "pe": 37.8, "pb": 5.1, "roe": 15.3, "roce": 14.2, "debt": 118400.0,
        "debt_to_equity": 1.25, "current_ratio": 1.22, "dividend_yield": 0.94,
        "free_cash_flow": 8200.0, "promoter_holding": 0.0, "market_cap": 501200.0,
        "enterprise_value": 605000.0, "period": "FY2025-26"
    }
]

with open(DEMO_DIR / "fundamentals.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(FUNDAMENTALS[0].keys()))
    writer.writeheader()
    writer.writerows(FUNDAMENTALS)

print(f"Generated {len(FUNDAMENTALS)} fundamentals rows into fundamentals.csv")

# 4. FINANCIAL STATEMENTS (Income, Balance Sheet, Cash Flow for 3 years)
FINANCIAL_STATEMENTS = []
years = [2024, 2025, 2026]

for stock in STOCKS:
    sym = stock["symbol"]
    f = next(item for item in FUNDAMENTALS if item["symbol"] == sym)
    base_rev = f["revenue"]
    
    for yr in years:
        mult = 1.0 if yr == 2026 else (0.88 if yr == 2025 else 0.76)
        rev = round(base_rev * mult, 2)
        opex = round(rev * 0.72, 2)
        ebitda = round(rev - opex, 2)
        ebit = round(ebitda * 0.85, 2)
        interest = round(f["debt"] * mult * 0.065, 2)
        pbt = round(ebit - interest, 2)
        tax = round(pbt * 0.25, 2)
        net_profit = round(pbt - tax, 2)
        
        income_data = {
            "revenue": rev, "operating_expenses": opex, "ebitda": ebitda,
            "ebit": ebit, "interest": interest, "profit_before_tax": pbt,
            "tax": tax, "net_profit": net_profit
        }
        
        balance_data = {
            "total_assets": round(rev * 1.4, 2), "total_liabilities": round(rev * 0.55, 2),
            "equity": round(rev * 0.85, 2), "cash": round(rev * 0.15, 2),
            "debt": round(f["debt"] * mult, 2), "current_assets": round(rev * 0.45, 2),
            "current_liabilities": round(rev * 0.35, 2)
        }
        
        cashflow_data = {
            "operating_cash_flow": round(net_profit * 1.25, 2),
            "investing_cash_flow": round(-net_profit * 0.65, 2),
            "financing_cash_flow": round(-net_profit * 0.45, 2),
            "free_cash_flow": round(net_profit * 0.60, 2)
        }
        
        FINANCIAL_STATEMENTS.append({
            "symbol": sym, "statement_type": "income", "period_type": "annual",
            "year": yr, "quarter": "", "data": json.dumps(income_data)
        })
        FINANCIAL_STATEMENTS.append({
            "symbol": sym, "statement_type": "balance_sheet", "period_type": "annual",
            "year": yr, "quarter": "", "data": json.dumps(balance_data)
        })
        FINANCIAL_STATEMENTS.append({
            "symbol": sym, "statement_type": "cash_flow", "period_type": "annual",
            "year": yr, "quarter": "", "data": json.dumps(cashflow_data)
        })

with open(DEMO_DIR / "financials.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(FINANCIAL_STATEMENTS[0].keys()))
    writer.writeheader()
    writer.writerows(FINANCIAL_STATEMENTS)

print(f"Generated {len(FINANCIAL_STATEMENTS)} financial statement rows into financials.csv")

# 5. IPOS (Upcoming, Open, Closed, Listed)
IPOS = [
    {
        "id": 1, "symbol": "SWIGGY", "company_name": "Swiggy Ltd", "ipo_type": "Mainboard",
        "price_band_low": 371.0, "price_band_high": 390.0, "lot_size": 38, "issue_size": 11327.0,
        "open_date": "2024-11-06", "close_date": "2024-11-08", "listing_date": "2024-11-13",
        "face_value": 1.0, "fresh_issue": 4499.0, "offer_for_sale": 6828.0,
        "registrar": "Link Intime India Pvt Ltd", "lead_managers": "Kotak Mahindra Capital, Citigroup, BofA Securities",
        "exchange": "NSE, BSE", "status": "Listed", "sector": "Consumer Tech / Quick Commerce",
        "revenue": 11247.0, "profit": -2350.0, "eps": -12.4, "roe": -18.5, "roce": -14.2, "debt": 480.0
    },
    {
        "id": 2, "symbol": "HYUNDAI", "company_name": "Hyundai Motor India Ltd", "ipo_type": "Mainboard",
        "price_band_low": 1865.0, "price_band_high": 1960.0, "lot_size": 7, "issue_size": 27870.0,
        "open_date": "2024-10-15", "close_date": "2024-10-17", "listing_date": "2024-10-22",
        "face_value": 10.0, "fresh_issue": 0.0, "offer_for_sale": 27870.0,
        "registrar": "KFin Technologies Ltd", "lead_managers": "Kotak Mahindra Capital, Morgan Stanley, JP Morgan",
        "exchange": "NSE, BSE", "status": "Listed", "sector": "Automobile",
        "revenue": 69829.0, "profit": 6060.0, "eps": 74.6, "roe": 29.8, "roce": 35.4, "debt": 120.0
    },
    {
        "id": 3, "symbol": "WAAREE", "company_name": "Waaree Energies Ltd", "ipo_type": "Mainboard",
        "price_band_low": 1427.0, "price_band_high": 1503.0, "lot_size": 9, "issue_size": 4321.0,
        "open_date": "2024-10-21", "close_date": "2024-10-23", "listing_date": "2024-10-28",
        "face_value": 10.0, "fresh_issue": 3600.0, "offer_for_sale": 721.0,
        "registrar": "Link Intime India Pvt Ltd", "lead_managers": "Axis Capital, Jefferies India, Nomura",
        "exchange": "NSE, BSE", "status": "Listed", "sector": "Solar Energy & CleanTech",
        "revenue": 11398.0, "profit": 1274.0, "eps": 53.4, "roe": 30.2, "roce": 34.8, "debt": 320.0
    },
    {
        "id": 4, "symbol": "NTPCGREEN", "company_name": "NTPC Green Energy Ltd", "ipo_type": "Mainboard",
        "price_band_low": 102.0, "price_band_high": 108.0, "lot_size": 138, "issue_size": 10000.0,
        "open_date": "2024-11-19", "close_date": "2024-11-22", "listing_date": "2024-11-27",
        "face_value": 10.0, "fresh_issue": 10000.0, "offer_for_sale": 0.0,
        "registrar": "KFin Technologies Ltd", "lead_managers": "IDBI Capital, HDFC Bank, IIFL Securities",
        "exchange": "NSE, BSE", "status": "Listed", "sector": "Renewable Energy",
        "revenue": 2038.0, "profit": 344.0, "eps": 0.44, "roe": 4.9, "roce": 6.8, "debt": 15200.0
    },
    {
        "id": 5, "symbol": "BAJAJHFL", "company_name": "Bajaj Housing Finance Ltd", "ipo_type": "Mainboard",
        "price_band_low": 66.0, "price_band_high": 70.0, "lot_size": 214, "issue_size": 6560.0,
        "open_date": "2024-09-09", "close_date": "2024-09-11", "listing_date": "2024-09-16",
        "face_value": 10.0, "fresh_issue": 3560.0, "offer_for_sale": 3000.0,
        "registrar": "KFin Technologies Ltd", "lead_managers": "Kotak Mahindra Capital, BofA Securities, Axis Capital",
        "exchange": "NSE, BSE", "status": "Listed", "sector": "Housing Finance",
        "revenue": 7617.0, "profit": 1731.0, "eps": 2.52, "roe": 15.2, "roce": 12.8, "debt": 68400.0
    },
    {
        "id": 6, "symbol": "ATHER", "company_name": "Ather Energy Ltd", "ipo_type": "Mainboard",
        "price_band_low": 310.0, "price_band_high": 330.0, "lot_size": 45, "issue_size": 4500.0,
        "open_date": "2026-10-10", "close_date": "2026-10-14", "listing_date": "2026-10-20",
        "face_value": 1.0, "fresh_issue": 3100.0, "offer_for_sale": 1400.0,
        "registrar": "Link Intime India Pvt Ltd", "lead_managers": "Axis Capital, JM Financial, HSBC Securities",
        "exchange": "NSE, BSE", "status": "Upcoming", "sector": "Electric Vehicles",
        "revenue": 1789.0, "profit": -1060.0, "eps": -8.4, "roe": -35.2, "roce": -28.4, "debt": 380.0
    },
    {
        "id": 7, "symbol": "SWANENERGY", "company_name": "Apex Green Tech SME Ltd", "ipo_type": "SME",
        "price_band_low": 115.0, "price_band_high": 122.0, "lot_size": 1200, "issue_size": 48.5,
        "open_date": "2026-10-02", "close_date": "2026-10-06", "listing_date": "2026-10-11",
        "face_value": 10.0, "fresh_issue": 48.5, "offer_for_sale": 0.0,
        "registrar": "Bigshare Services Pvt Ltd", "lead_managers": "Hem Securities Ltd",
        "exchange": "NSE SME", "status": "Open", "sector": "Green Chemicals",
        "revenue": 92.4, "profit": 14.8, "eps": 11.2, "roe": 22.4, "roce": 25.1, "debt": 18.2
    },
    {
        "id": 8, "symbol": "NOVAAGRO", "company_name": "Nova Bio Agri Tech Ltd", "ipo_type": "SME",
        "price_band_low": 75.0, "price_band_high": 80.0, "lot_size": 1600, "issue_size": 32.0,
        "open_date": "2026-10-05", "close_date": "2026-10-08", "listing_date": "2026-10-14",
        "face_value": 10.0, "fresh_issue": 32.0, "offer_for_sale": 0.0,
        "registrar": "Skyline Financial Services", "lead_managers": "Beeline Capital Advisors",
        "exchange": "BSE SME", "status": "Upcoming", "sector": "Agri Biotechnology",
        "revenue": 64.2, "profit": 8.9, "eps": 7.4, "roe": 19.8, "roce": 21.3, "debt": 12.0
    }
]

with open(DEMO_DIR / "ipos.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(IPOS[0].keys()))
    writer.writeheader()
    writer.writerows(IPOS)

print(f"Generated {len(IPOS)} IPO rows into ipos.csv")

# 6. GMP DATA (Formula: Estimated Listing Price = Upper Price Band + GMP)
GMP_DATA = [
    {
        "ipo_id": 1, "company_name": "Swiggy Ltd", "gmp": 12.0, "gmp_percent": 3.08,
        "min_gmp": 10.0, "max_gmp": 18.0, "estimated_listing_price": 402.0, "estimated_listing_gain": 3.08,
        "source": "india-ipo-gmp-data (Spectrumz00)", "timestamp": "2024-11-12T16:00:00"
    },
    {
        "ipo_id": 2, "company_name": "Hyundai Motor India Ltd", "gmp": -25.0, "gmp_percent": -1.28,
        "min_gmp": -35.0, "max_gmp": 15.0, "estimated_listing_price": 1935.0, "estimated_listing_gain": -1.28,
        "source": "india-ipo-gmp-data (Spectrumz00)", "timestamp": "2024-10-21T18:30:00"
    },
    {
        "ipo_id": 3, "company_name": "Waaree Energies Ltd", "gmp": 1480.0, "gmp_percent": 98.47,
        "min_gmp": 1350.0, "max_gmp": 1520.0, "estimated_listing_price": 2983.0, "estimated_listing_gain": 98.47,
        "source": "india-ipo-gmp-data (Spectrumz00)", "timestamp": "2024-10-27T17:15:00"
    },
    {
        "ipo_id": 4, "company_name": "NTPC Green Energy Ltd", "gmp": 3.5, "gmp_percent": 3.24,
        "min_gmp": 2.0, "max_gmp": 4.5, "estimated_listing_price": 111.5, "estimated_listing_gain": 3.24,
        "source": "india-ipo-gmp-data (Spectrumz00)", "timestamp": "2024-11-26T17:00:00"
    },
    {
        "ipo_id": 5, "company_name": "Bajaj Housing Finance Ltd", "gmp": 78.0, "gmp_percent": 111.43,
        "min_gmp": 65.0, "max_gmp": 82.0, "estimated_listing_price": 148.0, "estimated_listing_gain": 111.43,
        "source": "india-ipo-gmp-data (Spectrumz00)", "timestamp": "2024-09-15T19:00:00"
    },
    {
        "ipo_id": 6, "company_name": "Ather Energy Ltd", "gmp": 45.0, "gmp_percent": 13.64,
        "min_gmp": 35.0, "max_gmp": 55.0, "estimated_listing_price": 375.0, "estimated_listing_gain": 13.64,
        "source": "india-ipo-gmp-data (Spectrumz00)", "timestamp": "2026-10-01T15:30:00"
    },
    {
        "ipo_id": 7, "company_name": "Apex Green Tech SME Ltd", "gmp": 38.0, "gmp_percent": 31.15,
        "min_gmp": 30.0, "max_gmp": 42.0, "estimated_listing_price": 160.0, "estimated_listing_gain": 31.15,
        "source": "india-ipo-gmp-data (Spectrumz00)", "timestamp": "2026-10-01T18:00:00"
    },
    {
        "ipo_id": 8, "company_name": "Nova Bio Agri Tech Ltd", "gmp": 18.0, "gmp_percent": 22.50,
        "min_gmp": 12.0, "max_gmp": 20.0, "estimated_listing_price": 98.0, "estimated_listing_gain": 22.50,
        "source": "india-ipo-gmp-data (Spectrumz00)", "timestamp": "2026-10-01T18:00:00"
    }
]

with open(DEMO_DIR / "gmp.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(GMP_DATA[0].keys()))
    writer.writeheader()
    writer.writerows(GMP_DATA)

print(f"Generated {len(GMP_DATA)} GMP rows into gmp.csv")

# 7. SUBSCRIPTIONS
SUBSCRIPTIONS = [
    {"ipo_id": 1, "qib": 4.53, "nii": 1.24, "retail": 1.14, "employee": 1.65, "total": 3.59, "as_of_date": "2024-11-08"},
    {"ipo_id": 2, "qib": 6.97, "nii": 0.60, "retail": 0.50, "employee": 1.74, "total": 2.37, "as_of_date": "2024-10-17"},
    {"ipo_id": 3, "qib": 215.03, "nii": 65.25, "retail": 11.27, "employee": 9.62, "total": 79.44, "as_of_date": "2024-10-23"},
    {"ipo_id": 4, "qib": 3.32, "nii": 0.84, "retail": 3.44, "employee": 0.0, "total": 2.55, "as_of_date": "2024-11-22"},
    {"ipo_id": 5, "qib": 222.05, "nii": 43.50, "retail": 7.41, "employee": 2.10, "total": 67.43, "as_of_date": "2024-09-11"},
    {"ipo_id": 6, "qib": 0.0, "nii": 0.0, "retail": 0.0, "employee": 0.0, "total": 0.0, "as_of_date": "2026-10-01"},
    {"ipo_id": 7, "qib": 14.2, "nii": 38.5, "retail": 42.1, "employee": 0.0, "total": 34.6, "as_of_date": "2026-10-01"},
    {"ipo_id": 8, "qib": 0.0, "nii": 0.0, "retail": 0.0, "employee": 0.0, "total": 0.0, "as_of_date": "2026-10-01"}
]

with open(DEMO_DIR / "subscriptions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(SUBSCRIPTIONS[0].keys()))
    writer.writeheader()
    writer.writerows(SUBSCRIPTIONS)

print(f"Generated {len(SUBSCRIPTIONS)} subscription rows into subscriptions.csv")

# 8. NEWS DATA (JSON with sentiment analysis)
NEWS = [
    {
        "id": 1,
        "title": "RBI Keeps Repo Rate Steady Amid Robust Indian GDP Growth Forecasts",
        "source": "Business Standard RSS",
        "published_at": "2026-10-01T14:30:00",
        "url": "https://www.business-standard.com/economy/news",
        "related_stock": "HDFCBANK",
        "category": "Economy & Banking",
        "sentiment": "Positive",
        "sentiment_score": 0.72,
        "summary": "Monetary policy committee maintains benchmark interest rate as domestic demand and manufacturing indicators show strong momentum."
    },
    {
        "id": 2,
        "title": "Reliance Industries Announces Major Solar & Green Hydrogen Capacity Expansion in Jamnagar",
        "source": "LiveMint RSS",
        "published_at": "2026-10-01T12:15:00",
        "url": "https://www.livemint.com/companies/news",
        "related_stock": "RELIANCE",
        "category": "Corporate & Energy",
        "sentiment": "Positive",
        "sentiment_score": 0.85,
        "summary": "RIL green energy giga-factory complex nears phase-1 commissioning with planned electrolyzer and solar cell manufacturing."
    },
    {
        "id": 3,
        "title": "TCS Secures Multi-Million Dollar European Digital Banking Transformation Deal",
        "source": "Economic Times RSS",
        "published_at": "2026-10-01T11:00:00",
        "url": "https://economictimes.indiatimes.com/tech",
        "related_stock": "TCS",
        "category": "Information Technology",
        "sentiment": "Positive",
        "sentiment_score": 0.68,
        "summary": "India's largest IT exporter signs multi-year cloud modernization agreement with top Nordic financial services group."
    },
    {
        "id": 4,
        "title": "Indian Auto Retail Sales Witness Slight Festive Pre-Season Moderation",
        "source": "Reuters India",
        "published_at": "2026-10-01T09:45:00",
        "url": "https://in.reuters.com/markets",
        "related_stock": "TATAMOTORS",
        "category": "Automobile",
        "sentiment": "Neutral",
        "sentiment_score": -0.05,
        "summary": "Dealers note inventory accumulation in passenger vehicle segment while commercial vehicle volumes remain resilient."
    },
    {
        "id": 5,
        "title": "SEBI Releases Enhanced Framework for SME IPO Due Diligence and Allocation Transparency",
        "source": "NSE Public Circulars",
        "published_at": "2026-10-01T08:20:00",
        "url": "https://www.nseindia.com/resources/circulars",
        "related_stock": "",
        "category": "IPO Regulations",
        "sentiment": "Neutral",
        "sentiment_score": 0.15,
        "summary": "Markets regulator increases monitoring of financial disclosures, minimum application sizes, and promoter lock-in requirements for SME exchanges."
    },
    {
        "id": 6,
        "title": "Infosys Expands Enterprise Generative AI Portfolio Topaz Across Global Clients",
        "source": "BusinessLine",
        "published_at": "2026-09-30T16:40:00",
        "url": "https://www.thehindubusinessline.com/info-tech",
        "related_stock": "INFY",
        "category": "Information Technology",
        "sentiment": "Positive",
        "sentiment_score": 0.64,
        "summary": "Accelerating enterprise AI adoption drives incremental deal pipeline in financial services and life sciences."
    }
]

with open(DEMO_DIR / "news.json", "w", encoding="utf-8") as f:
    json.dump(NEWS, f, indent=2)

print(f"Generated {len(NEWS)} news items into news.json")
print("All demo data generation completed successfully!")
