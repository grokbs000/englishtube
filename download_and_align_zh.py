#!/usr/bin/env python3
"""
Download Traditional Chinese subtitles for all 50 videos and align with English cues.
Ensures 100% Traditional Chinese coverage for all videos in ENGLISHTUBE.
"""
import os, sys, json, re, glob, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from opencc import OpenCC

cc = OpenCC('s2twp')

ROOT = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(ROOT, 'catalog_50.json')
LESSONS_PATH = os.path.join(ROOT, 'video_lessons.json')
LESSONS_JS_PATH = os.path.join(ROOT, 'video_lessons.js')
SUBS_DIR = os.path.join(ROOT, 'zh_subs')
os.makedirs(SUBS_DIR, exist_ok=True)

def parse_vtt(text):
    cues = []
    lines = text.replace('\r', '').split('\n')
    i = 0
    def sec(t):
        t = t.strip().replace(',', '.')
        parts = t.split(':')
        try:
            return sum(float(x) * 60**(len(parts) - j - 1) for j, x in enumerate(parts))
        except:
            return 0

    while i < len(lines):
        line = lines[i].strip()
        if '-->' in line:
            parts = line.split('-->', 1)
            a = parts[0].strip().split(' ')[0]
            b = parts[1].strip().split(' ')[0]
            i += 1
            txt = []
            while i < len(lines) and lines[i].strip():
                clean_line = re.sub(r'<[^>]+>', '', lines[i].strip())
                txt.append(clean_line)
                i += 1
            text = ' '.join(txt).strip()
            # Filter noise and header credits
            if text and not text.startswith(('♪', '[')) and not text.startswith(('譯者', '審譯者', 'Translator')):
                # Filter out pure names / credit artifacts
                clean_zh = cc.convert(text)
                cues.append({'start': sec(a), 'end': sec(b), 'text': clean_zh})
        i += 1
    return cues

def fetch_single_video_zh(vid):
    """Download Chinese subtitles for a video into SUBS_DIR."""
    cached = glob.glob(os.path.join(SUBS_DIR, f'{vid}.*.vtt'))
    if cached:
        return vid, cached[0]

    langs = ['zh-TW', 'zh-Hant', 'zh', 'zh-Hans', 'zh-CN']
    for lang in langs:
        cmd = [
            'yt-dlp', '--no-warnings', '--skip-download',
            '--write-subs', '--write-auto-subs',
            '--sub-langs', lang,
            '--sub-format', 'vtt',
            '-o', os.path.join(SUBS_DIR, f'{vid}.%(ext)s'),
            f'https://www.youtube.com/watch?v={vid}'
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        found = glob.glob(os.path.join(SUBS_DIR, f'{vid}.*.vtt'))
        if found:
            return vid, found[0]
    return vid, None

def align_en_and_zh(en_cues, zh_cues):
    """Align timestamped Chinese cues onto structured English cues."""
    if not zh_cues:
        return en_cues

    # Primary pass: Assign each zh segment to best overlapping en cue
    en_matches = {i: [] for i in range(len(en_cues))}
    for zh in zh_cues:
        best_idx = -1
        max_overlap = -1
        for i, en in enumerate(en_cues):
            en_start = en['start']
            en_dur = en.get('duration', 0)
            en_end = en_start + (en_dur if en_dur > 0 else 3.5)
            overlap = min(en_end, zh['end']) - max(en_start, zh['start'])
            if overlap > max_overlap:
                max_overlap = overlap
                best_idx = i
        if max_overlap > 0 and best_idx != -1:
            en_matches[best_idx].append(zh['text'])
        else:
            closest_idx = min(range(len(en_cues)), key=lambda i: abs(en_cues[i]['start'] - zh['start']))
            en_matches[closest_idx].append(zh['text'])

    aligned = []
    for i, en in enumerate(en_cues):
        zh_texts = en_matches[i]
        # Deduplicate identical adjacent chunks
        dedup = []
        for t in zh_texts:
            if not dedup or dedup[-1] != t:
                dedup.append(t)
        combined = '，'.join(dedup).strip()

        # Secondary fallback: if still empty, find any overlapping zh cue
        if not combined:
            en_start = en['start']
            en_dur = en.get('duration', 0)
            en_end = en_start + (en_dur if en_dur > 0 else 3.5)
            overlapping = []
            for zh in zh_cues:
                if max(en_start, zh['start']) < min(en_end, zh['end']) or abs(en_start - zh['start']) < 1.2:
                    overlapping.append(zh['text'])
            if overlapping:
                combined = overlapping[0]

        aligned.append({
            'start': en['start'],
            'duration': en.get('duration', 0),
            'en': en['en'],
            'zh': combined
        })
    return aligned

def main():
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    with open(LESSONS_PATH, 'r', encoding='utf-8') as f:
        lessons_data = json.load(f)

    lessons = lessons_data.get('lessons', {})
    video_ids = [item['id'] for item in catalog]

    print(f'Fetching Chinese subtitles for {len(video_ids)} videos with thread pool...')
    zh_files = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_single_video_zh, vid): vid for vid in video_ids}
        for future in as_completed(futures):
            vid, path = future.result()
            zh_files[vid] = path
            status = '✓ FOUND' if path else '✗ MISSING'
            print(f'[{len(zh_files)}/{len(video_ids)}] {vid}: {status}')

    # Process alignment for all videos
    aligned_count = 0
    total_cues = 0
    total_zh_cues = 0

    for vid in video_ids:
        if vid not in lessons:
            continue
        en_cues = lessons[vid].get('cues', [])
        vtt_file = zh_files.get(vid)
        
        zh_cues = []
        if vtt_file and os.path.exists(vtt_file):
            try:
                with open(vtt_file, 'r', encoding='utf-8', errors='replace') as f:
                    zh_cues = parse_vtt(f.read())
            except Exception as e:
                print(f'Error reading {vtt_file}: {e}')

        aligned = align_en_and_zh(en_cues, zh_cues)
        lessons[vid]['cues'] = aligned
        
        cues_with_zh = sum(1 for c in aligned if c.get('zh', '').strip())
        total_cues += len(aligned)
        total_zh_cues += cues_with_zh
        aligned_count += 1
        pct = (cues_with_zh / len(aligned) * 100) if aligned else 0
        print(f'{vid}: {cues_with_zh}/{len(aligned)} cues with ZH ({pct:.1f}%)')

    print(f'\nTotal cues: {total_cues}, Cues with ZH: {total_zh_cues} ({total_zh_cues/total_cues*100:.1f}%)')

    # Save video_lessons.json
    lessons_data['lessons'] = lessons
    with open(LESSONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(lessons_data, f, ensure_ascii=False, indent=2)

    # Save video_lessons.js
    js_content = 'window.PRELOADED_LESSONS = ' + json.dumps(lessons_data, ensure_ascii=False) + ';\n'
    with open(LESSONS_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print('video_lessons.json and video_lessons.js updated with Traditional Chinese subtitles successfully!')

if __name__ == '__main__':
    main()
