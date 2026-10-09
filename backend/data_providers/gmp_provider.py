import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from backend.config import settings
from backend.data_providers.base_provider import BaseProvider

logger = logging.getLogger("GMPProvider")

class GMPProvider(BaseProvider):
    """
    Open-source machine-readable IPO GMP Provider (Spectrumz00/india-ipo-gmp-data).
    Data available under CC BY 4.0 attribution.
    Formula: Estimated Listing Price = Upper Price Band + GMP
    Mandatory notice: GMP is unofficial, unregulated, and non-binding.
    """
    DISCLAIMER = (
        "GMP is unofficial and unregulated. It is not an NSE/BSE price and "
        "should not be treated as a guaranteed listing price."
    )

    def __init__(self):
        super().__init__("Open Dataset (Spectrumz00/india-ipo-gmp-data)")
        self.raw_url = settings.GMP_GITHUB_RAW_URL

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.head(self.raw_url)
                return resp.status_code == 200
        except Exception:
            return False

    def fetch_live_gmp(self) -> List[Dict[str, Any]]:
        """
        Fetch machine-readable GMP dataset from open GitHub source.
        Validates structure and computes estimated listing metrics.
        """
        results = []
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(self.raw_url)
                if resp.status_code == 200:
                    raw_data = resp.json()
                    # The open dataset can be list or dict
                    items = raw_data if isinstance(raw_data, list) else raw_data.get("ipos", [])
                    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                    
                    for item in items:
                        name = item.get("name") or item.get("company_name", "")
                        gmp_val = float(item.get("gmp") or 0.0)
                        price_band = float(item.get("price") or item.get("upper_price", 0.0))
                        
                        est_listing_price = price_band + gmp_val if price_band > 0 else gmp_val
                        gmp_pct = round((gmp_val / price_band * 100), 2) if price_band > 0 else 0.0
                        
                        results.append({
                            "company_name": name,
                            "gmp": gmp_val,
                            "gmp_percent": gmp_pct,
                            "min_gmp": float(item.get("min_gmp") or gmp_val),
                            "max_gmp": float(item.get("max_gmp") or gmp_val),
                            "estimated_listing_price": est_listing_price,
                            "estimated_listing_gain": gmp_pct,
                            "source": self.name,
                            "disclaimer": self.DISCLAIMER,
                            "timestamp": now_str,
                            "status": "Live"
                        })
                    self.last_status = "Live"
                    self.last_updated = now_str
                    return results
        except Exception as e:
            logger.warning(f"Failed to fetch live GMP from GitHub repository: {e}")
        
        self.last_status = "Unavailable / Fallback"
        return []
