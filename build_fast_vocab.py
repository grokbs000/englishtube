#!/usr/bin/env python3
"""
Pre-build comprehensive Traditional Chinese dictionary cache for ENGLISHTUBE.
Enriches video_lessons.json and video_lessons.js with 2,500+ top frequent words.
Provides 0ms instant dictionary lookup in client memory.
"""
import os, sys, json, re, time, urllib.request, urllib.parse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from opencc import OpenCC

cc = OpenCC('s2twp')

ROOT = os.path.dirname(os.path.abspath(__file__))
LESSONS_PATH = os.path.join(ROOT, 'video_lessons.json')
LESSONS_JS_PATH = os.path.join(ROOT, 'video_lessons.js')
CACHE_PATH = os.path.join(ROOT, 'dict_cache.json')

def fetch_word_definition(word):
    word = word.strip().lower()
    if not word or len(word) < 2:
        return None

    url = f'https://dict.youdao.com/jsonapi?q={urllib.parse.quote(word)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=3.5) as r:
                d = json.loads(r.read())
                ec = d.get('ec', {})
                words_list = ec.get('word', [])
                if not words_list:
                    return None
                w = words_list[0]
                usphone = w.get('usphone') or w.get('ukphone') or ''
                ipa = f'/{usphone}/' if usphone else ''

                trs = w.get('trs', [])
                defs = []
                for item in trs:
                    for line in item.get('tr', []):
                        txt = line.get('l', {}).get('i', [''])[0].strip()
                        if txt:
                            defs.append(txt)

                if not defs:
                    return None

                raw_def = '； '.join(defs[:3])
                clean_def = cc.convert(raw_def)
                pos_match = re.match(r'^([a-z]+\.)\s*(.*)', clean_def)
                if pos_match:
                    pos = pos_match.group(1)
                    clean_def = pos_match.group(2)
                else:
                    pos = '單字'

                return {
                    'word': word,
                    'ipa': ipa,
                    'pos': pos,
                    'def': clean_def,
                    'ex': ''
                }
        except Exception:
            time.sleep(0.5)
    return None

def main():
    with open(LESSONS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lessons = data.get('lessons', {})
    existing_vocab = data.get('vocab', {})

    # Load persistent cache if exists
    cache = {}
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    counter = Counter()
    for vid, lesson in lessons.items():
        for c in lesson.get('cues', []):
            words = re.findall(r'[a-zA-Z]+', c.get('en', '').lower())
            for w in words:
                if len(w) > 1:
                    counter[w] += 1

    # Filter words appearing >= 2 times
    target_words = [w for w, count in counter.most_common() if count >= 2]
    print(f"Total target frequent words to index: {len(target_words)}")

    to_fetch = []
    for w in target_words:
        if w in cache:
            existing_vocab[w] = cache[w]
        elif w in existing_vocab and existing_vocab[w].get('def'):
            cache[w] = existing_vocab[w]
        else:
            to_fetch.append(w)

    print(f"Already in cache: {len(target_words) - len(to_fetch)}, Fetching new: {len(to_fetch)}")

    if to_fetch:
        completed = 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_word = {executor.submit(fetch_word_definition, w): w for w in to_fetch}
            for future in as_completed(future_to_word):
                word = future_to_word[future]
                res = future.result()
                if res and res.get('def'):
                    cache[word] = res
                    existing_vocab[word] = res
                completed += 1
                if completed % 200 == 0 or completed == len(to_fetch):
                    print(f"  Fetched {completed}/{len(to_fetch)} words ({(completed/len(to_fetch)*100):.1f}%)...")

    # Save cache
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    # Save to video_lessons.json
    data['vocab'] = existing_vocab
    with open(LESSONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Export to video_lessons.js
    js_content = 'window.PRELOADED_LESSONS = ' + json.dumps(data, ensure_ascii=False) + ';\n'
    with open(LESSONS_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"\n🎉 Successfully compiled instant vocab dictionary!")
    print(f"Total instant words in memory: {len(existing_vocab)}")

if __name__ == '__main__':
    main()
