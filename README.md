# ENGLISHTUBE

> YouTube 英文影片學習工具：字幕擷取、時間軸逐句學習、繁中 AI 翻譯、單字解說與 PWA 安裝。

- **本機網址**：<http://localhost:8885>
- **技術**：HTML/CSS/JavaScript、Python 標準庫 HTTP server、yt-dlp、OpenAI Responses API、PWA Service Worker。
- **部署設定**：`render.yaml`（Render Blueprint）。

## 目錄

- [功能概覽](#功能概覽)
- [快速開始--macos](#快速開始--macos)
- [手動啟動](#手動啟動)
- [如何使用](#如何使用)
- [自動字幕與時間同步](#自動字幕與時間同步)
- [AI 翻譯與單字解說](#ai-翻譯與單字解說)
- [PWA 安裝與離線](#pwa-安裝與離線)
- [部署到 HTTPS](#部署到-https)
- [API 端點](#api-端點)
- [常見問題](#常見問題)
- [安全、限制與下一步](#安全限制與下一步)

## 功能概覽

- 貼上 YouTube 網址並嘗試取得英文人工字幕或自動字幕。
- 保留字幕時間碼，顯示逐句字幕；點選句子可跳至對應影片時間（播放器平台允許時）。
- 透過 OpenAI API 將英文句子翻譯為繁體中文，並產生常用單字／片語解說。
- 以瀏覽器語音合成朗讀英文；支援字幕顯示、收藏與本機儲存。
- PWA manifest、安裝圖示、Service Worker 與基本靜態資源快取。
- Python 後端負責字幕擷取與 AI API 呼叫，API 金鑰不需要放進前端 HTML。

> 注意：YouTube 是否能嵌入播放、取得字幕，取決於影片設定、地區、帳號／年齡限制、YouTube 存取政策與網路環境。不是每支影片都能成功。此專案不下載或重新散布影片本體。

## 快速開始（macOS）

### 需求

- macOS、Python 3（建議 3.10 或更新版本）
- 首次啟動需網路，用來安裝 `yt-dlp`
- 若要 AI 翻譯，另需 OpenAI API Key 與可用額度

### 啟動

1. 解壓縮 `ENGLISHTUBE-PWA.zip`。
2. 進入解壓後的 `englishtube` 資料夾。
3. 對 `run-local.command` 按右鍵，選「打開」。若系統詢問安全性，確認來源後再允許執行。
4. 腳本會建立 `.venv` 虛擬環境並安裝 `requirements.txt` 中的依賴。
5. 瀏覽器開啟 <http://localhost:8885>。
6. 關閉服務時，回到終端機按 `Control+C`。

`run-local.command` 會在 `8885` 已被佔用時停止並提示。請關閉舊的 ENGLISHTUBE 服務後再啟動。

## 手動啟動

在終端機切換到專案資料夾：

```bash
cd englishtube
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

開啟 <http://localhost:8885>。若要改連接埠：

```bash
PORT=9000 python server.py
```

### 啟用 AI 翻譯

在同一個終端機設定環境變數，再啟動伺服器：

```bash
export OPENAI_API_KEY='貼上自己的 API 金鑰'
export OPENAI_MODEL='gpt-4.1-mini'
python server.py
```

請勿把真實金鑰寫入 `index.html`、提交到 Git、貼到聊天或公開分享。若使用 `run-local.command`，先在終端機執行 `export OPENAI_API_KEY=...` 再執行腳本，或用上述手動方式啟動。

## 如何使用

1. 在首頁貼上 YouTube 影片網址並載入影片。
2. 使用字幕擷取功能嘗試取得英文字幕。
3. 點擊字幕句子，可跳到對應時間並逐句練習。
4. 執行 AI 翻譯，取得繁體中文翻譯與單字／片語解說（需設定 API Key）。
5. 使用朗讀、字幕切換與收藏功能複習。

若影片沒有英文字幕或字幕擷取被限制，可在 YouTube 影片頁面查看是否有「顯示文字稿」；必要時將可取得的文字稿貼回學習流程。AI 翻譯與字幕擷取是兩項不同功能：前者需 OpenAI API，後者使用 yt-dlp 嘗試取得 YouTube 提供的字幕。

## 自動字幕與時間同步

後端透過 `yt-dlp` 請求英文字幕（人工字幕及自動字幕），優先解析 VTT，並嘗試 JSON3 格式。字幕會轉成包含開始時間、持續時間、文字的 cue 清單。前端使用時間碼顯示句子與進行跳轉。

可能失敗的情況：

- 影片沒有英文字幕，或只有其他語言字幕。
- 影片私人、年齡限制、會員限定、地區限制或禁止存取。
- YouTube 更改存取方式、觸發速率限制，或雲端主機 IP 被限制。
- 影片提供的字幕格式發生變化。

不要將字幕擷取視為繞過影片存取權限的方法。請遵守 YouTube 條款、影片著作權與字幕使用授權。

## AI 翻譯與單字解說

- API：`POST /api/translate`
- 模型預設：`gpt-4.1-mini`，可透過 `OPENAI_MODEL` 環境變數調整。
- 每次最多傳入 100 句英文，避免單次請求過大。
- 回應格式為 JSON，包含 `sentences`（英文原句及繁中翻譯）與 `words`（單字／片語及繁中解說）。
- AI 回應可能有誤，重要內容請自行核對；API 費用依帳戶與模型定價而定。

## PWA 安裝與離線

PWA 安裝需要透過 **HTTPS** 網站，或在同一台裝置使用 `localhost` 測試。直接用檔案總管開啟 `index.html`（`file://`）不適合測試安裝功能。

- **iPhone/iPad**：用 Safari 開啟 HTTPS 網址 →「分享」→「加入主畫面」。
- **Android**：用 Chrome 開啟 HTTPS 網址 → 選單 →「安裝應用程式」或「加到主畫面」。
- Service Worker 快取的是基本網站資源；這不代表 YouTube 影片、字幕、AI 回應或外部 API 能離線使用。
- 更新前端資源後，必要時關閉再重開頁面，或清除網站資料以移除舊快取。

## 部署到 HTTPS

專案附有 `render.yaml`，可用 Render Blueprint 建立 Web Service。

1. 將 `englishtube` 目錄內容推送到自己的 GitHub repository（不要提交 `.venv` 或任何 API 金鑰）。
2. 登入 Render，選擇建立 Blueprint，連接 repository 並套用 `render.yaml`。
3. 在 Render 環境變數中設定 `OPENAI_API_KEY`；`OPENAI_MODEL` 預設為 `gpt-4.1-mini`。
4. 等待部署完成，使用 Render 提供的 HTTPS 網址測試影片嵌入、字幕 API 與 AI 翻譯。
5. 在手機上開啟 HTTPS 網址並依上方步驟安裝。

### 部署提醒

- `render.yaml` 使用免費方案設定；免費服務可能休眠或冷啟動，實際限制以託管平台最新方案為準。
- 雲端環境的 YouTube 字幕擷取可能比本機更容易被限制。正式服務建議加上請求速率限制、快取、錯誤監控與濫用防護。
- 公開部署後，任何人都可能呼叫目前的 API。上線前應加上身分驗證、限流、配額與請求大小限制，避免 API 費用或資源被濫用。
- 不要將 API 金鑰寫入前端程式碼或 `render.yaml`；請使用平台的 Secret／Environment Variables。

## API 端點

### `POST /api/transcript`

請求：

```json
{"url":"https://www.youtube.com/watch?v=VIDEO_ID"}
```

成功回應：

```json
{
  "videoId": "VIDEO_ID",
  "language": "en",
  "cues": [
    {"start": 1.2, "duration": 2.4, "text": "Example sentence."}
  ]
}
```

錯誤時回傳 JSON `error` 欄位。擷取時間上限為 90 秒。

### `POST /api/translate`

請求：

```json
{"sentences":["Example sentence.","How are you?"]}
```

成功回應包含 `sentences` 與 `words`。需在伺服器設定 `OPENAI_API_KEY`。

## 常見問題

**啟動時顯示沒有 Python？**

在終端機執行 `python3 --version`。若找不到指令，請先安裝 Python 3，再重新啟動腳本。

**提示 yt-dlp 安裝失敗？**

確認網路正常，然後在專案目錄執行：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

**8885 已被使用？**

關閉先前開啟的服務，或用 `PORT=9000 python server.py` 改用其他連接埠。

**字幕取得失敗？**

確認影片網址正確、影片公開且存在英文字幕。更新工具：

```bash
.venv/bin/python -m pip install --upgrade yt-dlp
```

若雲端環境被 YouTube 限制，單純重試不保證成功。

**AI 翻譯顯示未設定金鑰？**

在啟動 Python 伺服器前設定 `OPENAI_API_KEY`。檢查 API 帳戶是否有可用額度及模型權限。

**手機無法安裝？**

確認使用 HTTPS 網址、網站已成功載入 manifest 與 Service Worker；iOS 請使用 Safari 的「加入主畫面」。本機 `localhost` 只適用於同一台裝置，不會自動讓手機連上 Mac。

## 安全、限制與下一步

目前版本定位為可測試的 MVP，不是完整的多使用者商用平台：

- 收藏等資料以瀏覽器本機儲存為主，沒有會員登入與跨裝置雲端同步。
- AI 功能需要自行提供 API Key，且會產生可能的使用費。
- YouTube 播放由 YouTube 嵌入播放器提供；影片擁有者可能禁止嵌入。
- 字幕擷取受 YouTube 存取限制與影片字幕狀態影響，無法保證每支影片都成功。
- 正式商用前建議加入登入、資料庫、快取、限流、監控、隱私權政策、錯誤回報與自動化測試。

## 專案檔案

| 檔案 | 用途 |
|---|---|
| `index.html` | 前端頁面與互動功能 |
| `server.py` | 本機／雲端 HTTP 伺服器、字幕 API、AI 翻譯 API |
| `requirements.txt` | Python 套件清單（yt-dlp） |
| `run-local.command` | macOS 本機啟動腳本，使用 8885 埠 |
| `manifest.webmanifest` | PWA 名稱、圖示與顯示模式 |
| `sw.js` | Service Worker 與基本靜態快取 |
| `icon.svg`, `icon-*.png` | 網站及安裝圖示 |
| `render.yaml` | Render Blueprint 部署設定 |

---

ENGLISHTUBE is an independent learning project. It is not affiliated with or endorsed by VoiceTube or YouTube.
