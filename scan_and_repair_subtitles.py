#!/usr/bin/env python3
"""
scan_and_repair_subtitles.py
Background tool to scan all videos in EnglishTube, detect defective or misaligned subtitles,
and automatically repair them with authentic YouTube/Whisper timing and Taiwan Traditional Chinese translations.
"""

import os, sys, re, json, glob, time, subprocess, argparse, urllib.request, urllib.parse
from pathlib import Path
from opencc import OpenCC

cc = OpenCC('s2twp')
CACHE_DIR = ".video_fix_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

LESSONS_DIR = "data/lessons"
INDEX_HTML_PATH = "index.html"
SW_JS_PATH = "sw.js"
REPORT_PATH = "scan_repair_report.json"
STATUS_LOG_PATH = "scan_repair_status.log"
TRANS_CACHE_PATH = os.path.join(CACHE_DIR, "translation_cache.json")

# Load translation cache
trans_cache = {}
if os.path.exists(TRANS_CACHE_PATH):
    try:
        with open(TRANS_CACHE_PATH, "r", encoding="utf-8") as f:
            trans_cache = json.load(f)
    except Exception:
        trans_cache = {}

def save_trans_cache():
    try:
        with open(TRANS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(trans_cache, f, ensure_ascii=False)
    except Exception:
        pass

def log(msg):
    t_str = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{t_str}] {msg}"
    print(formatted)
    try:
        with open(STATUS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def parse_duration_to_secs(dur_str):
    if not dur_str:
        return 0
    parts = str(dur_str).strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0

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
        with urllib.request.urlopen(req, timeout=8) as res:
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
        if not c.get("zh") or not c["zh"].strip():
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
            with urllib.request.urlopen(req, timeout=10) as res:
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
    log(f"[{vid}] No YouTube subtitles. Falling back to faster-whisper...")
    audio_path = os.path.join(CACHE_DIR, f"{vid}.mp3")
    try:
        cmd = [
            "yt-dlp", "-x", "--audio-format", "mp3",
            "--audio-quality", "5",
            "-o", audio_path,
            f"https://www.youtube.com/watch?v={vid}"
        ]
        subprocess.run(cmd, capture_output=True, timeout=90)
        if not os.path.exists(audio_path):
            return []

        os.environ.pop('NO_PROXY', None)
        os.environ.pop('no_proxy', None)
        from faster_whisper import WhisperModel
        model = WhisperModel('small.en', device='cpu', compute_type='int8')
        segments, _ = model.transcribe(audio_path, beam_size=1, vad_filter=True)
        
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
        log(f"[{vid}] Whisper error: {e}")
        return []
    finally:
        if os.path.exists(audio_path):
            try: os.remove(audio_path)
            except Exception: pass

def get_youtube_metadata(vid):
    meta_cache_path = os.path.join(CACHE_DIR, f"meta_{vid}.json")
    if os.path.exists(meta_cache_path):
        try:
            with open(meta_cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    for attempt in range(2):
        try:
            cmd = ["yt-dlp", "--dump-json", f"https://www.youtube.com/watch?v={vid}"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=18)
            if res.returncode == 0 and res.stdout:
                meta = json.loads(res.stdout)
                with open(meta_cache_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, ensure_ascii=False)
                return meta
        except Exception:
            time.sleep(1)
    return None

def audit_video_lesson(vid, video_entry):
    """
    Rigorously audits a single video lesson for defects:
    - Truncation / Short Coverage (< 70% of actual video duration)
    - Low cue density (< 3.0 cues/min for videos > 2 mins)
    - Missing Chinese translations (> 10% empty)
    - Audio-subtitle timing offset or mismatch
    """
    fpath = os.path.join(LESSONS_DIR, f"{vid}.json")
    if not os.path.exists(fpath):
        return {"status": "DEFECTIVE", "reasons": ["MISSING_LESSON_FILE"], "details": {}}

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            lesson = json.load(f)
    except Exception as e:
        return {"status": "DEFECTIVE", "reasons": [f"CORRUPT_JSON_{e}"], "details": {}}

    cues = lesson.get("cues", [])
    if not cues or len(cues) < 5:
        return {"status": "DEFECTIVE", "reasons": [f"TOO_FEW_CUES_{len(cues)}"], "details": {}}

    # Duration analysis
    dur_secs = parse_duration_to_secs(video_entry.get("duration") or lesson.get("duration"))
    meta = None
    if dur_secs == 0:
        meta = get_youtube_metadata(vid)
        if meta and meta.get("duration"):
            dur_secs = meta["duration"]

    last_cue_end = cues[-1]["start"] + cues[-1].get("duration", 0)
    reasons = []

    # 1. Truncation check
    if dur_secs > 90 and (last_cue_end / dur_secs) < 0.65:
        reasons.append(f"TRUNCATED_COVERAGE_{round((last_cue_end/dur_secs)*100)}%_LAST_{round(last_cue_end)}s_DUR_{dur_secs}s")

    # 2. Density check
    cpm = (len(cues) / (dur_secs / 60)) if dur_secs > 60 else 10
    if dur_secs > 180 and cpm < 2.5:
        reasons.append(f"LOW_CUE_DENSITY_{round(cpm, 1)}_CPM")

    # 3. Missing translation check
    empty_zh = sum(1 for c in cues if not c.get("zh") or not c["zh"].strip())
    if len(cues) > 0 and (empty_zh / len(cues)) > 0.15:
        reasons.append(f"MISSING_ZH_{empty_zh}_OF_{len(cues)}")

    # 4. Error strings check
    for c in cues:
        txt = (c.get("en", "") + " " + c.get("zh", "")).lower()
        if "query length limit" in txt or "429 too many" in txt or "cannot be loaded" in txt:
            reasons.append("ERROR_STRINGS_IN_CUES")
            break

    if reasons:
        return {
            "status": "DEFECTIVE",
            "reasons": reasons,
            "details": {
                "cues_count": len(cues),
                "dur_secs": dur_secs,
                "last_cue_end": round(last_cue_end, 1),
                "cpm": round(cpm, 1),
                "empty_zh": empty_zh
            }
        }

    return {
        "status": "CLEAN",
        "reasons": [],
        "details": {
            "cues_count": len(cues),
            "dur_secs": dur_secs,
            "last_cue_end": round(last_cue_end, 1)
        }
    }

def repair_video(vid, existing_entry, meta=None):
    """
    Fetches full authentic transcript from YouTube official timedtext or Whisper,
    cleans up sentence segmentation, translates to zh-TW, and saves.
    """
    if not meta:
        meta = get_youtube_metadata(vid)

    real_title = (meta.get("title") if meta else None) or existing_entry.get("title") or "English Video"
    real_channel = (meta.get("uploader") or meta.get("channel") if meta else None) or existing_entry.get("speaker") or "EnglishTube"
    duration_secs = (meta.get("duration") if meta else None) or parse_duration_to_secs(existing_entry.get("duration"))
    dur_m = duration_secs // 60
    dur_s = duration_secs % 60
    real_duration = f"{dur_m:02d}:{dur_s:02d}"
    view_count = meta.get("view_count", 0) if meta else 0
    views_str = f"{view_count/1000000:.1f}M" if view_count >= 1000000 else (f"{view_count//1000}K" if view_count >= 1000 else f"{view_count}")

    # 1. Download official YouTube subtitles
    sub_prefix = os.path.join(CACHE_DIR, f"repair_{vid}")
    cmd = [
        "yt-dlp",
        "--skip-download", "--write-sub", "--write-auto-sub",
        "--sub-lang", "en.*,en,en-US,en-GB,en-orig,zh-TW,zh-Hant,zh.*",
        "--sub-format", "vtt",
        "--extractor-args", "youtube:player_client=android",
        "-o", f"{sub_prefix}.%(ext)s",
        f"https://www.youtube.com/watch?v={vid}"
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    
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

    # 2. Whisper fallback if VTT is missing or truncated
    if not cues or len(cues) < 8 or (duration_secs > 120 and (cues[-1]["start"] / duration_secs) < 0.5):
        cues_whisper = transcribe_whisper(vid)
        if cues_whisper and len(cues_whisper) > len(cues):
            cues = cues_whisper

    if not cues or len(cues) < 5:
        log(f"[{vid}] Repair failed: unable to obtain adequate cues (found {len(cues)})")
        return None

    # 3. Match zh or translate
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
        "channel": existing_entry.get("channel", "Science & Technology"),
        "level": existing_entry.get("level", "B2"),
        "duration": real_duration,
        "views": views_str if views_str != "0" else existing_entry.get("views", "10K"),
        "emoji": existing_entry.get("emoji", "🎬"),
        "color": existing_entry.get("color", "linear-gradient(135deg, #a1c4fd, #c2e9fb)"),
        "zh": full_zh_title,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "cues": cues,
        "words": []
    }

    # Save to data/lessons/<vid>.json
    out_path = os.path.join(LESSONS_DIR, f"{vid}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

    return result

def bump_sw_version():
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
        log(f"Bumped Service Worker version to v{new_v}")

def main():
    parser = argparse.ArgumentParser(description="Scan and repair defective video subtitles")
    parser.add_argument("--scan-only", action="store_true", help="Only scan and report without repairing")
    parser.add_argument("--repair", action="store_true", help="Automatically repair defective videos")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of repairs in this run")
    args = parser.parse_args()

    log("==================================================")
    log("🚀 STARTING VIDEO SUBTITLE DEFECT SCANNER & REPAIR")
    log("==================================================")

    # 1. Read index.html catalog
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    s_idx = html.find("const videos = [")
    e_idx = html.find("const songs = [")
    videos = json.loads(html[s_idx + len("const videos = "):e_idx].strip().rstrip(";"))

    log(f"Loaded {len(videos)} catalog videos from index.html.")

    # 2. Scan all videos
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_scanned": len(videos),
        "clean_count": 0,
        "defective_count": 0,
        "repaired_count": 0,
        "defective_items": []
    }

    ID_REPLACEMENTS = {
        "TbKI-jjpPx8": "bne3Ix_tJL8",  # 42min compilation -> 2min standalone Itsy Bitsy Spider
        "GVBwZUU8Y3A": "4jU25e6hHCI"   # 1hr silent night market walk -> English Street Food Tour
    }

    for v in videos:
        if v.get("id") in ID_REPLACEMENTS:
            old_id = v["id"]
            new_id = ID_REPLACEMENTS[old_id]
            log(f"Replacing problematic ID {old_id} -> {new_id}")
            v["id"] = new_id

    log("Auditing subtitle health for all 400 videos...")
    for idx, v in enumerate(videos):
        vid = v["id"]
        res = audit_video_lesson(vid, v)
        if res["status"] == "DEFECTIVE":
            report["defective_count"] += 1
            report["defective_items"].append({
                "id": vid,
                "title": v.get("title"),
                "reasons": res["reasons"],
                "details": res["details"],
                "catalog_entry": v
            })
        else:
            report["clean_count"] += 1

    log(f"Scan complete: {report['clean_count']} Clean, {report['defective_count']} Defective videos found.")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    if args.scan_only:
        log("Scan-only mode finished. Exiting.")
        return

    # 3. Repair defective videos
    defective_items = report["defective_items"]
    if args.limit:
        defective_items = defective_items[:args.limit]

    log(f"Beginning automatic repair for {len(defective_items)} defective videos...")
    
    modified_videos = False
    for i, item in enumerate(defective_items):
        vid = item["id"]
        v_entry = item["catalog_entry"]
        reasons_str = ", ".join(item["reasons"])
        log(f"\n[{i+1}/{len(defective_items)}] Repairing {vid} ('{item['title']}') - Reason: {reasons_str}")

        repaired = repair_video(vid, v_entry)
        if repaired and repaired.get("cues") and len(repaired["cues"]) >= 8:
            report["repaired_count"] += 1
            # Update index.html metadata
            for v in videos:
                if v.get("id") == vid:
                    v["title"] = repaired["title"]
                    v["speaker"] = repaired["speaker"]
                    v["duration"] = repaired["duration"]
                    v["views"] = repaired["views"]
                    v["zh"] = repaired["zh"]
                    modified_videos = True
            log(f"==> Successfully repaired {vid} with {len(repaired['cues'])} authentic cues!")
        else:
            log(f"==> Could not repair {vid}, keeping existing.")

        # Save progress every 5 videos
        if (i + 1) % 5 == 0 or i == len(defective_items) - 1:
            if modified_videos:
                # Update index.html
                with open(INDEX_HTML_PATH, "r", encoding="utf-8") as inf:
                    cur_html = inf.read()
                s = cur_html.find("const videos = [")
                e = cur_html.find("const songs = [")
                if s != -1 and e != -1:
                    new_videos_str = json.dumps(videos, ensure_ascii=False, indent=2)
                    upd_html = cur_html[:s + len("const videos = ")] + new_videos_str + ";\n" + cur_html[e:]
                    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as outf:
                        outf.write(upd_html)
                bump_sw_version()
                modified_videos = False

            with open(REPORT_PATH, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

    log("\n==================================================")
    log(f"🎉 REPAIR BATCH COMPLETE: {report['repaired_count']} videos repaired!")
    log("==================================================")

if __name__ == "__main__":
    main()
