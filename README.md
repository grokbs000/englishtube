# ENGLISHTUBE

> VoiceTube 風格的英文跟讀學習平台 — 50 部精選 TED/YouTube 影片，即時卡拉OK字幕連動、單字即時查詢、Google 神經語音朗讀、克漏字練習與學習進度追蹤。

[![License: MIT](https://img.shields.io/badge/License-MIT-6d5dfc.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-brightgreen.svg)](https://web.dev/progressive-web-apps/)

---

## ✨ 功能特色

| 功能 | 說明 |
|---|---|
| 🎤 **卡拉OK逐詞字幕** | 與影片同步，逐字高亮跟讀 |
| 🔊 **Google 神經語音 TTS** | 高品質真人朗讀，備援 Web Speech API |
| 📖 **即時單字查詢** | 點擊任意單字，即時顯示音標、詞性與繁中釋義 |
| 🧩 **克漏字練習模式** | 遮蓋英文字幕，訓練聽力與拼字記憶 |
| 📊 **學習進度追蹤** | 逐句記錄已複習進度，即時顯示百分比 |
| 🌐 **50 部精選影片** | TED/YouTube 優質英文演講，A2–B2 全等級 |
| ⚡ **多速播放控制** | 0.5×、0.75×、1.0×、1.25×、1.5× |
| 📱 **PWA 離線安裝** | 可安裝至主畫面，基礎資源支援離線 |
| 🔤 **繁體中文介面** | 全中文操作，OpenCC 正體化翻譯 |

---

## 🚀 快速開始（macOS）

### 需求

- macOS、Python 3.10 或更新版本
- 首次啟動需網路，用來安裝 `yt-dlp`
- AI 翻譯功能另需 OpenAI API Key

### 一鍵啟動

1. 在 Finder 中對 **`run-local.command`** 按右鍵 → **「打開」**
2. 若系統詢問安全性，確認後允許執行
3. 腳本會自動建立虛擬環境、安裝依賴，並開啟瀏覽器

### 一鍵停止

- 對 **`stop-local.command`** 按右鍵 → **「打開」**，即可停止伺服器
- 或在終端機按 `Control + C`

### 手動啟動

```bash
cd englishtube
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

開啟 <http://localhost:8885>。若要改連接埠：

```bash
PORT=9000 python server.py
```

### 啟用 AI 翻譯

```bash
export OPENAI_API_KEY='貼上自己的 API 金鑰'
export OPENAI_MODEL='gpt-4.1-mini'
python server.py
```

> ⚠️ 請勿把金鑰寫入程式碼、提交到 Git 或公開分享。

---

## 📖 如何使用

1. 點選首頁任一影片卡片，進入卡拉OK跟讀畫面
2. 字幕會自動與影片同步高亮；點擊字幕列可跳轉時間點
3. 點擊任意 **英文單字** 可即時查詢音標與中文釋義
4. 按 **🧩 克漏字** 遮蓋英文，測試聽力記憶
5. 右側進度條顯示本場已複習句數
6. 使用速度按鈕調整播放速度（0.5× ~ 1.5×）
7. 點「AI 翻譯＋單字解說」取得繁中逐句翻譯（需 API Key）

---

## 📁 專案檔案

| 檔案 | 用途 |
|---|---|
| `index.html` | 前端完整頁面（VoiceTube UI、字幕引擎、TTS） |
| `server.py` | 本機/雲端 HTTP 伺服器、字幕 API、AI 翻譯 API |
| `sw.js` | Service Worker（v16）靜態快取與離線支援 |
| `video_lessons.js` | 50 部影片完整字幕與詞彙預載資料（2.4 MB） |
| `video_lessons.json` | 字幕 JSON 資料（fallback 異步載入） |
| `run-local.command` | macOS 雙擊啟動腳本 |
| `stop-local.command` | macOS 雙擊停止腳本 |
| `requirements.txt` | Python 依賴（yt-dlp、opencc-python-reimplemented） |
| `manifest.webmanifest` | PWA 名稱、圖示與顯示模式 |
| `render.yaml` | Render Blueprint 雲端部署設定 |
| `LICENSE` | MIT 授權條款 |

---

## 🌐 部署到 HTTPS（Render）

1. 將專案推送到自己的 GitHub repository（勿提交 `.venv`、`dict_cache.json` 或 API Key）
2. 登入 [Render](https://render.com)，建立 Blueprint，連接 repository 並套用 `render.yaml`
3. 在 Render 環境變數中設定 `OPENAI_API_KEY`
4. 部署完成後，用 HTTPS 網址在手機安裝 PWA

---

## 🔌 API 端點

### `POST /api/transcript`

```json
{ "url": "https://www.youtube.com/watch?v=VIDEO_ID" }
```

回應：

```json
{
  "videoId": "VIDEO_ID",
  "language": "en",
  "cues": [{ "start": 1.2, "duration": 2.4, "text": "Example sentence." }]
}
```

### `POST /api/translate`

```json
{ "sentences": ["Example sentence.", "How are you?"] }
```

回應包含 `sentences`（繁中翻譯）與 `words`（單字解說）。需設定 `OPENAI_API_KEY`。

### `GET /api/dict?word=philosopher`

回應即時單字查詢結果（音標、詞性、繁中釋義）。

---

## ⚠️ 常見問題

| 問題 | 解決方式 |
|---|---|
| 沒有字幕顯示 | 在 Chrome DevTools → Application → Service Workers → Unregister，再 `Cmd+Shift+R` |
| 8885 port 被佔用 | 執行 `stop-local.command` 或 `PORT=9000 python server.py` |
| yt-dlp 安裝失敗 | 確認網路正常：`.venv/bin/python -m pip install -r requirements.txt` |
| AI 翻譯顯示未設定 | 啟動前執行 `export OPENAI_API_KEY=...` |
| 手機無法安裝 PWA | 需使用 HTTPS 網址；iOS 用 Safari「加入主畫面」|

---

## 📄 授權

本專案採用 [MIT License](./LICENSE) 授權。

> ENGLISHTUBE is an independent learning project. It is not affiliated with or endorsed by VoiceTube, TED, or YouTube.
