"""
Dedicated Index Data Provider for Indian Benchmark Indices.
Fetches verified live quotes for NIFTY 50, SENSEX, NIFTY BANK, NIFTY IT, and NIFTY AUTO.
Zero paid APIs. Validates mathematical change and previous close.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

from backend.data.symbol_mapper import symbol_mapper, INDEX_REGISTRY
from backend.data.data_validator import data_validator

logger = logging.getLogger("IndexProvider")

class IndexProvider:
    """
    Dedicated provider for official Indian market indices.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"

    def get_index_quote(self, index_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves real-time index value and previous close from free public feed.
        """
        meta = symbol_mapper.get_index_meta(index_name)
        if not meta:
            logger.error(f"Unknown index requested: {index_name}")
            return None

        yahoo_sym = meta["yahoo_symbol"]
        url = f"{self.base_url}/{yahoo_sym}?interval=1d&range=5d"

        try:
            with httpx.Client(timeout=6.0, headers=self.headers) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    chart_result = data.get("chart", {}).get("result")
                    if chart_result and len(chart_result) > 0:
                        chart_meta = chart_result[0].get("meta", {})
                        price = chart_meta.get("regularMarketPrice")
                        prev_close = chart_meta.get("chartPreviousClose") or chart_meta.get("previousClose")
                        raw_ts = chart_meta.get("regularMarketTime")

                        raw_payload = {
                            "index_name": meta["canonical_name"],
                            "price": price,
                            "previous_close": prev_close,
                            "timestamp": raw_ts,
                            "source": "NSE/BSE Public Feed via Yahoo Finance",
                            "exchange": meta["exchange"],
                            "currency": "INR"
                        }

                        is_valid, validated_data, error = data_validator.validate_and_compute_quote(raw_payload, is_index=True)
                        if is_valid:
                            return validated_data
                        else:
                            logger.warning(f"Validation rejected index {index_name}: {error}")
        except Exception as e:
            logger.warning(f"Live fetch failed for index {index_name}: {e}")

        return None

    def get_all_indices(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetches all tracked benchmark indices.
        """
        results = {}
        for canonical_name in INDEX_REGISTRY.keys():
            quote = self.get_index_quote(canonical_name)
            if quote:
                results[canonical_name] = quote
        return results

    def health_check(self) -> bool:
        quote = self.get_index_quote("NIFTY 50")
        return quote is not None and quote.get("price", 0) > 0

index_provider = IndexProvider()
