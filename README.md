# ENGLISHTUBE

> **VoiceTube 風格的沉浸式英文跟讀與情歌學習平台【深度旗艦版】**  
> 具備 **500 部高品質精選教材**（400 部涵蓋 10 大主題頻道之 TED/YouTube 知識影片 + 100 首全曲雙語西洋經典情歌），支援 VoiceTube 10 大主題頻道導航與 CEFR A1~C1 5 級難度篩選、卡拉OK級即時動態逐字同步字幕、Google 神經網路語音朗讀、即時單字語境查詢、克漏字聽力訓練與 PWA 跨平台安裝支援。

🌐 **線上即時體驗（PWA 官方網址）**：[https://englishtube-tw.onrender.com/](https://englishtube-tw.onrender.com/)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-englishtube--tw.onrender.com-success?style=flat&logo=render)](https://englishtube-tw.onrender.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-6d5dfc.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-brightgreen.svg)](https://web.dev/progressive-web-apps/)
[![Service Worker](https://img.shields.io/badge/Service%20Worker-v161-orange.svg)](./sw.js)
[![Flagship Edition](https://img.shields.io/badge/Edition-Stage%202%20Flagship%20(500%20Items)-6d5dfc.svg)](./index.html)

---

## ✨ 核心功能特色

| 功能類別 | 特色說明 |
|---|---|
| 🧭 **10 大主題頻道導航** | 涵蓋職場商業、學習口說、TED-Ed動畫、科技科學、健康心理、休閒旅遊、藝術娛樂、新聞時事、兒童初學與經典歌曲 |
| 🎯 **CEFR 5 級難度篩選** | 完整涵蓋 A1 入門、A2 初級、B1 中級、B2 中高級、C1 高級，依個人程度精準選課 |
| 📚 **500 部高品質教材庫** | 400 部知識演講/趣味科普 + 100 首全曲 100% 完整雙語歌詞西洋經典情歌 |
| 🎤 **卡拉OK逐詞連動** | 毫秒級時間軸同步，字幕隨影片發音逐字高亮反白，支援點擊跳轉播放 |
| 📺 **YouTube 原生 CC 完整相容** | 完美保留並修復 YouTube 原生自帶 CC 功能，使用者可隨心在畫面內開關或切換多國語言字幕 |
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
* **動態標題與分類濾鏡**：切換至歌曲模式時，自動替換分類標籤（Taylor Swift、Ed Sheeran、Adele、Bruno Mars、Maroon 5、Coldplay、電影主題曲等），並呈現「探索英文歌曲：選你喜歡的歌曲，學習就不再無聊」等動態指引文案。
* **優先級覆蓋保護**：改寫 `openVideo` 邏輯，確保歌曲模式一律優先載入精心校準的歌詞庫（`songs_100.json`），避免被通用快取或未完整校準的預載資料覆蓋。

### 2. 100 首經典情歌全曲全時序歌詞庫（Full-Coverage Lyrics Engine）
* **全曲時間軸覆蓋**：全面擴充至 100 首跨時代全球經典西洋情歌，時間軸自前奏開口一路涵蓋至尾聲淡出，覆蓋率達 90%~100%。
* **多模型彈性降級與限流保護**：具備指數退避重試（Exponential Backoff）與多端點容錯切換（`gemini-3.1-flash-lite` ⇄ `gemini-2.5-flash-lite` ⇄ `gemini-2.5-flash` ⇄ `gemini-2.5-pro`），杜絕 HTTP 429 速率限制阻斷。

### 3. YouTube 原生播放器與 CC 自帶功能完整保護（Native CC Harmony & Control）
* **非破壞性原生相容**：移除過往強制呼叫 `unloadModule('captions')` 導致原生 CC 按鈕失效的暴力阻絕邏輯，完美修復並保留 YouTube 播放器控制列自帶之 [CC] 字幕切換按鈕，尊重使用者自主控制權。
* **雙層字幕無干擾架構**：影片本體可正常開啟 YouTube 原生字幕，下方 VoiceTube 學習舞台則同步提供高精度逐字反白與繁中對照，兩者互不干擾、相輔相成。

### 4. 智慧平滑過渡與黏性結尾字幕機制（Sticky Last Cue & Smooth Bridging）
* **跨句平滑橋接**：在計算字幕當前句時，動態比對下一句的起始點，避免句子與句子之間的短暫空隙導致字幕突然閃爍消失。
* **黏性結尾防呆（Sticky Last Cue）**：當播放進度超過最後一句歌詞時，自動將最後一句歌詞保持懸浮顯示，徹底解決歌曲結尾長段樂器尾奏期間字幕提前消失的問題。

### 5. 零記憶體洩漏與播放器生命週期管理（Zero-Leak Lifecycle）
* **播放器銷毀保護**：在關閉學習視窗（`closeModal`）時，主動呼叫 `ytPlayer.stopVideo()` 與 `ytPlayer.destroy()`，並清除 DOM 節點容器，阻斷未回收的 Event Loop 與背景音訊播放。
* **背景同步循環防呆**：離開視窗時自動清除即時同步計時器（`cancelAnimationFrame` / `clearInterval`），避免背景空轉消耗 CPU 效能。

### 6. Service Worker 快取擊穿與零等待啟用（Cache Busting v32）
* **強制作業系統級重新啟用**：升級 Service Worker 快取版本至 `v32`，搭配 `self.skipWaiting()` 與 `clients.claim()`，在快取被淘汰時自動清除舊版快取並推播最新版本，解決 PWA 在不同客戶端上的快取殘留問題。
* **零假載入殘留與動態舞台響應標準 (Zero-Stale-Placeholder Standard)**：徹底移除 HTML 中「正在準備影片與字幕…」靜態殘留字串，點擊教材即刻載入對齊字幕；若無自定義字幕則主動呈現原生 CC 導航卡，杜絕畫面卡死假象。
* **100% 全教材雙語字幕完整覆蓋 (Zero-Empty-Cues Gate)**：全平台 500 部教材（400 部影片 + 100 首情歌）均達成 100% 逐句字幕對齊覆蓋（488/488 影片與 100/100 歌曲），零空字幕殘留。

### 7. 100% YouTube 官方真實影片驗證機制（100% Genuine Video & Song Verification）
* **全面終結「無法播放影片」痛點**：全平台 500 部教材（400 部知識演講/趣味科普 + 100 首西洋經典情歌）均透過 `yt-dlp` 檢索與 YouTube 官方 `oEmbed` API（HTTP 200）進行 100% 嚴格校驗，確保每一部影片均為真實、高畫質、允許嵌入且可流暢播放的官方正版視頻（500/500 驗證通過）。
* **無縫教學字幕連動**：兒童初學（English Singsing、Super Simple Songs）、TED-Ed 動畫、BBC 英語教學、各類知識專題等，時間軸與 YouTube 官方播放器完美對齊。

### 8. VoiceTube 10 大主題頻道與 CEFR 5 級難度導航體系（10-Channel & CEFR Matrix）
* **階段二【深度旗艦版】500 部教材庫存架構**：
  在使用者探索教材時，導入雙維度即時過濾（主題頻道 + CEFR 難度），並於卡片上呈現精緻的難度色標與頻道膠囊標籤：

| 主題頻道 (Channel) | 收錄部數 | 涵蓋主題特色與精選範例 |
|---|---|---|
| **💼 職場商業 (Business & Finance)** | **45 部** | 亞馬遜電商帝國、球鞋經濟學、巴菲特價值投資、Costco熱狗定價心理、Stripe在線支付革命 |
| **🎓 學習口說 (Learning Resources)** | **45 部** | 10大高頻母語成語、擺脫腦中翻譯直覺口說、美語節奏語調心法、如何用英文優雅表達反對意見 |
| **🎬 TED-Ed 動畫 (Animation)** | **50 部** | 貓咪呼嚕原理、記憶如何形成、太陽變成黑洞會怎樣、為什麼洋蔥讓人流淚、深海生物抗壓秘密 |
| **🔬 科技科學 (Science & Technology)** | **50 部** | GPS衛星定位原理、光速極限之謎、馬里亞納海溝深淵、2nm晶片製造、韋伯望遠鏡紅外攝影 |
| **🧘 健康心理 (Health & Wellness)** | **45 部** | 每日一萬步好處、晝夜節律生物鐘、運動如何重塑大腦海馬迴、慢性壓力與皮質醇、睡眠對情緒的療癒 |
| **✈️ 休閒旅遊 (Leisure & Travel)** | **45 部** | 長途飛行舒適技巧、京都千年木造寺廟、義大利高鐵漫遊指南、巴黎奧斯曼建築美學、挪威峽灣徒步 |
| **🎨 藝術娛樂 (Arts & Entertainment)** | **40 部** | 漢斯季默電影配樂魔法、文藝復興黃金比例、皮克斯動畫情緒骨骼綁定、諾蘭導演攝影美學、爵士即興 |
| **📰 新聞時事 (News & Current Affairs)** | **40 部** | 全球半導體地緣戰略、Starlink衛星網路軌道、珊瑚礁白化搶救、電動車電池回收潮、深偽技術識別 |
| **👶 兒童初學 (Kids / A1 Beginner)** | **40 部** | Super Simple Songs、English Singsing、農場動物對話、美味水果英文、早安問候兒歌、ABC自然發音 |
| **🎵 經典歌曲 (Music)** | **100 首** | Taylor Swift、Adele、Ed Sheeran、Coldplay、Maroon 5、Bruno Mars、Imagine Dragons 100% 完整雙語歌詞 |
| **總計** | **500 部** | **完整的 A1 入門 (48部)、A2 初級 (115部)、B1 中級 (206部)、B2 中高級 (108部)、C1 高級 (23部)** |

* **平滑水平捲軸與人因滾輪轉換（Sleek Scrollbar & Wheel Scrolling）**：
  - 頻道導航列（`.vt-channel-nav`）與難度等級列（`.vt-level-nav`）配備專屬精緻自訂水平捲軸，支援明亮與深色模式動態對比。
  - 支援滑鼠垂直滾輪自動轉換為水平滾動（Wheel to Horizontal Scroll），搭配點選標籤自動平滑居中對齊（Auto Center Scroll），提供桌機與觸控雙端極致流暢之探索體驗。

### 9. 貼上 YouTube 製作教材全自動管線（Custom YouTube Lesson Pipeline）
* **專屬一鍵製作彈窗（Custom Maker Modal）**：首頁「＋ 貼上 YouTube 製作教材」開啟現代獨立視窗，支援剪貼簿一鍵貼上、YouTube 網址正規化（標準 URL、短網址 `youtu.be`、`shorts` 均自動相容）。
* **雙軌字幕智慧建立機制**：
  1. **自動提取軌**：透過後端 `/api/transcript` 與 `yt-dlp` 自動下載影片英文字幕並解析時間軸。
  2. **手動備選軌**：無官方字幕時可直接展開「自備逐字稿」貼上 YouTube「顯示文字稿」逐句對齊。
* **無縫接軌 VoiceTube Studio**：生成教材後自動啟動最新版雙欄學習工作台，連動 YouTube 官方播放器、右側逐句跟讀清單與卡拉OK高亮舞台，並自動持久化保存於瀏覽器本地，隨時可複習。

### 10. 卡拉OK聲畫同步與三軌音訊對齊標準（Tri-Tier Audio Alignment & 60fps Continuous Clock Engine）

為徹底解決影片開頭前奏延遲、背景配樂期間字幕空轉與搶跑痛點，平台全面落實三軌校準與三層自動化時鐘對齊架構：

#### 脫節三大根本成因與對策
1. **MV 前奏與劇情過場時差**：YouTube 官方 MV 常包含 5–180 秒的視覺前奏、劇情對白或長鏡頭（例如 *My Heart Will Go On* 前奏約 176 秒、*Right Here Waiting* 鋼琴特寫約 45 秒、*Love Story* 古堡長鏡頭約 16 秒）。若直接套用 CD 錄音室版本時序，字幕會明顯超前。
2. **中段句組與副歌提前觸發**：舊版手工切分或大模型粗切的句組，經常漏掉主歌過渡句（如 Taylor Swift《Speak Now》35.72s 的 “This is certainly not...”），或將副歌開頭提早 2–3 秒觸發（如 106.14s 覆蓋 “You wish it was me”），導致歌唱者與文字嚴重錯位。
3. **YouTube Iframe 250ms 階梯式取樣抖動**：Iframe API 的 `getCurrentTime()` 每 250ms 才更新一次。若直接高頻 polling 覆蓋時間戳，會造成時鐘停滯後突跳，破壞連續性。

#### 三軌高精度音訊校準架構 (Tri-Tier Audio Alignment Standard)
* **第一軌：VTT 官方字幕軌 (`calibrate_song_timings.py`)**：
  - 使用 `yt-dlp` 檢索 YouTube 官方 MV 是否內建官方英文字幕或自動辨識字幕。
  - 解析 `.vtt` 的毫秒級時間標記，並以 `SequenceMatcher` 進行語義時序比對，自動校準現存雙語歌詞的起始與結束拍點。
* **第二軌：Whisper 音訊軌 (`batch_calibrate_whisper.py`)**：
  - 當影片無可用 YouTube 字幕軌時，下載音訊並以本機 `faster-whisper`（`base.en`、`word_timestamps=True`、`beam_size=5`）萃取單字級（Word-Level）毫秒波形時序。
  - 採用滑動視窗模糊序列匹配（Sliding-Window Fuzzy Matching，`threshold > 0.42`），將雙語歌詞每一句錨定至實際歌唱發音起點，消除前奏與唱詞間的隱性落差。
  - 執行單調遞增時長平滑（Monotonic Smoothing），防止前後句時間重疊。
* **第三軌：LRCLIB 全球毫秒同步歌詞軌 + 智慧 MV 前奏補償 (`audit_and_fix_entire_catalog.py`)**：
  - 針對 VEVO 封鎖字幕或防爬蟲阻絕的官方 MV，直連開源毫秒同步歌詞資料庫（LRCLIB），取得完整未截斷的真值歌詞，徹底根除 AI 幻覺、7 句短模板與演員口白偽歌詞。
  - 內建智慧 MV 前奏時差補償演算法（`compute_smart_offset`），自動偵測 MV 視覺前奏、長鏡頭電影開場與 CD 版的秒數差（例如 Whitney Houston 前奏 +6.4s、Boyz II Men 對話過場 +47.5s、Coldplay 漫步海灘 35s），精準無縫對齊。
  - 搭配記憶體雙語快取（7,000+ 句詞庫）與 OpenCC `s2twp`，確保 100% 台灣繁體中文自然語義翻譯。

#### 前端 60 FPS 實時平滑插值與知覺補償（Triple-Shield Protection）
* **高精準動態插值**：`getExactPlaybackTime()` 僅在 `getCurrentTime()` 發生真值變動時記錄基準點，其餘時間以 `performance.now()` 高精準時鐘補足差值，並輔以 80ms 視聽知覺超前補償。
* **智慧前奏倒數**：當 `time < cues[0].start - 0.5` 時，舞台顯示 `🎵 (前奏演奏中 · 倒數 Xs)`，避免第一句歌詞無謂早顯；開唱前 0.5 秒平滑淡入。
* **智慧長間奏倒數與預載**：兩句之間間隔大於 4.5 秒時，自動顯示 `🎵 (間奏音樂演奏中 · 倒數 Xs)`，並在下一句開唱前 0.8 秒平滑預載，杜絕突兀與搶拍。
* **零分配單字高亮**：`updateKaraokeWordHighlight()` 杜絕高頻 DOM 查詢與 GC 抖動，採一次性 class 差分切換；兩字間遇 `>= 2.2 秒` 音樂或停頓時，高亮指針定格靜止，杜絕任何背景音樂期間的字詞空轉。
* **字幕時長自然語速箝位引擎（Auto Duration Normalizer）**：針對官方 VTT 字幕將短句持續時間粗糙拉長覆蓋配樂的現象，後端 `normalize_cues()` 依單字數量動態計算自然語速上限，主動箝位過長字幕，將被覆蓋的配樂過場空間完全釋放。

### 11. YouTube 探索搜尋滾輪到底連續擴展（Infinite Scroll Auto-Expansion）
* **後端高並發串流分頁**：`/api/yt-search` 端點深度整合 `yt-dlp --playlist-start` 與 `--playlist-end`，支援毫秒級分頁提取，每次動態請求僅需約 3 秒即可無痛獲得下一批全新未收錄優質教材。
* **零 DOM 重組與並發保護**：前端監聽捲軸距離底部 `< 160px` 自動預載，搭配 `isExplorerLoadingMore` 狀態鎖防連點，採用 `insertAdjacentHTML('beforeend', ...)` 直接追加節點，完全保留用戶當前捲動位置，展示計數器動態即時累加（36 ➔ 60 ➔ 85+ 部）。

### 12. 3Blue1Brown 數學動畫解說影片與 ElevenLabs 配音管線（3B1B Manim & ElevenLabs Engine）
* **Manim 0.22.0 系統架構動畫建置**：以 3Blue1Brown 經典深色美學（`#0c0d14`、發光貝茲曲線、連續時鐘座標軸），全程式化渲染 EnglishTube 架構解說動畫（`englishtube_3b1b.py`），全片 4 幕 49.12 秒毫秒級音畫同步。
* **ElevenLabs 隨時換聲管線**：隨附 `generate_elevenlabs_voice.py`，支援用戶直接填入 `ELEVENLABS_API_KEY`，隨時將解說配音無縫替換為 Adam、George 等頂級高擬真 AI 聲線。

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
