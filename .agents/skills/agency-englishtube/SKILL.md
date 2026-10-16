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

---

## 📁 System Architecture & File Registry

| 核心檔案 / 目錄 | 職責與用途 | 關鍵注意事項 |
|---|---|---|
| `index.html` | 前端主介面、VoiceTube UI、10 大頻道與 CEFR 難度導航列、卡拉OK字幕引擎、YT 播放器、TTS 朗讀器 | 內嵌 400 部影片與 100 首情歌（合計 500 部） |
| `songs_100.json` | 100 首精選情歌完整雙語 Cues 庫（每首 25～66 組句組，涵蓋率 90%~100%） | 包含 id, title, speaker, channel: Music, level, duration, cues 等結構 |
| `video_lessons.json` | 500 部各類影片與歌曲雙語 Cues、繁中翻譯與重點詞彙庫 | 提供卡片的 fallback 異步載入與資料庫備援 |
| `video_lessons.js` | 演講字幕與詞彙的 JavaScript 快速全域預載變數（`window.PRELOADED_LESSONS`） | 提高載入速度，避免首屏二次請求 |
| `server.py` | 本機輕量 HTTP 伺服器（預設 Port `8885`）、yt-dlp 字幕提取端點、字典快取 API | 支援 `PORT` 環境變數自訂埠號 |
| `sw.js` | Service Worker 快取與 PWA 離線機制 | 每次修改前端或資料需同步遞增 `CACHE` 版本字串 |
| `fill_all_50_songs_gemini.py` | 歌詞全曲時序補齊工具（多模型自動降級、防 429 退避重試、自動注入 HTML） | 支援續傳，已完成歌曲自動跳過 |
| `run-local.command` | macOS 雙擊一鍵啟動腳本（自動 venv、pip install 與開啟瀏覽器） | 雙擊即可啟動開發伺服器 |
| `stop-local.command` | macOS 雙擊一鍵停止腳本（安全釋放 port 8885） | 快速關閉伺服器行程 |
| `requirements.txt` | Python 相依套件（`yt-dlp`, `opencc-python-reimplemented`） | 維護輕量，無大型笨重依賴 |

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

### E. 卡拉OK聲畫同步與平滑時鐘插值標準 (Karaoke Audio-Subtitle Sync & 60fps Continuous Clock)

* **脫節根本成因**：
  1. **MV 前奏劇情時差**：YouTube 官方 MV 常有 5s 至 180s 的過場前奏或劇情對白（例如 *My Heart Will Go On* 電影劇情前奏達 176 秒、*Right Here Waiting* 鋼琴特寫達 45 秒），若以 CD 錄音室版本時序套用，字幕會超前幾十秒。所有情歌必須經由 `calibrate_song_timings.py` 依據官方 YouTube MV 實際字幕精準錨定。
  2. **YouTube Iframe 250ms 階梯式取樣抖動**：Iframe API 的 `getCurrentTime()` 每 250ms 才更新一次，若直接高頻 polling 覆蓋時間戳，會導致時鐘停滯再突跳。
* **工程解法**：
  1. **60 FPS 實時平滑插值**：`getExactPlaybackTime()` 僅在 `getCurrentTime()` 發生真值變動時記錄基準點，其餘時間以 `performance.now()` 高精準時鐘補足差值，並輔以 80ms 視聽知覺超前補償。
  2. **前奏倒數與間奏防呆**：當 `time < cues[0].start - 0.5` 時，舞台呈現 `🎵 (前奏演奏中 · 倒數 Xs)`，杜絕第一句歌詞無謂早顯；兩句之間大於 4.5 秒時，自動顯示 `🎵 (間奏音樂演奏中 · 倒數 Xs)`，並在下一句開唱前 0.8 秒平滑預載。
  3. **零分配單字高亮**：`updateKaraokeWordHighlight()` 杜絕高頻 DOM 查詢與 GC 抖動，採一次性 class 差分切換。

---

## 🏛️ 三專家架構檢驗清單 (Tri-Architect Checklist)

在對本專案進行任何功能修改或代碼提交前，必須自檢：

1. **⚡ 低階並發與管線專家 (Concurrency & Pipeline)**：
   - [ ] 外部 API（Gemini / OpenAI / YouTube）調用是否皆具備逾時保護（`timeout=45`）與異常捕獲？
   - [ ] 播放器 Event Listener 與 requestAnimationFrame 迴圈是否在離開視窗時 100% 被清理？
2. **🧠 記憶體與零分配專家 (Memory Efficiency)**：
   - [ ] 50 首情歌大容量 JSON（數萬行 Cues）是否有效壓縮並避免重複深度拷貝？
   - [ ] YouTube iframe 容器在每次切換影片時是否徹底清空，杜絕孤兒 iframe 殘留？
3. **🎨 狀態響應與人因防呆專家 (Reactive State & Human-Centric)**：
   - [ ] 播放速度設定是否透過 localStorage 非同步安全持久化？
   - [ ] 影片內部 CC 軟字幕與平台跟讀字幕是否保持互斥無干擾？
   - [ ] 彈窗是否支援「點擊 X 按鈕」與「鍵盤 ESC 鍵」安全關閉？
