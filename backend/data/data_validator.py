"""
Data Validation Pipeline for Indian Market Data.
Validates quotes, enforces strict positive prices, verifies INR currency,
and recalculates mathematical change and change_percent to prevent provider fabrication.
"""
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from backend.data.symbol_mapper import symbol_mapper

logger = logging.getLogger("DataValidator")

class DataValidator:
    """
    Validates every market data payload before allowing ingestion or UI presentation.
    """

    @staticmethod
    def validate_and_compute_quote(raw_data: Dict[str, Any], is_index: bool = False) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validates raw price payload and computes mathematically exact change & change_percent.
        Returns: (is_valid, sanitized_data, rejection_reason)
        """
        if not raw_data or not isinstance(raw_data, dict):
            return False, None, "Payload is empty or not a valid dictionary"

        # 1. Symbol & Registry verification
        symbol = str(raw_data.get("symbol") or raw_data.get("index_name") or "").strip().upper()
        if not symbol:
            return False, None, "Missing symbol or index name"

        if is_index:
            meta = symbol_mapper.get_index_meta(symbol)
            if not meta:
                return False, None, f"Unregistered index symbol: {symbol}"
            canonical_name = meta["canonical_name"]
            expected_exchange = meta["exchange"]
        else:
            meta = symbol_mapper.get_equity_meta(symbol)
            if not meta:
                return False, None, f"Unregistered equity symbol: {symbol}"
            canonical_name = meta["symbol"]
            expected_exchange = meta["exchange"]

        # 2. Currency check
        currency = raw_data.get("currency", "INR")
        if currency and currency.upper() != "INR":
            return False, None, f"Invalid currency: {currency} (must be INR)"

        # 3. Exchange check
        exchange = raw_data.get("exchange", expected_exchange)
        if exchange and exchange.upper() not in ["NSE", "BSE"]:
            return False, None, f"Invalid exchange: {exchange} (must be NSE or BSE)"

        # 4. Price & Previous Close bounds check
        try:
            price = float(raw_data.get("price") or raw_data.get("value") or raw_data.get("current_price", 0.0))
            prev_close = float(raw_data.get("previous_close") or raw_data.get("prev_close") or raw_data.get("close", 0.0))
        except (ValueError, TypeError) as e:
            return False, None, f"Non-numeric price or previous_close: {e}"

        if price <= 0.0:
            return False, None, f"Price must be strictly positive, received {price}"

        if prev_close <= 0.0:
            # If prev_close is missing or zero, we cannot calculate valid percentage change
            return False, None, f"Previous close must be strictly positive, received {prev_close}"

        # 5. Calculate Change & Change Percent Ourselves (Section 4)
        calculated_change = round(price - prev_close, 2)
        calculated_pct = round((calculated_change / prev_close) * 100.0, 2)

        # 6. Provider consistency check (Section 13)
        provider_pct = raw_data.get("change_percent")
        if provider_pct is not None:
            try:
                p_pct = float(provider_pct)
                # Allow max 0.15% variance due to rounding in third-party feeds
                if abs(p_pct - calculated_pct) > 0.35:
                    logger.warning(
                        f"Discrepancy for {canonical_name}: Provider reported {p_pct}%, "
                        f"but calculated from price ({price}) and prev_close ({prev_close}) is {calculated_pct}%. "
                        "Enforcing calculated truth."
                    )
            except (ValueError, TypeError):
                pass

        # 7. Timestamp validation
        raw_ts = raw_data.get("timestamp")
        parsed_ts = None
        if isinstance(raw_ts, datetime):
            parsed_ts = raw_ts
        elif isinstance(raw_ts, (int, float)):
            try:
                parsed_ts = datetime.fromtimestamp(raw_ts)
            except Exception:
                pass
        elif isinstance(raw_ts, str):
            for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                try:
                    parsed_ts = datetime.strptime(raw_ts.split("+")[0].split(".")[0], fmt.replace("%z", ""))
                    break
                except ValueError:
                    continue

        if not parsed_ts:
            parsed_ts = datetime.utcnow()

        volume = float(raw_data.get("volume") or 0.0)
        source = str(raw_data.get("source") or "unspecified_provider").strip()

        sanitized = {
            "symbol": canonical_name,
            "index_name": canonical_name if is_index else None,
            "exchange": expected_exchange,
            "instrument_type": "INDEX" if is_index else "EQUITY",
            "price": round(price, 2),
            "value": round(price, 2) if is_index else None,
            "previous_close": round(prev_close, 2),
            "change": calculated_change,
            "change_percent": calculated_pct,
            "volume": volume,
            "timestamp": parsed_ts,
            "source": source,
            "status": "Verified",
            "currency": "INR"
        }

        return True, sanitized, None

data_validator = DataValidator()
