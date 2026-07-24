from typing import List, Dict, Optional

def _bold_or_na(v: Optional[str]) -> str:
    if v is None or v == "" or v.lower() == "n/a":
        return "n/a"
    return f"**{v}**"

def render_md(date_disp: str, rows: List[Dict], notes: Dict) -> str:
    lines = []
    lines.append(f"# 石化產品價格日誌 ({date_disp}) \n")
    lines.append("## 今日價格與變動\n")
    lines.append("| 產品 | 基準/地區 & 交易條件 | 今日價格 | 與前一日差 | 與上一周均價差* | 單位 |")
    lines.append("|---|---|---:|---:|---:|---|")
    for r in rows:
        # today, d1, dw columns already formatted per spec
        lines.append(f"| **{r['name']}** | {r['basis']} | {r['today']} | {r['d1']} | {r['dw']} | {r['unit']} |")
    lines.append("\n\\* 上一周均價：  ")
    lines.append("- 原油：近五個結算價均值  ")
    lines.append("- Naphtha：近五個亞洲收盤均值（OSN M1）  \n")
    lines.append("† Dubai：採 ICE Dubai 1st Line 近月期貨（以 Platts Dubai 日評結算）  \n")
    lines.append("---\n")
    lines.append("## 趨勢分析\n")
    # If user provides analysis notes use them; otherwise use general placeholders
    analysis = notes.get("analysis_notes") or [
        "原油（Brent、WTI）  \n  受供需與地緣影響，留意美國庫存與歐亞供應變動。  ",
        "Dubai 原油  \n  若以 Brent 代理，短線與 Brent 同步為主；需關注中東 OSP 與裝船節奏。  ",
        "Naphtha（CFR Japan）  \n  與汽油/裂解利差密切相關，颱風/檢修將影響到港節奏。  ",
        "芳烴/烯烴（MX、乙烯、丙烯、苯、甲苯、OX、PX）  \n  多屬付費日評市場，建議接入授權數據源以獲得逐日追蹤。  ",
    ]
    for item in analysis:
        lines.append(f"- {item}")
    lines.append("\n---\n")
    lines.append("## 來源與方法\n")
    for s in notes.get("sources", [
        "原油數據：路透社即時與前日結算（若失敗回退 Yahoo Finance）。  ",
        "Naphtha/芳烴/烯烴：由 `data/manual_overrides.json` 提供價格、來源與交易條件。  ",
        "單位換算：$ / bbl → $ / ton 以 **1 ton ≈ 7.33 bbl**。  ",
    ]):
        lines.append(f"- {s}")
    lines.append("\n---\n")
    lines.append("> ⚠️ 註：部分石化品每日報價屬付費資訊（Platts / ICIS / Argus 等），此處僅引用可公開數據；若需完整日追蹤，建議接入付費數據源。")
    return "\n".join(lines)
