import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Tuple
from .yahoo_fallback import get_oil_from_yahoo

REUTERS_COMMODITIES_URL = "https://www.reuters.com/markets/commodities/"

def _extract_number(blob: str) -> Optional[float]:
    m = re.search(r"[-+]?\d+(?:\.\d+)?", blob.replace(",", ""))
    if m:
        try:
            return float(m.group())
        except Exception:
            return None
    return None

def fetch_oil_prices() -> Tuple[Dict[str, float], str, bool]:
    """
    Try to fetch Brent/WTI/Dubai prices from Reuters commodities page.
    Returns: (prices_dict, source_label, dubai_proxied)
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    prices = {"Brent": None, "WTI": None, "Dubai": None}
    dubai_proxied = False
    try:
        resp = requests.get(REUTERS_COMMODITIES_URL, headers=headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        label_map = {
            "Brent": ["Brent crude", "Brent"],
            "WTI": ["U.S. crude", "WTI crude", "WTI"],
            "Dubai": ["Dubai crude", "Dubai"],
        }

        for k, aliases in label_map.items():
            found = None
            for alias in aliases:
                node = soup.find(string=re.compile(alias, re.I))
                if not node:
                    continue
                # look around node's parent
                parent = node.parent
                text = parent.get_text(" ", strip=True)
                val = _extract_number(text)
                if val is None:
                    # search some next siblings
                    sibs = getattr(parent, "next_siblings", [])
                    for s in sibs:
                        try:
                            t = s.get_text(" ", strip=True)
                            val = _extract_number(t)
                            if val is not None:
                                break
                        except Exception:
                            continue
                if val is not None:
                    found = val
                    break
            prices[k] = found

        # Fallback from Yahoo for missing
        if any(v is None for v in prices.values()):
            y, ysrc = get_oil_from_yahoo()
            for k in ["Brent", "WTI"]:
                if prices.get(k) is None and y.get(k) is not None:
                    prices[k] = y[k]

        # Dubai proxy by Brent if still missing
        if prices.get("Dubai") is None and prices.get("Brent") is not None:
            prices["Dubai"] = prices["Brent"]
            dubai_proxied = True

        # Clean None
        prices = {k: v for k, v in prices.items() if v is not None}
        source = "Reuters with Yahoo fallback" if len(prices) < 3 else "Reuters"

        return prices, source, dubai_proxied
    except Exception:
        y, ysrc = get_oil_from_yahoo()
        # proxy Dubai
        if "Brent" in y:
            y["Dubai"] = y["Brent"]
            dubai_proxied = True
        return y, ysrc, dubai_proxied
