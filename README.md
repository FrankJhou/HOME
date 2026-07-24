# Gallery 相簿（GitHub Pages）

把照片放進 `/images/`，這個頁面會 **自動** 顯示所有圖片（不需手動改 HTML）。
此做法使用 GitHub 公開 API 讀取檔案清單，因此 Repository 需要設為 **Public**。

## 使用方式
1. 將 `gallery.html`、`gallery.css`、`gallery.js` 放在你的 GitHub Pages 專案根目錄。
2. 在專案根目錄建立 `images/` 資料夾，將 `.jpg/.png/.webp/.avif/.gif` 等圖片放入。
3. 確保專案是 Public，且 Pages 已啟用。
4. 打開 `https://你的帳號.github.io/你的repo名/gallery.html`（若是個人主站則是 `https://你的帳號.github.io/gallery.html`）。

## 為什麼可以自動顯示？
`gallery.js` 會：
- 從當前網址推斷使用者名稱與 Repository 名稱
- 呼叫 GitHub API 取得 `/images/` 下的檔案清單
- 依副檔名篩選圖片並動態插入頁面

> 注意：若你的預設分支不是 `main`，程式會自動偵測 `default_branch`（例如 `master`）。

## 常見問題
- 看不到圖片：
  - Repository 必須是 **Public**
  - 確認已建立 `/images/` 並放入圖片
  - 等待 Pages 部署完成後再重整
- 想要自訂說明文字：請把檔名命名為 `2024-taipei-101.jpg`，頁面會用檔名當作標題（可自行改 `gallery.js` 轉換邏輯）。
