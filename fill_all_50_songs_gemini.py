#!/usr/bin/env python3
"""
fill_all_50_songs_gemini.py (v2 with multi-model fallback and robust rate limiting)
"""
import os, sys, json, time, re, urllib.request

API_KEY = os.environ.get('GEMINI_API_KEY')
if not API_KEY:
    print("Error: GEMINI_API_KEY not found in environment.")
    sys.exit(1)

MODELS = [
    'gemini-3.1-flash-lite',
    'gemini-2.5-flash-lite',
    'gemini-2.5-flash',
    'gemini-2.5-pro'
]

def parse_duration_to_seconds(dur_str):
    parts = dur_str.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 240

def generate_cues_for_song(song):
    title = song['title']
    speaker = song.get('speaker', '')
    dur_str = song.get('duration', '04:00')
    total_sec = parse_duration_to_seconds(dur_str)

    prompt = f"""You are an expert music lyric subtitle editor for English language learners in Taiwan.
Song: "{title}" by {speaker}
Song Duration: {dur_str} ({total_sec} seconds).

Task: Generate a complete, sequential array of timed subtitle cues covering the ENTIRE song lyrics from the first vocal line until the end of the song (~{total_sec - 10}s).
Requirements:
1. Cover ALL parts of the song: Verse 1, Chorus, Verse 2, Chorus, Bridge, Final Chorus, Outro.
2. Total number of cues should be between 25 and 45 cues so the user always has subtitles playing throughout the song.
3. Every cue must have:
   - "start": float or int seconds from start (monotonically increasing)
   - "duration": float or int seconds (typically 3.0 to 7.0 seconds)
   - "en": Accurate English lyric line
   - "zh": Natural, fluent Traditional Chinese (繁體中文，台灣常用語法與詞彙，避免簡體字或中國用語)
4. The first vocal cue should start around 10-25 seconds in, and the last cue should end near {total_sec - 10} seconds.

Output format: ONLY a valid JSON array of objects, no markdown formatting:
[
  {{"start": 12.0, "duration": 5.0, "en": "...", "zh": "..."}},
  ...
]
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json"
        }
    }

    for model_name in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    res = json.loads(resp.read().decode('utf-8'))
                    text = res['candidates'][0]['content']['parts'][0]['text'].strip()
                    if text.startswith('```'):
                        text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()
                    cues = json.loads(text)
                    if isinstance(cues, list) and len(cues) >= 15:
                        valid_cues = []
                        for c in cues:
                            if 'start' in c and 'en' in c and 'zh' in c:
                                valid_cues.append({
                                    "start": round(float(c['start']), 1),
                                    "duration": round(float(c.get('duration', 5.0)), 1),
                                    "en": str(c['en']).strip(),
                                    "zh": str(c['zh']).strip()
                                })
                        valid_cues.sort(key=lambda x: x['start'])
                        return valid_cues
            except urllib.error.HTTPError as e:
                print(f"  [{model_name}] HTTP {e.code}: {e.reason}")
                if e.code == 429:
                    time.sleep(8)
                else:
                    time.sleep(3)
            except Exception as e:
                print(f"  [{model_name}] error: {e}")
                time.sleep(3)

    return None

def update_index_and_lessons(songs):
    print("\nUpdating index.html with complete songs array...")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    compact_songs_json = json.dumps(songs, ensure_ascii=False)
    # Replace inline songs
    new_html = re.sub(
        r'const songs\s*=\s*\[.*?\];\s*window\.songs',
        f'const songs = {compact_songs_json};\nwindow.songs',
        html,
        flags=re.DOTALL
    )

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("✓ index.html successfully updated!")

    # Also update video_lessons.json for songs
    if os.path.exists('video_lessons.json'):
        with open('video_lessons.json', 'r', encoding='utf-8') as f:
            vl = json.load(f)
        lessons = vl.get('lessons', {})
        for s in songs:
            sid = s['id']
            if sid in lessons:
                lessons[sid]['cues'] = s['cues']
                lessons[sid]['en'] = s.get('en', [c['en'] for c in s['cues']])
                lessons[sid]['cn'] = s.get('cn', [c['zh'] for c in s['cues']])
        with open('video_lessons.json', 'w', encoding='utf-8') as f:
            json.dump(vl, f, ensure_ascii=False, indent=2)
        print("✓ video_lessons.json updated!")

    if os.path.exists('video_lessons.js'):
        with open('video_lessons.json', 'r', encoding='utf-8') as f:
            vl = json.load(f)
        with open('video_lessons.js', 'w', encoding='utf-8') as f:
            f.write("window.PRELOADED_LESSONS = " + json.dumps(vl, ensure_ascii=False) + ";\n")
        print("✓ video_lessons.js updated!")

def main():
    songs_file = 'songs_50.json'
    with open(songs_file, 'r', encoding='utf-8') as f:
        songs = json.load(f)

    updated_count = 0
    for i, song in enumerate(songs, 1):
        cues = song.get('cues', [])
        dur_sec = parse_duration_to_seconds(song.get('duration', '04:00'))
        
        # Check if song needs full cues
        if len(cues) < 20 or (cues and cues[-1]['start'] < dur_sec * 0.7):
            print(f"[{i}/50] Generating full cues for: {song['title']} ({song.get('speaker')}) - {song.get('duration')}...")
            new_cues = generate_cues_for_song(song)
            if new_cues:
                song['cues'] = new_cues
                song['en'] = [c['en'] for c in new_cues]
                song['cn'] = [c['zh'] for c in new_cues]
                updated_count += 1
                print(f"  ✓ Success! Got {len(new_cues)} cues (span: {new_cues[0]['start']}s - {new_cues[-1]['start'] + new_cues[-1]['duration']}s)")
                
                with open(songs_file, 'w', encoding='utf-8') as f:
                    json.dump(songs, f, ensure_ascii=False, indent=2)
            else:
                print(f"  ✗ Failed to generate cues for {song['title']}")
            
            time.sleep(2.5) # safe pause to avoid 429
        else:
            print(f"[{i}/50] {song['title']} already has {len(cues)} cues. Skipping.")

    print(f"\n==========================================")
    print(f"Finished generating! Total updated: {updated_count} songs.")
    print(f"==========================================")

    update_index_and_lessons(songs)

if __name__ == '__main__':
    main()
