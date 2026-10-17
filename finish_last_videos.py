import os, sys, re, json, glob, time, subprocess, urllib.request, urllib.parse
from opencc import OpenCC

cc = OpenCC('s2twp')
CACHE_DIR = ".video_fix_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
INDEX_HTML_PATH = "index.html"
LESSONS_JSON_PATH = "video_lessons.json"
LESSONS_JS_PATH = "video_lessons.js"
SW_JS_PATH = "sw.js"
TRANS_CACHE_PATH = os.path.join(CACHE_DIR, "translation_cache.json")

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

def transcribe_whisper(vid):
    print(f"[{vid}] Extracting audio for faster-whisper...")
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
        print(f"[{vid}] Whisper error: {e}")
        return []
    finally:
        if os.path.exists(audio_path):
            try: os.remove(audio_path)
            except Exception: pass

def fetch_and_build_video(vid, fallback_meta=None):
    # 1. Fetch metadata
    meta = None
    for attempt in range(2):
        try:
            cmd = ["yt-dlp", "--dump-json", f"https://www.youtube.com/watch?v={vid}"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=18)
            if res.returncode == 0 and res.stdout:
                meta = json.loads(res.stdout)
                break
        except Exception:
            time.sleep(1)

    if not meta and not fallback_meta:
        print(f"[{vid}] Could not retrieve metadata")
        return None

    meta = meta or fallback_meta or {}
    real_title = meta.get("title") or "English Lesson"
    real_channel = meta.get("uploader") or meta.get("channel") or "EnglishTube"
    duration_secs = meta.get("duration", 0)
    dur_m = duration_secs // 60
    dur_s = duration_secs % 60
    real_duration = f"{dur_m:02d}:{dur_s:02d}"
    view_count = meta.get("view_count", 0)
    views_str = f"{view_count/1000000:.1f}M" if view_count >= 1000000 else (f"{view_count//1000}K" if view_count >= 1000 else f"{view_count}")

    # 2. Download subtitles
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
    subprocess.run(cmd, capture_output=True, timeout=30)
    
    en_vtts = glob.glob(f"{sub_prefix}*.en*.vtt")
    cues = []
    if en_vtts:
        en_vtts.sort(key=lambda x: (not x.endswith('.en.vtt') and not x.endswith('.en-US.vtt'), x))
        cues = parse_vtt(en_vtts[0])

    for vf in glob.glob(f"{sub_prefix}*.vtt"):
        try: os.remove(vf)
        except Exception: pass

    if not cues or len(cues) < 6:
        cues_whisper = transcribe_whisper(vid)
        if cues_whisper and len(cues_whisper) > len(cues):
            cues = cues_whisper

    if not cues or len(cues) < 5:
        print(f"[{vid}] Failed to obtain cues (found {len(cues)})")
        return None

    batch_translate_cues(cues)

    zh_title_prefix = f"【{real_channel}】"
    zh_title_content = translate_single(real_title)
    full_zh_title = f"{zh_title_prefix}{zh_title_content}（精選雙語跟讀教材）"

    return {
        "id": vid,
        "title": real_title,
        "speaker": real_channel,
        "channel": "English Learning",
        "level": "B2",
        "duration": real_duration,
        "views": views_str,
        "emoji": "🎬",
        "color": "linear-gradient(135deg, #a1c4fd, #c2e9fb)",
        "zh": full_zh_title,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "cues": cues,
        "words": []
    }

def main():
    print("=== FINISHING ALL REMAINING SHORT CUES VIDEOS ===")
    
    # 1. Load files
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    start_idx = html.find("const videos = [")
    end_idx = html.find("const songs = [")
    videos = json.loads(html[start_idx + len("const videos = "):end_idx].strip().rstrip(";"))

    with open(LESSONS_JSON_PATH, "r", encoding="utf-8") as f:
        vld = json.load(f)
    lessons = vld.get("lessons", {})

    # ID replacements for broken / foreign-language / 10s teaser videos:
    ID_REPLACEMENTS = {
        "i8GoihLte7U": "o2DDU4g0PRo",  # Arabic video -> TED: Fake videos of real people and how to spot them
        "3aTA7I9yP4Q": "2jAH-51feAA",  # 10s teaser -> Supersonic Planes Are Coming BACK
        "CJhURDNPfH4": "I4C2LeIx0OM",  # 54s no-sub challenge -> Tongue Twisters to Improve Pronunciation
        "a9WprkKesKI": "T4DN0SMW1JE",  # instrumental chiptune -> Video Essay: When Music and Video Games Collide
    }

    for v in videos:
        old_id = v.get("id")
        if old_id in ID_REPLACEMENTS:
            new_id = ID_REPLACEMENTS[old_id]
            print(f"Replacing problematic video ID {old_id} -> {new_id}")
            v["id"] = new_id

    # Sync any videos that already have full cues in lessons
    synced_from_lessons = 0
    for v in videos:
        vid = v.get("id")
        if vid in lessons:
            l_cues = lessons[vid].get("cues", [])
            if len(l_cues) > len(v.get("cues", [])):
                v["cues"] = l_cues
                synced_from_lessons += 1
    print(f"Synchronized {synced_from_lessons} video entries from lessons into index.html videos array.")

    # Target specific videos that need full subtitles
    REMAINING_TARGETS = [
        "t3E9lIXvcrg", # Luxury brands (previously 3 cues)
        "yCjJyiqpAuU", # Twinkle twinkle (previously 2 cues)
        "4YOwEqGykDM", # Caffeine tolerance
        "BEbW2fXSShc", # Movie posters
        "vc2W9CVdMMI", # Hickory dickory dock
        "yzPX6zmaBdg", # Telephone English
        "Y2tm40uMhDI", # Mariana Trench
        "OONaPcZ4EAs", # Foley Sound
        "o2DDU4g0PRo", # Deepfake detection (replacement)
        "2jAH-51feAA", # Supersonic planes (replacement)
        "I4C2LeIx0OM", # Tongue twisters (replacement)
        "T4DN0SMW1JE", # Video game music (replacement)
    ]

    for vid in REMAINING_TARGETS:
        print(f"\nProcessing target: {vid}")
        built = fetch_and_build_video(vid)
        if built and built.get("cues") and len(built["cues"]) >= 6:
            lessons[vid] = built
            for v in videos:
                if v.get("id") == vid:
                    v["title"] = built["title"]
                    v["speaker"] = built["speaker"]
                    v["duration"] = built["duration"]
                    v["views"] = built["views"]
                    v["zh"] = built["zh"]
                    v["cues"] = built["cues"]
            print(f"==> Successfully upgraded {vid} with {len(built['cues'])} cues!")
        else:
            print(f"==> WARNING: Could not upgrade {vid}")

    # Final check of all videos in videos list
    under_6 = [v for v in videos if len(v.get("cues", [])) < 6]
    print(f"\nFinal count of videos with < 6 cues: {len(under_6)}")
    for v in under_6:
        print(f"  {v.get('id')}: {len(v.get('cues', []))} cues - {v.get('title')}")

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

    print("\n=== FINISH COMPLETE ===")

if __name__ == "__main__":
    main()
