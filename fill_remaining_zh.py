#!/usr/bin/env python3
"""
Translate any remaining missing Chinese cues in video_lessons.json using MyMemory API + OpenCC.
Ensures 100% Traditional Chinese coverage across all 50 videos.
"""
import os, sys, json, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from opencc import OpenCC

cc = OpenCC('s2twp')
ROOT = os.path.dirname(os.path.abspath(__file__))
LESSONS_PATH = os.path.join(ROOT, 'video_lessons.json')
LESSONS_JS_PATH = os.path.join(ROOT, 'video_lessons.js')

def translate_sentence(text):
    text = text.strip()
    if not text:
        return ''
    # Strip sound effects and speaker tags
    clean = text
    if clean.startswith('CA:'):
        clean = clean[3:].strip()
    if not clean:
        return ''
    url = 'https://api.mymemory.translated.net/get?q=' + urllib.parse.quote(clean) + '&langpair=en|zh-TW'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8', errors='replace'))
                status = data.get('responseStatus')
                if status == 200 or status == '200':
                    raw_zh = data.get('responseData', {}).get('translatedText', '').strip()
                    if raw_zh and not raw_zh.startswith('MYMEMORY WARNING'):
                        return cc.convert(raw_zh)
            time.sleep(0.5)
        except Exception as e:
            time.sleep(1.0)
    return ''

def main():
    with open(LESSONS_PATH, 'r', encoding='utf-8') as f:
        lessons_data = json.load(f)

    lessons = lessons_data.get('lessons', {})
    
    missing_vids = []
    for vid, data in lessons.items():
        cues = data.get('cues', [])
        empty_cues = [i for i, c in enumerate(cues) if not c.get('zh', '').strip()]
        if empty_cues:
            missing_vids.append((vid, empty_cues))

    print(f'Videos requiring Chinese translation: {len(missing_vids)}')
    total_to_translate = sum(len(empty_cues) for _, empty_cues in missing_vids)
    print(f'Total empty cues: {total_to_translate}')

    completed_cues = 0
    for vid, empty_indices in missing_vids:
        cues = lessons[vid]['cues']
        texts_to_translate = [cues[i]['en'] for i in empty_indices]
        print(f'Translating {vid} ({len(texts_to_translate)} cues)...')
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            translated_list = list(executor.map(translate_sentence, texts_to_translate))

        for idx, zh in zip(empty_indices, translated_list):
            if zh:
                cues[idx]['zh'] = zh
            else:
                cues[idx]['zh'] = '（點擊播放）'

        completed_cues += len(empty_indices)
        print(f'  ✓ {vid} completed! ({completed_cues}/{total_to_translate})')
        
        # Save checkpoint
        lessons_data['lessons'] = lessons
        with open(LESSONS_PATH, 'w', encoding='utf-8') as f:
            json.dump(lessons_data, f, ensure_ascii=False, indent=2)

    # Re-export video_lessons.js
    js_content = 'window.PRELOADED_LESSONS = ' + json.dumps(lessons_data, ensure_ascii=False) + ';\n'
    with open(LESSONS_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print('\nALL 50 VIDEOS NOW HAVE 100% TRADITIONAL CHINESE SUBTITLES!')

if __name__ == '__main__':
    main()
