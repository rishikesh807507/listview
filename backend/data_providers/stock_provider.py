import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from backend.config import settings
from backend.data_providers.base_provider import BaseProvider

logger = logging.getLogger("StockProvider")

class IndianStockProvider(BaseProvider):
    """
    Community Indian Stock Market API Provider (0xramm/Indian-Stock-Market-API).
    Zero API key required, MIT Licensed.
    Falls back gracefully if external community service is unreachable or rate limited.
    """
    def __init__(self):
        super().__init__("Community Indian Stock Market API")
        self.base_url = settings.INDIAN_STOCK_API_BASE

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(f"{self.base_url}/health")
                return resp.status_code == 200
        except Exception:
            return False

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time quote for symbol (e.g. RELIANCE, TCS)."""
        clean_symbol = symbol.upper().replace(".NS", "").replace(".BO", "")
        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(f"{self.base_url}/quote/{clean_symbol}")
                if resp.status_code == 200:
                    data = resp.json()
                    self.last_status = "Live"
                    self.last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                    return {
                        "symbol": clean_symbol,
                        "current_price": float(data.get("price") or data.get("current_price", 0.0)),
                        "change": float(data.get("change", 0.0)),
                        "change_percent": float(data.get("change_percent", 0.0)),
                        "open": float(data.get("open", 0.0)),
                        "high": float(data.get("high", 0.0)),
                        "low": float(data.get("low", 0.0)),
                        "volume": float(data.get("volume", 0.0)),
                        "source": self.name,
                        "status": "Live",
                        "updated_at": self.last_updated
                    }
        except Exception as e:
            logger.warning(f"Live stock provider failed for {symbol}: {e}. Fallback will be used.")
        return None

    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Batch quote request."""
        results = {}
        for sym in symbols:
            q = self.get_quote(sym)
            if q:
                results[sym] = q
        return results

    def search_symbol(self, query: str) -> List[Dict[str, Any]]:
        """Search symbol by ticker or company name."""
        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(f"{self.base_url}/search", params={"q": query})
                if resp.status_code == 200:
                    return resp.json().get("results", [])
        except Exception as e:
            logger.warning(f"Search API request failed: {e}")
        return []

    def get_symbols(self) -> List[str]:
        """Fetch list of traded symbols."""
        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(f"{self.base_url}/symbols")
                if resp.status_code == 200:
                    return resp.json().get("symbols", [])
        except Exception:
            pass
        return ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "BHARTIARTL", "ITC", "SBIN", "TATAMOTORS", "SUNPHARMA"]

    def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        return self.get_quote(symbol)
