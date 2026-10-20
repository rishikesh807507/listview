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
    Zero paid APIs. Validates mathematical change and previous close.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.endpoints = [
            ("https://query1.finance.yahoo.com/v8/finance/chart", "NSE/BSE Public Feed via Yahoo Finance"),
            ("https://query2.finance.yahoo.com/v8/finance/chart", "NSE/BSE Public Feed via Yahoo Query2")
        ]
        self._client = httpx.Client(
            timeout=3.5,
            headers=self.headers,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )

    def _get_client(self) -> httpx.Client:
        if self._client.is_closed:
            self._client = httpx.Client(
                timeout=3.5,
                headers=self.headers,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._client

    def get_index_quote(self, index_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves real-time index value and previous close from free public feeds.
        Tries primary and secondary endpoints with strict mathematical validation.
        """
        meta = symbol_mapper.get_index_meta(index_name)
        if not meta:
            logger.error(f"Unknown index requested: {index_name}")
            return None

        yahoo_sym = meta["yahoo_symbol"]
        clean_sym = yahoo_sym.replace("%5E", "^")

        client = self._get_client()
        for base_url, source_name in self.endpoints:
            # Try with unencoded symbol, then with encoded if needed
            for sym in [clean_sym, yahoo_sym]:
                url = f"{base_url}/{sym}?interval=1d&range=5d"
                try:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        chart_result = data.get("chart", {}).get("result")
                        if chart_result and len(chart_result) > 0:
                            chart_meta = chart_result[0].get("meta", {})
                            price = chart_meta.get("regularMarketPrice")
                            prev_close = chart_meta.get("chartPreviousClose") or chart_meta.get("previousClose")
                            raw_ts = chart_meta.get("regularMarketTime")

                            if price is not None and price > 0:
                                raw_payload = {
                                    "index_name": meta["canonical_name"],
                                    "price": float(price),
                                    "previous_close": float(prev_close) if prev_close else None,
                                    "timestamp": raw_ts,
                                    "source": source_name,
                                    "exchange": meta["exchange"],
                                    "currency": "INR"
                                }

                                is_valid, validated_data, error = data_validator.validate_and_compute_quote(raw_payload, is_index=True)
                                if is_valid:
                                    return validated_data
                                else:
                                    logger.warning(f"Validation rejected index {index_name} from {source_name}: {error}")
                except Exception as e:
                    logger.debug(f"Endpoint {base_url} failed for {index_name} ({sym}): {e}")

        logger.warning(f"All live endpoints exhausted for index {index_name}")
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
