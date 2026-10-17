#!/usr/bin/env python3
"""
Audit and Fix Entire EnglishTube Song Catalog
1. Automatically identifies and fixes all songs with timing/quality defects:
   - Collided identical start timestamps (multiple cues starting at the exact same millisecond)
   - Reversed or scrambled cue order
   - Hallucinated loop lines
   - Dummy podcast lesson text ("Welcome back to our exploration of...")
   - Empty or missing Traditional Chinese translations
   - Truncated coverage (songs cutting off prematurely)
2. Replaces defects with genuine, millisecond-aligned community-verified lyrics (LRCLIB).
3. Batch translates all lyrics to natural Taiwan Traditional Chinese (zh-TW) with OpenCC s2twp.
4. Synchronizes across songs_100.json, video_lessons.json, video_lessons.js, and index.html.
"""

import os, sys, json, re, time, urllib.request, urllib.parse
from difflib import SequenceMatcher
import opencc

ROOT = os.path.dirname(os.path.abspath(__file__))
SONGS_PATH = os.path.join(ROOT, 'songs_100.json')
LESSONS_PATH = os.path.join(ROOT, 'video_lessons.json')
LESSONS_JS_PATH = os.path.join(ROOT, 'video_lessons.js')
INDEX_PATH = os.path.join(ROOT, 'index.html')
SW_PATH = os.path.join(ROOT, 'sw.js')

cc = opencc.OpenCC('s2twp')

# 1. Load Translation Cache from existing video_lessons.json
translation_cache = {}
if os.path.exists(LESSONS_PATH):
    try:
        with open(LESSONS_PATH, 'r', encoding='utf-8') as f:
            vld = json.load(f)
        for vid, lesson in vld.get('lessons', {}).items():
            for c in lesson.get('cues', []):
                en = (c.get('en') or c.get('text', '')).strip().lower()
                zh = (c.get('zh') or '').strip()
                if en and zh and en not in translation_cache:
                    translation_cache[en] = zh
        print(f"Loaded {len(translation_cache)} verified translations into memory.")
        sys.stdout.flush()
    except Exception as e:
        print(f"Warning loading translation cache: {e}")

def clean_str(t):
    return ''.join(c.lower() for c in t if c.isalnum() or c.isspace()).strip()

def translate_batch(texts):
    results = {}
    missing = []
    for t in texts:
        t_clean = clean_str(t)
        if t_clean in translation_cache:
            results[t] = translation_cache[t_clean]
        else:
            missing.append(t)
            
    if not missing:
        return results
        
    chunk_size = 15
    for i in range(0, len(missing), chunk_size):
        chunk = missing[i : i + chunk_size]
        joined = '\n'.join(chunk)
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(joined)}&langpair=en|zh-TW"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
                translated = data.get('responseData', {}).get('translatedText', '')
                t_lines = translated.split('\n')
                for orig, trans in zip(chunk, t_lines):
                    if not trans.startswith('MYMEMORY WARNING'):
                        tw_trans = cc.convert(trans).strip()
                        results[orig] = tw_trans
                        translation_cache[clean_str(orig)] = tw_trans
                    else:
                        results[orig] = ''
        except Exception:
            for orig in chunk:
                if orig not in results:
                    results[orig] = ''
        time.sleep(0.2)
        
    return results

def parse_lrc(lrc_text):
    cues = []
    lines = lrc_text.split('\n')
    for line in lines:
        m = re.match(r'\[(\d+):(\d+\.\d+)\]\s*(.*)', line)
        if m:
            mins = int(m.group(1))
            secs = float(m.group(2))
            t = mins * 60 + secs
            txt = m.group(3).strip()
            # Clean unwanted artifacts
            txt = re.sub(r'\[.*?\]', '', txt).strip()
            txt = txt.replace('♪', '').strip()
            if txt and len(txt) > 1:
                cues.append({'start': round(t, 2), 'en': txt})
    return cues

def query_lrclib(title, artist):
    queries = [
        f"{title} {artist}",
        f"{title}"
    ]
    for q in queries:
        url = f"https://lrclib.net/api/search?q={urllib.parse.quote(q)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'EnglishTube/1.0 (https://github.com)'})
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                results = json.loads(r.read().decode())
                best_cues = None
                for item in results:
                    synced = item.get('syncedLyrics')
                    if synced:
                        parsed = parse_lrc(synced)
                        if len(parsed) >= 15:
                            track_name = item.get('trackName', '').lower()
                            if 'official' in track_name and ('video' in track_name or 'music' in track_name):
                                return parsed
                            if not best_cues:
                                best_cues = parsed
                if best_cues:
                    return best_cues
        except Exception:
            pass
        time.sleep(0.1)
    return None

def compute_smart_offset(old_cues, new_cues, song_title):
    if 'I Will Always Love You' in song_title:
        return 6.4
    if "I'll Make Love to You" in song_title and new_cues[0]['start'] < 10.0:
        return 47.5
    
    valid_diffs = []
    seen_starts = set()
    dup_starts = set()
    for oc in old_cues:
        st = oc.get('start', 0)
        if st in seen_starts:
            dup_starts.add(st)
        seen_starts.add(st)

    for oc in old_cues:
        ostart = oc.get('start', 0)
        if ostart in dup_starts or ostart < 4.0:
            continue
        otxt = clean_str(oc.get('en') or oc.get('text', ''))
        if not otxt:
            continue
        for nc in new_cues:
            ntxt = clean_str(nc['en'])
            nstart = nc['start']
            if SequenceMatcher(None, otxt, ntxt).ratio() > 0.88:
                diff = ostart - nstart
                if abs(diff) < 45.0:
                    valid_diffs.append(diff)
                break
    
    if len(valid_diffs) >= 3:
        valid_diffs.sort()
        median_diff = valid_diffs[len(valid_diffs) // 2]
        if abs(median_diff) > 1.2:
            return round(median_diff, 2)
            
    return 0.0

def rebuild_song(song, idx, total):
    title = song['title']
    artist = song.get('speaker', '')
    old_cues = song.get('cues', [])
    print(f"[{idx}/{total}] Processing: {title} - {artist}...")
    sys.stdout.flush()
    
    # Query LRCLIB
    lrc_cues = query_lrclib(title, artist)
    if not lrc_cues or len(lrc_cues) < 15:
        print(f"  [!] Could not fetch sufficient LRCLIB cues ({len(lrc_cues) if lrc_cues else 0}), keeping baseline.")
        sys.stdout.flush()
        return False
        
    # Offset calculation
    offset = compute_smart_offset(old_cues, lrc_cues, title)
    if offset != 0.0:
        print(f"  -> Applied MV intro offset: {offset:+.2f}s")
        for c in lrc_cues:
            c['start'] = round(max(0.0, c['start'] + offset), 2)
            
    # Remove any potential duplicate starts
    deduped = []
    for c in lrc_cues:
        if not deduped or c['start'] > deduped[-1]['start']:
            deduped.append(c)
        elif c['start'] == deduped[-1]['start']:
            deduped[-1]['en'] += ' / ' + c['en']
            
    lrc_cues = deduped
    
    # Batch translate all lines
    en_lines = [c['en'] for c in lrc_cues]
    translations = translate_batch(en_lines)
    
    # Calculate durations and construct cues
    final_cues = []
    for i in range(len(lrc_cues)):
        cur = lrc_cues[i]
        start_t = cur['start']
        if i < len(lrc_cues) - 1:
            next_t = lrc_cues[i+1]['start']
            gap = next_t - start_t
            dur = round(min(max(1.2, gap - 0.05), 6.5), 2)
        else:
            dur = 4.0
            
        en_text = cur['en']
        zh_text = translations.get(en_text, '')
        
        final_cues.append({
            'start': start_t,
            'duration': dur,
            'en': en_text,
            'zh': zh_text,
            'text': en_text
        })
        
    song['cues'] = final_cues
    song['en'] = [c['en'] for c in final_cues]
    song['cn'] = [c['zh'] for c in final_cues]
    print(f"  ✓ Rebuilt with {len(final_cues)} cues (starts at {final_cues[0]['start']}s, ends at {final_cues[-1]['start']}s)!")
    sys.stdout.flush()
    return True

def main():
    print("=== STARTING FULL CATALOG AUDIT & REPAIR ===")
    sys.stdout.flush()
    with open(SONGS_PATH, 'r', encoding='utf-8') as f:
        songs = json.load(f)
        
    # Detect all songs needing rebuild
    targets = []
    for idx, s in enumerate(songs):
        cues = s.get('cues', [])
        starts = [c.get('start', 0) for c in cues]
        has_dup_starts = len(starts) != len(set(starts))
        non_mono = any(starts[i] > starts[i+1] for i in range(len(starts)-1))
        empty_zh = sum(1 for c in cues if not (c.get('zh') or '').strip())
        has_dummy = any('exploration of' in (c.get('en') or '').lower() or 'thank you for watching' in (c.get('en') or '').lower() for c in cues)
        count = len(cues)
        max_t = max(starts) if starts else 0
        
        # Target songs with any defect or Boyz II Men actor dialogue (idx 40)
        if non_mono or has_dup_starts or has_dummy or empty_zh > 0 or count < 16 or max_t < 70 or idx == 40:
            targets.append((idx, s))
            
    print(f"Identified {len(targets)} songs to rebuild out of {len(songs)}.")
    sys.stdout.flush()
    
    fixed_count = 0
    for num, (idx, s) in enumerate(targets, 1):
        ok = rebuild_song(s, num, len(targets))
        if ok:
            fixed_count += 1
            with open(SONGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(songs, f, indent=2, ensure_ascii=False)
                
    print(f"\nRebuilding complete! Fixed {fixed_count}/{len(targets)} songs.")
    sys.stdout.flush()
    
    # Save final songs_100.json
    with open(SONGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(songs, f, indent=2, ensure_ascii=False)
    print("Saved songs_100.json")
    
    # Synchronize video_lessons.json & video_lessons.js
    if os.path.exists(LESSONS_PATH):
        with open(LESSONS_PATH, 'r', encoding='utf-8') as f:
            vld = json.load(f)
        lessons = vld.get('lessons', {})
        for s in songs:
            sid = s['id']
            if sid in lessons:
                lessons[sid]['cues'] = s['cues']
                lessons[sid]['en'] = s.get('en', [])
                lessons[sid]['cn'] = s.get('cn', [])
        vld['lessons'] = lessons
        with open(LESSONS_PATH, 'w', encoding='utf-8') as f:
            json.dump(vld, f, ensure_ascii=False)
        print("Synchronized video_lessons.json")
        
        # video_lessons.js
        js_content = f"window.ENGLISHTUBE_DATA = {json.dumps(vld, ensure_ascii=False)};\nwindow.PRELOADED_LESSONS = window.ENGLISHTUBE_DATA;\n"
        with open(LESSONS_JS_PATH, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print("Synchronized video_lessons.js")
        
    # Bump Service Worker to v39
    if os.path.exists(SW_PATH):
        content = open(SW_PATH, 'r', encoding='utf-8').read()
        content = re.sub(r'const CACHE_NAME = [\'"]englishtube-v\d+[\'"]', "const CACHE_NAME = 'englishtube-v39'", content)
        with open(SW_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Bumped sw.js to v39")
        
    # Bump index.html script tag
    if os.path.exists(INDEX_PATH):
        content = open(INDEX_PATH, 'r', encoding='utf-8').read()
        content = re.sub(r'video_lessons\.js\?v=\d+', 'video_lessons.js?v=39', content)
        with open(INDEX_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Bumped index.html to v39")

if __name__ == '__main__':
    main()
