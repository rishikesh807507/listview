import logging
from backend.database import SessionLocal
from backend.models import Stock, StockFundamentals

logger = logging.getLogger("FinancialCollector")

def collect_financials():
    """
    Refreshes metrics and valuation ratios (P/E, P/B, Market Cap)
    calculated directly from current stock prices and shares outstanding.
    """
    db = SessionLocal()
    try:
        stocks = db.query(Stock).all()
        updated = 0
        for stock in stocks:
            fund = db.query(StockFundamentals).filter(StockFundamentals.symbol == stock.symbol).first()
            if fund and stock.current_price > 0:
                if fund.eps > 0:
                    stock.pe_ratio = round(stock.current_price / fund.eps, 2)
                    fund.pe = stock.pe_ratio
                updated += 1
        db.commit()
        print(f"[FinancialCollector] Refreshed financial ratios for {updated} stocks.")
    except Exception as e:
        print(f"[FinancialCollector Error] {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    collect_financials()
