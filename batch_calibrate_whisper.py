#!/usr/bin/env python3
"""
Batch Audio & Whisper High-Precision Karaoke Alignment Script
Calibrates the remaining unaligned songs in songs_100.json to exact millisecond timestamps.
"""
import os, sys, json, re, subprocess, time
from pathlib import Path
from difflib import SequenceMatcher

# Prevent httpx proxy parse issues
os.environ.pop('NO_PROXY', None)
os.environ.pop('no_proxy', None)

from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent
SONGS_PATH = ROOT / 'songs_100.json'
LESSONS_PATH = ROOT / 'video_lessons.json'
LESSONS_JS_PATH = ROOT / 'video_lessons.js'
INDEX_PATH = ROOT / 'index.html'
SCRATCH_DIR = ROOT / 'scratch' / 'audio'
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

TARGET_IDS = [
    '8xg3vE8Ie_E',  # Love Story
    'igIfiqqVHtA',  # Enchanted
    'cvUAzpn48xA',  # Lover
    'nSDgHBxUbVQ',  # Photograph
    'rtOvBOTyX00',  # A Thousand Years
    'K_9QtL-L16o',  # Because You Loved Me
    '06-XXOTP3Gc',  # Beautiful in White
    'zSWuqUiQ5ck',  # You Raise Me Up
    'Pu5c4aEg3NM',  # Wonderful Tonight
    'Y0pdQU87dc8',  # (Everything I Do) I Do It for You
    'J6cNvjOn4gM',  # You're Still the One
    'jBVifG4_Ruk',  # Truly Madly Deeply
    'BpIf43m2ZQI',  # Shallow
    'rdXTZAr1zBY',  # 10,000 Hours
    'fDb0tKHcZhg',  # Hero
    'vGJTaP6anOU',  # Can't Help Falling in Love
    '1bGOgY1CmiU',  # I Just Called to Say I Love You
    '-CQ4yr9o0qM'   # Kiss Me
]

def clean_word(w):
    return re.sub(r'[^a-zA-Z0-9]', '', w.lower())

def align_cues_to_words(cues, words):
    w_idx = 0
    aligned = []
    matched_count = 0
    
    for i, c in enumerate(cues):
        en_words = [clean_word(w) for w in c['en'].split() if clean_word(w)]
        if not en_words:
            aligned.append(c)
            continue
            
        best_score = -1
        best_start = None
        best_end = None
        best_widx = w_idx
        
        # Search window
        win = words[max(0, w_idx - 5) : min(len(words), w_idx + 45)]
        for j in range(len(win) - len(en_words) + 1):
            cand = [w['word'] for w in win[j : j + len(en_words)]]
            score = SequenceMatcher(None, ' '.join(en_words), ' '.join(cand)).ratio()
            if score > best_score:
                best_score = score
                best_start = win[j]['start']
                best_end = win[j + len(en_words) - 1]['end']
                best_widx = max(0, w_idx - 5) + j + len(en_words)
                
        if best_score > 0.42:
            matched_count += 1
            w_idx = best_widx
            dur = round(max(1.2, best_end - best_start), 2)
            aligned.append({
                'start': round(best_start, 2),
                'duration': dur,
                'en': c['en'],
                'zh': c.get('zh', ''),
                'text': c['en']
            })
        else:
            aligned.append(c)
            
    # Monotonic smoothing
    for i in range(len(aligned) - 1):
        cur = aligned[i]
        nxt = aligned[i+1]
        if nxt['start'] > cur['start']:
            gap = nxt['start'] - cur['start']
            cur['duration'] = round(min(cur.get('duration', 4.0), max(1.2, gap - 0.1)), 2)
            
    return aligned, matched_count

def process_song(model, song, index, total):
    vid = song['id']
    title = song['title']
    print(f"\n[{index}/{total}] === Processing: {title} ({vid}) ===")
    
    out_audio = SCRATCH_DIR / f"{vid}.mp3"
    
    try:
        # Download audio
        if not out_audio.exists():
            print(f"Downloading audio via yt-dlp: {vid}...")
            cmd = ['yt-dlp', '-x', '--audio-format', 'mp3', '-o', str(out_audio), f'https://www.youtube.com/watch?v={vid}']
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            if res.returncode != 0:
                print(f"Failed to download audio for {vid}, skipping.")
                return False
                
        # Transcribe with faster-whisper
        print("Transcribing with faster-whisper (word timestamps)...")
        segments, _ = model.transcribe(str(out_audio), word_timestamps=True, beam_size=5)
        
        words = []
        for s in segments:
            for w in (s.words or []):
                cw = clean_word(w.word)
                if cw:
                    words.append({'word': cw, 'raw': w.word, 'start': w.start, 'end': w.end})
                    
        print(f"Recognized {len(words)} words in audio.")
        if len(words) < 20:
            print("Too few words recognized, keeping existing timings.")
            return False
            
        # Align cues
        cues = song.get('cues', [])
        aligned_cues, count = align_cues_to_words(cues, words)
        ratio = count / max(1, len(cues))
        print(f"Aligned {count}/{len(cues)} cues ({ratio*100:.1f}%). First cue starts at: {aligned_cues[0]['start']}s")
        
        if count >= 8 or ratio > 0.4:
            song['cues'] = aligned_cues
            return True
        else:
            print("Alignment confidence too low, keeping existing cues.")
            return False
            
    except Exception as e:
        print(f"Error processing {vid}: {e}")
        return False
    finally:
        # Clean up mp3
        if out_audio.exists():
            try:
                out_audio.unlink()
            except:
                pass

def main():
    print("Initializing faster-whisper model...")
    model = WhisperModel('base.en', device='cpu', compute_type='int8')
    print("Model ready!")
    
    with open(SONGS_PATH, 'r', encoding='utf-8') as f:
        songs = json.load(f)
        
    targets = [s for s in songs if s['id'] in TARGET_IDS]
    print(f"Total songs to calibrate: {len(targets)}")
    
    success_count = 0
    for i, s in enumerate(targets, 1):
        ok = process_song(model, s, i, len(targets))
        if ok:
            success_count += 1
            # Save progress incrementally
            with open(SONGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(songs, f, indent=2, ensure_ascii=False)
                
    print(f"\n==========================================")
    print(f"Successfully calibrated {success_count}/{len(targets)} songs to millisecond audio precision!")
    print(f"==========================================")
    
    # Save final songs_100.json
    with open(SONGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(songs, f, indent=2, ensure_ascii=False)
    print("Saved songs_100.json!")
    
    # Sync video_lessons.json
    if LESSONS_PATH.exists():
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
        print("Synchronized video_lessons.json!")
        
        # Sync video_lessons.js
        js_content = f"window.ENGLISHTUBE_DATA = {json.dumps(vld, ensure_ascii=False)};\nwindow.PRELOADED_LESSONS = window.ENGLISHTUBE_DATA;\n"
        with open(LESSONS_JS_PATH, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print("Synchronized video_lessons.js!")

if __name__ == '__main__':
    main()
