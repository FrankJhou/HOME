# 石化產品價格日誌自動化（每周一 09:00 台北時間）

本專案會：
- **每周一 09:00（台北時間）** 自動執行 GitHub Actions，抓取/整合數據 → 產生 Markdown（`logs/YYYY-MM-DD.md`）→ 自動 commit。
- 原油（Brent、WTI、Dubai）以 **路透社** 為首選來源；若抓取失敗則回退 **Yahoo Finance**（只作後備）。
- 石腦油/芳烴/烯烴（Naphtha、MX、Ethylene、Propylene、Benzene、Toluene、OX、PX）可在 `data/manual_overrides.json` 供應價格、來源、交易條件（FOB/CFR 等）。

> **重要**：部分價目為付費日評（Platts / S&P Global Commodity Insights / ICIS / Argus 等），本專案不包含這些付費 API；請在 `manual_overrides.json` 補入可用數據。

---

## 一、快速使用（5 步完成）

1. **建立 GitHub Repo**（或使用既有 Repo）。
2. 將此專案所有檔案上傳到 Repo 的根目錄（建議保留原結構）。
3. 進入 **Settings → Secrets and variables → Actions** 新增：
   - `GH_TOKEN`：具備 `repo` 權限的 PAT（用來讓 workflow commit & push）。
4. （可選）到 `data/manual_overrides.json` 補入 Naphtha/芳烴/烯烴的價格、來源與交易條件。
5. 開啟 **Actions** 頁籤：
   - 你可以按 **Run workflow** 立即產生一份（`workflow_dispatch`），
   - 或等到每週一 09:00（台北）自動跑。

產出的 Markdown 會位在：`logs/YYY-MM-DD.md`，檔名使用執行當天的日期。

---

## 二、檔案結構

```
.
├─ .github/workflows/petro-weekly.yml  # 每周一 09:00（台北）觸發
├─ scripts/
│  ├─ fetch_prices.py                  # 主流程：抓取/整合 → 計算 → 產生 Markdown
│  ├─ render_markdown.py               # 輸出你指定的「表格 + 分析 + 來源與方法」格式
│  └─ sources/
│     ├─ reuters.py                    # 解析 Reuters commodities 頁面（可能變動，內含防呆）
│     └─ yahoo_fallback.py             # Yahoo Finance 後備（BZ=F、CL=F）
├─ data/
│  ├─ history.jsonl                    # 歷史紀錄（每天/每週一行），用於計算「與前一日/上一周均價差」
│  └─ manual_overrides.json            # Naphtha/芳烴/烯烴價格與備註（來源、交易條件）
├─ logs/                                # 產出的 md 會放這裡
├─ requirements.txt
└─ README.md
```

---

## 三、如何寫入來源與交易條件（manual_overrides.json）

`data/manual_overrides.json` 範例（你可以直接改成當天最新數值）：
```json
{
  "Naphtha": { "price": 599, "basis": "CFR Japan（OSN M1）", "source": "Reuters/Refinitiv" },
  "Isomer Xylene": { "price": 680, "basis": "FOB Korea", "source": "Echemi (2025-08-14)" },
  "Ethylene": { "price": 825, "basis": "CFR NE Asia", "source": "Echemi (2025-08-15)" },
  "Propylene": { "price": 775, "basis": "CFR China", "source": "Echemi (2025-08-15)" },
  "Benzene": { "price": 732, "basis": "FOB Korea", "source": "Echemi (2025-08-18)" },
  "Toluene": { "price": 682, "basis": "FOB Korea", "source": "Echemi (2025-08-14)" },
  "OX": { "price": 830, "basis": "FOB Korea", "source": "Public dashboard" },
  "PX": { "price": 828, "basis": "CFR Taiwan/China", "source": "Public report (2025-06-03)" }
}
```

- `price` 單位皆為 **USD/ton**。  
- `basis` 建議寫清楚基準與交易條件（例如 *FOB Korea*、*CFR Japan*）。
- `source` 寫明出處（網站/報價商/日期）。

> 你也可以每天/每週更新這個檔案；Workflow 會自動把它寫入 `history.jsonl`，讓「與前一日」與「上一周均價」逐步有意義。

---

## 四、排程（CRON）與手動執行

- 本專案預設 **每周一 09:00 台北時間** 執行（對應 **01:00 UTC**）。
- 你可以在 `.github/workflows/petro-weekly.yml` 調整：

```yaml
on:
  schedule:
    - cron: '0 1 * * 1'  # 01:00 UTC = 09:00 Asia/Taipei, Mondays
  workflow_dispatch:      # 允許手動按鈕觸發
```

---

## 五、常見問題

- **Dubai 當天抓不到怎麼辦？**  
  會在程式內自動以 **Brent 近月** 代理（表格裡「Dubai 原油†」會加註 †）。

- **上一周均價怎麼算？**  
  以「最近 5 筆歷史（不含今天）」的均值為上一周均價；若不足 5 筆，會顯示 `n/a`。

- **如何立即看到產出？**  
  在 Actions 頁面 **Run workflow**；或本機執行：  
  ```bash
  python -m pip install -r requirements.txt
  python scripts/fetch_prices.py
  ```

---

## 六、輸出格式（與你指定的 GitHub MD 完全一致）

本專案輸出的 md 會長這樣（日期自動帶入今天）：

```
# 石化產品價格日誌 (2025/08/29) 

## 今日價格與變動

| 產品 | 基準/地區 & 交易條件 | 今日價格 | 與前一日差 | 與上一周均價差* | 單位 |
|---|---|---:|---:|---:|---|
| **Brent 原油** | ICE Brent 近月 | **XX.XX** / **XXXX.XX** | **+/-X.XX** / **+/-X.XX** | n/a | USD/bbl、USD/ton |
| **WTI 原油** | NYMEX WTI 近月 | **XX.XX** / **XXXX.XX** | **+/-X.XX** / **+/-X.XX** | n/a | USD/bbl、USD/ton |
| **Dubai 原油†** | ICE Dubai 近月（期貨） | **XX.XX** / **XXXX.XX** | **+/-X.XX** / **+/-X.XX** | n/a | USD/bbl、USD/ton |
| **Naphtha** | CFR Japan（OSN M1） | **XXXX** | **+/-X.X** | n/a | USD/ton |
| **Isomer Xylene（MX）** | FOB Korea | **XXXX**（MM/DD） | n/a | n/a | USD/ton |
| **Ethylene** | CFR NE Asia | **XXXX**（MM/DD） | n/a | n/a | USD/ton |
| **Propylene** | CFR China | **XXXX**（MM/DD） | n/a | n/a | USD/ton |
| **Benzene** | FOB Korea | **XXXX**（MM/DD） | n/a | n/a | USD/ton |
| **Toluene** | FOB Korea | **XXXX**（MM/DD） | **+/-X** | n/a | USD/ton |
| **o-Xylene（OX）** | FOB Korea | **XXXX**（近期） | n/a | n/a | USD/ton |
| **p-Xylene（PX）** | CFR Taiwan/China | **XXXX–XXXX**（MM/DD） | n/a | n/a | USD/ton |

\* 上一周均價：  
- 原油：近五個結算價均值  
- Naphtha：近五個亞洲收盤均值（OSN M1）  

† Dubai：採 ICE Dubai 1st Line 近月期貨（以 Platts Dubai 日評結算）  

---

## 趨勢分析
（會帶入 overrides 的 `analysis_notes`，沒寫就放通用條目）

---

## 來源與方法
（會標示油價來源（Reuters / Yahoo fallback）與 overrides 來源與交易條件）
```
