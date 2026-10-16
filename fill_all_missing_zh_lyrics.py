#!/usr/bin/env python3
"""
Fill All Missing Traditional Chinese Lyrics in songs_100.json and video_lessons.json
Uses registered MyMemory API with batch processing and OpenCC s2twp for natural Taiwan Traditional Chinese.
"""

import os, sys, json, time, urllib.request, urllib.parse
import opencc

ROOT = os.path.dirname(os.path.abspath(__file__))
SONGS_PATH = os.path.join(ROOT, 'songs_100.json')
LESSONS_PATH = os.path.join(ROOT, 'video_lessons.json')
LESSONS_JS_PATH = os.path.join(ROOT, 'video_lessons.js')

cc = opencc.OpenCC('s2twp')

def clean_str(t):
    return ''.join(c.lower() for c in t if c.isalnum() or c.isspace()).strip()

def main():
    print("Loading songs_100.json and video_lessons.json...")
    with open(SONGS_PATH, 'r', encoding='utf-8') as f:
        songs = json.load(f)
        
    cache = {}
    if os.path.exists(LESSONS_PATH):
        with open(LESSONS_PATH, 'r', encoding='utf-8') as f:
            vld = json.load(f)
        for vid, lesson in vld.get('lessons', {}).items():
            for c in lesson.get('cues', []):
                en = clean_str(c.get('en') or c.get('text', ''))
                zh = (c.get('zh') or '').strip()
                if en and zh and en not in cache:
                    cache[en] = zh
                    
    # Find all empty lines in songs_100.json
    missing_texts = set()
    for s in songs:
        for c in s.get('cues', []):
            zh = (c.get('zh') or '').strip()
            en = (c.get('en') or c.get('text', '')).strip()
            c_en = clean_str(en)
            if not zh:
                if c_en in cache:
                    c['zh'] = cache[c_en]
                elif en:
                    missing_texts.add(en)
                    
    missing_list = list(missing_texts)
    print(f"Total unique missing lines to translate: {len(missing_list)}")
    
    # Batch translate in chunks of 15
    chunk_size = 15
    translated_count = 0
    for i in range(0, len(missing_list), chunk_size):
        chunk = missing_list[i : i + chunk_size]
        joined = '\n'.join(chunk)
        url = 'https://api.mymemory.translated.net/get?q=' + urllib.parse.quote(joined) + '&langpair=en|zh-TW&de=banson.study@gmail.com'
        req = urllib.request.Request(url, headers={'User-Agent': 'EnglishTube/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                raw_trans = data.get('responseData', {}).get('translatedText', '')
                t_lines = raw_trans.split('\n')
                for orig, trans in zip(chunk, t_lines):
                    if trans and not trans.startswith('MYMEMORY WARNING'):
                        zh_tw = cc.convert(trans).strip()
                        cache[clean_str(orig)] = zh_tw
                        translated_count += 1
        except Exception as e:
            print(f"Error on chunk {i}: {e}")
        time.sleep(0.3)
        print(f"Progress: {min(i + chunk_size, len(missing_list))}/{len(missing_list)} lines...")
        sys.stdout.flush()
        
    print(f"Translation complete! Successfully translated {translated_count} lines.")
    
    # Apply to all songs
    for s in songs:
        cues = s.get('cues', [])
        for c in cues:
            if not (c.get('zh') or '').strip():
                c_en = clean_str(c.get('en') or c.get('text', ''))
                if c_en in cache:
                    c['zh'] = cache[c_en]
        s['en'] = [c['en'] for c in cues]
        s['cn'] = [c['zh'] for c in cues]
        
    # Save songs_100.json
    with open(SONGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(songs, f, indent=2, ensure_ascii=False)
    print("Saved songs_100.json")
    
    # Sync video_lessons.json & video_lessons.js
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
        
        js_content = f"window.ENGLISHTUBE_DATA = {json.dumps(vld, ensure_ascii=False)};\nwindow.PRELOADED_LESSONS = window.ENGLISHTUBE_DATA;\n"
        with open(LESSONS_JS_PATH, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print("Synchronized video_lessons.js")

if __name__ == '__main__':
    main()
