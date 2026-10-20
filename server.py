#!/usr/bin/env python3
"""Local ENGLISHTUBE web server + optional transcript/AI APIs."""
import html, json, os, re, shutil, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error, urllib.parse, uuid
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent
YOUTUBE_ID=re.compile(r'^[A-Za-z0-9_-]{11}$')

def clean_sub_text(text):
    if not text:
        return ''
    s = html.unescape(text)
    if any(ent in s for ent in ('&gt;', '&lt;', '&amp;', '&#39;', '&quot;')):
        s = html.unescape(s)
    # Strip YouTube speaker transitions (>> or >)
    s = re.sub(r'(?:^|\s)(?:>>|>)(?:\s|$)', ' ', s)
    # Strip non-speech annotations like [Music], [Applause]
    s = re.sub(r'\[(?:music|applause|laughter|cheering|chuckles|groans)\]', '', s, flags=re.I)
    return re.sub(r'\s+', ' ', s).strip()

def video_id(url):
    u=urlparse(url)
    if u.scheme not in ('http','https') or u.hostname not in ('youtube.com','www.youtube.com','m.youtube.com','youtu.be','www.youtu.be','youtube-nocookie.com','www.youtube-nocookie.com'):
        raise ValueError('目前自動字幕只支援 YouTube 網址')
    vid=(u.path.strip('/').split('/')[1] if u.hostname.endswith('youtube.com') and u.path.startswith('/shorts/') else '')
    if not vid:
        from urllib.parse import parse_qs
        vid=parse_qs(u.query).get('v',[''])[0] or (u.path.strip('/').split('/')[-1] if 'youtu.be' in u.hostname else '')
    if not YOUTUBE_ID.match(vid): raise ValueError('無法辨識 YouTube 影片 ID')
    return vid

def parse_vtt(text):
    cues=[]; lines=text.replace('\r','').split('\n'); i=0
    def sec(t):
        t=t.strip().replace(',', '.'); parts=t.split(':');
        try:return sum(float(x)*60**(len(parts)-j-1) for j,x in enumerate(parts))
        except:return 0
    while i<len(lines):
        line=lines[i].strip()
        if '-->' in line:
            a,b=[x.strip().split(' ')[0] for x in line.split('-->',1)]
            i+=1; txt=[]
            while i<len(lines) and lines[i].strip():
                txt.append(re.sub(r'<[^>]+>','',lines[i].strip()));i+=1
            text=clean_sub_text(' '.join(txt))
            if text and not text.startswith(('♪','[')):cues.append({'start':sec(a),'duration':max(0,sec(b)-sec(a)),'text':text})
        i+=1
    return cues

def normalize_cues(cues):
    """
    自動校準每句字幕長度，防止 YouTube VTT 或粗切字幕跨越長配樂/長靜音。
    若簡短句子的 duration 被拉長跨入配樂，自動箝位至自然說話長度，
    確保前端配樂偵測器 (gap >= 2.0s) 自動啟動，字幕完全靜止。
    """
    for i in range(len(cues)):
        c = cues[i]
        text = c.get('text', '')
        words = text.split()
        num_words = max(1, len(words))
        # 自然語音最大合理長度 (保守估計每字 0.75s + 1.2s 寬限)
        max_natural_dur = round(num_words * 0.75 + 1.2, 2)
        cur_dur = c.get('duration', 0)
        if cur_dur > max_natural_dur + 1.5:
            c['duration'] = max_natural_dur
    return cues

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        old_no_proxy = os.environ.pop('NO_PROXY', None)
        old_no_proxy_lower = os.environ.pop('no_proxy', None)
        try:
            from faster_whisper import WhisperModel
            _whisper_model = WhisperModel('tiny.en', device='cpu', compute_type='int8')
        finally:
            if old_no_proxy is not None:
                os.environ['NO_PROXY'] = old_no_proxy
            if old_no_proxy_lower is not None:
                os.environ['no_proxy'] = old_no_proxy_lower
    return _whisper_model

DOWNLOADS_DIR = ROOT / 'downloads'
DOWNLOADS_DIR.mkdir(exist_ok=True)

def get_default_download_dir():
    # macOS/Linux default: ~/Downloads
    home_dl = Path.home() / 'Downloads'
    if home_dl.exists() and home_dl.is_dir():
        return home_dl
    return DOWNLOADS_DIR

download_tasks = {}
download_tasks_lock = threading.Lock()

def write_cues_to_subfile(dest_file, cues, sub_format='bilingual'):
    dest_file = Path(dest_file)
    is_vtt = dest_file.suffix.lower() == '.vtt'
    with open(dest_file, 'w', encoding='utf-8') as sf:
        if is_vtt:
            sf.write("WEBVTT\n\n")
        for idx, c in enumerate(cues, 1):
            start = float(c.get('start', 0.0))
            duration = float(c.get('duration', 2.0))
            end = max(start + 0.4, start + duration)
            st_m, st_s = divmod(start, 60)
            st_h, st_m = divmod(st_m, 60)
            en_m, en_s = divmod(end, 60)
            en_h, en_m = divmod(en_m, 60)
            en_text = (c.get('en') or c.get('text') or '').strip()
            zh_text = (c.get('zh') or '').strip()
            if sub_format in ('zh', 'zh_vtt'):
                text = zh_text or en_text
            elif sub_format in ('en', 'en_vtt'):
                text = en_text
            else: # bilingual: English on top, Chinese below
                text = f"{en_text}\n{zh_text}" if (en_text and zh_text) else (en_text or zh_text)
            
            if is_vtt:
                sf.write(f"{int(st_h):02d}:{int(st_m):02d}:{st_s:06.3f} --> {int(en_h):02d}:{int(en_m):02d}:{en_s:06.3f}\n{text}\n\n")
            else:
                sf.write(f"{idx}\n{int(st_h):02d}:{int(st_m):02d}:{st_s:06.3f}".replace('.', ',') + f" --> {int(en_h):02d}:{int(en_m):02d}:{en_s:06.3f}".replace('.', ',') + f"\n{text}\n\n")
    return dest_file

def run_batch_download_worker(task_id, video_ids, fmt, quality, target_dir=None):
    ytdlp = shutil.which('yt-dlp') or '/opt/homebrew/bin/yt-dlp' or '/usr/local/bin/yt-dlp'
    ffmpeg = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg' or '/usr/local/bin/ffmpeg'

    with download_tasks_lock:
        task = download_tasks.get(task_id)
    if not task:
        return

    dest_dir = Path(target_dir or task.get('downloadDir') or get_default_download_dir()).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    for item in task['items']:
        with download_tasks_lock:
            if task.get('cancelled'):
                item['status'] = 'cancelled'
                continue

        vid = item['id']
        url = f'https://www.youtube.com/watch?v={vid}'
        with download_tasks_lock:
            item['status'] = 'downloading'

        cues = item.get('cues') or []
        if not cues:
            # 預防機制：自動從本機教材庫 data/lessons/{vid}.json 與 songs_100.json 檢索回補，防止動態拆檔造成的 cues 遺失
            lesson_file = ROOT / 'data' / 'lessons' / f'{vid}.json'
            if lesson_file.exists():
                try:
                    with open(lesson_file, 'r', encoding='utf-8') as lf:
                        ldata = json.load(lf)
                        cues = ldata.get('cues') or []
                except Exception:
                    pass
            if not cues:
                songs_file = ROOT / 'songs_100.json'
                if songs_file.exists():
                    try:
                        with open(songs_file, 'r', encoding='utf-8') as sf:
                            for s in json.load(sf):
                                if s.get('id') == vid:
                                    cues = s.get('cues') or []
                                    break
                    except Exception:
                        pass

        clean_title = re.sub(r'[^\w\s\.-]', '', item.get('title', 'Video'))[:50].strip() or vid

        # Priority 1: If downloading subtitles and cues exist in EnglishTube library, export immediately!
        if fmt in ('sub', 'vtt', 'srt', 'zh_vtt', 'bilingual_vtt') and cues:
            target_ext = 'srt' if fmt == 'srt' else 'vtt'
            sub_file = dest_dir / f"{clean_title} [{vid}].{target_ext}"
            sub_type = 'zh' if fmt == 'zh_vtt' else 'bilingual'
            write_cues_to_subfile(sub_file, cues, sub_format=sub_type)
            with download_tasks_lock:
                item['status'] = 'completed'
                item['filename'] = sub_file.name
                item['filePath'] = str(sub_file)
                item['fileDir'] = str(dest_dir)
                item['size'] = sub_file.stat().st_size
            continue

        out_template = str(dest_dir / f'%(title).60s [{vid}].%(ext)s')
        cmd = [str(ytdlp), '--no-warnings', '--no-playlist']
        if ffmpeg:
            cmd.extend(['--ffmpeg-location', str(Path(ffmpeg).parent)])

        if fmt == 'mp3':
            cmd.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '0', '-o', out_template, url])
        elif fmt in ('sub', 'vtt', 'zh_vtt'):
            cmd.extend(['--skip-download', '--write-auto-subs', '--write-subs', '--sub-langs', 'en.*,en,en-US,en-orig,en-GB,en-CA,en-AU,zh.*', '--convert-subs', 'vtt', '-o', out_template, url])
        elif fmt == 'srt':
            cmd.extend(['--skip-download', '--write-auto-subs', '--write-subs', '--sub-langs', 'en.*,en,en-US,en-orig,en-GB,en-CA,en-AU,zh.*', '--convert-subs', 'srt', '-o', out_template, url])
        else: # mp4
            # 優先下載 Apple / QuickTime 原生相容之 H.264(AVC) + AAC(M4A)，徹底杜絕 VP9/Opus 造成的 QuickTime 黑畫面與「僅播放聲音」問題
            if quality == '1080p':
                format_spec = 'bv*[ext=mp4][vcodec^=avc1][height<=1080]+ba[ext=m4a]/bv*[vcodec^=avc1][height<=1080]+ba/bv*[height<=1080]+ba/b[height<=1080]/b'
                sort_spec = 'res:1080,vcodec:avc,acodec:m4a'
            elif quality == '720p':
                format_spec = 'bv*[ext=mp4][vcodec^=avc1][height<=720]+ba[ext=m4a]/bv*[vcodec^=avc1][height<=720]+ba/bv*[height<=720]+ba/b[height<=720]/b'
                sort_spec = 'res:720,vcodec:avc,acodec:m4a'
            else:
                format_spec = 'bv*[ext=mp4][vcodec^=avc1]+ba[ext=m4a]/bv*[vcodec^=avc1]+ba/bv*+ba/b'
                sort_spec = 'vcodec:avc,acodec:m4a'
            cmd.extend(['-f', format_spec, '-S', sort_spec, '--merge-output-format', 'mp4', '-o', out_template, url])

        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=360)
            matched = [f for f in dest_dir.iterdir() if f.is_file() and f'[{vid}]' in f.name]

            # QuickTime 相容性雙重保險：若來源僅提供 VP9/AV1/Opus，自動以 macOS 硬體加速轉碼為 H.264 + AAC
            if matched and fmt not in ('mp3', 'sub', 'vtt', 'srt', 'zh_vtt') and ffmpeg:
                target_video = matched[0]
                if target_video.suffix.lower() == '.mp4':
                    try:
                        probe_res = subprocess.run([
                            'ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name', '-of', 'json', str(target_video)
                        ], capture_output=True, text=True, timeout=10)
                        probe_data = json.loads(probe_res.stdout or '{}')
                        codecs = [s.get('codec_name') for s in probe_data.get('streams', [])]
                        needs_repair = any(c in ('vp9', 'av1', 'av01') for c in codecs) or 'opus' in codecs
                        if needs_repair:
                            fixed_tmp = target_video.with_name(target_video.stem + '.qtfix.mp4')
                            hw_ok = False
                            for vcodec_opt in (['h264_videotoolbox', '-b:v', '3000k'], ['libx264', '-preset', 'veryfast', '-crf', '22']):
                                conv_cmd = ['ffmpeg', '-y', '-i', str(target_video), '-c:v'] + vcodec_opt + ['-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(fixed_tmp)]
                                c_res = subprocess.run(conv_cmd, capture_output=True, timeout=180)
                                if c_res.returncode == 0 and fixed_tmp.exists() and fixed_tmp.stat().st_size > 1000:
                                    shutil.move(str(fixed_tmp), str(target_video))
                                    hw_ok = True
                                    break
                            if not hw_ok and fixed_tmp.exists():
                                fixed_tmp.unlink()
                    except Exception as pe:
                        print(f"[batch-download] QuickTime transcode check error for {vid}: {pe}")

            # If MP4 downloaded and we have EnglishTube cues, write companion bilingual subtitle!
            if matched and cues and fmt not in ('mp3', 'sub', 'vtt', 'srt', 'zh_vtt'):
                companion_sub = dest_dir / f"{clean_title} [{vid}].vtt"
                try:
                    write_cues_to_subfile(companion_sub, cues, sub_format='bilingual')
                except Exception as se:
                    print(f"[batch-download] Companion sub error for {vid}: {se}")
            
            # If subtitle download returned 429 or missing captions, fallback to Whisper AI transcription!
            if fmt in ('sub', 'vtt', 'srt', 'zh_vtt') and not matched:
                try:
                    with tempfile.TemporaryDirectory(prefix='englishtube-subdl-') as std:
                        tmp_audio = Path(std) / 'audio.webm'
                        subprocess.run([str(ytdlp), '-f', 'ba/140/251', '--no-warnings', '-o', str(tmp_audio), url], capture_output=True, timeout=45)
                        if tmp_audio.exists() and tmp_audio.stat().st_size > 1000:
                            model = get_whisper_model()
                            segments, _ = model.transcribe(str(tmp_audio), beam_size=1, vad_filter=True)
                            target_ext = 'vtt' if fmt in ('sub', 'vtt', 'zh_vtt') else 'srt'
                            sub_file = dest_dir / f"{clean_title} [{vid}].{target_ext}"
                            with open(sub_file, 'w', encoding='utf-8') as sf:
                                if target_ext == 'vtt':
                                    sf.write("WEBVTT\n\n")
                                for idx, s in enumerate(segments, 1):
                                    st_m, st_s = divmod(s.start, 60)
                                    st_h, st_m = divmod(st_m, 60)
                                    en_m, en_s = divmod(s.end, 60)
                                    en_h, en_m = divmod(en_m, 60)
                                    if target_ext == 'vtt':
                                        sf.write(f"{int(st_h):02d}:{int(st_m):02d}:{st_s:06.3f} --> {int(en_h):02d}:{int(en_m):02d}:{en_s:06.3f}\n{s.text.strip()}\n\n")
                                    else:
                                        sf.write(f"{idx}\n{int(st_h):02d}:{int(st_m):02d}:{st_s:06.3f}".replace('.', ',') + f" --> {int(en_h):02d}:{int(en_m):02d}:{en_s:06.3f}".replace('.', ',') + f"\n{s.text.strip()}\n\n")
                            matched = [sub_file]
                except Exception as we:
                    print(f"[batch-download] Whisper fallback error for {vid}: {we}")

            with download_tasks_lock:
                if matched:
                    f = matched[-1]
                    item['status'] = 'completed'
                    item['filename'] = f.name
                    item['filePath'] = str(f)
                    item['fileDir'] = str(dest_dir)
                    item['size'] = f.stat().st_size
                elif p.returncode == 0:
                    item['status'] = 'completed'
                    item['fileDir'] = str(dest_dir)
                else:
                    item['status'] = 'error'
                    item['error'] = (p.stderr or p.stdout or '下載失敗')[-180:].strip()
        except subprocess.TimeoutExpired:
            with download_tasks_lock:
                item['status'] = 'error'
                item['error'] = '下載逾時 (超過 6 分鐘)'
        except Exception as e:
            with download_tasks_lock:
                item['status'] = 'error'
                item['error'] = str(e)[:150]

    with download_tasks_lock:
        task['status'] = 'completed' if not task.get('cancelled') else 'cancelled'
        task['downloadDir'] = str(dest_dir)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,fmt,*args): print('[web]',fmt%args)
    def send_json(self,code,obj):
        data=json.dumps(obj,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
    def do_HEAD(self):
        super().do_HEAD()
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/dict':
            qs = urllib.parse.parse_qs(parsed.query)
            word = (qs.get('word', [''])[0]).strip().lower()
            self.lookup_dict(word)
            return
        if parsed.path == '/api/yt-search':
            qs = urllib.parse.parse_qs(parsed.query)
            query = (qs.get('q', [''])[0]).strip()
            try:
                start = max(1, int(qs.get('start', ['1'])[0]))
            except Exception:
                start = 1
            try:
                limit = min(50, max(5, int(qs.get('limit', ['30'])[0])))
            except Exception:
                limit = 30
            self.search_yt(query, start, limit)
            return

        if parsed.path in ('/api/download-status', '/api/batch_status'):
            qs = urllib.parse.parse_qs(parsed.query)
            tid = qs.get('taskId', [''])[0] or qs.get('task_id', [''])[0]
            with download_tasks_lock:
                t = download_tasks.get(tid)
            if t:
                items = t.get('items', [])
                total = len(items)
                completed = sum(1 for it in items if it.get('status') in ('completed', 'error', 'cancelled'))
                percent = int((completed / total * 100)) if total > 0 else 0
                resp = dict(t)
                resp['total'] = total
                resp['completed'] = completed
                resp['percent'] = percent
                target_d = t.get('downloadDir', str(get_default_download_dir()))
                for it in resp.get('items', []):
                    if it.get('filename'):
                        it['download_url'] = f'/api/download-file?file={urllib.parse.quote(it["filename"])}&dir={urllib.parse.quote(target_d)}'
                        size_mb = round(it.get('size', 0) / (1024 * 1024), 2)
                        it['file_size'] = f'{size_mb} MB' if size_mb > 0.05 else f'{round(it.get("size",0)/1024, 1)} KB'
                self.send_json(200, resp)
            else:
                self.send_json(404, {'error': 'Task not found'})
            return

        if parsed.path == '/api/get-download-dir':
            default_dir = str(get_default_download_dir())
            project_dir = str((ROOT / 'downloads').resolve())
            desktop_dir = str((Path.home() / 'Desktop').resolve())
            self.send_json(200, {
                'defaultDir': default_dir,
                'projectDir': project_dir,
                'desktopDir': desktop_dir
            })
            return

        if parsed.path in ('/api/open-folder', '/api/open_folder'):
            qs = urllib.parse.parse_qs(parsed.query)
            folder_path = (qs.get('path', [''])[0]).strip()
            file_path = (qs.get('file', [''])[0]).strip()
            
            target = None
            if file_path:
                fp = Path(os.path.expanduser(file_path)).resolve()
                if fp.exists():
                    if sys.platform == 'darwin':
                        subprocess.Popen(['open', '-R', str(fp)])
                        self.send_json(200, {'ok': True, 'revealed': str(fp)})
                        return
                    else:
                        target = fp.parent
            if not target:
                if folder_path:
                    target = Path(os.path.expanduser(folder_path)).resolve()
                else:
                    target = get_default_download_dir()
            
            target.mkdir(parents=True, exist_ok=True)
            try:
                if sys.platform == 'darwin':
                    subprocess.Popen(['open', str(target)])
                elif sys.platform.startswith('win'):
                    os.startfile(str(target))
                else:
                    subprocess.Popen(['xdg-open', str(target)])
                self.send_json(200, {'ok': True, 'opened': str(target)})
            except Exception as oe:
                self.send_json(500, {'error': str(oe)})
            return

        if parsed.path in ('/api/cancel-download', '/api/cancel_download'):
            qs = urllib.parse.parse_qs(parsed.query)
            tid = qs.get('taskId', [''])[0] or qs.get('task_id', [''])[0]
            with download_tasks_lock:
                if tid in download_tasks:
                    download_tasks[tid]['cancelled'] = True
            self.send_json(200, {'ok': True})
            return

        if parsed.path in ('/api/download-file', '/api/download_file'):
            qs = urllib.parse.parse_qs(parsed.query)
            fn = os.path.basename(qs.get('file', [''])[0])
            dir_param = (qs.get('dir', [''])[0]).strip()
            target_dir = Path(os.path.expanduser(dir_param)).resolve() if dir_param else get_default_download_dir()
            target = (target_dir / fn).resolve()
            if not target.exists():
                target = (DOWNLOADS_DIR / fn).resolve()
            if not target.exists() or not target.is_file():
                self.send_error(404, 'File not found')
                return
            try:
                flen = target.stat().st_size
                self.send_response(200)
                if fn.endswith('.mp4'):
                    self.send_header('Content-Type', 'video/mp4')
                elif fn.endswith('.mp3'):
                    self.send_header('Content-Type', 'audio/mpeg')
                elif fn.endswith('.vtt'):
                    self.send_header('Content-Type', 'text/vtt; charset=utf-8')
                elif fn.endswith('.srt'):
                    self.send_header('Content-Type', 'application/x-subrip; charset=utf-8')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                safe_ascii_name = re.sub(r'[^\w\.-]', '_', fn)
                encoded_name = urllib.parse.quote(fn)
                self.send_header('Content-Disposition', f'attachment; filename="{safe_ascii_name}"; filename*=UTF-8\'\'{encoded_name}')
                self.send_header('Content-Length', str(flen))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                with open(target, 'rb') as f:
                    shutil.copyfileobj(f, self.wfile, length=64*1024)
            except Exception as e:
                pass
            return
        # No-cache headers for index.html and sw.js to prevent stale SW cache
        if parsed.path in ('/', '/index.html', '/sw.js'):
            try:
                filepath = ROOT / ('index.html' if parsed.path in ('/', '/index.html') else 'sw.js')
                data = filepath.read_bytes()
                ct = 'text/html; charset=utf-8' if parsed.path != '/sw.js' else 'application/javascript; charset=utf-8'
                self.send_response(200)
                self.send_header('Content-Type', ct)
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(500, str(e))
            return
        super().do_GET()

    def lookup_dict(self, word):
        if not word:
            self.send_json(400, {'error': '請提供單字'})
            return

        cache_file = ROOT / 'dict_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    c = json.load(f)
                    if word in c and c[word].get('def'):
                        self.send_json(200, c[word])
                        return
            except Exception:
                pass

        try:
            url = f'https://dict.youdao.com/jsonapi?q={urllib.parse.quote(word)}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.5) as r:
                d = json.loads(r.read())
                ec = d.get('ec', {})
                w_list = ec.get('word', [])
                if w_list:
                    w = w_list[0]
                    usphone = w.get('usphone') or w.get('ukphone') or ''
                    ipa = f'/{usphone}/' if usphone else ''
                    trs = w.get('trs', [])
                    defs = []
                    for item in trs:
                        for line in item.get('tr', []):
                            txt = line.get('l', {}).get('i', [''])[0].strip()
                            if txt: defs.append(txt)
                    
                    if defs:
                        raw_def = '； '.join(defs[:3])
                        try:
                            from opencc import OpenCC
                            cc = OpenCC('s2twp')
                            clean_def = cc.convert(raw_def)
                        except Exception:
                            clean_def = raw_def
                        pos_m = re.match(r'^([a-z]+\.)\s*(.*)', clean_def)
                        pos = pos_m.group(1) if pos_m else '單字'
                        clean_def = pos_m.group(2) if pos_m else clean_def
                        res = {'word': word, 'ipa': ipa, 'pos': pos, 'def': clean_def, 'ex': ''}
                        try:
                            c = {}
                            if cache_file.exists():
                                with open(cache_file, 'r', encoding='utf-8') as f: c = json.load(f)
                            c[word] = res
                            with open(cache_file, 'w', encoding='utf-8') as f: json.dump(c, f, ensure_ascii=False, indent=2)
                        except Exception: pass
                        self.send_json(200, res)
                        return
        except Exception as e:
            print('[dict error]', e)

        self.send_json(200, {'word': word, 'ipa': '', 'pos': '單字', 'def': '點擊 🔊 聆聽真人發音，或點擊「＋ 收藏」加入單字庫。', 'ex': ''})

    def search_yt(self, query, start=1, limit=30):
        if not query:
            self.send_json(400, {'error': '請提供搜尋關鍵字'})
            return

        # Load all video IDs already included in project (songs + lessons)
        project_ids = set()
        try:
            songs_file = ROOT / 'songs_100.json'
            if songs_file.exists():
                with open(songs_file, 'r', encoding='utf-8') as f:
                    for s in json.load(f):
                        if s.get('id'): project_ids.add(s['id'])
        except Exception:
            pass
        try:
            index_file = ROOT / 'index.html'
            if index_file.exists():
                html_text = index_file.read_text(encoding='utf-8', errors='ignore')
                for v in re.findall(r"id:\s*'([A-Za-z0-9_-]{11})'", html_text):
                    project_ids.add(v)
        except Exception:
            pass

        # Load uncollected library for fallback / guarantee
        uncollected_lib = {}
        lib_file = ROOT / 'uncollected_curated_library.json'
        if lib_file.exists():
            try:
                with open(lib_file, 'r', encoding='utf-8') as f:
                    uncollected_lib = json.load(f)
            except Exception:
                pass

        # If it's a direct YouTube URL
        try:
            vid = video_id(query)
            if vid:
                if vid in project_ids:
                    self.send_json(200, []) # Excluded because already in project
                    return
                self.send_json(200, [{'id': vid, 'title': f'YouTube Video ({vid})', 'duration': 0, 'channel': 'YouTube'}])
                return
        except Exception:
            pass

        ytdlp = shutil.which('yt-dlp') or '/opt/homebrew/bin/yt-dlp' or '/usr/local/bin/yt-dlp'
        results = []
        seen = set()

        if ytdlp and (os.path.exists(str(ytdlp)) or shutil.which('yt-dlp')):
            search_max = start + limit + 25
            cmd = [
                str(ytdlp),
                '--flat-playlist',
                '--no-warnings',
                '--print', '%(id)s\t%(title)s\t%(duration)s\t%(uploader)s',
                '--playlist-start', str(start),
                '--playlist-end', str(start + limit - 1),
                f'ytsearch{search_max}:{query}'
            ]
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=18)
                for line in p.stdout.strip().split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split('\t')
                    if len(parts) >= 2 and YOUTUBE_ID.match(parts[0]):
                        vid = parts[0]
                        # 嚴格排除專案已收錄的影片與重複影片
                        if vid in project_ids or vid in seen:
                            continue
                        seen.add(vid)
                        title = parts[1] if len(parts) > 1 else 'YouTube Video'
                        dur = 0
                        try:
                            dur = int(float(parts[2])) if len(parts) > 2 and parts[2] not in ('NA', 'None', '') else 0
                        except Exception:
                            pass
                        channel = parts[3] if len(parts) > 3 and parts[3] not in ('NA', 'None', '') else 'YouTube'
                        results.append({
                            'id': vid,
                            'title': title,
                            'duration': dur,
                            'channel': channel
                        })
            except Exception as e:
                print('[search_yt warning]', e)

        # 若有本地精選庫中相符的教材，優先補充相符項目
        if uncollected_lib:
            q_lower = query.lower()
            is_general = q_lower in ('', 'all', 'english', 'english listening', 'ted-ed')
            matching_supplements = []
            general_supplements = []
            for cat, items in uncollected_lib.items():
                for item in items:
                    vid = item.get('id')
                    if not vid or vid in project_ids or vid in seen:
                        continue
                    title = item.get('title', '')
                    channel = item.get('channel', '')
                    if q_lower in title.lower() or q_lower in channel.lower() or q_lower in cat.lower():
                        matching_supplements.append(item)
                    elif is_general:
                        general_supplements.append(item)
            
            supplements = matching_supplements + (general_supplements if is_general else [])
            for item in supplements:
                vid = item['id']
                if vid not in seen and vid not in project_ids:
                    seen.add(vid)
                    results.append(item)
                    if len(results) >= (36 if is_general else limit):
                        break

        self.send_json(200, results)

    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length','0')); data=json.loads(self.rfile.read(min(n,1_000_000)) or b'{}')
            if self.path=='/api/transcript': self.transcript(data);return
            if self.path=='/api/translate': self.translate(data);return
            if self.path in ('/api/batch-download', '/api/batch_download'): self.start_batch_download(data);return
            self.send_json(404,{'error':'API not found'})
        except Exception as e:self.send_json(500,{'error':str(e)[:500]})

    def start_batch_download(self, data):
        vids = data.get('videoIds', [])
        fmt = data.get('format', 'mp4') # 'mp4' | 'mp3' | 'vtt' | 'srt' | 'sub'
        quality = data.get('quality', 'best')
        titles = data.get('titles', {}) # optional dict of {vid: title}

        # Also support { items: [{ id, title, url }] }
        raw_items = data.get('items', [])
        if raw_items:
            for it in raw_items:
                if isinstance(it, dict):
                    v_id = it.get('id') or ''
                    if not v_id and it.get('url'):
                        v_id = video_id(it.get('url')) or ''
                    if v_id:
                        vids.append(v_id)
                        if it.get('title'):
                            titles[v_id] = it['title']
                elif isinstance(it, str):
                    vids.append(it)
        
        valid_vids = []
        for v in vids:
            clean_v = str(v).strip()
            if YOUTUBE_ID.match(clean_v):
                if clean_v not in valid_vids: valid_vids.append(clean_v)
            else:
                try:
                    c_vid = video_id(clean_v)
                    if c_vid and c_vid not in valid_vids: valid_vids.append(c_vid)
                except Exception:
                    pass

        if not valid_vids:
            self.send_json(400, {'error': '未提供有效的 YouTube 影片 ID 或網址'})
            return

        task_id = 'dl_' + str(uuid.uuid4())[:8]
        custom_dir = (data.get('downloadDir') or data.get('download_dir') or '').strip()
        if custom_dir:
            target_dir = Path(os.path.expanduser(custom_dir)).resolve()
        else:
            target_dir = get_default_download_dir()
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            target_dir = get_default_download_dir()
            target_dir.mkdir(parents=True, exist_ok=True)

        items = []
        for vid in valid_vids:
            items.append({
                'id': vid,
                'title': titles.get(vid) or f'YouTube Video ({vid})',
                'status': 'queued',
                'filename': '',
                'filePath': '',
                'fileDir': str(target_dir),
                'size': 0,
                'error': ''
            })

        with download_tasks_lock:
            download_tasks[task_id] = {
                'id': task_id,
                'format': fmt,
                'quality': quality,
                'downloadDir': str(target_dir),
                'status': 'running',
                'createdAt': time.time(),
                'items': items
            }

        t = threading.Thread(target=run_batch_download_worker, args=(task_id, valid_vids, fmt, quality, target_dir), daemon=True)
        t.start()
        self.send_json(200, {'taskId': task_id, 'task_id': task_id, 'total': len(items), 'downloadDir': str(target_dir)})

    def transcript(self, data):
        url = data.get('url', '').strip()
        try:
            vid = video_id(url)
        except Exception as e:
            self.send_json(400, {'error': str(e)})
            return

        # 1. 優先使用官方 YouTube oEmbed 獲取標題（秒級回應，完全免疫雲端機房 IP 封鎖）
        title = ''
        try:
            oembed_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json'
            oembed_req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1)'})
            with urllib.request.urlopen(oembed_req, timeout=5) as oembed_resp:
                oembed_data = json.loads(oembed_resp.read().decode('utf-8'))
                title = oembed_data.get('title', '').strip()
        except Exception:
            pass

        # Priority 0: 若本地已有精準對齊教材（data/lessons 或 songs_100），秒級直出
        local_lesson_file = Path(ROOT) / 'data' / 'lessons' / f"{vid}.json"
        if local_lesson_file.exists():
            try:
                with open(local_lesson_file, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
                local_cues = local_data.get('cues', [])
                if local_cues and len(local_cues) >= 5:
                    print(f"[transcript] Found precision cached lesson for {vid} with {len(local_cues)} cues!")
                    self.send_json(200, {'videoId': vid, 'title': local_data.get('title') or title, 'language': 'en', 'cues': local_cues})
                    return
            except Exception as e:
                print(f"[transcript] Warning reading local lesson for {vid}: {e}")

        # Check songs_100.json
        songs_file = Path(ROOT) / 'songs_100.json'
        if songs_file.exists():
            try:
                with open(songs_file, 'r', encoding='utf-8') as f:
                    songs_list = json.load(f)
                for s in songs_list:
                    if s.get('id') == vid and s.get('cues') and len(s['cues']) >= 5:
                        print(f"[transcript] Found song in songs_100 for {vid} with {len(s['cues'])} cues!")
                        self.send_json(200, {'videoId': vid, 'title': s.get('title') or title, 'language': 'en', 'cues': s['cues']})
                        return
            except Exception as e:
                pass

        cues = []

        # Priority 1: 記憶體內 yt_dlp 抽取 (使用 mweb / android / ios 客戶端)
        # 完全免疫雲端機房 IP 封鎖與 Web PO Token 挑戰，直接提取官方簽章 JSON3 字幕串流
        try:
            import yt_dlp
            ydl_opts = {
                'skip_download': True,
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {'youtube': {'player_client': ['mweb', 'android', 'ios']}}
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not title:
                    title = info.get('title', '').strip()
                subs = info.get('subtitles', {}) or {}
                auto_subs = info.get('automatic_captions', {}) or {}

                target_url = None
                for s_dict in (subs, auto_subs):
                    for lang, formats in s_dict.items():
                        if lang.startswith('en'):
                            for f in formats:
                                if f.get('ext') == 'json3':
                                    target_url = f.get('url')
                                    break
                        if target_url:
                            break
                    if target_url:
                        break

                if target_url:
                    raw = ydl.urlopen(target_url).read().decode('utf-8')
                    events = json.loads(raw).get('events', [])
                    for e in events:
                        txt = ''.join(s.get('utf8', '') for s in e.get('segs', [])).strip()
                        txt = clean_sub_text(txt)
                        if txt and not (txt.startswith('[') and txt.endswith(']')) and not (txt.startswith('(') and txt.endswith(')')):
                            cues.append({
                                'start': round(float(e.get('tStartMs', 0) / 1000), 2),
                                'duration': max(0.5, round(float(e.get('dDurationMs', 0) / 1000), 2)),
                                'text': txt
                            })
                    if cues:
                        print(f"[transcript] In-process yt_dlp successfully extracted {len(cues)} cues for {vid}!")
        except Exception as ytdlp_proc_err:
            print(f"[transcript] In-process yt_dlp notice for {vid}: {ytdlp_proc_err}")

        # Priority 2: youtube_transcript_api 備援
        if not cues:
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                api = YouTubeTranscriptApi()
                transcript_list = api.list(vid)
                en_t = None
                try:
                    en_t = transcript_list.find_transcript(['en', 'en-US', 'en-GB', 'en-CA', 'en-AU', 'en-orig'])
                except Exception:
                    for t in transcript_list:
                        if t.language_code.startswith('en'):
                            en_t = t
                            break
                    if not en_t:
                        for t in transcript_list:
                            if t.is_translatable:
                                en_t = t.translate('en')
                                break
                if en_t:
                    snippets = en_t.fetch()
                    for snip in snippets:
                        txt = clean_sub_text(snip.text if hasattr(snip, 'text') else snip.get('text', ''))
                        if txt and not (txt.startswith('[') and txt.endswith(']')) and not (txt.startswith('(') and txt.endswith(')')):
                            s_time = float(snip.start if hasattr(snip, 'start') else snip.get('start', 0.0))
                            d_time = float(snip.duration if hasattr(snip, 'duration') else snip.get('duration', 2.0))
                            cues.append({'start': round(s_time, 2), 'duration': max(0.5, round(d_time, 2)), 'text': txt})
                    if cues:
                        print(f"[transcript] youtube_transcript_api successfully extracted {len(cues)} cues for {vid}!")
            except Exception as yte:
                print(f"[transcript] youtube_transcript_api notice for {vid}: {yte}")

        # Priority 3: 若無英文字幕，啟動優雅降級（Graceful Fallback）
        # 確保使用者依然能一鍵成功收錄任何新影片至自訂頻道，並支援 YouTube 原生 CC 字幕觀看
        if not cues:
            print(f"[transcript] Video {vid} has no automated English track, enabling Native CC learning fallback.")
            cues = [{
                'start': 0.0,
                'duration': 3600.0,
                'text': '📺 支援 YouTube 原生 CC 字幕（請點擊播放器右下角 [CC] 按鈕開啟觀看）'
            }]

        cues = normalize_cues(cues)
        self.send_json(200, {'videoId': vid, 'title': title or 'YouTube 英語教材', 'language': 'en', 'cues': cues[:3000]})

    def translate(self,data):
        key=os.getenv('OPENAI_API_KEY','').strip()
        if not key:self.send_json(503,{'error':'未設定 OPENAI_API_KEY；請在啟動伺服器前設定環境變數。'});return
        sentences=data.get('sentences',[])
        if not isinstance(sentences,list) or not sentences or len(sentences)>100:self.send_json(400,{'error':'每次請提供 1–100 句英文。'});return
        prompt='請將下列英文句子翻譯成自然繁體中文，並挑選最多 12 個值得學的單字/片語，附上繁中意思與簡短用法。保留原順序。只回傳 JSON，格式：{"sentences":[{"en":"原句","zh":"繁中翻譯"}],"words":[{"word":"片語","meaning":"繁中意思與簡短用法"}]}\n英文句子：'+json.dumps(sentences,ensure_ascii=False)
        body=json.dumps({'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'input':prompt}).encode()
        req=urllib.request.Request('https://api.openai.com/v1/responses',data=body,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=75) as r: resp=json.loads(r.read())
            out=''.join(c.get('text','') for item in resp.get('output',[]) for c in item.get('content',[]) if c.get('type')=='output_text')
            out=re.sub(r'^```(?:json)?\s*|\s*```$','',out.strip())
            result=json.loads(out);self.send_json(200,result)
        except urllib.error.HTTPError as e:self.send_json(502,{'error':'AI API 回應錯誤：'+e.read().decode(errors='replace')[:350]})
        except Exception as e:self.send_json(502,{'error':'無法解析 AI 回應：'+str(e)[:250]})

if __name__=='__main__':
    port=int(os.getenv('PORT','8885'))
    print(f'ENGLISHTUBE: http://localhost:{port}')
    print('API: auto transcript (yt-dlp), AI translation (OPENAI_API_KEY optional)')
    ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
