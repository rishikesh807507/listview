"""
Automatic IPO Status Engine for Indian Stock Markets (NSE / BSE).
Timezone: Asia/Kolkata (IST).
Strict date and event-based status calculation.
Never assigns statuses manually; never allows past listed IPOs to appear as Upcoming or Open.

Statuses:
  - UPCOMING: Issue open date is in the future.
  - OPEN: Current date/time is between issue open date and issue close date (inclusive).
  - CLOSED: Issue close date has passed, awaiting allotment.
  - ALLOTMENT: Allotment date has arrived/passed, awaiting refund/demat credit.
  - REFUND: Refund initiation date has arrived/passed.
  - DEMAT_CREDIT: Shares credited to demat accounts.
  - LISTING_TODAY: Listing date matches current IST date.
  - LISTED: Listing date has passed in IST.
  - POSTPONED: Officially postponed by exchange/issuer.
  - WITHDRAWN: Officially withdrawn by issuer.
  - UNKNOWN: Dates are missing or indeterminate.
"""
from datetime import datetime, date, time
from typing import Optional, Dict, Any
import pytz

IST = pytz.timezone("Asia/Kolkata")

class IPOStatus:
    UPCOMING = "UPCOMING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ALLOTMENT = "ALLOTMENT"
    REFUND = "REFUND"
    DEMAT_CREDIT = "DEMAT_CREDIT"
    LISTING_TODAY = "LISTING_TODAY"
    LISTED = "LISTED"
    POSTPONED = "POSTPONED"
    WITHDRAWN = "WITHDRAWN"
    UNKNOWN = "UNKNOWN"

def get_ist_now() -> datetime:
    """Returns the current localized IST datetime."""
    return datetime.now(IST)

def to_ist_date(dt: Optional[datetime]) -> Optional[date]:
    """Converts a datetime to an IST date object."""
    if not dt:
        return None
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt
    if dt.tzinfo is None:
        # Treat naive datetime as IST
        dt_ist = IST.localize(dt)
    else:
        dt_ist = dt.astimezone(IST)
    return dt_ist.date()

def compute_ipo_status(
    open_date: Optional[datetime],
    close_date: Optional[datetime],
    listing_date: Optional[datetime] = None,
    allotment_date: Optional[datetime] = None,
    refund_date: Optional[datetime] = None,
    demat_credit_date: Optional[datetime] = None,
    override_status: Optional[str] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Computes real-time verified IPO status based on Indian Standard Time.
    """
    now_ist = as_of.astimezone(IST) if as_of and as_of.tzinfo else (IST.localize(as_of) if as_of else get_ist_now())
    today_ist = now_ist.date()

    # Respect explicit regulatory statuses
    if override_status:
        norm = override_status.strip().upper()
        if norm in (IPOStatus.POSTPONED, IPOStatus.WITHDRAWN):
            return {
                "status": norm,
                "label": "Postponed" if norm == IPOStatus.POSTPONED else "Withdrawn",
                "badge": "neutral",
                "reason": f"Issue officially marked as {norm.lower()}",
                "as_of_date": today_ist.isoformat()
            }

    d_open = to_ist_date(open_date)
    d_close = to_ist_date(close_date)
    d_listing = to_ist_date(listing_date)
    d_allotment = to_ist_date(allotment_date)
    d_refund = to_ist_date(refund_date)
    d_demat = to_ist_date(demat_credit_date)

    # 1. Listing check: Has listing occurred or is it listing today?
    if d_listing:
        if today_ist > d_listing:
            return {
                "status": IPOStatus.LISTED,
                "label": "Listed",
                "badge": "neutral",
                "reason": f"Listed on {d_listing.strftime('%d %b %Y')}",
                "as_of_date": today_ist.isoformat()
            }
        elif today_ist == d_listing:
            return {
                "status": IPOStatus.LISTING_TODAY,
                "label": "Listing Today",
                "badge": "amber",
                "reason": f"Listing today ({d_listing.strftime('%d %b %Y')}) on Indian Exchanges",
                "as_of_date": today_ist.isoformat()
            }

    # 2. Demat Credit check
    if d_demat and today_ist >= d_demat:
        return {
            "status": IPOStatus.DEMAT_CREDIT,
            "label": "Demat Credit",
            "badge": "blue",
            "reason": f"Shares credited to Demat ({d_demat.strftime('%d %b %Y')})",
            "as_of_date": today_ist.isoformat()
        }

    # 3. Refund check
    if d_refund and today_ist >= d_refund:
        return {
            "status": IPOStatus.REFUND,
            "label": "Refund Initiated",
            "badge": "blue",
            "reason": f"Refunds initiated on {d_refund.strftime('%d %b %Y')}",
            "as_of_date": today_ist.isoformat()
        }

    # 4. Allotment check
    if d_allotment and today_ist >= d_allotment:
        return {
            "status": IPOStatus.ALLOTMENT,
            "label": "Allotment Finalized",
            "badge": "blue",
            "reason": f"Basis of allotment finalized on {d_allotment.strftime('%d %b %Y')}",
            "as_of_date": today_ist.isoformat()
        }

    # 5. Closed check: Past close date, awaiting allotment
    if d_close and today_ist > d_close:
        return {
            "status": IPOStatus.CLOSED,
            "label": "Closed",
            "badge": "rose",
            "reason": f"Bidding closed on {d_close.strftime('%d %b %Y')}",
            "as_of_date": today_ist.isoformat()
        }

    # 6. Open check: Active bidding period
    if d_open and d_close and d_open <= today_ist <= d_close:
        # Note: on closing day, retail bidding closes at 5:00 PM IST
        is_closing_day = (today_ist == d_close)
        note = "Closes today at 5:00 PM IST" if is_closing_day else f"Open until {d_close.strftime('%d %b %Y')}"
        return {
            "status": IPOStatus.OPEN,
            "label": "Open (Bidding Active)",
            "badge": "emerald",
            "reason": note,
            "as_of_date": today_ist.isoformat()
        }

    # 7. Upcoming check: Open date in future
    if d_open and today_ist < d_open:
        days_left = (d_open - today_ist).days
        return {
            "status": IPOStatus.UPCOMING,
            "label": "Upcoming",
            "badge": "sky",
            "reason": f"Opens on {d_open.strftime('%d %b %Y')} ({days_left} day{'s' if days_left > 1 else ''} to open)",
            "as_of_date": today_ist.isoformat()
        }

    # Missing dates
    return {
        "status": IPOStatus.UNKNOWN,
        "label": "Dates To Be Announced",
        "badge": "neutral",
        "reason": "Official issue dates not yet finalized",
        "as_of_date": today_ist.isoformat()
    }
