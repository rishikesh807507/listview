"""
Market session and timezone logic for Indian stock exchanges (NSE / BSE).
Timezone: Asia/Kolkata
Handles Pre-open, Regular market, Post-market, Market closed, Weekends, and Holidays.
Strict freshness classification (Live, Recent, Delayed, Stale).
"""
from datetime import datetime, time, date
import pytz

IST = pytz.timezone("Asia/Kolkata")

# Recognized NSE/BSE Trading Holidays (sample standard calendar)
NSE_HOLIDAYS = {
    date(2026, 1, 26),  # Republic Day
    date(2026, 3, 6),   # Holi
    date(2026, 4, 3),   # Good Friday
    date(2026, 4, 14),  # Dr. Ambedkar Jayanti
    date(2026, 5, 1),   # Maharashtra Day
    date(2026, 8, 15),  # Independence Day
    date(2026, 10, 2),  # Mahatma Gandhi Jayanti
    date(2026, 10, 20), # Dussehra
    date(2026, 11, 8),  # Diwali Laxmi Pujan
    date(2026, 11, 24), # Guru Nanak Jayanti
    date(2026, 12, 25), # Christmas
}

class MarketSessionState:
    PRE_OPEN = "Pre-Open"
    REGULAR = "Regular Market"
    POST_MARKET = "Post-Market"
    CLOSED = "Market Closed"
    WEEKEND = "Weekend Closed"
    HOLIDAY = "Holiday Closed"

def get_ist_now() -> datetime:
    """Returns current localized IST datetime."""
    return datetime.now(IST)

def get_market_session(dt: datetime = None) -> dict:
    """
    Evaluates the current Indian trading session state.
    """
    now_ist = dt if dt else get_ist_now()
    if now_ist.tzinfo is None:
        now_ist = IST.localize(now_ist)
    else:
        now_ist = now_ist.astimezone(IST)

    current_date = now_ist.date()
    current_time = now_ist.time()

    # 1. Weekend check (Saturday = 5, Sunday = 6)
    if now_ist.weekday() >= 5:
        return {
            "session": MarketSessionState.WEEKEND,
            "is_open": False,
            "description": "Market Closed (Weekend)",
            "ist_time": now_ist.strftime("%d %b %Y, %I:%M %p IST")
        }

    # 2. Holiday check
    if current_date in NSE_HOLIDAYS:
        return {
            "session": MarketSessionState.HOLIDAY,
            "is_open": False,
            "description": "Market Closed (Exchange Holiday)",
            "ist_time": now_ist.strftime("%d %b %Y, %I:%M %p IST")
        }

    # 3. Session hours
    pre_open_start = time(9, 0)
    market_open = time(9, 15)
    market_close = time(15, 30)
    post_market_start = time(15, 40)
    post_market_end = time(16, 0)

    if pre_open_start <= current_time < market_open:
        return {
            "session": MarketSessionState.PRE_OPEN,
            "is_open": False,
            "description": "Pre-Market Discovery (9:00 - 9:15 AM IST)",
            "ist_time": now_ist.strftime("%d %b %Y, %I:%M %p IST")
        }
    elif market_open <= current_time <= market_close:
        return {
            "session": MarketSessionState.REGULAR,
            "is_open": True,
            "description": "Normal Trading Session (9:15 AM - 3:30 PM IST)",
            "ist_time": now_ist.strftime("%d %b %Y, %I:%M %p IST")
        }
    elif post_market_start <= current_time <= post_market_end:
        return {
            "session": MarketSessionState.POST_MARKET,
            "is_open": False,
            "description": "Post-Closing Session (3:40 - 4:00 PM IST)",
            "ist_time": now_ist.strftime("%d %b %Y, %I:%M %p IST")
        }
    else:
        return {
            "session": MarketSessionState.CLOSED,
            "is_open": False,
            "description": "Market Closed",
            "ist_time": now_ist.strftime("%d %b %Y, %I:%M %p IST")
        }

# Alias for testing and standard imports
get_current_market_session = get_market_session

def evaluate_freshness(timestamp) -> dict:
    """
    Evaluates freshness of a quote based on timestamp age and market hours:
      LIVE: < 2 minutes old AND within regular session
      RECENT: 2–15 minutes old
      DELAYED: 15–60 minutes old
      STALE: > 60 minutes old
    """
    now_ist = get_ist_now()
    if isinstance(timestamp, (int, float)):
        ts_ist = datetime.fromtimestamp(timestamp, tz=IST)
    elif isinstance(timestamp, datetime):
        if timestamp.tzinfo is None:
            ts_ist = IST.localize(timestamp)
        else:
            ts_ist = timestamp.astimezone(IST)
    else:
        try:
            ts_ist = datetime.fromisoformat(str(timestamp))
            if ts_ist.tzinfo is None:
                ts_ist = IST.localize(ts_ist)
            else:
                ts_ist = ts_ist.astimezone(IST)
        except Exception:
            ts_ist = now_ist

    age_seconds = (now_ist - ts_ist).total_seconds()
    session_info = get_market_session(now_ist)

    # 1. Stale check: if older than 2 days (weekend threshold), it is always stale
    if age_seconds > 172800:
        days = round(age_seconds / 86400, 1)
        return {
            "freshness": "Stale",
            "age_seconds": int(age_seconds),
            "formatted_time": ts_ist.strftime("%d %b %Y, %I:%M %p IST"),
            "badge_color": "red",
            "is_live": False,
            "warning": f"⚠️ Stale snapshot (Last verified {days} days ago)"
        }

    # 2. If the market is closed, we cannot label data as "LIVE"
    if not session_info["is_open"]:
        return {
            "freshness": "Market Closed",
            "age_seconds": max(0, int(age_seconds)),
            "formatted_time": ts_ist.strftime("%d %b %Y, %I:%M %p IST"),
            "badge_color": "neutral",
            "is_live": False,
            "warning": "Market closed. Displaying last verified closing snapshot."
        }

    # 3. Regular trading session freshness thresholds
    if age_seconds < 120:  # < 2 min
        return {
            "freshness": "Live",
            "age_seconds": max(0, int(age_seconds)),
            "formatted_time": ts_ist.strftime("%I:%M:%S %p IST"),
            "badge_color": "green",
            "is_live": True,
            "warning": None
        }
    elif age_seconds < 900:  # 2 - 15 min
        return {
            "freshness": "Recent",
            "age_seconds": int(age_seconds),
            "formatted_time": ts_ist.strftime("%I:%M %p IST"),
            "badge_color": "green",
            "is_live": False,
            "warning": None
        }
    elif age_seconds < 3600:  # 15 - 60 min
        mins = int(age_seconds / 60)
        return {
            "freshness": "Delayed",
            "age_seconds": int(age_seconds),
            "formatted_time": ts_ist.strftime("%I:%M %p IST"),
            "badge_color": "amber",
            "is_live": False,
            "warning": f"Delayed by {mins} minutes"
        }
    else:
        hours = round(age_seconds / 3600, 1)
        return {
            "freshness": "Stale",
            "age_seconds": int(age_seconds),
            "formatted_time": ts_ist.strftime("%d %b %Y, %I:%M %p IST"),
            "badge_color": "red",
            "is_live": False,
            "warning": f"⚠️ Stale data (Last updated {hours} hours ago)"
        }
