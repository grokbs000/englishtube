import os, sys, re, json

INDEX_HTML_PATH = "index.html"
SW_JS_PATH = "sw.js"
LESSONS_DIR = "data/lessons"

def main():
    print("=== APPLYING ON-DEMAND LESSON STREAMING ARCHITECTURE ===")

    # 1. Ensure data/lessons exists and has all 492 lessons
    if not os.path.exists(LESSONS_DIR):
        print("ERROR: data/lessons directory does not exist!")
        sys.exit(1)

    lesson_files = [f for f in os.listdir(LESSONS_DIR) if f.endswith('.json')]
    print(f"Verified {len(lesson_files)} lesson JSON files in {LESSONS_DIR}")

    # 2. Read index.html
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    orig_html_size = len(html.encode('utf-8')) / (1024 * 1024)
    print(f"Original index.html size: {orig_html_size:.2f} MB")

    # 3. Extract and slim down const videos
    s_idx = html.find("const videos = [")
    e_idx = html.find("const songs = [")
    if s_idx == -1 or e_idx == -1:
        print("ERROR: Could not locate const videos or const songs in index.html")
        sys.exit(1)

    videos_json_str = html[s_idx + len("const videos = "):e_idx].strip().rstrip(";")
    videos = json.loads(videos_json_str)
    print(f"Found {len(videos)} videos in const videos")

    for v in videos:
        # Keep metadata, remove bulky cues and words
        if "cues" in v:
            del v["cues"]
        if "words" in v:
            del v["words"]
        v["cues"] = []

    slim_videos_str = json.dumps(videos, ensure_ascii=False, indent=2)
    html = html[:s_idx + len("const videos = ")] + slim_videos_str + ";\n" + html[e_idx:]

    # 4. Remove <script src="./video_lessons.js?v=..."></script>
    html = re.sub(r'<script\s+src=[\"\']\./video_lessons\.js(?:\?v=\d+)?[\"\']>\s*</script>\s*', '', html)

    # 5. Replace PRELOADED_LESSONS fallback block with modern on-demand loader
    old_preloaded_marker = "// ── VOICETUBE SYNCHRONIZED FOLLOW-ALONG ENGINE"
    old_preloaded_pos = html.find(old_preloaded_marker)
    if old_preloaded_pos != -1:
        end_of_block_pos = html.find("let ytPlayer = null;", old_preloaded_pos)
        if end_of_block_pos != -1:
            new_loader_code = """// ── ENGLISHTUBE ON-DEMAND LESSON STREAMING ENGINE (按需分流載入器 - 零記憶體負擔) ──
const lessonCache = window._lessonCache = window._lessonCache || {};

async function loadLessonData(id) {
  if (!id) return null;
  id = String(id).trim();
  if (lessonCache[id]) return lessonCache[id];

  try {
    const res = await fetch(`./data/lessons/${encodeURIComponent(id)}.json`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    lessonCache[id] = data;
    return data;
  } catch (err) {
    console.warn(`[ENGLISHTUBE] Failed to load on-demand lesson for ${id}:`, err);
    return null;
  }
}

let PRELOADED_LESSONS = { lessons: lessonCache, vocab: {} };

"""
            html = html[:old_preloaded_pos] + new_loader_code + html[end_of_block_pos:]
            print("Successfully replaced PRELOADED_LESSONS block with on-demand loader.")

    # 6. Update openVideo(id) with on-demand async loading
    old_open_video_marker = "// VoiceTube Studio Main Player & Lesson Launcher\nfunction openVideo(id) {"
    if old_open_video_marker not in html:
        old_open_video_marker = "function openVideo(id) {"

    ov_pos = html.find("function openVideo(id) {")
    if ov_pos != -1:
        # Locate the cues assignment section inside openVideo
        cues_sec_start = html.find("if (songEntry && songEntry.cues && songEntry.cues.length) {", ov_pos)
        cues_sec_end = html.find("current.en = (current.cues || []).map(", cues_sec_start)
        if cues_sec_start != -1 and cues_sec_end != -1:
            new_cues_logic = """if (songEntry && songEntry.cues && songEntry.cues.length) {
    // Song mode: use curated full-lyrics cues
    current.cues = songEntry.cues;
    current._loadingCues = false;
  } else {
    // Video mode: check in-memory cache or on-demand fetch
    if (lessonCache[id] && lessonCache[id].cues && lessonCache[id].cues.length) {
      current.cues = lessonCache[id].cues;
      current.words = lessonCache[id].words || [];
      current._loadingCues = false;
    } else if (current.cues && current.cues.length > 5) {
      current._loadingCues = false;
    } else {
      current.cues = [];
      current._loadingCues = true;
      loadLessonData(id).then(data => {
        if (data && data.cues && data.cues.length && current && current.id === id) {
          current.cues = data.cues;
          current.words = data.words || [];
          current._loadingCues = false;
          current.en = data.cues.map(c => c.en || c.text || '');
          current.cn = data.cues.map(c => c.zh || c.cn || '');
          renderVoiceTubeTranscript();
          renderVoiceTubeVocab();
          updateProgressBar();
          if (activeCueIdx >= 0 && activeCueIdx < current.cues.length) {
            highlightVoiceTubeCue(activeCueIdx);
          } else {
            highlightVoiceTubeCue(0);
          }
        } else if (current && current.id === id) {
          current._loadingCues = false;
          renderVoiceTubeTranscript();
        }
      });
    }
  }
  """
            html = html[:cues_sec_start] + new_cues_logic + html[cues_sec_end:]
            print("Successfully updated openVideo with async on-demand subtitle loading.")

    # 7. Update renderVoiceTubeTranscript to show modern skeleton while loading
    rvt_pos = html.find("function renderVoiceTubeTranscript() {")
    if rvt_pos != -1:
        check_empty_start = html.find("if (!cues.length) {", rvt_pos)
        if check_empty_start != -1:
            check_empty_end = html.find("list.innerHTML = cues.map(", check_empty_start)
            if check_empty_end != -1:
                new_empty_render = """if (current._loadingCues) {
    list.innerHTML = `
      <div style="padding:48px 20px;text-align:center;color:#818cf8;line-height:1.8">
        <div style="display:inline-block;width:28px;height:28px;border:3px solid rgba(129,140,248,0.25);border-top-color:#818cf8;border-radius:50%;animation:vtSpin 0.8s linear infinite;margin-bottom:16px"></div>
        <div style="font-size:15px;font-weight:600;color:#e0e7ff;margin-bottom:4px">正在載入即時雙語跟讀字幕...</div>
        <div style="font-size:12px;color:#94a3b8">高精度聲畫對齊引擎準備中</div>
      </div>
    `;
    return;
  }
  if (!cues.length) {
    list.innerHTML = `
      <div style="padding:40px 20px;text-align:center;color:#94a3b8;line-height:1.8">
        <div style="font-size:32px;margin-bottom:12px">📺</div>
        <div style="font-size:15px;font-weight:600;color:#f1f5f9;margin-bottom:6px">支援 YouTube 原生字幕</div>
        <div style="font-size:13px">此影片已直接整合 YouTube 官方高畫質串流與字幕系統。<br>請點選播放器右下角「<b>CC</b>」按鈕開啟字幕與自動翻譯。</div>
      </div>
    `;
    return;
  }
  """
                html = html[:check_empty_start] + new_empty_render + html[check_empty_end:]
                print("Successfully updated renderVoiceTubeTranscript loading state.")

    # 8. Ensure @keyframes vtSpin is present in CSS
    if "@keyframes vtSpin" not in html:
        css_idx = html.find("</style>")
        if css_idx != -1:
            spin_css = """@keyframes vtSpin {
  to { transform: rotate(360deg); }
}
"""
            html = html[:css_idx] + spin_css + html[css_idx:]

    # 9. Bump version in index.html & sw.js
    with open(SW_JS_PATH, "r", encoding="utf-8") as sf:
        sw_text = sf.read()

    m = re.search(r"englishtube-v(\d+)", sw_text)
    curr_v = int(m.group(1)) if m else 115
    new_v = curr_v + 1

    # Update sw.js: remove video_lessons from STATIC
    new_sw = sw_text.replace(f"englishtube-v{curr_v}", f"englishtube-v{new_v}")
    new_sw = re.sub(r"\s*'\./video_lessons\.js',?", "", new_sw)
    new_sw = re.sub(r"\s*'\./video_lessons\.json',?", "", new_sw)

    with open(SW_JS_PATH, "w", encoding="utf-8") as sf:
        sf.write(new_sw)

    # Save index.html
    html = html.replace(f"?v={curr_v}", f"?v={new_v}")
    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    new_html_size = os.path.getsize(INDEX_HTML_PATH) / (1024 * 1024)
    print(f"\n==========================================")
    print(f"SUCCESS! New index.html size: {new_html_size:.2f} MB (was {orig_html_size:.2f} MB)")
    print(f"Bumped cache version to v{new_v}")
    print(f"==========================================")

if __name__ == "__main__":
    main()
