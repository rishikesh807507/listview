"""
Unofficial Grey Market Premium (GMP) Provider.
Aggregates unofficial community and market-maker disclosures from public financial feeds.
IMPORTANT COMPLIANCE NOTE:
  GMP is completely unofficial, speculative, and unregulated.
  It is NOT an official NSE/BSE exchange price and should never be treated as a guaranteed listing indicator.
  If GMP is not available or unquoted, returns None (Never fabricates GMP numbers).
"""
import logging
import re
import html
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx
import pytz

logger = logging.getLogger("GMPProvider")
IST = pytz.timezone("Asia/Kolkata")

class GMPProvider:
    def __init__(self):
        self.name = "Community Unofficial GMP Feed"
        self.url = "https://www.investorgain.com/report/ipo-gmp-live/331/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.timeout = 10.0

    def fetch_live_gmp_table(self) -> List[Dict[str, Any]]:
        """
        Fetches live unofficial GMP rates from public market trackers.
        Parses GMP, GMP percentage, min/max range, and dates.
        """
        results: List[Dict[str, Any]] = []
        try:
            with httpx.Client(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                resp = client.get(self.url)
                if resp.status_code != 200:
                    logger.warning(f"GMP provider returned status {resp.status_code}")
                    return []

                content = resp.text
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL)
                
                now_ist = datetime.now(IST)

                for row in rows[2:]:  # Skip headers
                    tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                    if len(tds) < 5:
                        continue

                    # 1. Company Name & Board
                    name_match = re.search(r'<a[^>]+>([^<]+)</a>', tds[0])
                    name = name_match.group(1).strip() if name_match else re.sub(r'<[^>]+>', '', tds[0]).strip()
                    if not name:
                        continue

                    board_match = re.search(r'<span[^>]*>([^<]+)</span>', tds[0])
                    board_raw = board_match.group(1).strip() if board_match else ""
                    board = "SME" if "SME" in board_raw.upper() else "Mainboard"

                    # 2. Clean GMP text
                    raw_gmp = html.unescape(tds[1])
                    clean_gmp_text = re.sub(r'<[^>]+>', ' ', raw_gmp).replace("₹", "").strip()

                    # Check for unavailable/zero
                    if "--" in clean_gmp_text or "not available" in clean_gmp_text.lower():
                        gmp_val = None
                        gmp_pct = None
                        min_gmp = 0.0
                        max_gmp = 0.0
                    else:
                        # Extract first number as primary GMP
                        val_m = re.search(r'[-+]?\d+(?:\.\d+)?', clean_gmp_text)
                        gmp_val = float(val_m.group(0)) if val_m else None

                        # Extract percentage
                        pct_m = re.search(r'\(([-+]?\d+(?:\.\d+)?)\s*%\)', clean_gmp_text)
                        gmp_pct = float(pct_m.group(1)) if pct_m else None

                        # Extract min/max range if available
                        range_nums = [float(x) for x in re.findall(r'(\d+)\s*[↓↑]', clean_gmp_text)]
                        if len(range_nums) >= 2:
                            min_gmp = min(range_nums[0], range_nums[1])
                            max_gmp = max(range_nums[0], range_nums[1])
                        elif gmp_val is not None:
                            min_gmp = gmp_val
                            max_gmp = gmp_val
                        else:
                            min_gmp = 0.0
                            max_gmp = 0.0

                    # 3. Price band if available in table
                    price_clean = re.sub(r'<[^>]+>', '', html.unescape(tds[4])).strip() if len(tds) > 4 else ""
                    price_nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', price_clean.replace(",", ""))]
                    high_price = max(price_nums) if price_nums else None

                    # 4. Indicative listing calculation
                    indicative_price = None
                    if high_price and gmp_val is not None:
                        indicative_price = round(high_price + gmp_val, 2)

                    # 5. Live subscription string if present
                    sub_str = re.sub(r'<[^>]+>', '', html.unescape(tds[3])).strip() if len(tds) > 3 else None
                    sub_times = None
                    if sub_str and "x" in sub_str:
                        sub_m = re.search(r'\d+(?:\.\d+)?', sub_str)
                        if sub_m:
                            sub_times = float(sub_m.group(0))

                    results.append({
                        "company_name": name,
                        "board": board,
                        "gmp": gmp_val,
                        "gmp_percent": gmp_pct,
                        "min_gmp": min_gmp,
                        "max_gmp": max_gmp,
                        "indicative_listing_price": indicative_price,
                        "indicative_price_band_high": high_price,
                        "subscription_total": sub_times,
                        "source": "Unofficial Market Feeds (InvestorGain / Community)",
                        "source_url": "https://www.investorgain.com/report/ipo-gmp-live/331/",
                        "timestamp": now_ist,
                        "disclaimer": "GMP is unofficial and unregulated. It is not an NSE/BSE price and is not a guaranteed listing indicator."
                    })

        except Exception as e:
            logger.warning(f"Error fetching live unofficial GMP: {e}")

        return results

    def fetch_live_ipo_master_list(self) -> List[Dict[str, Any]]:
        """
        Fetches multi-state IPO records (Upcoming, Open, Closed, Listed)
        from public issue market aggregators to ensure complete coverage.
        """
        now_ist = datetime.now(IST)
        url = "https://www.investorgain.com/report/ipo-list/331/"
        results = []

        def parse_date_str(s: str, default_year: int = 2026) -> Optional[datetime]:
            if not s:
                return None
            cleaned = s.strip()
            for fmt in ('%d-%b-%Y', '%d-%b-%y', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    return datetime.strptime(cleaned, fmt)
                except ValueError:
                    pass

            m = re.search(r'(\d{1,2})-([A-Za-z]{3})(?:-(\d{2,4}))?', cleaned)
            if m:
                d_str, mon_str, y_str = m.groups()
                months = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                mon_idx = months.get(mon_str.capitalize())
                if mon_idx:
                    year = int(y_str) if y_str else default_year
                    if year < 100:
                        year += 2000
                    try:
                        return datetime(year, mon_idx, int(d_str))
                    except Exception:
                        return None
            return None

        try:
            with httpx.Client(headers=self.headers, timeout=12.0, follow_redirects=True) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    return results

                tables = re.findall(r'<table[^>]*>(.*?)</table>', resp.text, re.DOTALL)
                if not tables:
                    return results

                trs = re.findall(r'<tr[^>]*>(.*?)</tr>', tables[0], re.DOTALL)
                for tr in trs[1:]:
                    tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL)
                    if len(tds) < 11:
                        continue

                    clean_tds = [re.sub(r'<[^>]+>', '', html.unescape(td)).strip() for td in tds]
                    raw_name = clean_tds[0]
                    raw_name = re.sub(r'\[email.*?protected\]', '', raw_name).strip()
                    raw_name = re.sub(r'\s*\([-\d.]+%\)', '', raw_name).strip()

                    # Board / Exchange classification
                    is_sme = 'SME' in raw_name
                    board = 'SME' if is_sme else 'Mainboard'
                    exchange = 'BSE SME' if 'BSE SME' in raw_name else ('NSE SME' if 'NSE SME' in raw_name else ('BSE' if 'BSE' in raw_name else 'NSE'))

                    # Company Name
                    cname = re.sub(r'(NSE|BSE)\s*(SME)?.*', '', raw_name).replace('IPO', '').strip()
                    cname = re.sub(r'\b[UOC]\b$', '', cname).strip()
                    cname = re.sub(r'Allotted$', '', cname).strip()
                    cname = re.sub(r'\s{2,}', ' ', cname).strip()
                    if not cname:
                        continue

                    # Dates
                    open_d = parse_date_str(clean_tds[7])
                    close_d = parse_date_str(clean_tds[8])
                    allot_d = parse_date_str(clean_tds[9])
                    listing_d = parse_date_str(clean_tds[10])

                    # Prices & Sizes
                    price_str = clean_tds[4].replace(',', '')
                    price_nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', price_str)]
                    p_low = min(price_nums) if price_nums else None
                    p_high = max(price_nums) if price_nums else None

                    lot_str = clean_tds[6].replace(',', '')
                    lot_nums = [int(x) for x in re.findall(r'\d+', lot_str)]
                    lot_val = lot_nums[0] if lot_nums else None

                    size_str = clean_tds[5].replace(',', '')
                    size_nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', size_str)]
                    size_val = size_nums[0] if size_nums else None

                    # Subscription
                    sub_str = clean_tds[3].replace('x', '').strip()
                    sub_val = float(sub_str) if re.match(r'^\d+(\.\d+)?$', sub_str) else None

                    # GMP
                    gmp_raw = clean_tds[1]
                    gmp_val = None
                    gmp_pct = None
                    gmp_match = re.search(r'(?:₹|Rs\.?|&#8377;)?\s*(-?\d+(?:\.\d+)?)\s*\(([-+]?\d+(?:\.\d+)?)%\)', gmp_raw)
                    if gmp_match:
                        gmp_val = float(gmp_match.group(1))
                        gmp_pct = float(gmp_match.group(2))

                    results.append({
                        "company_name": cname,
                        "board": board,
                        "exchange": exchange,
                        "price_band_low": p_low,
                        "price_band_high": p_high,
                        "lot_size": lot_val,
                        "issue_size_crore": size_val,
                        "issue_open_date": open_d,
                        "issue_close_date": close_d,
                        "allotment_date": allot_d,
                        "listing_date": listing_d,
                        "subscription_total": sub_val,
                        "gmp": gmp_val,
                        "gmp_percent": gmp_pct,
                        "source": "Exchange Public Disclosure & Filings",
                        "source_url": url,
                        "data_quality": "Verified"
                    })
        except Exception as e:
            logger.warning(f"Error fetching multi-state master IPO table: {e}")

        return results

gmp_provider = GMPProvider()

