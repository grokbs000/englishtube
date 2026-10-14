import subprocess, re, json

# 1. Restore clean index.html from base fc7a0ed~1
clean_base = subprocess.check_output(['git', 'show', 'fc7a0ed~1:index.html'], text=True)

with open('catalog_50.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Format catalog as JavaScript array for index.html
js_videos = []
for item in catalog:
    js_videos.append({
        'id': item['id'],
        'title': item['title'],
        'zh': item['zh'],
        'cat': item['cat'],
        'level': item['level'],
        'duration': item['duration'],
        'views': item['views'],
        'emoji': item['emoji'],
        'color': item['color'],
        'desc': f"{item['speaker']} · {item['zh']}",
        'url': f"https://www.youtube.com/watch?v={item['id']}",
        'en': [],
        'cn': [],
        'words': []
    })

videos_js_code = "const videos = " + json.dumps(js_videos, ensure_ascii=False) + ";"

html = clean_base

# Replace videos array with 50 videos
html = re.sub(r'const videos=\[[\s\S]*?\];', videos_js_code, html, count=1)

# Update categories list to include all 50 video categories
html = html.replace(
    "const cats=['全部','生活','口說','科學','收藏'];",
    "const cats=['全部','生活','口說','科學','心理','職場','科技','收藏'];"
)

# Add YouTube iframe API script tag in <head>
if 'https://www.youtube.com/iframe_api' not in html:
    html = html.replace('</head>', '<script src="https://www.youtube.com/iframe_api"></script>\n</head>')

# Add complete VoiceTube CSS with left-aligned subtitle stage and vivid word-by-word karaoke highlight
vt_css = """
/* ═══════════════════════════════════════════════════════════════
   VOICETUBE STYLE LEARNING STUDIO (50 影片完整字幕 - 逐字連動 HIGHLIGHT)
   ═══════════════════════════════════════════════════════════════ */
.modal {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(10, 10, 20, 0.92);
  backdrop-filter: blur(8px);
  z-index: 100;
  padding: 16px;
  overflow-y: auto;
  align-items: center;
  justify-content: center;
}
.modal.open {
  display: flex;
}
.vt-modalbox {
  background: #141422;
  color: #e4e4f0;
  border: 1px solid #2a2a3e;
  border-radius: 20px;
  width: min(1320px, 98vw);
  max-height: 94vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0,0,0,0.6);
  animation: slideUp .3s cubic-bezier(.22,1,.36,1);
}
/* Studio Header */
.vt-studio-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #10101b;
  border-bottom: 1px solid #252538;
  gap: 12px;
  flex-wrap: wrap;
}
.vt-head-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.vt-listen-tag {
  font-size: 20px;
  font-weight: 900;
  letter-spacing: -0.5px;
  color: #fff;
  border-bottom: 3px solid #6d5dfc;
  padding-bottom: 2px;
}
.vt-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.3px;
}
.vt-badge.level {
  background: #199468;
  color: #fff;
}
.vt-badge.accent {
  background: #d67a18;
  color: #fff;
}
.vt-meta-views {
  font-size: 13px;
  color: #9292ab;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.vt-head-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.vt-btn-act {
  background: #202033;
  color: #d0d0e6;
  border: 1px solid #303048;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: .15s;
}
.vt-btn-act:hover {
  background: #2d2d48;
  color: #fff;
}
.vt-btn-act.liked {
  background: #2563eb;
  color: #fff;
  border-color: #3b82f6;
}
.vt-btn-act.saved {
  background: #059669;
  color: #fff;
  border-color: #10b981;
}
.vt-close-btn {
  background: #25253a;
  color: #fff;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  font-size: 20px;
  border: 0;
  cursor: pointer;
}
.vt-close-btn:hover {
  background: #3c3c58;
}

/* Studio Body Grid */
.vt-studio-body {
  padding: 16px 20px;
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 20px;
  overflow-y: auto;
  flex: 1;
}
@media (max-width: 960px) {
  .vt-studio-body {
    grid-template-columns: 1fr;
    padding: 12px;
    gap: 16px;
  }
}

/* Left Column: Player & Subtitle Stage */
.vt-main-col {
  display: flex;
  flex-direction: column;
}
.vt-player-wrapper {
  position: relative;
  aspect-ratio: 16/9;
  background: #000;
  border-radius: 14px 14px 0 0;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.vt-player-wrapper iframe, .vt-player-wrapper div#playerContainer {
  width: 100%;
  height: 100%;
  border: 0;
}

/* VoiceTube Subtitle Stage (靠左對齊 + 左側裝飾條 + 逐字反白移動) */
.vt-sub-stage {
  background: #0d0d1a;
  border: 1px solid #232338;
  border-top: none;
  border-left: 5px solid #6d5dfc;
  border-radius: 0 0 14px 14px;
  padding: 18px 24px;
  min-height: 115px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  text-align: left;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.4);
}
.vt-sub-en-line {
  font-size: 23px;
  font-weight: 750;
  line-height: 1.6;
  color: #ffffff;
  letter-spacing: -0.2px;
  width: 100%;
  text-align: left;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 3px 6px;
}
.vt-sub-zh-line {
  font-size: 15px;
  font-weight: 500;
  line-height: 1.5;
  color: #9ea0be;
  margin-top: 8px;
  width: 100%;
  text-align: left;
}

/* ══════════ 逐字連動 HIGHLIGHT 核心樣式 ══════════ */
.vt-word-token {
  cursor: pointer;
  display: inline-block;
  padding: 2px 6px;
  border-radius: 5px;
  transition: background 0.08s ease, color 0.08s ease, transform 0.08s ease, box-shadow 0.08s ease;
  line-height: 1.25;
}
/* 尚未說到的單字：低調微光 */
.vt-word-token.future {
  color: #6b6b85 !important;
  font-weight: 500;
}
/* 已經講過的單字：清晰白字 */
.vt-word-token.passed {
  color: #ffffff !important;
  font-weight: 700 !important;
}
/* 當前正在發音的單字：鮮明反白高亮焦點 (反白移動中) */
.vt-word-token.current {
  background: #ffffff !important;
  color: #0b0b18 !important;
  font-weight: 900 !important;
  box-shadow: 0 0 16px rgba(255, 255, 255, 0.95), 0 2px 8px rgba(0,0,0,0.5);
  transform: translateY(-2px) scale(1.08);
  display: inline-block;
}
.vt-word-token:hover {
  background: rgba(109, 93, 252, 0.4) !important;
  color: #a49aff !important;
  text-decoration: underline;
}
.vt-punct {
  color: #6b6b85;
  margin-right: 2px;
}

/* 右側清單內微型逐字反白樣式 */
.vt-mini-word {
  display: inline;
  transition: color 0.1s ease, background 0.1s ease;
}
.vt-mini-word.future {
  color: #8b8ba4;
}
.vt-mini-word.passed {
  color: #ffffff;
  font-weight: 600;
}
.vt-mini-word.current {
  background: #6d5dfc !important;
  color: #ffffff !important;
  padding: 1px 4px;
  border-radius: 4px;
  font-weight: 800 !important;
}

/* Control Bar Under Subtitle */
.vt-controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #171728;
  border: 1px solid #28283e;
  border-radius: 12px;
  padding: 10px 14px;
  margin-top: 12px;
  gap: 10px;
  flex-wrap: wrap;
}
.vt-ctrl-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.vt-ctrl-btn {
  background: #222236;
  color: #dedee8;
  border: 1px solid #30304a;
  border-radius: 8px;
  padding: 7px 12px;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: .15s;
}
.vt-ctrl-btn:hover {
  background: #31314d;
  color: #fff;
}
.vt-repeat-btn.active {
  background: #6d5dfc !important;
  color: #fff !important;
  border-color: #8b7cff !important;
  box-shadow: 0 0 14px rgba(109,93,252,0.6);
}
.vt-pill-btn {
  background: #222236;
  color: #8f8fa8;
  border: 1px solid #2c2c42;
  padding: 5px 9px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 750;
  cursor: pointer;
  transition: .15s;
}
.vt-pill-btn.active {
  background: #6d5dfc;
  color: #fff;
  border-color: #6d5dfc;
}

/* Custom Tool Accordion */
.vt-custom-details {
  background: #151525;
  border: 1px solid #28283e;
  border-radius: 12px;
  padding: 10px 14px;
  margin-top: 12px;
  font-size: 13px;
}
.vt-custom-details summary {
  cursor: pointer;
  font-weight: 750;
  color: #8b7cff;
}

/* Right Column: Subtitle List & Dictionary Panel */
.vt-side-col {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.vt-panel-card {
  background: #161627;
  border: 1px solid #26263b;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.vt-transcript-card {
  height: 380px;
}
.vt-panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #121221;
  border-bottom: 1px solid #242438;
}
.vt-panel-title {
  font-size: 13px;
  font-weight: 800;
  color: #c8c8de;
  letter-spacing: 0.3px;
}
.vt-transcript-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 8px 10px;
  scroll-behavior: smooth;
}
/* Subtitle List Row */
.vt-cue-row {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 6px;
  cursor: pointer;
  transition: all .15s ease;
  border-left: 3px solid transparent;
  color: #b5b5c9;
  font-size: 14px;
  line-height: 1.45;
}
.vt-cue-row:hover {
  background: #202035;
  color: #fff;
}
/* VoiceTube Highlight Effect */
.vt-cue-row.active {
  background: #2c274d !important;
  color: #ffffff !important;
  border-left: 3px solid #8b7cff;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  font-weight: 600;
}
.vt-cue-play-btn {
  color: #6d5dfc;
  font-size: 12px;
  flex-shrink: 0;
  margin-top: 2px;
}
.vt-cue-row.active .vt-cue-play-btn {
  color: #a49aff;
}
.vt-cue-content {
  flex: 1;
}
.vt-cue-en {
  display: block;
}
.vt-cue-zh {
  display: block;
  font-size: 12px;
  color: #8888a2;
  margin-top: 3px;
  font-weight: 400;
}
.vt-cue-time {
  font-size: 11px;
  color: #6e6e87;
  flex-shrink: 0;
  margin-top: 2px;
  font-family: monospace;
}

/* Dictionary & Vocabulary Card */
.vt-dict-card {
  min-height: 250px;
}
.vt-tab-header {
  display: flex;
  background: #11111f;
  border-bottom: 1px solid #242438;
}
.vt-tab-btn {
  flex: 1;
  padding: 10px;
  background: transparent;
  color: #8b8b9e;
  border: 0;
  font-size: 13px;
  font-weight: 750;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: .15s;
}
.vt-tab-btn.active {
  color: #8b7cff;
  border-bottom-color: #6d5dfc;
  background: #161627;
}
.vt-tab-body {
  padding: 12px 14px;
  flex: 1;
  overflow-y: auto;
}
.vt-dict-search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}
.vt-dict-search-row input {
  flex: 1;
  padding: 7px 11px;
  background: #10101c;
  border: 1px solid #2b2b40;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  outline: none;
}
.vt-dict-search-row button {
  background: #6d5dfc;
  color: #fff;
  padding: 7px 13px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 12px;
}
/* Word Detail Card */
.vt-word-view {
  background: #11111f;
  border: 1px solid #232338;
  border-radius: 10px;
  padding: 12px 14px;
}
.vt-word-main {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}
.vt-word-term {
  font-size: 22px;
  font-weight: 900;
  color: #a49aff;
}
.vt-word-ipa {
  font-size: 13px;
  color: #82829c;
  font-family: serif;
}
.vt-word-actions {
  display: flex;
  gap: 6px;
}
.vt-word-pos {
  display: inline-block;
  background: #23233a;
  color: #8b7cff;
  font-size: 11px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  margin-top: 6px;
}
.vt-word-def {
  font-size: 14px;
  color: #d6d6ea;
  margin-top: 6px;
  line-height: 1.5;
}
.vt-word-ex {
  font-size: 12px;
  color: #8888a2;
  margin-top: 6px;
  font-style: italic;
  padding-left: 8px;
  border-left: 2px solid #6d5dfc;
}
"""

html = html.replace('</style>', vt_css + '\n</style>')

# VoiceTube Modal HTML
vt_modal_html = """
<div class="modal" id="modal">
  <div class="vt-modalbox">
    <!-- Header -->
    <div class="vt-studio-head">
      <div class="vt-head-left">
        <div class="vt-listen-tag">聽力</div>
        <span class="vt-badge level" id="vtLevel">A2 初級</span>
        <span class="vt-badge accent">美式發音</span>
        <span class="vt-meta-views">🎧 <span id="vtViews">16.4M</span></span>
        <span id="modalTitle" style="font-weight:700;font-size:15px;color:#fff;margin-left:8px;max-width:320px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis"></span>
      </div>
      <div class="vt-head-right">
        <button class="vt-btn-act" id="vtLikeBtn" onclick="toggleLike()">👍 讚 <span id="vtLikes">225</span></button>
        <button class="vt-btn-act" onclick="shareVideo()">分享</button>
        <button class="vt-btn-act" id="vtSaveBtn" onclick="toggleSaveCurrent()">♡ 收藏</button>
        <button class="vt-close-btn" onclick="closeModal()" title="關閉">×</button>
      </div>
    </div>

    <!-- Studio Body -->
    <div class="vt-studio-body">
      <!-- Left Column: Video & Synchronized Subtitle Display (靠左對齊舞台) -->
      <div class="vt-main-col">
        <div class="vt-player-wrapper">
          <div id="playerContainer"></div>
        </div>

        <!-- VoiceTube Synchronized Subtitle Display (靠左對齊 + 逐字反白移動舞台) -->
        <div class="vt-sub-stage" id="vtSubtitleStage">
          <div class="vt-sub-en-line" id="vtActiveEn">正在準備影片與字幕…</div>
          <div class="vt-sub-zh-line" id="vtActiveZh">點選單字可即時查字典與聽發音</div>
        </div>

        <!-- VoiceTube Control Bar -->
        <div class="vt-controls-bar">
          <div class="vt-ctrl-group">
            <button class="vt-ctrl-btn" onclick="stepCue(-1)" title="上一句">⏮ 上一句</button>
            <button class="vt-ctrl-btn vt-repeat-btn" id="vtRepeatBtn" onclick="toggleRepeatCue()" title="循環播放此句">🔁 重複單句</button>
            <button class="vt-ctrl-btn" onclick="stepCue(1)" title="下一句">⏭ 下一句</button>
            <div style="display:inline-flex;gap:4px;margin-left:4px">
              <button class="vt-pill-btn active" id="subModeBoth" onclick="setSubMode('both')">雙語</button>
              <button class="vt-pill-btn" id="subModeEn" onclick="setSubMode('en')">英</button>
              <button class="vt-pill-btn" id="subModeZh" onclick="setSubMode('zh')">中</button>
              <button class="vt-pill-btn" id="subModeNone" onclick="setSubMode('none')">無</button>
            </div>
          </div>
          <div class="vt-ctrl-group">
            <span style="font-size:11px;color:#8888a2;font-weight:700">語速：</span>
            <button class="vt-pill-btn" id="speed075" onclick="setPlayerSpeed(0.75)">0.75×</button>
            <button class="vt-pill-btn active" id="speed100" onclick="setPlayerSpeed(1.0)">1.0×</button>
            <button class="vt-pill-btn" id="speed125" onclick="setPlayerSpeed(1.25)">1.25×</button>
            <button class="vt-ctrl-btn" id="autoScrollToggleBtn" onclick="toggleAutoScroll()" style="margin-left:4px">📜 自動捲動: ON</button>
          </div>
        </div>

        <!-- Custom Video & AI Tools Collapsible -->
        <details class="vt-custom-details">
          <summary>⚙️ 自訂 YouTube 網址與 AI 進階工具</summary>
          <div style="padding-top:10px">
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
              <input id="videoUrl" placeholder="貼上自訂 YouTube 網址" style="flex:1;min-width:200px;padding:8px 12px;background:#10101c;border:1px solid #2b2b40;border-radius:8px;color:#fff;font-size:13px">
              <button class="pill" onclick="loadVideoSource()">載入影片</button>
              <button class="ghost" onclick="autoFetchTranscript()">⚡ 自動取得字幕</button>
              <button class="ghost" onclick="translateLesson()">✨ AI 翻譯＋單字</button>
            </div>
            <textarea id="transcriptInput" rows="3" placeholder="貼上 YouTube「顯示文字稿」逐字稿..." style="width:100%;padding:8px;background:#10101c;border:1px solid #2b2b40;border-radius:8px;color:#fff;font:inherit;font-size:12px;resize:vertical"></textarea>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px">
              <button class="pill" onclick="makeLessonFromTranscript()">轉成逐句教材</button>
              <span id="aiStatus" style="font-size:12px;color:#888">支援 yt-dlp 字幕與 OpenAI API 翻譯</span>
            </div>
          </div>
        </details>
      </div>

      <!-- Right Column: Subtitle List & Dictionary Panel -->
      <div class="vt-side-col">
        <!-- Top: Transcript Follow-Along List -->
        <div class="vt-panel-card vt-transcript-card">
          <div class="vt-panel-head">
            <span class="vt-panel-title">逐句字幕跟讀</span>
            <div style="display:flex;gap:6px">
              <button class="vt-pill-btn" onclick="adjustSubtitleSize(-1)">A-</button>
              <button class="vt-pill-btn" onclick="adjustSubtitleSize(1)">A+</button>
            </div>
          </div>
          <div class="vt-transcript-scroll" id="vtTranscriptList">
            <!-- Dynamically populated -->
          </div>
        </div>

        <!-- Bottom: Dictionary & Vocabulary Panel -->
        <div class="vt-panel-card vt-dict-card">
          <div class="vt-tab-header">
            <button class="vt-tab-btn active" id="tabDict" onclick="switchVtTab('dict')">即時單字</button>
            <button class="vt-tab-btn" id="tabVocab" onclick="switchVtTab('vocab')">本課單字 (<span id="lessonWordCount">0</span>)</button>
            <button class="vt-tab-btn" id="tabPractice" onclick="switchVtTab('practice')">跟讀錄音</button>
          </div>
          <div class="vt-tab-body">
            <!-- Tab 1: Interactive Dictionary -->
            <div id="vtPaneDict">
              <div class="vt-dict-search-row">
                <input id="dictInput" placeholder="點選左側字幕中的單字，或在此輸入查詢..." onkeydown="if(event.key==='Enter')lookupCustomWord()">
                <button onclick="lookupCustomWord()">查詢</button>
              </div>
              <div id="vtWordView">
                <div class="vt-word-view">
                  <div class="vt-word-main">
                    <span class="vt-word-term">點擊單字查閱</span>
                    <span class="vt-word-ipa">/ˈlɜːrnɪŋ/</span>
                    <div class="vt-word-actions">
                      <button class="save" onclick="say('learning')">🔊 發音</button>
                    </div>
                  </div>
                  <div class="vt-word-pos">tip</div>
                  <div class="vt-word-def">點擊影片下方或右側字幕中的任何單字，即可在此處即時查詢發音、詞性與繁體中文解釋。</div>
                </div>
              </div>
            </div>

            <!-- Tab 2: Vocab List -->
            <div id="vtPaneVocab" style="display:none">
              <div id="vtVocabList" style="display:flex;flex-direction:column;gap:8px"></div>
            </div>

            <!-- Tab 3: Recording Practice -->
            <div id="vtPanePractice" style="display:none">
              <p style="font-size:12px;color:#8888a2;margin:0 0 8px">請聽完原句後，按下錄音跟讀練習：</p>
              <div id="practiceSentenceTarget" style="font-weight:700;color:#fff;font-size:14px;background:#10101c;padding:10px;border-radius:8px;border:1px solid #2b2b40"></div>
              <button class="pill" id="recordBtn" onclick="recordPractice()" style="width:100%;margin-top:10px">🎙 開始錄音對比</button>
              <p id="recordStatus" style="font-size:12px;color:#888;margin-top:6px"></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
"""

# Replace old modal with VoiceTube modal
modal_pattern = re.compile(r'<div class="modal" id="modal">[\s\S]*?</div>\s*</div>\s*</div>\s*(?=<div class="toast")', re.MULTILINE)
if modal_pattern.search(html):
    html = modal_pattern.sub(vt_modal_html + '\n', html)
else:
    old_modal_start = html.find('<div class="modal" id="modal">')
    old_modal_end = html.find('<div class="toast" id="toast">')
    if old_modal_start != -1 and old_modal_end != -1:
        html = html[:old_modal_start] + vt_modal_html + '\n' + html[old_modal_end:]

# VoiceTube Real-Time Synchronized Follow-Along & Karaoke Highlight Engine for 50 Videos
vt_script = """
// ── VOICETUBE SYNCHRONIZED FOLLOW-ALONG ENGINE (50 影片完整字幕 - 逐字連動 HIGHLIGHT) ──
let PRELOADED_LESSONS = { lessons: {}, vocab: {} };

// Asynchronously load the 50 full video lessons with complete untruncated subtitles
fetch('./video_lessons.json').then(r => r.json()).then(data => {
  PRELOADED_LESSONS = data;
  console.log('[ENGLISHTUBE] 50 video lessons loaded:', Object.keys(data.lessons || {}).length);
  if (current && current.id && PRELOADED_LESSONS.lessons?.[current.id]) {
    current.cues = PRELOADED_LESSONS.lessons[current.id].cues;
    renderVoiceTubeTranscript();
    renderVoiceTubeVocab();
  }
}).catch(err => {
  console.warn('Lessons fetch fallback:', err);
});

let ytPlayer = null;
let ytReady = false;
let syncTimer = null;
let activeCueIdx = -1;
let repeatCueMode = false;
let autoScrollEnabled = true;
let currentSubMode = 'both';
let currentPlaybackRate = 1.0;
let subtitleBaseSize = 23;
let likedVideos = new Set(JSON.parse(localStorage.getItem('et_liked') || '[]'));

let lastVideoTime = 0;
let lastTimeReceivedAt = performance.now();
let isPlaying = false;

// YouTube Iframe API ready callback
window.onYouTubeIframeAPIReady = function() {
  ytReady = true;
  console.log('[VoiceTube] YouTube Iframe API Ready');
};

// Native postMessage listener for YouTube iframe events
window.addEventListener('message', function(e) {
  if (!e || typeof e.data !== 'string') return;
  try {
    const msg = JSON.parse(e.data);
    if (msg.event === 'infoDelivery' && msg.info) {
      if (typeof msg.info.currentTime === 'number') {
        lastVideoTime = msg.info.currentTime;
        lastTimeReceivedAt = performance.now();
      }
      if (msg.info.playerState === 1) isPlaying = true;
      if (msg.info.playerState === 2) isPlaying = false;
    }
  } catch(err) {}
});

function initOrLoadPlayer(videoId) {
  const container = document.getElementById('playerContainer');
  if (!container) return;
  
  if (!window.YT || !window.YT.Player) {
    container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#a0a0c0;font-size:14px">載入 YouTube 播放器與即時字幕引擎中…</div>';
    let attempts = 0;
    const waitTimer = setInterval(() => {
      attempts++;
      if (window.YT && window.YT.Player) {
        clearInterval(waitTimer);
        createYTPlayer(videoId);
      } else if (attempts > 50) {
        clearInterval(waitTimer);
        createYTPlayer(videoId);
      }
    }, 60);
    return;
  }

  createYTPlayer(videoId);
}

function createYTPlayer(videoId) {
  const container = document.getElementById('playerContainer');
  if (!container) return;
  
  if (ytPlayer && typeof ytPlayer.loadVideoById === 'function') {
    try {
      ytPlayer.loadVideoById(videoId);
      startContinuousSync();
      return;
    } catch(e) {
      console.warn('Player reload fallback', e);
    }
  }

  container.innerHTML = '';
  const playerDiv = document.createElement('div');
  playerDiv.id = 'ytPlayerInstance';
  container.appendChild(playerDiv);

  try {
    ytPlayer = new YT.Player('ytPlayerInstance', {
      videoId: videoId,
      playerVars: {
        autoplay: 1,
        playsinline: 1,
        rel: 0,
        modestbranding: 1,
        enablejsapi: 1,
        origin: window.location.origin
      },
      events: {
        onReady: function(event) {
          event.target.playVideo();
          isPlaying = true;
          startContinuousSync();
        },
        onStateChange: function(event) {
          if (event.data === 1) { // PLAYING
            isPlaying = true;
            startContinuousSync();
          } else if (event.data === 2) { // PAUSED
            isPlaying = false;
          }
        }
      }
    });
  } catch(e) {
    container.innerHTML = `<iframe id="fallbackIframe" src="https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&enablejsapi=1&rel=0&origin=${encodeURIComponent(window.location.origin)}" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="width:100%;height:100%;border:0"></iframe>`;
  }

  startContinuousSync();
}

function startContinuousSync() {
  if (syncTimer) clearInterval(syncTimer);
  // High-frequency 30ms (approx 30 FPS) ticker for smooth word sweep
  syncTimer = setInterval(syncSubtitleAndWords, 30);
}

function stopSubtitleSync() {
  if (syncTimer) {
    clearInterval(syncTimer);
    syncTimer = null;
  }
}

function getExactPlaybackTime() {
  let t = null;
  if (ytPlayer && typeof ytPlayer.getCurrentTime === 'function') {
    try { t = ytPlayer.getCurrentTime(); } catch(e) {}
  }
  if (t != null && !isNaN(t) && t > 0) {
    lastVideoTime = t;
    lastTimeReceivedAt = performance.now();
    return t;
  }
  // Smooth real-time time interpolation between update ticks
  if (isPlaying) {
    const dt = (performance.now() - lastTimeReceivedAt) / 1000;
    return lastVideoTime + (dt * currentPlaybackRate);
  }
  return lastVideoTime;
}

function syncSubtitleAndWords() {
  const modal = document.getElementById('modal');
  if (!modal || !modal.classList.contains('open')) return;

  const time = getExactPlaybackTime();
  const cues = current?.cues || [];
  if (!cues.length) return;

  // 1. Single sentence repeat loop mode
  if (repeatCueMode && activeCueIdx >= 0 && activeCueIdx < cues.length) {
    const cur = cues[activeCueIdx];
    const dur = cur.duration > 0 ? cur.duration : 4.0;
    if (time >= cur.start + dur - 0.1) {
      seekCue(activeCueIdx);
      return;
    }
  }

  // 2. Find matching sentence cue
  let matchIdx = -1;
  for (let i = 0; i < cues.length; i++) {
    const c = cues[i];
    const dur = c.duration > 0 ? c.duration : (cues[i+1] ? Math.max(0.5, cues[i+1].start - c.start) : 5);
    if (time >= c.start && time < c.start + dur) {
      matchIdx = i;
      break;
    }
  }

  if (matchIdx !== -1) {
    if (matchIdx !== activeCueIdx) {
      highlightVoiceTubeCue(matchIdx);
    }
    // 3. 字幕隨影片聲音逐字連動反白移動
    updateKaraokeWordHighlight(time, cues[matchIdx]);
  }
}

function highlightVoiceTubeCue(idx) {
  activeCueIdx = idx;
  const cue = current?.cues?.[idx];
  if (!cue) return;

  // 1. Update VoiceTube Subtitle Stage
  const enStage = document.getElementById('vtActiveEn');
  const zhStage = document.getElementById('vtActiveZh');
  
  if (enStage) {
    if (currentSubMode === 'zh' || currentSubMode === 'none') {
      enStage.style.display = 'none';
    } else {
      enStage.style.display = 'flex';
      enStage.innerHTML = tokenizeWords(cue.en || cue.text || '');
    }
  }

  if (zhStage) {
    if (currentSubMode === 'en' || currentSubMode === 'none') {
      zhStage.style.display = 'none';
    } else {
      zhStage.style.display = 'block';
      zhStage.textContent = cue.zh || current.cn?.[idx] || '';
    }}

  // 2. Highlight row in Right Transcript List
  const rows = document.querySelectorAll('.vt-cue-row');
  rows.forEach((row, i) => {
    row.classList.toggle('active', i === idx);
  });

  // 3. Smooth auto-scroll
  if (autoScrollEnabled) {
    const activeRow = document.querySelector('.vt-cue-row.active');
    if (activeRow) {
      activeRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  // Update recording practice target
  const practiceTarget = document.getElementById('practiceSentenceTarget');
  if (practiceTarget) practiceTarget.textContent = cue.en || cue.text || '';
}

// ── 逐字連動 HIGHLIGHT 核心實作 ──
function updateKaraokeWordHighlight(time, cue) {
  const words = document.querySelectorAll('#vtActiveEn .vt-word-token');
  if (!words.length) return;

  const start = cue.start;
  const dur = Math.max(0.5, cue.duration > 0 ? cue.duration : 4.0);
  const elapsed = Math.max(0, time - start);
  const ratio = Math.min(0.999, elapsed / dur);

  // Character weight calculation for natural speaking cadence
  let totalChars = 0;
  const charWeights = [];
  words.forEach(w => {
    const len = parseInt(w.getAttribute('data-len') || '3', 10);
    charWeights.push(len);
    totalChars += len;
  });

  const targetPos = ratio * totalChars;
  let accumulated = 0;
  let activeWIdx = 0;
  for (let i = 0; i < charWeights.length; i++) {
    accumulated += charWeights[i];
    if (accumulated >= targetPos) {
      activeWIdx = i;
      break;
    }
  }

  // 1. Update left subtitle stage words
  words.forEach((w, i) => {
    if (i < activeWIdx) {
      if (w.className !== 'vt-word-token passed') w.className = 'vt-word-token passed';
    } else if (i === activeWIdx) {
      if (w.className !== 'vt-word-token current') w.className = 'vt-word-token current';
    } else {
      if (w.className !== 'vt-word-token future') w.className = 'vt-word-token future';
    }
  });

  // 2. Also update right transcript active row words
  const activeRowEn = document.querySelector('.vt-cue-row.active .vt-cue-en');
  if (activeRowEn) {
    const miniWords = activeRowEn.querySelectorAll('.vt-mini-word');
    if (miniWords.length === words.length) {
      miniWords.forEach((mw, i) => {
        if (i < activeWIdx) {
          if (mw.className !== 'vt-mini-word passed') mw.className = 'vt-mini-word passed';
        } else if (i === activeWIdx) {
          if (mw.className !== 'vt-mini-word current') mw.className = 'vt-mini-word current';
        } else {
          if (mw.className !== 'vt-mini-word future') mw.className = 'vt-mini-word future';
        }
      });
    }
  }
}

function tokenizeWords(sentence) {
  const parts = sentence.split(/(\\s+|[^\\w\\s'-]+)/);
  let wordCounter = 0;
  return parts.map(part => {
    if (/^[a-zA-Z0-9'-]{2,}$/.test(part)) {
      const clean = part.replace(/[^a-zA-Z]/g, '').toLowerCase();
      const idx = wordCounter++;
      return `<span class="vt-word-token future" data-word-idx="${idx}" data-len="${clean.length}" onclick="lookupWord('${clean}')">${escapeHTML(part)}</span>`;
    } else if (/^[a-zA-Z]$/.test(part)) {
      const clean = part.toLowerCase();
      const idx = wordCounter++;
      return `<span class="vt-word-token future" data-word-idx="${idx}" data-len="${clean.length}" onclick="lookupWord('${clean}')">${escapeHTML(part)}</span>`;
    } else {
      return `<span class="vt-punct">${escapeHTML(part)}</span>`;
    }
  }).join('');
}

function tokenizeMiniWords(sentence) {
  const parts = sentence.split(/(\\s+|[^\\w\\s'-]+)/);
  let wordCounter = 0;
  return parts.map(part => {
    if (/^[a-zA-Z0-9'-]+$/.test(part)) {
      return `<span class="vt-mini-word future" data-w="${wordCounter++}">${escapeHTML(part)}</span>`;
    } else {
      return escapeHTML(part);
    }
  }).join('');
}

function stepCue(delta) {
  if (!current?.cues?.length) return;
  let nextIdx = activeCueIdx + delta;
  if (nextIdx < 0) nextIdx = 0;
  if (nextIdx >= current.cues.length) nextIdx = current.cues.length - 1;
  seekCue(nextIdx);
}

function toggleRepeatCue() {
  repeatCueMode = !repeatCueMode;
  const btn = document.getElementById('vtRepeatBtn');
  if (btn) btn.classList.toggle('active', repeatCueMode);
  toast(repeatCueMode ? '🔁 已開啟單句重複跟讀' : '單句重複已關閉');
  if (repeatCueMode && activeCueIdx >= 0 && current?.cues?.[activeCueIdx]) {
    seekCue(activeCueIdx);
  }
}

function toggleAutoScroll() {
  autoScrollEnabled = !autoScrollEnabled;
  const btn = document.getElementById('autoScrollToggleBtn');
  if (btn) btn.textContent = '📜 自動捲動: ' + (autoScrollEnabled ? 'ON' : 'OFF');
  toast(autoScrollEnabled ? '自動捲動已開啟' : '自動捲動已暫停');
}

function setSubMode(mode) {
  currentSubMode = mode;
  ['both', 'en', 'zh', 'none'].forEach(m => {
    const b = document.getElementById('subMode' + m.charAt(0).toUpperCase() + m.slice(1));
    if (b) b.classList.toggle('active', m === mode);
  });
  if (activeCueIdx >= 0) highlightVoiceTubeCue(activeCueIdx);
  renderVoiceTubeTranscript();
}

function setPlayerSpeed(speed) {
  currentPlaybackRate = speed;
  [0.75, 1.0, 1.25].forEach(s => {
    const b = document.getElementById('speed' + String(s).replace('.', ''));
    if (b) b.classList.toggle('active', s === speed);
  });
  if (ytPlayer && typeof ytPlayer.setPlaybackRate === 'function') {
    ytPlayer.setPlaybackRate(speed);
  }
  toast('播放速度：' + speed + '×');
}

function adjustSubtitleSize(delta) {
  subtitleBaseSize = Math.max(18, Math.min(32, subtitleBaseSize + delta * 2));
  const enStage = document.getElementById('vtActiveEn');
  if (enStage) enStage.style.fontSize = subtitleBaseSize + 'px';
}

function renderVoiceTubeTranscript() {
  const list = document.getElementById('vtTranscriptList');
  if (!list || !current?.cues) return;
  const cues = current.cues;
  list.innerHTML = cues.map((c, i) => `
    <div class="vt-cue-row ${i === activeCueIdx ? 'active' : ''}" onclick="seekCue(${i})">
      <span class="vt-cue-play-btn">▶</span>
      <div class="vt-cue-content">
        <span class="vt-cue-en" style="display:${currentSubMode === 'zh' ? 'none' : 'block'}">${tokenizeMiniWords(c.en || c.text || '')}</span>
        <span class="vt-cue-zh" style="display:${currentSubMode === 'en' || currentSubMode === 'none' ? 'none' : 'block'}">${escapeHTML(c.zh || current.cn?.[i] || '')}</span>
      </div>
      <span class="vt-cue-time">${formatTime(c.start)}</span>
    </div>
  `).join('');
}

function renderVoiceTubeVocab() {
  const list = document.getElementById('vtVocabList');
  const countEl = document.getElementById('lessonWordCount');
  if (!list) return;
  const vocabObj = PRELOADED_LESSONS.vocab || {};
  const keys = Object.keys(vocabObj);
  if (countEl) countEl.textContent = keys.length;
  
  list.innerHTML = keys.map(k => {
    const item = vocabObj[k];
    return `
      <div style="background:#11111f;border:1px solid #24243a;border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center">
        <div>
          <b style="color:#a49aff;font-size:15px">${k}</b> <small style="color:#777">${item.ipa || ''} ${item.pos || ''}</small>
          <div style="font-size:12px;color:#c0c0d8;margin-top:2px">${item.def || ''}</div>
        </div>
        <div style="display:flex;gap:4px">
          <button class="save" onclick="say('${k}')">🔊</button>
          <button class="save ${savedWords.has(k) ? 'saved' : ''}" onclick="toggleWord('${k}')">${savedWords.has(k) ? '✓' : '＋'}</button>
        </div>
      </div>
    `;
  }).join('');
}

function switchVtTab(tab) {
  ['dict', 'vocab', 'practice'].forEach(t => {
    const btn = document.getElementById('tab' + t.charAt(0).toUpperCase() + t.slice(1));
    const pane = document.getElementById('vtPane' + t.charAt(0).toUpperCase() + t.slice(1));
    if (btn) btn.classList.toggle('active', t === tab);
    if (pane) pane.style.display = t === tab ? 'block' : 'none';
  });
}

function lookupWord(word) {
  if (!word) return;
  switchVtTab('dict');
  const clean = word.toLowerCase().trim();
  const input = document.getElementById('dictInput');
  if (input) input.value = clean;
  
  const vocab = PRELOADED_LESSONS.vocab || {};
  const item = vocab[clean];
  const view = document.getElementById('vtWordView');
  if (!view) return;

  say(clean);

  if (item) {
    view.innerHTML = `
      <div class="vt-word-view">
        <div class="vt-word-main">
          <span class="vt-word-term">${clean}</span>
          <span class="vt-word-ipa">${item.ipa || ''}</span>
          <div class="vt-word-actions">
            <button class="save" onclick="say('${clean}')">🔊 發音</button>
            <button class="save ${savedWords.has(clean) ? 'saved' : ''}" onclick="toggleWord('${clean}')">${savedWords.has(clean) ? '✓ 已收藏' : '＋ 收藏'}</button>
          </div>
        </div>
        <div class="vt-word-pos">${item.pos || '單字'}</div>
        <div class="vt-word-def">${item.def || ''}</div>
        ${item.ex ? `<div class="vt-word-ex">例句：${item.ex}</div>` : ''}
      </div>
    `;
  } else {
    view.innerHTML = `
      <div class="vt-word-view">
        <div class="vt-word-main">
          <span class="vt-word-term">${clean}</span>
          <div class="vt-word-actions">
            <button class="save" onclick="say('${clean}')">🔊 發音</button>
            <button class="save ${savedWords.has(clean) ? 'saved' : ''}" onclick="toggleWord('${clean}')">${savedWords.has(clean) ? '✓ 已收藏' : '＋ 收藏'}</button>
          </div>
        </div>
        <div class="vt-word-pos">英文字彙</div>
        <div class="vt-word-def">點擊上方 🔊 按鈕聆聽真人發音，或點擊「＋ 收藏」加入個人專屬生字本。</div>
      </div>
    `;
  }
}

function lookupCustomWord() {
  const val = document.getElementById('dictInput')?.value.trim();
  if (val) lookupWord(val);
}

function toggleLike() {
  if (!current) return;
  const btn = document.getElementById('vtLikeBtn');
  const num = document.getElementById('vtLikes');
  if (likedVideos.has(current.id)) {
    likedVideos.delete(current.id);
    btn?.classList.remove('liked');
    if (num) num.textContent = parseInt(num.textContent || 225) - 1;
  } else {
    likedVideos.add(current.id);
    btn?.classList.add('liked');
    if (num) num.textContent = parseInt(num.textContent || 225) + 1;
    toast('👍 已按讚');
  }
  localStorage.setItem('et_liked', JSON.stringify([...likedVideos]));
}

function toggleSaveCurrent() {
  if (!current) return;
  toggleSave(current.id);
  const btn = document.getElementById('vtSaveBtn');
  if (btn) btn.classList.toggle('saved', saved.has(current.id));
}

function shareVideo() {
  if (navigator.share && current) {
    navigator.share({
      title: current.title,
      text: '來跟我一起在 ENGLISHTUBE 練習跟讀英文影片！',
      url: window.location.href
    }).catch(() => {});
  } else {
    navigator.clipboard?.writeText(window.location.href);
    toast('✓ 學習連結已複製到剪貼簿');
  }
}

// Upgraded openVideo with VoiceTube data
const _origOpenVideo = openVideo;
openVideo = function(id) {
  current = videos.find(v => v.id === id);
  if (!current) return;

  const lessonData = PRELOADED_LESSONS.lessons?.[id];
  if (lessonData && lessonData.cues && lessonData.cues.length) {
    current.cues = lessonData.cues;
    current.en = lessonData.cues.map(c => c.en);
    current.cn = lessonData.cues.map(c => c.zh);
  } else {
    current.cues = current.cues || [];
    current.en = current.en || [];
    current.cn = current.cn || [];
  }

  // Populate header info
  const titleEl = document.getElementById('modalTitle');
  if (titleEl) titleEl.textContent = current.title;
  const levelEl = document.getElementById('vtLevel');
  if (levelEl) levelEl.textContent = current.level + ' 程度';
  const viewsEl = document.getElementById('vtViews');
  if (viewsEl) viewsEl.textContent = current.views;

  const saveBtn = document.getElementById('vtSaveBtn');
  if (saveBtn) saveBtn.classList.toggle('saved', saved.has(current.id));
  const likeBtn = document.getElementById('vtLikeBtn');
  if (likeBtn) likeBtn.classList.toggle('liked', likedVideos.has(current.id));

  // Render Subtitles and Vocab
  renderVoiceTubeTranscript();
  renderVoiceTubeVocab();

  // Reset subtitle stage
  activeCueIdx = 0;
  highlightVoiceTubeCue(0);

  // Mount YouTube Player
  initOrLoadPlayer(current.id);

  document.getElementById('modal').classList.add('open');
  document.body.style.overflow = 'hidden';
};

// Override seekCue to use YouTube Iframe API
seekCue = function(i) {
  const cue = current?.cues?.[i];
  if (!cue) return;
  highlightVoiceTubeCue(i);
  lastVideoTime = cue.start;
  lastTimeReceivedAt = performance.now();
  if (ytPlayer && typeof ytPlayer.seekTo === 'function') {
    ytPlayer.seekTo(cue.start, true);
    ytPlayer.playVideo();
    isPlaying = true;
  } else {
    const frame = document.querySelector('#playerContainer iframe');
    if (frame && frame.contentWindow) {
      frame.contentWindow.postMessage(JSON.stringify({event:'command',func:'seekTo',args:[cue.start,true]}),'*');
      frame.contentWindow.postMessage(JSON.stringify({event:'command',func:'playVideo',args:[]}),'*');
      isPlaying = true;
    }
  }
};

// Override closeModal to pause video
const _origCloseModal = closeModal;
closeModal = function() {
  stopSubtitleSync();
  isPlaying = false;
  if (ytPlayer && typeof ytPlayer.pauseVideo === 'function') {
    try { ytPlayer.pauseVideo(); } catch(e) {}
  }
  _origCloseModal();
};
"""

# Append VoiceTube script right before closing </script>
html = html.replace('</script></body>', vt_script + '\n</script></body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html completely rebuilt with 50 full videos and reliable karaoke word highlight engine!")
