# ENGLISHTUBE

> **VoiceTube 風格的沉浸式英文跟讀與情歌學習平台**  
> 結合 50 部精選 TED/YouTube 演講與 50 首經典西洋情歌，具備卡拉OK級即時動態逐字同步字幕、Google 神經網路語音朗讀、即時單字語境查詢、克漏字聽力訓練與 PWA 跨平台安裝支援。

[![License: MIT](https://img.shields.io/badge/License-MIT-6d5dfc.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-brightgreen.svg)](https://web.dev/progressive-web-apps/)
[![Service Worker](https://img.shields.io/badge/Service%20Worker-v24-orange.svg)](./sw.js)

---

## ✨ 核心功能特色

| 功能類別 | 特色說明 |
|---|---|
| 🎵 **雙模態媒體切換** | 支援「精選演講（50 部 TED/YouTube）」與「探索情歌（50 首西洋經典）」一鍵無縫切換 |
| 🎤 **卡拉OK逐詞連動** | 毫秒級時間軸同步，字幕隨影片發音逐字高亮反白，支援點擊跳轉播放 |
| 🛡️ **YouTube CC 阻絕** | 強制卸載 YouTube 內建雜亂語音辨識字幕，專注於平台專屬繁中雙語對照字幕 |
| 🧲 **黏性結尾字幕 (Sticky Cue)** | 結尾伴奏期間字幕持續穩定駐留，解決「歌曲未播完字幕早停」問題 |
| 🔊 **Google 神經語音 TTS** | 整合 Google Neural TTS 高擬真發音引擎，備援 Web Speech API 原生語音 |
| 📖 **即時單字語境查詢** | 點擊字幕任一單字即彈出詞彙卡，包含音標、詞性、繁中釋義與當前句子例句 |
| 🧩 **克漏字聽力挑戰** | 一鍵遮蓋英文字幕關鍵字，訓練盲聽與單字拼寫回想能力 |
| 📊 **學習進度視覺化** | 實時統計已跟讀句數百分比進度條，激勵持續學習 |
| ⚡ **多段速播放調節** | 支援 0.5×、0.75×、1.0×、1.25×、1.5× 五段變速播放，支援播放速率持久化 |
| 📱 **PWA 桌面/行動 App** | 符合現代 PWA 標準，支援 iOS / Android / macOS / Windows 一鍵安裝至桌面 |
| 🇹🇼 **台灣正體中文支援** | 全面採用 OpenCC (s2twp) 進行在地化詞彙與繁體中文校準 |

---

## 🛠️ 重點改善技術與架構設計

本專案在效能、字幕準確度、人因互動與播放控制進行了多次系統級深度重構與技術升級：

### 1. 雙模態分段控制系統（Media Segmented Architecture）
* **動態數據切換**：在前端實作分段式選單控制（Segmented Control），整合影片學習（`videos`）與歌曲學習（`songs`）雙資料流。
* **動態標題與分類濾鏡**：切換至歌曲模式時，自動替換分類標籤（Taylor Swift、Ed Sheeran、90經典、千禧抒情、電影主題曲等），並呈現「探索英文歌曲：選你喜歡的歌曲，學習就不再無聊」等動態指引文案。
* **優先級覆蓋保護**：改寫 `openVideo` 邏輯，確保歌曲模式一律優先載入精心校準的歌詞庫（`songs_50.json`），避免被通用快取或未完整校準的預載資料覆蓋。

### 2. 50 首經典情歌全曲全時序歌詞庫（Full-Coverage Lyrics Engine）
* **全曲時間軸覆蓋**：針對原先部分歌曲僅有開頭 30 秒歌詞的缺陷，透過 Gemini Flash / Pro 多模型協同批次產出，為全部 50 首經典英文情歌補齊了 **25 ～ 66 組完整時序歌詞**，時間軸自前奏開口一路涵蓋至尾聲淡出，覆蓋率達 90%~100%。
* **多模型彈性降級與限流保護**：具備指數退避重試（Exponential Backoff）與多端點容錯切換（`gemini-3.1-flash-lite` ⇄ `gemini-2.5-flash-lite` ⇄ `gemini-2.5-flash` ⇄ `gemini-2.5-pro`），杜絕 HTTP 429 速率限制阻斷。

### 3. YouTube 內建 CC 阻絕與純淨無壓字播放（CC Caption Suppression）
* **雙重 API 卸載**：YouTube 官方播放器在影片播放開始（`onStateChange === 1`）時，常自動載入低品質且延遲的內建語音辨識字幕。本平台在 `onReady` 與 `onStateChange` 雙重階段強制調用 `unloadModule('captions')` 與 `setOption('captions', 'track', {})`。
* **PostMessage 跨域指令**：控制按鈕「📺 影片CC 開/關」除了呼叫 API 外，同步透過 `postMessage` 發送清空 track 指令，讓使用者可自主強制開關 YouTube 畫面內的軟字幕。

### 4. 智慧平滑過渡與黏性結尾字幕機制（Sticky Last Cue & Smooth Bridging）
* **跨句平滑橋接**：在計算字幕當前句時，動態比對下一句的起始點：
  $$\text{cueEnd} = \max(\text{start} + \text{dur}, \min(\text{start} + \text{dur} + 1.2, \text{nextStart}))$$
  避免句子與句子之間的短暫空隙導致字幕突然閃爍消失。
* **黏性結尾防呆（Sticky Last Cue）**：當播放進度超過最後一句歌詞時，自動將最後一句歌詞保持懸浮顯示，徹底解決歌曲結尾長段樂器尾奏期間字幕提前消失的問題。

### 5. 零記憶體洩漏與播放器生命週期管理（Zero-Leak Lifecycle）
* **播放器銷毀保護**：在關閉學習視窗（`closeModal`）時，主動呼叫 `ytPlayer.stopVideo()` 與 `ytPlayer.destroy()`，並清除 DOM 節點容器，阻斷未回收的 Event Loop 與背景音訊播放。
* **背景同步循環防呆**：離開視窗時自動清除即時同步計時器（`cancelAnimationFrame` / `clearInterval`），避免背景空轉消耗 CPU 效能。

### 6. Service Worker 快取擊穿與零等待啟用（Cache Busting v24）
* **強制作業系統級重新啟用**：升級 Service Worker 快取版本至 `v24`，搭配 `self.skipWaiting()` 與 `clients.claim()`，在快取被淘汰時自動清除舊版快取並推播最新版本，解決 PWA 在不同客戶端上的快取殘留問題。

---

## 🚀 快速開始（macOS）

### 系統需求

* macOS 12+，Python 3.10 或更新版本
* 首次啟動建議連線網路以安裝相關套件
* AI 翻譯功能需準備 OpenAI API Key（非必要，預載內容皆已可直接學習）

### 一鍵啟動

1. 在 Finder 中對 **`run-local.command`** 按右鍵 → **「打開」**
2. 系統會自動建立虛擬環境、安裝相依套件並開啟瀏覽器造訪 `http://localhost:8885`

### 一鍵停止

* 對 **`stop-local.command`** 按右鍵 → **「打開」**，即可乾淨關閉伺服器行程
* 或在終端機中按下 `Control + C`

### 手動指令啟動

```bash
cd englishtube
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

開啟瀏覽器前往 <http://localhost:8885>。若需自訂連接埠：

```bash
PORT=9000 python3 server.py
```

### 啟用可選的自訂 AI 翻譯 API

```bash
export OPENAI_API_KEY='貼上您的 API 金鑰'
export OPENAI_MODEL='gpt-4.1-mini'
python3 server.py
```

---

## 📖 平台使用導引

1. **選擇學習模式**：在首頁上方點選「🎥 精選演講」或「🎵 探索歌曲」。
2. **開啟學習卡片**：點擊任一演講或情歌，進入卡拉OK沈浸式播放視窗。
3. **即時跟讀高亮**：字幕隨發音即時高亮；點擊任一句字幕可直接跳轉至該秒數播放。
4. **即時字典查詢**：點擊字幕中的任意英文單字，即可查看詳細音標、詞性與繁中釋義。
5. **發音朗讀練習**：點擊字典卡片上的「🔊 發音」按鈕，聆聽 Google 神經語音發音。
6. **克漏字挑戰**：點選「🧩 克漏字」按鈕隱藏英文，訓練聽力理解力。
7. **控制 CC 字幕**：若影片內建 CC 遮擋視線，可點擊「📺 影片CC」按鈕自由切換。

---

## 📁 專案檔案結構

| 檔案 / 目錄 | 用途說明 |
|---|---|
| `index.html` | 核心前端介面（VoiceTube 風格 UI、卡拉OK引擎、雙模態切換） |
| `songs_50.json` | 50 首精選經典英文情歌完整英中雙語字幕資料庫 |
| `video_lessons.json` | 50 部精選演講字幕、翻譯與重點詞彙庫 |
| `video_lessons.js` | 演講字幕與詞彙的 JavaScript 快速預載檔 |
| `server.py` | 本機高效能 HTTP 伺服器、字幕剖析與 AI 翻譯端點 |
| `sw.js` | Service Worker（v24）快取管理與 PWA 離線機制 |
| `fill_all_50_songs_gemini.py` | 歌詞時間軸批次補齊與多模型容錯生成工具 |
| `run-local.command` | macOS 雙擊一鍵啟動腳本 |
| `stop-local.command` | macOS 雙擊一鍵停止腳本 |
| `requirements.txt` | Python 相依套件列表（`yt-dlp`、`opencc-python-reimplemented`） |
| `manifest.webmanifest` | PWA 應用程式名稱、佈景主題色與多解析度圖示宣告 |
| `render.yaml` | 雲端一鍵部署至 Render 的 Blueprint 配置檔 |
| `LICENSE` | MIT 開源授權條款 |

---

## 🔌 API 端點說明

### 1. `POST /api/transcript`
取得指定 YouTube 影片的自動英文字幕：
```json
{ "url": "https://www.youtube.com/watch?v=VIDEO_ID" }
```
回應格式：
```json
{
  "videoId": "VIDEO_ID",
  "language": "en",
  "cues": [{ "start": 1.2, "duration": 2.4, "text": "Example sentence." }]
}
```

### 2. `POST /api/translate`
翻譯指定句子並提取核心教學詞彙（需設定 `OPENAI_API_KEY`）：
```json
{ "sentences": ["Example sentence.", "How are you?"] }
```
回應包含繁體中文逐句翻譯與單字釋義解析。

### 3. `GET /api/dict?word={word}`
即時查詢單字之音標、詞性與中文解釋。

---

## ⚠️ 常見問題排查（FAQ）

| 常見情況 | 解決方法 |
|---|---|
| **字幕沒有正常顯示** | 在瀏覽器開啟 DevTools → Application → Service Workers 點選「Unregister」，並按下 `Cmd + Shift + R` 強制重新整理。 |
| **8885 連接埠被佔用** | 執行 `stop-local.command`，或指定其他埠號啟動：`PORT=9000 python3 server.py`。 |
| **YouTube 影片畫面內出現重複英文字幕** | 點擊播放器工具列的「📺 影片CC 關」按鈕，平台會強制卸載 YouTube 內建 CC。 |
| **歌曲播放到最後字幕消失** | 專案已實作「黏性結尾（Sticky Last Cue）」，重新整理套用 v24 快取即可獲得修正。 |

---

## 📄 授權條款

本專案採用 [MIT License](./LICENSE) 開源授權。

> *Disclaimer: ENGLISHTUBE is an independent English learning project. It is not affiliated with, endorsed by, or in any way associated with VoiceTube, TED Conferences, or YouTube LLC.*
