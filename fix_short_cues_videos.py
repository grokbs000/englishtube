#!/usr/bin/env python3
"""
fix_short_cues_videos.py

Comprehensive repair pipeline for all EnglishTube videos with < 20 cues:
1. Scans `index.html` (const videos) and `video_lessons.json` for all videos where cue count < 20.
2. Sorts target videos by fewest cues first (2, 3, 4, 5 cues prioritized immediately).
3. Fetches authentic YouTube metadata (real channel/uploader, official video title, exact duration, views).
4. Downloads genuine English subtitles (`en,en-US,en-GB,en-orig`) and official Chinese subtitles (`zh-TW,zh-Hant`) via yt-dlp.
5. Falls back to local faster-whisper transcription if no subtitles exist on YouTube.
6. Cleans VTT cues, merges line fragments into natural 3~7s units for shadowing and listening practice.
7. Ultra-fast batch translation to Taiwan Traditional Chinese (zh-TW) with OpenCC s2twp.
8. Generates informative, natural titles (e.g. 【Channel】Title（精選雙語跟讀教材）).
9. Synchronizes across index.html, video_lessons.json, and video_lessons.js.
10. Automatically increments Service Worker cache version in sw.js and index.html.
"""

import os, sys, json, re, time, glob, subprocess, urllib.parse, urllib.request
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
    try:
        with open(trans_cache_file, 'w', encoding='utf-8') as f:
            json.dump(trans_cache, f, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving trans cache: {e}")

def translate_single(text):
    if not text or not text.strip():
        return ""
    clean_k = text.strip().lower()
    if clean_k in trans_cache:
        return trans_cache[clean_k]
    try:
        q = urllib.parse.quote(text.strip())
        url = f"https://translate.googleapis.com/translate_a/single?client=dict-chrome-ex&sl=en&tl=zh-TW&dt=t&q={q}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            trans = ''.join([part[0] for part in data[0] if part[0]])
            tw = cc.convert(trans).strip()
            if tw:
                trans_cache[clean_k] = tw
                return tw
    except Exception:
        pass
    return ""

def batch_translate_cues(cues):
    needed_indices = []
    needed_texts = []
    for i, c in enumerate(cues):
        if not c.get("zh"):
            clean_k = c["en"].strip().lower()
            if clean_k in trans_cache:
                c["zh"] = trans_cache[clean_k]
            else:
                needed_indices.append(i)
                needed_texts.append(c["en"].strip())

    if not needed_texts:
        return

    CHUNK_SIZE = 25
    for start_idx in range(0, len(needed_texts), CHUNK_SIZE):
        chunk_texts = needed_texts[start_idx:start_idx + CHUNK_SIZE]
        chunk_indices = needed_indices[start_idx:start_idx + CHUNK_SIZE]
        
        batch_text = "\n".join(chunk_texts)
        translated_lines = []
        try:
            q = urllib.parse.quote(batch_text)
            url = f"https://translate.googleapis.com/translate_a/single?client=dict-chrome-ex&sl=en&tl=zh-TW&dt=t&q={q}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as res:
                data = json.loads(res.read().decode('utf-8'))
                trans = ''.join([part[0] for part in data[0] if part[0]])
                translated_lines = [cc.convert(line).strip() for line in trans.split('\n')]
        except Exception:
            translated_lines = []

        if len(translated_lines) == len(chunk_texts):
            for orig, tr, c_idx in zip(chunk_texts, translated_lines, chunk_indices):
                clean_k = orig.strip().lower()
                trans_cache[clean_k] = tr
                cues[c_idx]["zh"] = tr
        else:
            for orig, c_idx in zip(chunk_texts, chunk_indices):
                tr = translate_single(orig)
                cues[c_idx]["zh"] = tr
        
        time.sleep(0.04)
    
    save_trans_cache()

def clean_sub_text(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'^[\s\-\–\—:]+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = ' '.join(text.split())
    return text.strip()

def parse_vtt(vtt_file):
    with open(vtt_file, "r", encoding="utf-8", errors="ignore") as f:
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
                t = clean_sub_text(lines[i])
                if t and t not in text_lines:
                    text_lines.append(t)
                i += 1
            
            if len(text_lines) == 2 and text_lines[0] in last_text:
                txt = text_lines[1]
            else:
                txt = " ".join(text_lines)
            
            txt = clean_sub_text(txt)
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
        is_long = dur >= 3.5 and len(joined.split()) >= 8
        if is_punct or is_long or dur >= 6.5:
            clean_text = clean_sub_text(joined)
            if clean_text:
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
        clean_text = clean_sub_text(" ".join(curr_words))
        if clean_text:
            cues.append({
                "start": round(curr_start, 2),
                "duration": round(curr_end - curr_start, 2),
                "text": clean_text,
                "en": clean_text,
                "zh": ""
            })
    return cues

def parse_zh_vtt(vtt_file):
    with open(vtt_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    time_pat = re.compile(r"(\d{2}:)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}:)?(\d{2}):(\d{2})\.(\d{3})")
    def to_secs(h, m, s, ms):
        hours = int(h[:-1]) if h else 0
        return hours * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

    zh_items = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = time_pat.search(line)
        if m:
            start = to_secs(m.group(1), m.group(2), m.group(3), m.group(4))
            end = to_secs(m.group(5), m.group(6), m.group(7), m.group(8))
            text_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() and not time_pat.search(lines[i]):
                t = clean_sub_text(lines[i])
                if t and not t.startswith("譯者:") and not t.startswith("審譯者:"):
                    text_lines.append(t)
                i += 1
            txt = " ".join(text_lines).strip()
            if txt:
                zh_items.append((start, end, cc.convert(txt)))
        else:
            i += 1
    return zh_items

def match_zh_to_cues(cues, zh_items):
    if not zh_items:
        return
    for c in cues:
        st = c["start"]
        en = st + c["duration"]
        matched_zh = []
        for z_st, z_en, z_txt in zh_items:
            if max(st, z_st) < min(en, z_en):
                matched_zh.append(z_txt)
            elif abs(st - z_st) < 1.0:
                matched_zh.append(z_txt)
        if matched_zh:
            seen = set()
            filtered = []
            for t in matched_zh:
                if t not in seen:
                    seen.add(t)
                    filtered.append(t)
            c["zh"] = " ".join(filtered).strip()

def transcribe_whisper(vid):
    print(f"[{vid}] No YouTube subtitles. Falling back to faster-whisper...")
    audio_path = os.path.join(CACHE_DIR, f"{vid}.mp3")
    try:
        cmd = [
            "yt-dlp", "-x", "--audio-format", "mp3",
            "--audio-quality", "5",
            "-o", audio_path,
            f"https://www.youtube.com/watch?v={vid}"
        ]
        subprocess.run(cmd, capture_output=True, timeout=60)
        if not os.path.exists(audio_path):
            return []

        os.environ.pop('NO_PROXY', None)
        os.environ.pop('no_proxy', None)
        from faster_whisper import WhisperModel
        model = WhisperModel('small.en', device='cpu', compute_type='int8')
        segments, _ = model.transcribe(audio_path, beam_size=3, vad_filter=True)
        
        cues = []
        for seg in segments:
            txt = clean_sub_text(seg.text)
            if txt:
                dur = round(seg.end - seg.start, 2)
                if dur > 0.5:
                    cues.append({
                        "start": round(seg.start, 2),
                        "duration": dur,
                        "text": txt,
                        "en": txt,
                        "zh": ""
                    })
        return cues
    except Exception as e:
        print(f"[{vid}] Whisper error: {e}")
        return []
    finally:
        if os.path.exists(audio_path):
            try: os.remove(audio_path)
            except Exception: pass

def fix_single_video(vid, existing_entry=None):
    cache_path = os.path.join(CACHE_DIR, f"{vid}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if cached.get("cues") and len(cached["cues"]) >= 20:
                    print(f"[{vid}] Loaded from cache ({len(cached['cues'])} cues)")
                    return cached
        except Exception:
            pass

    # 1. Fetch metadata
    meta = None
    for attempt in range(2):
        try:
            cmd = ["yt-dlp", "--dump-json", f"https://www.youtube.com/watch?v={vid}"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=18)
            if res.returncode == 0 and res.stdout:
                meta = json.loads(res.stdout)
                break
        except Exception as e:
            time.sleep(1)

    if not meta:
        print(f"[{vid}] Could not retrieve YouTube metadata")
        return None

    real_title = meta.get("title") or (existing_entry.get("title") if existing_entry else "English Video")
    real_channel = meta.get("uploader") or meta.get("channel") or (existing_entry.get("speaker") if existing_entry else "EnglishTube")
    duration_secs = meta.get("duration", 0)
    dur_m = duration_secs // 60
    dur_s = duration_secs % 60
    real_duration = f"{dur_m:02d}:{dur_s:02d}"
    view_count = meta.get("view_count", 0)
    views_str = f"{view_count/1000000:.1f}M" if view_count >= 1000000 else (f"{view_count//1000}K" if view_count >= 1000 else f"{view_count}")

    # 2. Download subtitles (both EN and ZH)
    sub_prefix = os.path.join(CACHE_DIR, f"sub_{vid}")
    cmd = [
        "yt-dlp",
        "--skip-download", "--write-sub", "--write-auto-sub",
        "--sub-lang", "en.*,en,en-US,en-GB,en-orig,zh-TW,zh-Hant,zh.*",
        "--sub-format", "vtt",
        "--extractor-args", "youtube:player_client=android",
        "-o", f"{sub_prefix}.%(ext)s",
        f"https://www.youtube.com/watch?v={vid}"
    ]
    subprocess.run(cmd, capture_output=True, timeout=25)
    
    en_vtts = glob.glob(f"{sub_prefix}*.en*.vtt")
    zh_vtts = glob.glob(f"{sub_prefix}*.zh*.vtt")
    
    cues = []
    if en_vtts:
        en_vtts.sort(key=lambda x: (not x.endswith('.en.vtt') and not x.endswith('.en-US.vtt'), x))
        cues = parse_vtt(en_vtts[0])
    
    zh_items = []
    if zh_vtts:
        zh_items = parse_zh_vtt(zh_vtts[0])

    for vf in glob.glob(f"{sub_prefix}*.vtt"):
        try: os.remove(vf)
        except Exception: pass

    # If no cues found from VTT, fallback to Whisper
    if not cues or len(cues) < 8:
        cues_whisper = transcribe_whisper(vid)
        if cues_whisper and len(cues_whisper) > len(cues):
            cues = cues_whisper

    if not cues or len(cues) < 6:
        print(f"[{vid}] Failed to obtain adequate cues (only {len(cues)} found).")
        return None

    if zh_items:
        match_zh_to_cues(cues, zh_items)

    batch_translate_cues(cues)

    zh_title_prefix = f"【{real_channel}】"
    zh_title_content = translate_single(real_title)
    full_zh_title = f"{zh_title_prefix}{zh_title_content}（精選雙語跟讀教材）"

    result = {
        "id": vid,
        "title": real_title,
        "speaker": real_channel,
        "channel": existing_entry.get("channel", "Science & Technology") if existing_entry else "Science & Technology",
        "level": existing_entry.get("level", "B2") if existing_entry else "B2",
        "duration": real_duration,
        "views": views_str,
        "emoji": existing_entry.get("emoji", "🎬") if existing_entry else "🎬",
        "color": existing_entry.get("color", "linear-gradient(135deg, #a1c4fd, #c2e9fb)") if existing_entry else "linear-gradient(135deg, #a1c4fd, #c2e9fb)",
        "zh": full_zh_title,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "cues": cues,
        "words": []
    }

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result

def save_all_updates(videos, lessons, vld):
    print("\n>>> Saving synchronized updates to disk...")
    # 1. Update video_lessons.json
    vld["lessons"] = lessons
    with open(LESSONS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(vld, f, ensure_ascii=False, separators=(",", ":"))

    # 2. Update video_lessons.js
    with open(LESSONS_JS_PATH, "w", encoding="utf-8") as f:
        f.write("window.ENGLISHTUBE_DATA=" + json.dumps(vld, ensure_ascii=False, separators=(",", ":")) + ";\n")

    # 3. Update index.html (preserving const songs completely!)
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as inf:
        current_html = inf.read()
    s_idx = current_html.find("const videos = [")
    e_idx = current_html.find("const songs = [")
    if s_idx != -1 and e_idx != -1:
        new_videos_str = json.dumps(videos, ensure_ascii=False, indent=2)
        updated_html = current_html[:s_idx + len("const videos = ")] + new_videos_str + ";\n" + current_html[e_idx:]
        with open(INDEX_HTML_PATH, "w", encoding="utf-8") as outf:
            outf.write(updated_html)

    # 4. Bump SW version
    with open(SW_JS_PATH, "r", encoding="utf-8") as sf:
        sw_text = sf.read()
    m = re.search(r"englishtube-v(\d+)", sw_text)
    if m:
        curr_v = int(m.group(1))
        new_v = curr_v + 1
        new_sw = sw_text.replace(f"englishtube-v{curr_v}", f"englishtube-v{new_v}")
        with open(SW_JS_PATH, "w", encoding="utf-8") as sf:
            sf.write(new_sw)
        
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as inf:
            html = inf.read()
        html = html.replace(f"?v={curr_v}", f"?v={new_v}")
        with open(INDEX_HTML_PATH, "w", encoding="utf-8") as outf:
            outf.write(html)
        print(f"Bumped cache version to v{new_v}")

def main(limit=None):
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    start_idx = html.find("const videos = [")
    end_idx = html.find("const songs = [")
    videos = json.loads(html[start_idx + len("const videos = "):end_idx].strip().rstrip(";"))

    with open(LESSONS_JSON_PATH, "r", encoding="utf-8") as f:
        vld = json.load(f)
    lessons = vld.get("lessons", {})

    target_entries = []
    seen_ids = set()
    for idx, v in enumerate(videos):
        vid = v.get("id")
        cues = v.get("cues", [])
        if not cues and vid in lessons:
            cues = lessons[vid].get("cues", [])
        
        if len(cues) < 20:
            target_entries.append((idx, v, len(cues)))

    # Sort strictly by fewest cues first! (2, 3, 4, 5, 7, 8...)
    target_entries.sort(key=lambda item: item[2])

    print(f"Total videos identified with < 20 cues: {len(target_entries)}")
    shortest_count = sum(1 for _, _, cnt in target_entries if cnt <= 5)
    print(f"  -> Critical priority (<= 5 cues): {shortest_count} videos")
    print(f"  -> Secondary priority (6-19 cues): {len(target_entries) - shortest_count} videos")

    if limit:
        target_entries = target_entries[:limit]
        print(f"Processing batch of {len(target_entries)} videos...")

    fixed_count = 0
    failed_count = 0

    for i, (v_idx, v_entry, old_cue_cnt) in enumerate(target_entries):
        vid = v_entry["id"]
        print(f"\n[{i+1}/{len(target_entries)}] Target: {vid} (currently {old_cue_cnt} cues: '{v_entry.get('title')}')")
        fixed = fix_single_video(vid, v_entry)
        if fixed and fixed.get("cues") and len(fixed["cues"]) >= 10:
            # Update all matching entries in videos with this vid
            for v in videos:
                if v.get("id") == vid:
                    v["title"] = fixed["title"]
                    v["speaker"] = fixed["speaker"]
                    v["duration"] = fixed["duration"]
                    v["views"] = fixed["views"]
                    v["zh"] = fixed["zh"]
                    v["cues"] = fixed["cues"]

            # Update lessons dict
            lessons[vid] = fixed
            fixed_count += 1
            print(f"==> Successfully upgraded {vid} from {old_cue_cnt} cues to {len(fixed['cues'])} cues!")
        else:
            failed_count += 1
            print(f"==> Could not upgrade {vid}, keeping existing.")

        # Save progress every 5 videos
        if (i + 1) % 5 == 0 or i == len(target_entries) - 1:
            save_all_updates(videos, lessons, vld)

    print(f"\n==========================================")
    print(f"Batch processing completed: {fixed_count} upgraded, {failed_count} failed")
    print(f"==========================================")

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit)
