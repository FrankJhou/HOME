import os, json, math
from datetime import datetime
from typing import Optional
import pytz
import pandas as pd
from dateutil.relativedelta import relativedelta

from scripts.config import DATA_DIR, OUTPUT_DIR, BBL_PER_TON, TZ_NAME
from scripts.sources.reuters import fetch_oil_prices
from scripts.render_markdown import render_md

TZ = pytz.timezone(TZ_NAME)

def usd_per_bbl_to_ton(v: Optional[float]) -> Optional[float]:
    if v is None:
        return None
    return v * BBL_PER_TON

def load_json(path: str, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_jsonl(path: str):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def append_jsonl(path: str, obj: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def diff_vs_prev(cur: Optional[float], prev: Optional[float]) -> Optional[float]:
    if cur is None or prev is None or (isinstance(prev, float) and (pd.isna(prev))):
        return None
    return float(cur - prev)

def diff_vs_week_avg(cur: Optional[float], series: pd.Series) -> Optional[float]:
    # Use previous 5 non-null entries (excluding today) as "上一周均價"
    clean = series.dropna().astype(float)
    if len(clean) < 6:
        return None
    last6 = clean.tail(6)
    today_val = last6.iloc[-1]
    prev5 = last6.iloc[:-1]
    if len(prev5) < 5:
        return None
    return float(today_val - prev5.mean())

def fmt_val(v: Optional[float], digits=2, bold=True) -> str:
    if v is None or (isinstance(v, float) and (pd.isna(v))):
        return "n/a"
    s = f"{v:.{digits}f}"
    return f"**{s}**" if bold else s

def fmt_val0(v: Optional[float], bold=True) -> str:
    # no decimals
    if v is None or (isinstance(v, float) and (pd.isna(v))):
        return "n/a"
    s = f"{v:.0f}"
    return f"**{s}**" if bold else s

def fmt_signed(v: Optional[float], digits=2, bold=True) -> str:
    if v is None or (isinstance(v, float) and (pd.isna(v))):
        return "n/a"
    s = f"{v:+.{digits}f}"
    return f"**{s}**" if bold else s

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    today = datetime.now(TZ).date()
    date_str = today.strftime("%Y-%m-%d")
    date_disp = today.strftime("%Y/%m/%d")

    # Load history and overrides
    hist_path = os.path.join(DATA_DIR, "history.jsonl")
    history = load_jsonl(hist_path)
    df = pd.DataFrame(history)

    overrides = load_json(os.path.join(DATA_DIR, "manual_overrides.json"), default={})

    # Fetch oils
    oil_prices, oil_source, dubai_proxied = fetch_oil_prices()
    brent_bbl = oil_prices.get("Brent")
    wti_bbl = oil_prices.get("WTI")
    dubai_bbl = oil_prices.get("Dubai")

    # Convert to ton
    brent_ton = usd_per_bbl_to_ton(brent_bbl) if brent_bbl is not None else None
    wti_ton = usd_per_bbl_to_ton(wti_bbl) if wti_bbl is not None else None
    dubai_ton = usd_per_bbl_to_ton(dubai_bbl) if dubai_bbl is not None else None

    # Build today's record
    rec = {
        "date": date_str,
        "Brent_usd_bbl": brent_bbl,
        "Brent_usd_ton": brent_ton,
        "WTI_usd_bbl": wti_bbl,
        "WTI_usd_ton": wti_ton,
        "Dubai_usd_bbl": dubai_bbl,
        "Dubai_usd_ton": dubai_ton,
        "Naphtha_usd_ton": overrides.get("Naphtha", {}).get("price"),
        "MX_usd_ton": overrides.get("Isomer Xylene", {}).get("price"),
        "Ethylene_usd_ton": overrides.get("Ethylene", {}).get("price"),
        "Propylene_usd_ton": overrides.get("Propylene", {}).get("price"),
        "Benzene_usd_ton": overrides.get("Benzene", {}).get("price"),
        "Toluene_usd_ton": overrides.get("Toluene", {}).get("price"),
        "OX_usd_ton": overrides.get("OX", {}).get("price"),
        "PX_usd_ton": overrides.get("PX", {}).get("price"),
        "_basis": {
            "Brent 原油": "ICE Brent 近月",
            "WTI 原油": "NYMEX WTI 近月",
            "Dubai 原油†": "ICE Dubai 近月（期貨）",
            "Naphtha": overrides.get("Naphtha", {}).get("basis", "—"),
            "Isomer Xylene（MX）": overrides.get("Isomer Xylene", {}).get("basis", "—"),
            "Ethylene": overrides.get("Ethylene", {}).get("basis", "—"),
            "Propylene": overrides.get("Propylene", {}).get("basis", "—"),
            "Benzene": overrides.get("Benzene", {}).get("basis", "—"),
            "Toluene": overrides.get("Toluene", {}).get("basis", "—"),
            "o-Xylene（OX）": overrides.get("OX", {}).get("basis", "—"),
            "p-Xylene（PX）": overrides.get("PX", {}).get("basis", "—"),
        },
        "_sources": {
            "oil": ("Reuters（fallback: Yahoo）; Dubai 代理" if dubai_proxied else "Reuters"),
            "Naphtha": overrides.get("Naphtha", {}).get("source"),
            "Isomer Xylene（MX）": overrides.get("Isomer Xylene", {}).get("source"),
            "Ethylene": overrides.get("Ethylene", {}).get("source"),
            "Propylene": overrides.get("Propylene", {}).get("source"),
            "Benzene": overrides.get("Benzene", {}).get("source"),
            "Toluene": overrides.get("Toluene", {}).get("source"),
            "o-Xylene（OX）": overrides.get("OX", {}).get("source"),
            "p-Xylene（PX）": overrides.get("PX", {}).get("source"),
        }
    }

    # Append today's record, then compute diffs using the new df (so today has index at tail)
    df = pd.concat([df, pd.DataFrame([rec])], ignore_index=True)
    today_idx = len(df) - 1

    def col_delta(col: str):
        d1 = None
        if today_idx > 0 and col in df.columns:
            prev = df[col].iloc[today_idx - 1]
            cur = df[col].iloc[today_idx]
            if pd.notna(prev) and pd.notna(cur):
                d1 = float(cur - prev)
        dw = None
        if col in df.columns:
            dw = diff_vs_week_avg(df[col].iloc[today_idx], df[col])
        return d1, dw

    rows = []

    # Oil rows: display "bbl / ton" for values and deltas
    def oil_row(name: str, bbl_col: str, ton_col: str):
        bbl = df[bbl_col].iloc[today_idx] if bbl_col in df else None
        ton = df[ton_col].iloc[today_idx] if ton_col in df else None
        d1_bbl, dw_bbl = col_delta(bbl_col)

        today_txt = "n/a"
        if bbl is not None and ton is not None and pd.notna(bbl) and pd.notna(ton):
            today_txt = f"**{bbl:.2f}** / **{ton:.2f}**"

        d1_txt = "n/a"
        if d1_bbl is not None:
            d1_txt = f"**{d1_bbl:+.2f}** / **{(d1_bbl*BBL_PER_TON):+.2f}**"
        dw_txt = "n/a"
        if dw_bbl is not None:
            dw_txt = f"**{dw_bbl:+.2f}** / **{(dw_bbl*BBL_PER_TON):+.2f}**"

        return {
            "name": name,
            "basis": rec["_basis"][name],
            "today": today_txt,
            "d1": d1_txt,
            "dw": dw_txt,
            "unit": "USD/bbl、USD/ton"
        }

    rows.append(oil_row("Brent 原油", "Brent_usd_bbl", "Brent_usd_ton"))
    rows.append(oil_row("WTI 原油", "WTI_usd_bbl", "WTI_usd_ton"))
    rows.append(oil_row("Dubai 原油†", "Dubai_usd_bbl", "Dubai_usd_ton"))

    # Others (usd/ton only)
    def other_row(key: str, display: str, date_suffix: Optional[str] = None):
        col = f"{key}_usd_ton"
        val = df[col].iloc[today_idx] if col in df else None
        d1, dw = col_delta(col)
        today_txt = "n/a"
        if val is not None and pd.notna(val):
            today_txt = f"**{val:.0f}**"
            if date_suffix:
                today_txt += f"（{date_suffix}）"
        d1_txt = "n/a" if d1 is None else f"**{d1:+.1f}**"
        dw_txt = "n/a" if dw is None else f"**{dw:+.1f}**"
        return {
            "name": display,
            "basis": rec["_basis"][display],
            "today": today_txt,
            "d1": d1_txt,
            "dw": dw_txt,
            "unit": "USD/ton"
        }

    rows.append(other_row("Naphtha", "Naphtha"))
    rows.append(other_row("MX", "Isomer Xylene（MX）"))
    rows.append(other_row("Ethylene", "Ethylene"))
    rows.append(other_row("Propylene", "Propylene"))
    rows.append(other_row("Benzene", "Benzene"))
    rows.append(other_row("Toluene", "Toluene"))
    rows.append(other_row("OX", "o-Xylene（OX）"))
    rows.append(other_row("PX", "p-Xylene（PX）"))

    # Notes for trailing sections
    notes = {
        "analysis_notes": overrides.get("analysis_notes", []),
        "sources": [
            f"原油數據：{rec['_sources']['oil']}。  ",
            f"Naphtha：{rec['_sources'].get('Naphtha') or 'manual_overrides.json'}。  ",
            "芳烴/烯烴：見 manual_overrides.json（來源與交易條件由你提供）。  ",
            "單位換算：$ / bbl → $ / ton 以 **1 ton ≈ 7.33 bbl**。  ",
        ]
    }

    md = render_md(date_disp, rows, notes)

    # Write outputs
    out_path = os.path.join(OUTPUT_DIR, f"{date_str}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)

    # Persist today's record
    with open(hist_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
