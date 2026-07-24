from typing import Dict, Tuple
import yfinance as yf

# Yahoo tickers
TICKERS = {
    "Brent": "BZ=F",
    "WTI": "CL=F",
    # Dubai has no direct ticker; caller may proxy with Brent
}

def get_oil_from_yahoo() -> Tuple[Dict[str, float], str]:
    data = {}
    for name, ticker in TICKERS.items():
        try:
            t = yf.Ticker(ticker)
            price = None
            info = getattr(t, "fast_info", None)
            if info:
                price = getattr(info, "last_price", None) or info.get("last_price")
            if price is None:
                hist = t.history(period="5d")
                if len(hist) > 0 and "Close" in hist.columns:
                    price = float(hist["Close"].iloc[-1])
            if price is not None:
                data[name] = float(price)
        except Exception:
            continue

    return data, "Yahoo Finance"
