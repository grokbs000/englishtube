#!/usr/bin/env python3
"""
batch_fix_youtube_creator_videos.py

Automated repair pipeline for all EnglishTube videos with synthetic/dummy subtitles:
1. Identifies all video entries labeled 'YouTube Creator' or containing dummy template cues.
2. Extracts authentic YouTube metadata (real channel/uploader, official video title, exact duration, views).
3. Downloads genuine English subtitles using yt-dlp android client (prevents 429 rate-limiting).
4. Cleans VTT cues, merges line fragments into natural sentence units (3-7s), and deduplicates auto-sub scrolling lines.
5. Translates English cues to natural Taiwan Traditional Chinese (zh-TW) with OpenCC s2twp.
6. Synchronizes across video_lessons.json, video_lessons.js, and index.html.
7. Maintains persistent progress cache in .video_fix_cache/ to allow safe resume at any time.
"""

import os, sys, json, re, time, glob, subprocess, urllib.parse
import opencc

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(ROOT, '.video_fix_cache')
os.makedirs(CACHE_DIR, exist_ok=True)

LESSONS_JSON_PATH = os.path.join(ROOT, 'video_lessons.json')
LESSONS_JS_PATH = os.path.join(ROOT, 'video_lessons.js')
INDEX_HTML_PATH = os.path.join(ROOT, 'index.html')
SW_JS_PATH = os.path.join(ROOT, 'sw.js')

cc = opencc.OpenCC('s2twp')

# 1. Translation Cache
trans_cache_file = os.path.join(CACHE_DIR, 'translation_cache.json')
trans_cache = {}
if os.path.exists(trans_cache_file):
    try:
        with open(trans_cache_file, 'r', encoding='utf-8') as f:
            trans_cache = json.load(f)
    except Exception:
        trans_cache = {}

def save_trans_cache():
    with open(trans_cache_file, 'w', encoding='utf-8') as f:
        json.dump(trans_cache, f, ensure_ascii=False)

def translate_zh(text):
    clean_k = text.strip().lower()
    if clean_k in trans_cache:
        return trans_cache[clean_k]
    try:
        q = urllib.parse.quote(text)
        cmd = ["curl", "-s", f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-TW&dt=t&q={q}"]
        out = subprocess.check_output(cmd, timeout=6).decode("utf-8")
        data = json.loads(out)
        trans = "".join([part[0] for part in data[0] if part[0]])
        tw = cc.convert(trans).strip()
        trans_cache[clean_k] = tw
        return tw
    except Exception:
        return ""

def parse_vtt(vtt_file):
    with open(vtt_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    time_pat = re.compile(r"(\d{2}:)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}:)?(\d{2}):(\d{2})\.(\d{3})")
    def to_secs(h, m, s, ms):
        hours = int(h[:-1]) if h else 0
        return hours * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

    raw_items = []
    i = 0
    last_text = ""
    while i < len(lines):
        line = lines[i].strip()
        m = time_pat.search(line)
        if m:
            start = to_secs(m.group(1), m.group(2), m.group(3), m.group(4))
            end = to_secs(m.group(5), m.group(6), m.group(7), m.group(8))
            text_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() and not time_pat.search(lines[i]):
                t = lines[i].strip()
                t = re.sub(r"<[^>]+>", "", t)
                t = re.sub(r"&nbsp;", " ", t)
                t = " ".join(t.split())
                if t and t not in text_lines:
                    text_lines.append(t)
                i += 1
            
            # YouTube auto-caption scrolling deduplication
            if len(text_lines) == 2 and text_lines[0] in last_text:
                txt = text_lines[1]
            else:
                txt = " ".join(text_lines)
            
            # Remove duplicate adjacent words
            words = txt.split()
            dedup = []
            for w in words:
                if not dedup or w.lower() != dedup[-1].lower():
                    dedup.append(w)
            txt = " ".join(dedup).strip()

            if txt and not txt.startswith("WEBVTT") and not txt.startswith("Kind:") and not txt.startswith("Language:"):
                raw_items.append((start, end, txt))
                last_text = txt
        else:
            i += 1

    # Merge into sentence cues
    cues = []
    curr_start = None
    curr_end = None
    curr_words = []

    for st, en, txt in raw_items:
        if curr_start is None:
            curr_start = st
        curr_end = en
        curr_words.append(txt)
        
        joined = " ".join(curr_words)
        dur = curr_end - curr_start
        is_punct = txt.endswith(".") or txt.endswith("?") or txt.endswith("!")
        is_long = dur >= 4.0 and len(joined.split()) >= 8
        if is_punct or is_long or dur >= 6.5:
            clean_text = " ".join(joined.split())
            cues.append({
                "start": round(curr_start, 2),
                "duration": round(curr_end - curr_start, 2),
                "text": clean_text,
                "en": clean_text,
                "zh": ""
            })
            curr_start = None
            curr_end = None
            curr_words = []

    if curr_words:
        clean_text = " ".join(" ".join(curr_words).split())
        cues.append({
            "start": round(curr_start, 2),
            "duration": round(curr_end - curr_start, 2),
            "text": clean_text,
            "en": clean_text,
            "zh": ""
        })
    return cues

def fix_single_video(vid, existing_entry=None):
    cache_path = os.path.join(CACHE_DIR, f"{vid}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    print(f"\n--- Processing Video: {vid} ---")
    # 1. Fetch metadata
    meta = None
    for attempt in range(2):
        try:
            cmd = ["yt-dlp", "--dump-json", f"https://www.youtube.com/watch?v={vid}"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if res.returncode == 0 and res.stdout:
                meta = json.loads(res.stdout)
                break
        except Exception as e:
            print(f"Meta attempt {attempt+1} failed: {e}")
            time.sleep(1)

    if not meta:
        print(f"Could not retrieve YouTube metadata for {vid}")
        return None

    real_title = meta.get("title")
    real_channel = meta.get("uploader") or meta.get("channel") or "TED-Ed"
    duration_secs = meta.get("duration", 0)
    dur_m = duration_secs // 60
    dur_s = duration_secs % 60
    real_duration = f"{dur_m:02d}:{dur_s:02d}"
    view_count = meta.get("view_count", 0)
    views_str = f"{view_count/1000000:.1f}M" if view_count >= 1000000 else f"{view_count//1000}K"

    # 2. Download subtitles
    sub_prefix = os.path.join(CACHE_DIR, f"sub_{vid}")
    cmd = [
        "yt-dlp", "--extractor-args", "youtube:player_client=android",
        "--skip-download", "--write-sub", "--write-auto-sub",
        "--sub-lang", "en,en-orig", "--sub-format", "vtt",
        "-o", f"{sub_prefix}.%(ext)s",
        f"https://www.youtube.com/watch?v={vid}"
    ]
    subprocess.run(cmd, capture_output=True, timeout=20)
    sub_files = glob.glob(f"{sub_prefix}*.vtt")
    if not sub_files:
        print(f"No subtitle file found for {vid}")
        return None

    # Priority to manual en, then en-orig
    sub_files.sort(key=lambda x: (not x.endswith('.en.vtt'), x))
    cues = parse_vtt(sub_files[0])
    for sf in sub_files:
        try: os.remove(sf)
        except Exception: pass

    if not cues:
        print(f"Parsed 0 cues for {vid}")
        return None

    print(f"Parsed {len(cues)} cues for {vid} ({real_title[:35]} | {real_channel} | {real_duration})")

    # 3. Translate cues
    for idx, c in enumerate(cues):
        c["zh"] = translate_zh(c["en"])
        if (idx + 1) % 40 == 0:
            print(f"  Translated {idx+1}/{len(cues)} cues...")
            save_trans_cache()
            time.sleep(0.1)

    save_trans_cache()

    # Generate Traditional Chinese Title
    zh_title_prefix = f"【{real_channel}】"
    zh_title_content = translate_zh(real_title)
    full_zh_title = f"{zh_title_prefix}{zh_title_content}（精選雙語跟讀教材）"

    result = {
        "id": vid,
        "title": real_title,
        "speaker": real_channel,
        "duration": real_duration,
        "views": views_str,
        "zh": full_zh_title,
        "cues": cues
    }

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result

def main(batch_limit=None):
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    start_idx = html.find("const videos = [")
    end_idx = html.find("const songs = [")
    videos = json.loads(html[start_idx + len("const videos = "):end_idx].strip().rstrip(";"))

    with open(LESSONS_JSON_PATH, "r", encoding="utf-8") as f:
        vld = json.load(f)
    lessons = vld.get("lessons", {})

    target_vids = []
    for v in videos:
        vid = v.get("id")
        speaker = v.get("speaker")
        cues = v.get("cues", [])
        text_sample = " ".join([c.get("text", "") or c.get("en", "") for c in cues])
        if speaker == "YouTube Creator" or "Welcome back to our exploration of" in text_sample:
            target_vids.append((vid, v))

    print(f"Total videos identified with dummy subtitles: {len(target_vids)}")
    if batch_limit:
        target_vids = target_vids[:batch_limit]
        print(f"Processing batch of {len(target_vids)} videos...")

    fixed_count = 0
    failed_count = 0

    for idx, (vid, v_entry) in enumerate(target_vids):
        print(f"\n[{idx+1}/{len(target_vids)}] Starting {vid} - {v_entry.get('title')}")
        fixed = fix_single_video(vid, v_entry)
        if fixed and fixed.get("cues"):
            # Update in memory
            v_entry["title"] = fixed["title"]
            v_entry["speaker"] = fixed["speaker"]
            v_entry["duration"] = fixed["duration"]
            v_entry["views"] = fixed["views"]
            v_entry["zh"] = fixed["zh"]
            v_entry["cues"] = fixed["cues"]

            lessons[vid] = {
                "id": vid,
                "title": fixed["title"],
                "speaker": fixed["speaker"],
                "channel": v_entry.get("channel", "Science & Technology"),
                "level": v_entry.get("level", "B2"),
                "duration": fixed["duration"],
                "views": fixed["views"],
                "emoji": v_entry.get("emoji", "🎬"),
                "color": v_entry.get("color", "linear-gradient(135deg, #a1c4fd, #c2e9fb)"),
                "zh": fixed["zh"],
                "url": f"https://www.youtube.com/watch?v={vid}",
                "cues": fixed["cues"],
                "words": []
            }
            fixed_count += 1
        else:
            failed_count += 1

        # Periodic save every 5 videos
        if (idx + 1) % 5 == 0 or idx == len(target_vids) - 1:
            print(f"\n>>> Saving progress ({fixed_count} fixed, {failed_count} skipped)...")
            # 1. Update video_lessons.json
            vld["lessons"] = lessons
            with open(LESSONS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(vld, f, ensure_ascii=False, separators=(",", ":"))

            # 2. Update video_lessons.js
            with open(LESSONS_JS_PATH, "w", encoding="utf-8") as f:
                f.write("window.ENGLISHTUBE_DATA=" + json.dumps(vld, ensure_ascii=False, separators=(",", ":")) + ";\n")

            # 3. Update index.html
            new_videos_str = json.dumps(videos, ensure_ascii=False, indent=2)
            new_html = html[:start_idx + len("const videos = ")] + new_videos_str + ";\n" + html[end_idx:]
            with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
                f.write(new_html)

            # Bump SW
            with open(SW_JS_PATH, "r", encoding="utf-8") as sf:
                sw_text = sf.read()
            m = re.search(r"englishtube-v(\d+)", sw_text)
            if m:
                curr_v = int(m.group(1))
                new_sw = sw_text.replace(f"englishtube-v{curr_v}", f"englishtube-v{curr_v+1}")
                with open(SW_JS_PATH, "w", encoding="utf-8") as sf:
                    sf.write(new_sw)

        time.sleep(0.5)

    print(f"\n=== Batch Complete: {fixed_count} fixed, {failed_count} failed ===")

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit)
