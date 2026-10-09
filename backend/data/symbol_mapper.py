"""
Central Symbol Registry and Verified Instrument Mapping for Indian Equities and Indices.
Never guesses or synthesizes provider tickers dynamically.
"""
from typing import Dict, Any, Optional, List

INDEX_REGISTRY: Dict[str, Dict[str, Any]] = {
    "NIFTY 50": {
        "canonical_name": "NIFTY 50",
        "aliases": ["NIFTY", "NIFTY50", "^NSEI"],
        "exchange": "NSE",
        "instrument_type": "INDEX",
        "yahoo_symbol": "%5ENSEI",
        "isin": "IN9014101018",
        "currency": "INR",
        "description": "NSE Flagship 50 Bluechip Index"
    },
    "SENSEX": {
        "canonical_name": "SENSEX",
        "aliases": ["BSE SENSEX", "BSESN", "^BSESN"],
        "exchange": "BSE",
        "instrument_type": "INDEX",
        "yahoo_symbol": "%5EBSESN",
        "isin": "IN9014101026",
        "currency": "INR",
        "description": "BSE Benchmark 30 Index"
    },
    "NIFTY BANK": {
        "canonical_name": "NIFTY BANK",
        "aliases": ["BANKNIFTY", "NIFTYBANK", "^NSEBANK"],
        "exchange": "NSE",
        "instrument_type": "INDEX",
        "yahoo_symbol": "%5ENSEBANK",
        "isin": "IN9014101034",
        "currency": "INR",
        "description": "Banking Sector Benchmark Index"
    },
    "NIFTY IT": {
        "canonical_name": "NIFTY IT",
        "aliases": ["CNXIT", "NIFTYIT", "^CNXIT"],
        "exchange": "NSE",
        "instrument_type": "INDEX",
        "yahoo_symbol": "%5ECNXIT",
        "isin": "IN9014101042",
        "currency": "INR",
        "description": "Information Technology Sector Index"
    },
    "NIFTY AUTO": {
        "canonical_name": "NIFTY AUTO",
        "aliases": ["CNXAUTO", "NIFTYAUTO", "^CNXAUTO"],
        "exchange": "NSE",
        "instrument_type": "INDEX",
        "yahoo_symbol": "%5ECNXAUTO",
        "isin": "IN9014101059",
        "currency": "INR",
        "description": "Automotive Sector Benchmark Index"
    }
}

EQUITY_REGISTRY: Dict[str, Dict[str, Any]] = {
    "RELIANCE": {
        "symbol": "RELIANCE",
        "company_name": "Reliance Industries Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE002A01018",
        "yahoo_symbol": "RELIANCE.NS",
        "currency": "INR",
        "sector": "Energy"
    },
    "TCS": {
        "symbol": "TCS",
        "company_name": "Tata Consultancy Services Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE467B01029",
        "yahoo_symbol": "TCS.NS",
        "currency": "INR",
        "sector": "IT"
    },
    "HDFCBANK": {
        "symbol": "HDFCBANK",
        "company_name": "HDFC Bank Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE040A01034",
        "yahoo_symbol": "HDFCBANK.NS",
        "currency": "INR",
        "sector": "Banking"
    },
    "INFY": {
        "symbol": "INFY",
        "company_name": "Infosys Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE009A01021",
        "yahoo_symbol": "INFY.NS",
        "currency": "INR",
        "sector": "IT"
    },
    "ICICIBANK": {
        "symbol": "ICICIBANK",
        "company_name": "ICICI Bank Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE090A01021",
        "yahoo_symbol": "ICICIBANK.NS",
        "currency": "INR",
        "sector": "Banking"
    },
    "BHARTIARTL": {
        "symbol": "BHARTIARTL",
        "company_name": "Bharti Airtel Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE397D01024",
        "yahoo_symbol": "BHARTIARTL.NS",
        "currency": "INR",
        "sector": "Telecom"
    },
    "AXISBANK": {
        "symbol": "AXISBANK",
        "company_name": "Axis Bank Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE238A01034",
        "yahoo_symbol": "AXISBANK.NS",
        "currency": "INR",
        "sector": "Banking"
    },
    "KOTAKBANK": {
        "symbol": "KOTAKBANK",
        "company_name": "Kotak Mahindra Bank Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE237A01028",
        "yahoo_symbol": "KOTAKBANK.NS",
        "currency": "INR",
        "sector": "Banking"
    },
    "TITAN": {
        "symbol": "TITAN",
        "company_name": "Titan Company Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE280A01028",
        "yahoo_symbol": "TITAN.NS",
        "currency": "INR",
        "sector": "Consumer Durables"
    },
    "ITC": {
        "symbol": "ITC",
        "company_name": "ITC Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE154A01025",
        "yahoo_symbol": "ITC.NS",
        "currency": "INR",
        "sector": "FMCG"
    },
    "LT": {
        "symbol": "LT",
        "company_name": "Larsen & Toubro Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE018A01030",
        "yahoo_symbol": "LT.NS",
        "currency": "INR",
        "sector": "Infrastructure"
    },
    "SUNPHARMA": {
        "symbol": "SUNPHARMA",
        "company_name": "Sun Pharmaceutical Industries Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE044A01036",
        "yahoo_symbol": "SUNPHARMA.NS",
        "currency": "INR",
        "sector": "Pharma"
    },
    "SBIN": {
        "symbol": "SBIN",
        "company_name": "State Bank of India",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE062A01020",
        "yahoo_symbol": "SBIN.NS",
        "currency": "INR",
        "sector": "Banking"
    },
    "BAJFINANCE": {
        "symbol": "BAJFINANCE",
        "company_name": "Bajaj Finance Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE296A01024",
        "yahoo_symbol": "BAJFINANCE.NS",
        "currency": "INR",
        "sector": "Finance"
    },
    "MARUTI": {
        "symbol": "MARUTI",
        "company_name": "Maruti Suzuki India Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE585B01010",
        "yahoo_symbol": "MARUTI.NS",
        "currency": "INR",
        "sector": "Automobile"
    },
    "HINDUNILVR": {
        "symbol": "HINDUNILVR",
        "company_name": "Hindustan Unilever Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE030A01027",
        "yahoo_symbol": "HINDUNILVR.NS",
        "currency": "INR",
        "sector": "FMCG"
    },
    "WIPRO": {
        "symbol": "WIPRO",
        "company_name": "Wipro Ltd",
        "exchange": "NSE",
        "instrument_type": "EQUITY",
        "isin": "INE075A01022",
        "yahoo_symbol": "WIPRO.NS",
        "currency": "INR",
        "sector": "IT"
    }
}

class SymbolMapper:
    @staticmethod
    def get_index_meta(index_name: str) -> Optional[Dict[str, Any]]:
        clean = index_name.strip().upper()
        if clean in INDEX_REGISTRY:
            return INDEX_REGISTRY[clean]
        for key, val in INDEX_REGISTRY.items():
            if clean in [a.upper() for a in val["aliases"]]:
                return val
        return None

    @staticmethod
    def get_equity_meta(symbol: str) -> Optional[Dict[str, Any]]:
        clean = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        if clean in EQUITY_REGISTRY:
            return EQUITY_REGISTRY[clean]
        
        # Check database for this symbol
        try:
            from backend.database import SessionLocal
            from backend.models import Stock
            db = SessionLocal()
            stock = db.query(Stock).filter(Stock.symbol == clean).first()
            if stock:
                exchange = stock.exchange or "NSE"
                meta = {
                    "symbol": stock.symbol,
                    "company_name": stock.name or stock.symbol,
                    "exchange": exchange,
                    "instrument_type": "EQUITY",
                    "isin": stock.isin or "",
                    "yahoo_symbol": f"{stock.symbol}.BO" if exchange.upper() == "BSE" else f"{stock.symbol}.NS",
                    "currency": "INR",
                    "sector": stock.sector or ""
                }
                db.close()
                return meta
            db.close()
        except Exception:
            pass

        return None

    @staticmethod
    def is_valid_index(index_name: str) -> bool:
        return SymbolMapper.get_index_meta(index_name) is not None

    @staticmethod
    def is_valid_equity(symbol: str) -> bool:
        return SymbolMapper.get_equity_meta(symbol) is not None

    @staticmethod
    def get_all_indices() -> List[str]:
        return list(INDEX_REGISTRY.keys())

    @staticmethod
    def get_all_equity_symbols() -> List[str]:
        return list(EQUITY_REGISTRY.keys())

symbol_mapper = SymbolMapper()
