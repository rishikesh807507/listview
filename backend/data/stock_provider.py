"""
Dedicated Stock Data Provider for Indian Equities.
Fetches verified live quotes and historical OHLCV data using public community feeds.
Validates payloads through DataValidator and enforces exact mathematical change calculations.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

from backend.data.symbol_mapper import symbol_mapper
from backend.data.data_validator import data_validator

logger = logging.getLogger("StockDataProvider")

class StockDataProvider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self._client = httpx.Client(timeout=8.0, headers=self.headers, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10))

    def _get_client(self) -> httpx.Client:
        if self._client.is_closed:
            self._client = httpx.Client(timeout=8.0, headers=self.headers, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10))
        return self._client

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetches live quote for an equity symbol (e.g., RELIANCE, TCS).
        """
        meta = symbol_mapper.get_equity_meta(symbol)
        if not meta:
            logger.warning(f"Unregistered equity requested: {symbol}")
            return None

        yahoo_sym = meta["yahoo_symbol"]
        url = f"{self.base_url}/{yahoo_sym}?interval=1d&range=5d"

        for attempt in range(2):
            try:
                client = self._get_client()
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    chart_result = data.get("chart", {}).get("result")
                    if chart_result and len(chart_result) > 0:
                        chart_meta = chart_result[0].get("meta", {})
                        price = chart_meta.get("regularMarketPrice")
                        prev_close = chart_meta.get("chartPreviousClose") or chart_meta.get("previousClose")
                        volume = chart_meta.get("regularMarketVolume", 0.0)
                        raw_ts = chart_meta.get("regularMarketTime")

                        raw_payload = {
                            "symbol": meta["symbol"],
                            "price": price,
                            "previous_close": prev_close,
                            "volume": volume,
                            "timestamp": raw_ts,
                            "source": "NSE Public Feed via Yahoo Finance",
                            "exchange": meta["exchange"],
                            "currency": "INR"
                        }

                        is_valid, validated_data, error = data_validator.validate_and_compute_quote(raw_payload, is_index=False)
                        if is_valid:
                            return validated_data
                        else:
                            logger.warning(f"Validation rejected {symbol}: {error}")
                            return None
            except Exception as e:
                if attempt == 0:
                    import time
                    time.sleep(0.3)
                else:
                    logger.warning(f"Live fetch failed for equity {symbol}: {e}")

        return None

    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Batch retrieves quotes for a list of symbols.
        """
        results = {}
        for s in symbols:
            q = self.get_quote(s)
            if q:
                results[q["symbol"]] = q
        return results

    def get_historical(self, symbol: str, period: str = "1y", interval: str = "1d") -> List[Dict[str, Any]]:
        """
        Retrieves real chronological OHLCV candles for the specified equity.
        Supports both daily ('1d') and intraday ('5m', '15m') intervals.
        """
        meta = symbol_mapper.get_equity_meta(symbol)
        if not meta:
            return []

        yahoo_sym = meta["yahoo_symbol"]
        url = f"{self.base_url}/{yahoo_sym}?interval={interval}&range={period}"

        try:
            with httpx.Client(timeout=10.0, headers=self.headers) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    result = data.get("chart", {}).get("result", [{}])[0]
                    timestamps = result.get("timestamp", [])
                    indicators = result.get("indicators", {}).get("quote", [{}])[0]
                    opens = indicators.get("open", [])
                    highs = indicators.get("high", [])
                    lows = indicators.get("low", [])
                    closes = indicators.get("close", [])
                    volumes = indicators.get("volume", [])

                    candles = []
                    seen_times = set()
                    is_intraday = interval in ["5m", "15m", "30m", "1h", "60m"]

                    for i in range(len(timestamps)):
                        if (
                            timestamps[i] is not None
                            and opens[i] is not None
                            and highs[i] is not None
                            and lows[i] is not None
                            and closes[i] is not None
                        ):
                            try:
                                o = float(opens[i])
                                h = float(highs[i])
                                l = float(lows[i])
                                c = float(closes[i])
                                v = float(volumes[i] or 0.0)
                            except (ValueError, TypeError):
                                continue

                            if o <= 0 or h <= 0 or l <= 0 or c <= 0:
                                continue

                            # Ensure mathematically valid OHLC bounds
                            h = max(h, o, c)
                            l = min(l, o, c)

                            raw_ts = timestamps[i]
                            dt = datetime.fromtimestamp(raw_ts)

                            if is_intraday:
                                time_val = int(raw_ts)
                                iso_ts = dt.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                time_val = dt.strftime("%Y-%m-%d")
                                iso_ts = time_val

                            if time_val in seen_times:
                                continue
                            seen_times.add(time_val)

                            candles.append({
                                "timestamp": iso_ts,
                                "time": time_val,
                                "open": round(o, 2),
                                "high": round(h, 2),
                                "low": round(l, 2),
                                "close": round(c, 2),
                                "volume": round(v, 2)
                            })

                    # Ensure strictly chronological ordering
                    candles.sort(key=lambda x: x["time"])
                    return candles
        except Exception as e:
            logger.warning(f"Failed to fetch historical data for {symbol} ({period}, {interval}): {e}")

        return []

    def health_check(self) -> bool:
        quote = self.get_quote("RELIANCE")
        return quote is not None and quote.get("price", 0) > 0

stock_data_provider = StockDataProvider()
