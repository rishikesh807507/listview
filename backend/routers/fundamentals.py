from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import csv
import io
from backend.database import get_db
from backend.models import StockFundamentals, FinancialStatement, Stock
from backend.schemas import StockFundamentalsResponse

router = APIRouter(prefix="/fundamentals", tags=["Fundamentals"])

@router.get("/{symbol}", response_model=StockFundamentalsResponse)
def get_fundamentals(symbol: str, db: Session = Depends(get_db)):
    clean_sym = symbol.upper().strip()
    fund = db.query(StockFundamentals).filter(StockFundamentals.symbol == clean_sym).first()
    if not fund:
        raise HTTPException(status_code=404, detail=f"Fundamentals for {clean_sym} not found.")
    return fund

@router.get("/{symbol}/statements")
def get_financial_statements(
    symbol: str,
    statement_type: Optional[str] = None,  # income, balance_sheet, cash_flow
    db: Session = Depends(get_db)
):
    clean_sym = symbol.upper().strip()
    query = db.query(FinancialStatement).filter(FinancialStatement.symbol == clean_sym)
    if statement_type:
        query = query.filter(FinancialStatement.statement_type == statement_type)
    
    statements = query.order_by(FinancialStatement.year.asc()).all()
    results = {}
    for st in statements:
        st_type = st.statement_type
        if st_type not in results:
            results[st_type] = []
        try:
            parsed_data = json.loads(st.data)
        except Exception:
            parsed_data = {}
        results[st_type].append({
            "year": st.year,
            "quarter": st.quarter,
            "period_type": st.period_type,
            "metrics": parsed_data
        })
    return {"symbol": clean_sym, "statements": results}

@router.post("/import-csv")
async def import_fundamentals_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Allows manual CSV upload of company fundamentals."""
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    count = 0
    for row in reader:
        sym = row["symbol"].upper().strip()
        existing = db.query(StockFundamentals).filter(StockFundamentals.symbol == sym).first()
        if existing:
            existing.revenue = float(row.get("revenue", existing.revenue))
            existing.revenue_growth = float(row.get("revenue_growth", existing.revenue_growth))
            existing.net_profit = float(row.get("net_profit", existing.net_profit))
            existing.eps = float(row.get("eps", existing.eps))
            existing.roe = float(row.get("roe", existing.roe))
            existing.roce = float(row.get("roce", existing.roce))
        else:
            new_f = StockFundamentals(
                symbol=sym,
                revenue=float(row.get("revenue", 0.0)),
                revenue_growth=float(row.get("revenue_growth", 0.0)),
                ebitda=float(row.get("ebitda", 0.0)),
                ebitda_margin=float(row.get("ebitda_margin", 0.0)),
                net_profit=float(row.get("net_profit", 0.0)),
                profit_growth=float(row.get("profit_growth", 0.0)),
                eps=float(row.get("eps", 0.0)),
                pe=float(row.get("pe", 0.0)),
                pb=float(row.get("pb", 0.0)),
                roe=float(row.get("roe", 0.0)),
                roce=float(row.get("roce", 0.0)),
                debt=float(row.get("debt", 0.0)),
                debt_to_equity=float(row.get("debt_to_equity", 0.0)),
                current_ratio=float(row.get("current_ratio", 0.0)),
                dividend_yield=float(row.get("dividend_yield", 0.0)),
                free_cash_flow=float(row.get("free_cash_flow", 0.0)),
                promoter_holding=float(row.get("promoter_holding", 0.0)),
                market_cap=float(row.get("market_cap", 0.0)),
                enterprise_value=float(row.get("enterprise_value", 0.0)),
                period=row.get("period", "FY2025-26")
            )
            db.add(new_f)
        count += 1
    db.commit()
    return {"message": f"Successfully processed {count} fundamental records", "status": "success"}
