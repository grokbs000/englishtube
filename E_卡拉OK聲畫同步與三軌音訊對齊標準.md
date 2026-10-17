# E. 卡拉OK聲畫同步與三軌音訊對齊標準
(Tri-Tier Audio Alignment & 60fps Continuous Clock Engine)

## 脫節三大根本成因

1. **MV 前奏與劇情過場時差**  
   YouTube 官方 MV 常包含 5–180 秒的視覺前奏、劇情對白或長鏡頭（例如 *My Heart Will Go On* 電影前奏約 176 秒、*Right Here Waiting* 鋼琴特寫約 45 秒、*Love Story* 古堡長鏡頭約 16 秒）。若直接套用 CD 錄音室版本時序，字幕會明顯超前。

2. **中段句組與副歌提前觸發**  
   舊版手工切分或大模型粗切的句組，經常漏掉主歌過渡句（如 Taylor Swift《Speak Now》35.72s 的 “This is certainly not...”），或將副歌開頭提早 2–3 秒觸發（如 106.14s 覆蓋 “You wish it was me”），導致歌唱者與文字嚴重錯位。

3. **YouTube Iframe 250ms 階梯式取樣抖動**  
   Iframe API 的 `getCurrentTime()` 每 250ms 才更新一次。若直接高頻 polling 覆蓋時間戳，會造成時鐘停滯後突跳，破壞連續性。

---

## 三軌高精度音訊校準架構 (Tri-Tier Audio Alignment Standard)

### 第一軌：VTT 官方字幕軌 — `calibrate_song_timings.py`
* 使用 `yt-dlp` 檢索 YouTube 官方 MV 是否內建官方英文字幕或自動辨識字幕。
* 解析 `.vtt` 的毫秒級時間標記，並以 `SequenceMatcher` 進行語義時序比對，自動校準現存雙語歌詞的起始與結束拍點。

### 第二軌：Whisper 音訊軌 — `batch_calibrate_whisper.py`
* 當影片無可用 YouTube 字幕軌時，下載音訊並以本機 `faster-whisper`（`base.en`、`word_timestamps=True`、`beam_size=5`）萃取單字級（Word-Level）毫秒波形時序。
* 採用滑動視窗模糊序列匹配（Sliding-Window Fuzzy Matching，`threshold > 0.42`），將雙語歌詞每一句錨定至實際歌唱發音起點，消除前奏與唱詞間的隱性落差。
* 執行單調遞增時長平滑（Monotonic Smoothing），防止前後句時間重疊。

### 第三軌：LRCLIB 全球毫秒同步歌詞軌 + 智慧 MV 前奏補償 — `audit_and_fix_entire_catalog.py`
* 針對 VEVO 封鎖字幕或防爬蟲阻絕的官方 MV，直連開源毫秒同步歌詞資料庫（LRCLIB），取得完整未截斷的真值歌詞，徹底根除 AI 幻覺、7 句短模板與演員口白偽歌詞。
* 內建智慧 MV 前奏時差補償演算法（`compute_smart_offset`），自動偵測 MV 視覺前奏、長鏡頭電影開場與 CD 版的秒數差（例如 Whitney Houston 前奏 +6.4s、Boyz II Men 對話過場 +47.5s、Coldplay 漫步海灘 35s），精準無縫對齊。
* 搭配記憶體雙語快取（7,000+ 句詞庫）與 OpenCC `s2twp`，確保 100% 台灣繁體中文自然語義翻譯。

---

## 前端 60 FPS 實時平滑插值與知覺補償

1. **高精準動態插值**  
   `getExactPlaybackTime()` 僅在 `getCurrentTime()` 發生真值變動時記錄基準點，其餘時間以 `performance.now()` 高精準時鐘補足差值，並輔以 80ms 視聽知覺超前補償。

2. **智慧前奏倒數**  
   當 `time < cues[0].start - 0.5` 時，舞台顯示 `🎵 (前奏演奏中 · 倒數 Xs)`，避免第一句歌詞無謂早顯；開唱前 0.5 秒平滑淡入。

3. **智慧長間奏倒數與預載**  
   兩句之間間隔大於 4.5 秒時，自動顯示 `🎵 (間奏音樂演奏中 · 倒數 Xs)`，並在下一句開唱前 0.8 秒平滑預載，杜絕突兀與搶拍。

4. **零分配單字高亮**  
   `updateKaraokeWordHighlight()` 杜絕高頻 DOM 查詢與 GC 抖動，採一次性 class 差分切換。

---

## 優化改進對照表

| 項目 | 原問題 | 改進內容 |
| :--- | :--- | :--- |
| **標題一致性** | Dual-Tier 與三軌矛盾 | 統一改為 Tri-Tier / 三軌 |
| **結構清晰度** | 段落較長、層級不明 | 拆成「成因 → 三軌校準 → 前端補償」三大部分 |
| **用詞精準度** | 部分描述稍顯口語或冗長 | 改為更專業、平行的技術敘述 |
| **邏輯流暢性** | 因果關係不夠直觀 | 每個成因與對應解決方案更明確對應 |
| **可維護性** | 範例與參數散落 | 保留關鍵參數與範例，方便後續開發參考 |
