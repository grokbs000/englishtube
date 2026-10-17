#!/usr/bin/env python3
"""
Calibrate all 100 songs in songs_100.json using official YouTube MV millisecond subtitles.
Aligns English cues to exact MV vocal starts, resolving the 10~45s MV intro desync.
"""
import os, sys, json, re, glob, subprocess, time
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.abspath(__file__))
SONGS_PATH = os.path.join(ROOT, 'songs_100.json')
LESSONS_PATH = os.path.join(ROOT, 'video_lessons.json')
LESSONS_JS_PATH = os.path.join(ROOT, 'video_lessons.js')
TMP_DIR = os.path.join(ROOT, 'tmp_song_calib')
os.makedirs(TMP_DIR, exist_ok=True)

def sec(t):
    parts = t.strip().replace(',', '.').split(':')
    return sum(float(x) * 60**(len(parts) - j - 1) for j, x in enumerate(parts))

def clean_txt(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('♪', ' ')
    t = re.sub(r'\[.*?\]', '', t)
    t = re.sub(r'\(.*?\)', '', t)
    t = re.sub(r'[^a-zA-Z0-9\s]', '', t)
    return ' '.join(t.lower().split())

def parse_vtt(text):
    lines = text.split('\n')
    cues = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if '-->' in line:
            parts = line.split('-->', 1)
            a = parts[0].strip().split(' ')[0]
            b = parts[1].strip().split(' ')[0]
            i += 1
            txt = []
            while i < len(lines) and lines[i].strip():
                txt.append(lines[i].strip())
                i += 1
            raw = ' '.join(txt).replace('♪', '').strip()
            clean = clean_txt(raw)
            if clean and not any(w in clean for w in ['music', 'piano', 'applause', 'cheering', 'intro']):
                cues.append({
                    'start': round(sec(a), 2),
                    'end': round(sec(b), 2),
                    'duration': round(max(1.0, sec(b) - sec(a)), 2),
                    'text': raw,
                    'clean': clean
                })
        i += 1
    return cues

def align_song(song):
    vid = song['id']
    title = song['title']
    url = f"https://www.youtube.com/watch?v={vid}"
    out_tmpl = os.path.join(TMP_DIR, f"{vid}.%(ext)s")
    
    # Download subtitles
    cmd = [
        'yt-dlp', '--skip-download',
        '--write-sub', '--write-auto-sub',
        '--sub-lang', 'en.*',
        '--sub-format', 'vtt',
        '-o', out_tmpl, url
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    
    vtt_files = glob.glob(os.path.join(TMP_DIR, f"{vid}.*"))
    if not vtt_files:
        return False, 0
        
    vtt_text = open(vtt_files[0], 'r', encoding='utf-8', errors='ignore').read()
    vtt_cues = parse_vtt(vtt_text)
    
    for f in vtt_files:
        try: os.remove(f)
        except: pass
        
    if not vtt_cues:
        return False, 0
        
    old_cues = song.get('cues', [])
    updated_cues = []
    
    matched_count = 0
    # Match each old cue to the best vtt_cue
    for oc in old_cues:
        oc_en = oc.get('en') or oc.get('text', '')
        oc_clean = clean_txt(oc_en)
        if not oc_clean:
            updated_cues.append(oc)
            continue
            
        best_match = None
        best_ratio = 0
        for vc in vtt_cues:
            ratio = SequenceMatcher(None, oc_clean, vc['clean']).ratio()
            # Also check substring match
            if oc_clean in vc['clean'] or vc['clean'] in oc_clean:
                ratio = max(ratio, 0.75)
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = vc
                
        if best_match and best_ratio > 0.45:
            matched_count += 1
            updated_cues.append({
                'start': best_match['start'],
                'duration': best_match['duration'],
                'en': oc_en,
                'zh': oc.get('zh', ''),
                'text': oc_en
            })
        else:
            updated_cues.append(oc)
            
    # Sort cues chronologically by start
    updated_cues.sort(key=lambda c: c['start'])
    
    # Smooth monotonic duration
    for i in range(len(updated_cues)):
        cur = updated_cues[i]
        if i + 1 < len(updated_cues):
            next_start = updated_cues[i+1]['start']
            if next_start > cur['start']:
                cur['duration'] = round(min(cur.get('duration', 4.0), next_start - cur['start']), 2)
                
    song['cues'] = updated_cues
    return True, matched_count

def main():
    print("Loading songs_100.json...")
    with open(SONGS_PATH, 'r', encoding='utf-8') as f:
        songs = json.load(f)
        
    print(f"Total songs to calibrate: {len(songs)}")
    total_calibrated = 0
    
    for i, s in enumerate(songs, 1):
        vid = s['id']
        title = s['title']
        success, count = align_song(s)
        if success and count > 3:
            total_calibrated += 1
            first_start = s['cues'][0]['start'] if s['cues'] else 0
            print(f"[{i}/100] ✓ {title} ({vid}): {count} cues aligned (first cue starts at {first_start}s)")
        else:
            print(f"[{i}/100] ○ {title} ({vid}): kept baseline timings ({count} sub matches)")
        time.sleep(0.5)
        
    print(f"\nCalibrated {total_calibrated}/100 songs to official YouTube MV timestamps!")
    
    # Save songs_100.json
    with open(SONGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)
    print("Saved to songs_100.json")
    
    # Sync into video_lessons.json if present
    if os.path.exists(LESSONS_PATH):
        with open(LESSONS_PATH, 'r', encoding='utf-8') as f:
            vld = json.load(f)
        lessons = vld.get('lessons', {})
        for s in songs:
            sid = s['id']
            if sid in lessons:
                lessons[sid]['cues'] = s['cues']
        vld['lessons'] = lessons
        with open(LESSONS_PATH, 'w', encoding='utf-8') as f:
            json.dump(vld, f, ensure_ascii=False)
        print("Synchronized with video_lessons.json")
        
        js_content = f"window.ENGLISHTUBE_DATA = {json.dumps(vld, ensure_ascii=False)};\nwindow.PRELOADED_LESSONS = window.ENGLISHTUBE_DATA;\n"
        with open(LESSONS_JS_PATH, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print("Synchronized with video_lessons.js")

if __name__ == '__main__':
    main()
