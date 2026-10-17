#!/usr/bin/env python3
"""Local ENGLISHTUBE web server + optional transcript/AI APIs."""
import html, json, os, re, shutil, subprocess, tempfile, urllib.request, urllib.error, urllib.parse
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

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,fmt,*args): print('[web]',fmt%args)
    def send_json(self,code,obj):
        data=json.dumps(obj,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
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
                        from opencc import OpenCC
                        cc = OpenCC('s2twp')
                        raw_def = '； '.join(defs[:3])
                        clean_def = cc.convert(raw_def)
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

        # 首頁搜尋若少於 32 部且為第一頁，自精選未收錄庫補充 (保證 >= 36)
        if start == 1 and len(results) < 32 and uncollected_lib:
            q_lower = query.lower()
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
                    else:
                        general_supplements.append(item)
            
            for item in matching_supplements + general_supplements:
                vid = item['id']
                if vid not in seen and vid not in project_ids:
                    seen.add(vid)
                    results.append(item)
                    if len(results) >= 36:
                        break

        self.send_json(200, results)

    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length','0')); data=json.loads(self.rfile.read(min(n,1_000_000)) or b'{}')
            if self.path=='/api/transcript': self.transcript(data);return
            if self.path=='/api/translate': self.translate(data);return
            self.send_json(404,{'error':'API not found'})
        except Exception as e:self.send_json(500,{'error':str(e)[:500]})
    def transcript(self,data):
        url=str(data.get('url','')).strip();vid=video_id(url)
        ytdlp=shutil.which('yt-dlp') or '/opt/homebrew/bin/yt-dlp' or '/usr/local/bin/yt-dlp'
        if not os.path.exists(str(ytdlp)) and not shutil.which('yt-dlp'):
            self.send_json(503,{'error':'尚未安裝 yt-dlp。執行：python3 -m pip install -r requirements.txt'});return
        
        # Try fetching video title
        title = ''
        try:
            tp = subprocess.run([ytdlp, '--print', '%(title)s', '--no-warnings', url], capture_output=True, text=True, timeout=8)
            title = tp.stdout.strip().split('\n')[0]
        except Exception:
            pass

        cues = []
        with tempfile.TemporaryDirectory(prefix='englishtube-') as td:
            # 1. First attempt: download official/auto VTT subtitles via yt-dlp
            cmd=[ytdlp,'--no-warnings','--skip-download','--write-auto-subs','--write-subs','--sub-langs','en,en-orig,en-US','--sub-format','vtt/best','-o',str(Path(td)/'%(id)s.%(ext)s'),url]
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
            files=list(Path(td).glob('*.vtt'))
            if not files:
                cmd[cmd.index('--sub-format')+1]='json3/vtt/best'
                p=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
                files=list(Path(td).glob('*.vtt'))+list(Path(td).glob('*.json3'))
            
            if files:
                f=files[0]
                if f.suffix=='.vtt':
                    cues=parse_vtt(f.read_text(encoding='utf-8',errors='replace'))
                else:
                    raw=json.loads(f.read_text(encoding='utf-8',errors='replace'))
                    for e in raw.get('events',[]):
                        txt=''.join(seg.get('utf8','') for seg in e.get('segs',[])).strip()
                        txt = clean_sub_text(txt)
                        if txt:cues.append({'start':e.get('tStartMs',0)/1000,'duration':e.get('dDurationMs',0)/1000,'text':txt})

            # 2. If no subtitles (due to YouTube 429 or missing captions), use Whisper AI fallback!
            if not cues:
                print(f'[transcript] VTT subtitles not available or 429 for {vid}. Falling back to Whisper AI audio transcription...')
                audio_path = Path(td) / 'audio.webm'
                down_cmd = [ytdlp, '-f', 'ba/140/251', '--no-warnings', '-o', str(audio_path), url]
                down_p = subprocess.run(down_cmd, capture_output=True, text=True, timeout=90)
                if audio_path.exists() and audio_path.stat().st_size > 1000:
                    try:
                        model = get_whisper_model()
                        segments, info = model.transcribe(str(audio_path), beam_size=1, word_timestamps=True)
                        for s in segments:
                            words = list(s.words or [])
                            if not words:
                                txt = clean_sub_text(s.text)
                                if txt:
                                    cues.append({'start': round(s.start, 2), 'duration': max(0.5, round(s.end - s.start, 2)), 'text': txt})
                                continue

                            # 遇配樂或靜音中斷 (間隔 >= 2.2 秒) 自動斷句，避免配樂期間字句超前早顯
                            cur_words = []
                            for w in words:
                                if cur_words and (w.start - cur_words[-1].end >= 2.2):
                                    t_txt = clean_sub_text(' '.join(x.word.strip() for x in cur_words))
                                    if t_txt:
                                        w_start = round(cur_words[0].start, 2)
                                        w_dur = max(0.5, round(cur_words[-1].end - cur_words[0].start, 2))
                                        cues.append({
                                            'start': w_start,
                                            'duration': w_dur,
                                            'text': t_txt,
                                            'words': [{'w': clean_sub_text(x.word), 's': round(x.start, 2), 'e': round(x.end, 2)} for x in cur_words if clean_sub_text(x.word)]
                                        })
                                    cur_words = []
                                cur_words.append(w)
                            if cur_words:
                                t_txt = clean_sub_text(' '.join(x.word.strip() for x in cur_words))
                                if t_txt:
                                    w_start = round(cur_words[0].start, 2)
                                    w_dur = max(0.5, round(cur_words[-1].end - cur_words[0].start, 2))
                                    cues.append({
                                        'start': w_start,
                                        'duration': w_dur,
                                        'text': t_txt,
                                        'words': [{'w': clean_sub_text(x.word), 's': round(x.start, 2), 'e': round(x.end, 2)} for x in cur_words if clean_sub_text(x.word)]
                                    })
                        print(f'[transcript] Whisper AI successfully generated {len(cues)} precision cues for {vid}!')
                    except Exception as we:
                        print(f'[transcript] Whisper AI error: {we}')

            if not cues:
                msg=(p.stderr or '影片沒有可取得的英文字幕，且語音辨識暫時無法解析。')[-700:]
                self.send_json(422,{'error':msg, 'title': title});return
            
            self.send_json(200,{'videoId':vid,'title':title,'language':'en','cues':cues[:3000]})
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
