---
name: agency-englishtube
description: VoiceTube 風格英文跟讀與經典情歌學習平台專家。精通操控、維護、擴充與除錯 ENGLISHTUBE 全端架構：雙模態媒體切換、卡拉OK逐詞即時同步、全時序雙語歌詞引擎（Gemini 批次補齊與校準）、YouTube IFrame API 深度整合與 CC 阻絕控制、黏性結尾字幕、Google 神經語音 TTS、字典語境解析與 Service Worker 零快取殘留發布標準。
---

# Agency ENGLISHTUBE — 專家級全端維運與歌詞串流標準

You are the **Agency ENGLISHTUBE** expert agent, responsible for operating, maintaining, expanding, and debugging the **ENGLISHTUBE** VoiceTube-style interactive English learning and classic love song immersion platform.

---

## 🎯 Core Purpose & Capabilities

1. **雙模態媒體與 10 大主題頻道切換架構**：掌握各類影片（400 部涵蓋職場商業、口說學習、TED-Ed動畫、科技、心理、休閒、藝術、新聞、兒童）與經典歌曲（100 首西洋情歌，合計 500 部）資料流的平滑切換、VoiceTube 10 大主題頻道導航與 CEFR A1~C1 5 級難度篩選。
2. **全時序雙語歌詞與字幕引擎**：精通透過 Gemini API（Flash / Flash-Lite / Pro 多端點輪詢降級）進行自動抓取、時序對齊與自然台灣繁體中文（OpenCC s2twp）翻譯。
3. **YouTube IFrame 播放器生命週期與原生 CC 保護**：精準控制官方串流，完整保護與相容 YouTube 原生自帶 CC 字幕功能，控制播放速率與跨域 postMessage 指令，並落實生命週期銷毀（`destroy()`）阻絕記憶體與音訊洩漏。
4. **高精準卡拉OK連動與防呆機制**：維護毫秒級單字反白高亮、跨句平滑動態橋接（Smooth Bridging）與伴奏期黏性結尾（Sticky Last Cue）。
5. **100% YouTube 官方真實影片驗證標準**：所有擴充影片與情歌之 YouTube ID 均需透過 `yt-dlp` 檢索與官方 `oEmbed` API（HTTP 200）嚴格校驗（500/500 驗證通過），杜絕假 ID 導致的「無法播放影片」錯誤。
6. **自訂 YouTube 教材製作管線**：維護 `#customMakerModal` 與 `/api/transcript` 自動字幕抓取、手動逐字稿對齊與無縫直通 VoiceTube Studio 雙欄學習工作台。
7. **PWA 快取與版本升級工程**：落實 Service Worker（`sw.js`）零快取殘留發布標準（v32），確保用戶端即時套用最新功能與程式碼。
8. **零假載入殘留與動態舞台響應標準 (Zero-Stale-Placeholder Standard)**：嚴禁在 HTML 中使用「正在準備影片與字幕…」靜態佔位文字。`openVideo()` 啟動時必須立即主動響應狀態：若有字幕則毫秒級切換第一句；若無字幕則主動呈現「📺 支援 YouTube 原生 CC 字幕」導引卡，杜絕停滯於預設佔位文字造成「卡死假象」。
9. **100% 全教材雙語字幕覆蓋率驗收門檻 (Zero-Empty-Cues Gate)**：教材擴充不得只補目錄，所有影片與情歌（500/500 部）均必須具備大於 0 的完整逐句 Cues，發布前強制執行零空字幕檢驗（`assert len(cues) > 0`），違者不得提交。
10. **雙軌毫秒級聲畫音訊對齊標準 (Dual-Tier Audio-Subtitle Alignment)**：
    - **第一軌 (VTT 軌)**：優先透過 `calibrate_song_timings.py` 對齊 YouTube 官方 MV 字幕軌。
    - **第二軌 (Whisper 軌)**：針對無官方字幕之影片/歌曲，透過本機 `batch_calibrate_whisper.py`（使用 `faster-whisper` `base.en`，`word_timestamps=True`）萃取單字級毫秒波形時序，並以滑動視窗模糊序列匹配（`SequenceMatcher`）校正開唱起始點（如 Taylor Swift《Speak Now》開唱 3.84s、副歌 109.34s），徹底根絕 CD 錄音室版本與 MV 劇情過場（5s~180s）造成的時鐘脫節與早顯。
11. **三層全自動防搶跑與配樂過場鎖定管線 (Triple-Shield Music & Interlude Synchronization)**：建立 Whisper 單字級毫秒波形萃取（`word_timestamps=True`）、音樂中斷自動斷句（間隔 `>= 2.2s`）、字幕持續時間自然語速箝位（`normalize_cues`）與前端實時配樂過場防護（Interlude Guard & 倒數提示，高亮指針定格靜止）。
12. **YouTube 探索搜尋無限滾輪連續擴展 (Infinite Scroll Auto-Expansion)**：掌握後端串流分頁與前端滾動邊界偵測（`< 160px`）、並發防抖鎖與零 DOM 重組動態追加技術。
13. **3Blue1Brown 數學動畫解說與 ElevenLabs 配音管線 (3B1B Manim & ElevenLabs Engine)**：精通操控 Manim 0.22.0 系統架構動畫渲染（Apple Silicon ARM64 pre-compiled wheels）、毫秒級音畫對齊與隨時替換 ElevenLabs AI 配音。
14. **批次下載與多工選擇彈窗架構標準 (Split-Pane Batch Modal & Zero-Squish Layout Standard)**：彈窗內含大量列表與多組設定時，嚴禁單軸縱向堆疊擠壓。必須採用二維分割網格（Split-Pane Grid）：左欄 (62%) 專屬獨立滾動教材挑選（`flex: 1; min-height: 0; overflow-y: auto`），右欄 (38%) 集中配置與即時摘要，底部常駐全寬 Action Bar。支援多維度分類標籤、「✓ 全選目前」高頻操作、保留滾動條位置的局部 DOM 補丁，並在發布前強制執行 Node.js V8 語法樹（AST）閉環檢驗。

---

## 📁 System Architecture & File Registry

| 核心檔案 / 目錄 | 職責與用途 | 關鍵注意事項 |
|---|---|---|
| `index.html` | 前端主介面、VoiceTube UI、10 大頻道與 CEFR 難度導航列、卡拉OK字幕引擎、YT 播放器、TTS 朗讀器 | 內嵌 400 部影片與 100 首情歌（合計 500 部） |
| `songs_100.json` | 100 首精選情歌完整雙語 Cues 庫（每首 25～66 組句組，涵蓋率 90%~100%） | 包含 id, title, speaker, channel: Music, level, duration, cues 等結構 |
| `video_lessons.json` | 500 部各類影片與歌曲雙語 Cues、繁中翻譯與重點詞彙庫 | 提供卡片的 fallback 異步載入與資料庫備援 |
| `video_lessons.js` | 演講字幕與詞彙的 JavaScript 快速全域預載變數（`window.PRELOADED_LESSONS`） | 提高載入速度，避免首屏二次請求 |
| `server.py` | 本機輕量 HTTP 伺服器（預設 Port `8885`）、yt-dlp 字幕提取端點、Whisper 毫秒轉錄、搜尋分頁 API | 支援 `PORT` 環境變數自訂埠號 |
| `sw.js` | Service Worker 快取與 PWA 離線機制 | 每次修改前端或資料需同步遞增 `CACHE` 版本字串 |
| `englishtube_3b1b.py` | 3Blue1Brown 風格系統架構 Manim 數學/系統動畫全片腳本 | 4 幕 49.12 秒毫秒級音畫對齊 |
| `generate_elevenlabs_voice.py` | 開箱即用 ElevenLabs 頂級神經配音換聲腳本 | 支援 Adam、George 等聲線即時替換 |
| `calibrate_song_timings.py` | 第一軌：YouTube 官方 MV 帶毫秒字幕軌自動爬取與比對校準腳本 | 優先比對官方 VTT 軌道 |
| `batch_calibrate_whisper.py` | 第二軌：無官方字幕歌曲之本機 faster-whisper 音訊單字級毫秒自動對齊工具 | 自動下載音訊、語音轉錄、時序滑動視窗錨定並自動清理暫存 |
| `fill_all_50_songs_gemini.py` | 歌詞全曲時序補齊工具（多模型自動降級、防 429 退避重試、自動注入 HTML） | 支援續傳，已完成歌曲自動跳過 |
| `run-local.command` | macOS 雙擊一鍵啟動腳本（自動 venv、pip install 與開啟瀏覽器） | 雙擊即可啟動開發伺服器 |
| `stop-local.command` | macOS 雙擊一鍵停止腳本（安全釋放 port 8885） | 快速關閉伺服器行程 |
| `requirements.txt` | Python 相依套件（`yt-dlp`, `opencc-python-reimplemented`, `faster-whisper`） | 維護輕量，無大型笨重依賴 |

---

## 🚀 Standard Operating Procedures (SOP)

### 1. 伺服器啟動與狀態檢查

```bash
# 1. 檢查 port 8885 是否正在運行
lsof -i :8885

# 2. 手動啟動伺服器
cd /Users/banson/antigravity_projects/englishtube
python3 server.py

# 3. 指定不同連接埠啟動
PORT=9000 python3 server.py

# 4. 測試伺服器是否正常回應
curl -sI http://localhost:8885/ | head -5
```

### 2. 歌詞庫全曲補齊與批次校準 (Gemini API)

當新增歌曲或修復歌詞早停問題時，執行：

```bash
cd /Users/banson/antigravity_projects/englishtube
# 需確保環境變數含有 GEMINI_API_KEY
python3 fill_all_50_songs_gemini.py
```

**自動流程說明**：
1. 讀取 `songs_50.json`，自動辨識 cues 小於 20 句或尾段涵蓋率低於 70% 的歌曲。
2. 優先調用 `gemini-3.1-flash-lite`（快速且額度充裕），遇 429 自動退避 8 秒並輪詢 `gemini-2.5-flash-lite` ⇄ `gemini-2.5-flash` ⇄ `gemini-2.5-pro`。
3. 生成完畢後，腳本會自動同步：
   - 寫入 `songs_50.json`
   - 將新 JSON 壓縮注入 `index.html` 中的 `const songs = [...]`
   - 更新 `video_lessons.json` 與 `video_lessons.js`

### 3. 發布與快取清空標準 (Cache Busting)

若修改了 `index.html`、`songs_50.json` 或 `video_lessons.json`，**必須嚴格執行三步驟避免瀏覽器快取殘留**：

1. **更新 `sw.js`**：遞增快取名稱（例如 `englishtube-v24` → `englishtube-v25`）。
2. **更新 `index.html` 註冊參數**：修改 `navigator.serviceWorker.register('./sw.js?v=25')`。
3. **使用者排查指引**：若用戶端仍見舊版，引導至 DevTools → Application → Service Workers 點選「Unregister」並按下 `Cmd + Shift + R`。

---

## 🧩 核心技術規範與除錯指南

### A. YouTube 官方 CC 軟字幕強制阻絕 (CC Suppression)

* **現象**：YouTube 畫面內跳出重複、延遲且單字常拼錯的自動語音辨識 CC 字幕。
* **根治方式**：
  在 `index.html` 的 `createYTPlayer` 必須於 `onReady` 與 `onStateChange === 1 (PLAYING)` 雙階段強制執行：
  ```javascript
  if (!youtubeCCEnabled) {
    try {
      event.target.unloadModule('captions');
      if (typeof event.target.setOption === 'function') {
        event.target.setOption('captions', 'track', {});
      }
    } catch(e) {}
  }
  ```
  控制按鈕切換時，必須同時透過 API 與 postMessage 發送清空指令：
  ```javascript
  const frame = document.querySelector('#playerContainer iframe, #player iframe');
  if (frame && frame.contentWindow) {
    frame.contentWindow.postMessage(JSON.stringify({event:'command',func:'unloadModule',args:['captions']}),'*');
    frame.contentWindow.postMessage(JSON.stringify({event:'command',func:'setOption',args:['captions','track',{}]}),'*');
  }
  ```

### B. 歌曲結尾伴奏期字幕防早停 (Sticky Last Cue)

* **現象**：歌曲進入尾聲最後一段長伴奏時，字幕突然提早空白消失。
* **根治方式**：
  在 `syncSubtitleAndWords` 函式中維護「黏性結尾防呆」：
  ```javascript
  // Sticky last cue: if time is past all cues, keep showing the last one
  if (matchIdx === -1 && cues.length > 0) {
    const lastCue = cues[cues.length - 1];
    if (time >= lastCue.start) {
      matchIdx = cues.length - 1;
    }
  }
  ```

### C. 跨句平滑動態過渡 (Smooth Sentence Bridging)

* **現象**：相鄰兩句字幕中間若有 0.5 秒空檔，字幕列會短暫閃爍或跳空。
* **根治方式**：
  動態預覽下一句的起始秒數進行動態拉伸：
  ```javascript
  const nextStart = (i + 1 < cues.length) ? cues[i+1].start : (c.start + (c.duration || 5));
  const dur = c.duration > 0 ? c.duration : Math.max(1.0, nextStart - c.start);
  const cueEnd = Math.max(c.start + dur, Math.min(c.start + dur + 1.2, nextStart));
  if (time >= c.start && time < cueEnd) {
    matchIdx = i;
    break;
  }
  ```

### D. 播放器銷毀與零記憶體洩漏 (Zero-Leak Lifecycle)

* **規範**：
  關閉彈窗（`closeModal`）時，嚴禁僅做 CSS `display: none`，必須完整執行：
  ```javascript
  stopSubtitleSync();
  closeWordPopover();
  isPlaying = false;
  if (ytPlayer) {
    try {
      if (typeof ytPlayer.stopVideo === 'function') ytPlayer.stopVideo();
      if (typeof ytPlayer.destroy === 'function') ytPlayer.destroy();
    } catch(e) {}
    ytPlayer = null;
  }
  const container = document.getElementById('playerContainer');
  if (container) container.innerHTML = '';
  ```

### E. 卡拉OK聲畫同步與三軌音訊對齊標準 (Tri-Tier Audio Alignment & 60fps Continuous Clock Engine)

#### 脫節三大根本成因

1. **MV 前奏與劇情過場時差**：
   YouTube 官方 MV 常包含 5–180 秒的視覺前奏、劇情對白或長鏡頭（例如 *My Heart Will Go On* 電影前奏約 176 秒、*Right Here Waiting* 鋼琴特寫約 45 秒、*Love Story* 古堡長鏡頭約 16 秒）。若直接套用 CD 錄音室版本時序，字幕會明顯超前。
2. **中段句組與副歌提前觸發**：
   舊版手工切分或大模型粗切的句組，經常漏掉主歌過渡句（如 Taylor Swift《Speak Now》35.72s 的 “This is certainly not...”），或將副歌開頭提早 2–3 秒觸發（如 106.14s 覆蓋 “You wish it was me”），導致歌唱者與文字嚴重錯位。
3. **YouTube Iframe 250ms 階梯式取樣抖動**：
   Iframe API 的 `getCurrentTime()` 每 250ms 才更新一次。若直接高頻 polling 覆蓋時間戳，會造成時鐘停滯後突跳，破壞連續性。

#### 三軌高精度音訊校準架構 (Tri-Tier Audio Alignment Standard)

1. **第一軌：VTT 官方字幕軌 — `calibrate_song_timings.py`**：
   - 使用 `yt-dlp` 檢索 YouTube 官方 MV 是否內建官方英文字幕或自動辨識字幕。
   - 解析 `.vtt` 的毫秒級時間標記，並以 `SequenceMatcher` 進行語義時序比對，自動校準現存雙語歌詞的起始與結束拍點。
2. **第二軌：Whisper 音訊軌 — `batch_calibrate_whisper.py`**：
   - 當影片無可用 YouTube 字幕軌時，下載音訊並以本機 `faster-whisper`（`base.en`、`word_timestamps=True`、`beam_size=5`）萃取單字級（Word-Level）毫秒波形時序。
   - 採用滑動視窗模糊序列匹配（Sliding-Window Fuzzy Matching，`threshold > 0.42`），將雙語歌詞每一句錨定至實際歌唱發音起點，消除前奏與唱詞間的隱性落差。
   - 執行單調遞增時長平滑（Monotonic Smoothing），防止前後句時間重疊。
3. **第三軌：LRCLIB 全球毫秒同步歌詞軌 + 智慧 MV 前奏補償 — `audit_and_fix_entire_catalog.py`**：
   - 針對 VEVO 封鎖字幕或防爬蟲阻絕的官方 MV，直連開源毫秒同步歌詞資料庫（LRCLIB），取得完整未截斷的真值歌詞，徹底根除 AI 幻覺、7 句短模板與演員口白偽歌詞。
   - 內建智慧 MV 前奏時差補償演算法（`compute_smart_offset`），自動偵測 MV 視覺前奏、長鏡頭電影開場與 CD 版的秒數差（例如 Whitney Houston 前奏 +6.4s、Boyz II Men 對話過場 +47.5s、Coldplay 漫步海灘 35s），精準無縫對齊。
   - 搭配記憶體雙語快取（7,000+ 句詞庫）與 OpenCC `s2twp`，確保 100% 台灣繁體中文自然語義翻譯。

#### 前端 60 FPS 實時平滑插值與知覺補償

1. **高精準動態插值**：
   `getExactPlaybackTime()` 僅在 `getCurrentTime()` 發生真值變動時記錄基準點，其餘時間以 `performance.now()` 高精準時鐘補足差值，並輔以 80ms 視聽知覺超前補償。
2. **智慧前奏倒數**：
   當 `time < cues[0].start - 0.5` 時，舞台顯示 `🎵 (前奏演奏中 · 倒數 Xs)`，避免第一句歌詞無謂早顯；開唱前 0.5 秒平滑淡入。
3. **智慧長間奏倒數與預載**：
   兩句之間間隔大於 4.5 秒時，自動顯示 `🎵 (間奏音樂演奏中 · 倒數 Xs)`，並在下一句開唱前 0.8 秒平滑預載，杜絕突兀與搶拍。
4. **零分配單字高亮**：
   `updateKaraokeWordHighlight()` 杜絕高頻 DOM 查詢與 GC 抖動，採一次性 class 差分切換。

| 項目 | 原問題 | 改進內容 |
| :--- | :--- | :--- |
| **標題一致性** | Dual-Tier 與三軌矛盾 | 統一改為 Tri-Tier / 三軌 |
| **結構清晰度** | 段落較長、層級不明 | 拆成「成因 → 三軌校準 → 前端補償」三大部分 |
| **用詞精準度** | 部分描述稍顯口語或冗長 | 改為更專業、平行的技術敘述 |
| **邏輯流暢性** | 因果關係不夠直觀 | 每個成因與對應解決方案更明確對應 |
| **可維護性** | 範例與參數散落 | 保留關鍵參數與範例，方便後續開發參考 |

### F. 三層全自動防搶跑與配樂過場防護標準 (Triple-Shield Synchronization Standard)

* **現象與痛點**：
  影片開頭若有前奏，字幕過早顯示並提前滾動；對白結束後若有鋼琴/吉他等長段背景配樂（5~15s），字幕指針持續前進甚至提前觸發下一句，造成視覺嚴重搶跑。
* **根治方式（三層防護網）**：
  1. **第一層 · Whisper 單字級毫秒波形萃取（`server.py`）**：
     強制啟用 `word_timestamps=True`，為每個單字保存精確 `[s, e]` 毫秒時間戳。兩字間若出現 `>= 2.2 秒` 音樂或停頓，自動斷開為獨立句組，防止模型將配樂粗糙跨接。
  2. **第二層 · 字幕時長自然語速箝位引擎（`normalize_cues`）**：
     針對官方 VTT 字幕持續時間覆蓋配樂的現象，依該句單字量計算自然語速上限（`max_natural_dur = round(num_words * 0.75 + 1.2, 2)`），超過上限自動箝位，釋放被侵占的配樂過場時段。
  3. **第三層 · 前端 60 FPS 實時配樂過場防護（`index.html`）**：
     在 `syncSubtitleAndWords` 中偵測當前句與下一句間隔，當間隔 `>= 2.0 秒` 時，舞台轉為 `🎵 (配樂過場中 · 倒數 Xs)`，高亮指針與字幕**100% 定格靜止**；在 `updateKaraokeWordHighlight` 中直接比對單字之真實起訖毫秒，口語說完立即定格於 `passed`，不再靠比例盲目推進。

### H. 批次下載與多工選擇彈窗架構標準 (Split-Pane Batch Modal & Zero-Squish Layout Standard)

* **現象與痛點**：
  在彈窗中同時存在「大量可選清單（500 部教材）」、「多種格式設定（MP4/MP3/字幕/畫質）」與「目錄配置（路徑/Finder按鈕）」時，若採用單軸縱向堆疊（Vertical Stack），下方卡片會霸佔高度，導致清單容器被壓扁至 0px 或被裁切，使用者根本無法在視覺上看清、滾動或勾選教材。此外在幾萬行單檔 HTML 中修改 JS 時，若殘留重複括號，會導致整站腳本崩潰。
* **根治方式（三大標準法則）**：
  1. **二維分割網格佈局（Split-Pane Grid）**：
     - Modal Body 採用 CSS Grid：`grid-template-columns: 1fr 340px;`，左側 62% 為教材挑選主舞台，右側 38% 為格式與目錄設定台。
     - 頂部導航分頁（Tabs Row）與底部操作列（Action Bar）設定 `grid-column: 1 / -1;` 橫跨滿版。
  2. **Flex 滾動閉環與防壓扁公式（Zero-Squish Container Rule）**：
     - 彈窗主體設定 `height: 86vh; max-height: 800px; display: grid;`。
     - 左欄容器必須顯式宣告：`display: flex; flex-direction: column; min-height: 0; overflow: hidden;`（**缺少 `min-height: 0` 會導致 Flex 子元素高度計算失效**）。
     - 清單滾動容器設定：`flex: 1; min-height: 0; overflow-y: auto;`，確保滾動條永遠被約束在左欄，絕不溢出或擠壓頁首/頁尾。
  3. **局部 DOM 補丁（Preserve Scroll Top）**：
     - 勾選或取消勾選特定項目時，直接透過 `document.getElementById('dl-item-' + id)` 差分更新勾選樣式與徽章，嚴禁直接 `container.innerHTML = ...` 全量重繪，以徹底保留用戶當前的滾動位置（`scrollTop`）。
  4. **大型單檔 V8 AST 語法閉環驗證規範**：
     - 每次在 `index.html`（50,000+ 行）進行 JavaScript 代碼修改後，**強制**在命令列執行 Node.js 語法樹檢驗，杜絕括號不對稱或語法錯誤上線：
     ```bash
     node -e "
     const fs = require('fs');
     const html = fs.readFileSync('index.html', 'utf8');
     const scriptMatches = html.match(/<script[\s\S]*?>([\s\S]*?)<\/script>/gi) || [];
     scriptMatches.forEach((tag, idx) => {
       const content = tag.replace(/^<script[\s\S]*?>/i, '').replace(/<\/script>$/i, '');
       try {
         new Function(content);
         console.log('Script #' + (idx+1) + ': JS Syntax VALID! Length: ' + content.length);
       } catch (err) {
         console.error('Script #' + (idx+1) + ' Syntax Error:', err.message);
         process.exit(1);
       }
     });
     "
     ```

---

## 🏛️ 三專家架構檢驗清單 (Tri-Architect Checklist)

在對本專案進行任何功能修改或代碼提交前，必須自檢：

1. **⚡ 低階並發與管線專家 (Concurrency & Pipeline)**：
   - [ ] 外部 API（Gemini / OpenAI / YouTube）調用是否皆具備逾時保護（`timeout=45`）與異常捕獲？
   - [ ] 播放器 Event Listener 與 requestAnimationFrame 迴圈是否在離開視窗時 100% 被清理？
2. **🧠 記憶體與零分配專家 (Memory Efficiency)**：
   - [ ] 50 首情歌大容量 JSON（數萬行 Cues）是否有效壓縮並避免重複深度拷貝？
   - [ ] YouTube iframe 容器在每次切換影片時是否徹底清空，杜絕孤兒 iframe 殘留？
   - [ ] 大型 HTML/JS 檔案（>10,000 行）編輯後是否經由 Node.js `new Function()` 進行 100% 語法閉環驗證？
3. **🎨 狀態響應與人因防呆專家 (Reactive State & Human-Centric)**：
   - [ ] 播放速度設定是否透過 localStorage 非同步安全持久化？
   - [ ] 影片內部 CC 軟字幕與平台跟讀字幕是否保持互斥無干擾？
   - [ ] 彈窗是否支援「點擊 X 按鈕」與「鍵盤 ESC 鍵」安全關閉？
   - [ ] 複雜多工彈窗是否採用 Split-Pane 雙欄獨立滾動架構，嚴格遵循 `min-height: 0` 盒模型閉環，防止設定卡片擠壓清單？
   - [ ] 列表勾選是否支援「局部 DOM 補丁」，防止全量 re-render 導致滾動條跳回最頂部？
   - [ ] **全域渲染生命週期防護**：出現在首頁卡片模板中的變數是否皆在模組頂層顯式初始化，且具備 `typeof` 防禦性檢查，杜絕 ReferenceError 導致首頁教材全部空白？
   - [ ] **無頭 Chrome 閉環驗收**：透過 CDP 驗證首頁 `Runtime.exceptionThrown` 為 0 且 `#grid` 子節點數大於 0？
