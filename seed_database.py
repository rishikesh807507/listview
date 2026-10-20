"""
Database seeder for Listview — Indian Stocks & IPO Intelligence Platform.
Imports demo-data CSVs and JSONs into the SQLite/PostgreSQL database.
Can be run standalone: python seed_database.py
"""
import os
import csv
import json
from datetime import datetime
from pathlib import Path
from backend.database import Base, engine, SessionLocal
from backend.models import (
    Stock, StockPrice, StockFundamentals, FinancialStatement,
    IPO, IPOSubscription, IPOGMP, News, IndexQuote, MarketQuote
)

DEMO_DIR = Path(__file__).resolve().parent / "demo-data"

def seed():
    print("[*] Creating all database tables if not existing...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Stocks
        stocks_file = DEMO_DIR / "stocks.csv"
        if stocks_file.exists():
            with open(stocks_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing = db.query(Stock).filter(Stock.symbol == row["symbol"]).first()
                    if not existing:
                        stock = Stock(
                            symbol=row["symbol"],
                            name=row["name"],
                            exchange=row.get("exchange", "NSE"),
                            sector=row.get("sector"),
                            industry=row.get("industry"),
                            current_price=float(row["current_price"]),
                            change=float(row.get("change", 0.0)),
                            change_percent=float(row.get("change_percent", 0.0)),
                            market_cap=float(row.get("market_cap", 0.0)),
                            pe_ratio=float(row.get("pe_ratio", 0.0)),
                            pb_ratio=float(row.get("pb_ratio", 0.0)),
                            roe=float(row.get("roe", 0.0)),
                            roce=float(row.get("roce", 0.0)),
                            dividend_yield=float(row.get("dividend_yield", 0.0)),
                            debt_to_equity=float(row.get("debt_to_equity", 0.0)),
                            high_52w=float(row.get("high_52w", 0.0)),
                            low_52w=float(row.get("low_52w", 0.0)),
                            volume=float(row.get("volume", 0.0)),
                            updated_at=datetime.utcnow()
                        )
                        db.add(stock)
                db.commit()
            print("[+] Seeded stocks table.")

        # 2. Historical Prices
        prices_file = DEMO_DIR / "historical_prices.csv"
        if prices_file.exists():
            existing_count = db.query(StockPrice).count()
            if existing_count == 0:
                price_objects = []
                with open(prices_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        price_objects.append(StockPrice(
                            symbol=row["symbol"],
                            exchange=row.get("exchange", "NSE"),
                            timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d"),
                            open=float(row["open"]),
                            high=float(row["high"]),
                            low=float(row["low"]),
                            close=float(row["close"]),
                            volume=float(row.get("volume", 0.0)),
                            source=row.get("source", "demo_bundled"),
                            created_at=datetime.utcnow()
                        ))
                db.bulk_save_objects(price_objects)
                db.commit()
                print(f"[+] Seeded {len(price_objects)} historical price records.")

        # 3. Fundamentals
        fund_file = DEMO_DIR / "fundamentals.csv"
        if fund_file.exists():
            with open(fund_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing = db.query(StockFundamentals).filter(StockFundamentals.symbol == row["symbol"]).first()
                    if not existing:
                        fund = StockFundamentals(
                            symbol=row["symbol"],
                            revenue=float(row["revenue"]),
                            revenue_growth=float(row["revenue_growth"]),
                            ebitda=float(row["ebitda"]),
                            ebitda_margin=float(row["ebitda_margin"]),
                            net_profit=float(row["net_profit"]),
                            profit_growth=float(row["profit_growth"]),
                            eps=float(row["eps"]),
                            pe=float(row["pe"]),
                            pb=float(row["pb"]),
                            roe=float(row["roe"]),
                            roce=float(row["roce"]),
                            debt=float(row["debt"]),
                            debt_to_equity=float(row["debt_to_equity"]),
                            current_ratio=float(row["current_ratio"]),
                            dividend_yield=float(row["dividend_yield"]),
                            free_cash_flow=float(row["free_cash_flow"]),
                            promoter_holding=float(row["promoter_holding"]),
                            market_cap=float(row["market_cap"]),
                            enterprise_value=float(row["enterprise_value"]),
                            period=row.get("period", "FY2025-26"),
                            updated_at=datetime.utcnow()
                        )
                        db.add(fund)
                db.commit()
            print("[+] Seeded stock fundamentals.")

        # 4. Financial Statements
        fin_file = DEMO_DIR / "financials.csv"
        if fin_file.exists():
            existing_count = db.query(FinancialStatement).count()
            if existing_count == 0:
                stmt_objs = []
                with open(fin_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        stmt_objs.append(FinancialStatement(
                            symbol=row["symbol"],
                            statement_type=row["statement_type"],
                            period_type=row.get("period_type", "annual"),
                            year=int(row["year"]),
                            quarter=row.get("quarter") or None,
                            data=row["data"],
                            updated_at=datetime.utcnow()
                        ))
                db.bulk_save_objects(stmt_objs)
                db.commit()
                print(f"[+] Seeded {len(stmt_objs)} financial statement records.")

        # 5. IPOs
        ipos_file = DEMO_DIR / "ipos.csv"
        if ipos_file.exists():
            with open(ipos_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing = db.query(IPO).filter(IPO.id == int(row["id"])).first()
                    if not existing:
                        open_dt = datetime.strptime(row["open_date"], "%Y-%m-%d")
                        close_dt = datetime.strptime(row["close_date"], "%Y-%m-%d")
                        list_dt = datetime.strptime(row["listing_date"], "%Y-%m-%d") if row.get("listing_date") else None
                        ipo = IPO(
                            id=int(row["id"]),
                            symbol=row.get("symbol"),
                            company_name=row["company_name"],
                            ipo_type=row.get("ipo_type", "Mainboard"),
                            price_band_low=float(row["price_band_low"]),
                            price_band_high=float(row["price_band_high"]),
                            lot_size=int(row["lot_size"]),
                            issue_size=float(row["issue_size"]),
                            open_date=open_dt,
                            close_date=close_dt,
                            listing_date=list_dt,
                            face_value=float(row.get("face_value", 10.0)),
                            fresh_issue=float(row.get("fresh_issue", 0.0)),
                            offer_for_sale=float(row.get("offer_for_sale", 0.0)),
                            registrar=row.get("registrar", ""),
                            lead_managers=row.get("lead_managers", ""),
                            exchange=row.get("exchange", "NSE, BSE"),
                            status=row.get("status", "Upcoming"),
                            sector=row.get("sector", "General"),
                            revenue=float(row.get("revenue", 0.0)),
                            profit=float(row.get("profit", 0.0)),
                            eps=float(row.get("eps", 0.0)),
                            roe=float(row.get("roe", 0.0)),
                            roce=float(row.get("roce", 0.0)),
                            debt=float(row.get("debt", 0.0)),
                            updated_at=datetime.utcnow()
                        )
                        db.add(ipo)
                db.commit()
            print("[+] Seeded IPOs.")

        # 6. GMP
        gmp_file = DEMO_DIR / "gmp.csv"
        if gmp_file.exists():
            with open(gmp_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ipo_id = int(row["ipo_id"]) if row.get("ipo_id") else None
                    existing = db.query(IPOGMP).filter(IPOGMP.company_name == row["company_name"]).first()
                    if not existing:
                        gmp_obj = IPOGMP(
                            ipo_id=ipo_id,
                            company_name=row["company_name"],
                            gmp=float(row["gmp"]),
                            gmp_percent=float(row["gmp_percent"]),
                            min_gmp=float(row.get("min_gmp", row["gmp"])),
                            max_gmp=float(row.get("max_gmp", row["gmp"])),
                            estimated_listing_price=float(row["estimated_listing_price"]),
                            estimated_listing_gain=float(row["estimated_listing_gain"]),
                            source=row.get("source", "india-ipo-gmp-data (Spectrumz00)"),
                            timestamp=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(gmp_obj)
                db.commit()
            print("[+] Seeded IPO GMP data.")

        # 7. Subscriptions
        sub_file = DEMO_DIR / "subscriptions.csv"
        if sub_file.exists():
            with open(sub_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ipo_id = int(row["ipo_id"])
                    existing = db.query(IPOSubscription).filter(IPOSubscription.ipo_id == ipo_id).first()
                    if not existing:
                        sub = IPOSubscription(
                            ipo_id=ipo_id,
                            qib=float(row.get("qib", 0.0)),
                            nii=float(row.get("nii", 0.0)),
                            retail=float(row.get("retail", 0.0)),
                            employee=float(row.get("employee", 0.0)),
                            total=float(row.get("total", 0.0)),
                            as_of_date=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(sub)
                db.commit()
            print("[+] Seeded IPO Subscriptions.")

        # 8. News
        news_file = DEMO_DIR / "news.json"
        if news_file.exists():
            with open(news_file, "r", encoding="utf-8") as f:
                news_list = json.load(f)
                for item in news_list:
                    existing = db.query(News).filter(News.title == item["title"]).first()
                    if not existing:
                        news_obj = News(
                            title=item["title"],
                            source=item["source"],
                            published_at=datetime.fromisoformat(item["published_at"]),
                            url=item.get("url"),
                            related_stock=item.get("related_stock"),
                            category=item.get("category", "Markets"),
                            sentiment=item.get("sentiment", "Neutral"),
                            sentiment_score=float(item.get("sentiment_score", 0.0)),
                            summary=item.get("summary"),
                            created_at=datetime.utcnow()
                        )
                        db.add(news_obj)
                db.commit()
            print("[+] Seeded Market News.")
        
        # 9. Benchmark Indices
        existing_indices = db.query(IndexQuote).count()
        if existing_indices == 0:
            try:
                from backend.sync.scheduler import sync_indices
                res = sync_indices(db)
                print(f"[+] Synced benchmark indices: {res.get('success', 0)} verified, {res.get('failed', 0)} failed.")
            except Exception as e:
                print(f"[-] Benchmark indices live sync skipped during seed: {e}")

        # 10. Initial Market Quotes from Stocks
        existing_quotes = db.query(MarketQuote).count()
        if existing_quotes == 0:
            active_stocks = db.query(Stock).filter(Stock.is_active == True, Stock.current_price > 0).limit(30).all()
            for s in active_stocks:
                db.add(MarketQuote(
                    symbol=s.symbol,
                    exchange=s.exchange or "NSE",
                    instrument_type="EQUITY",
                    price=s.current_price,
                    previous_close=round(s.current_price - (s.change or 0.0), 2),
                    change=s.change or 0.0,
                    change_percent=s.change_percent or 0.0,
                    volume=s.volume or 0.0,
                    timestamp=s.updated_at or datetime.utcnow(),
                    source="NSE Securities Master",
                    status="Verified",
                    created_at=datetime.utcnow()
                ))
            db.commit()
            print("[+] Seeded Initial Market Quotes from active securities.")

        print("\n[SUCCESS] Database seeded successfully with zero paid APIs!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
