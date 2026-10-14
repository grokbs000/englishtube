#!/usr/bin/env python3
"""Local ENGLISHTUBE web server + optional transcript/AI APIs."""
import json, os, re, shutil, subprocess, tempfile, urllib.request, urllib.error
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent
YOUTUBE_ID=re.compile(r'^[A-Za-z0-9_-]{11}$')

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
            text=' '.join(txt).strip()
            if text and not text.startswith(('♪','[')):cues.append({'start':sec(a),'duration':max(0,sec(b)-sec(a)),'text':text})
        i+=1
    return cues

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,fmt,*args): print('[web]',fmt%args)
    def send_json(self,code,obj):
        data=json.dumps(obj,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length','0')); data=json.loads(self.rfile.read(min(n,1_000_000)) or b'{}')
            if self.path=='/api/transcript': self.transcript(data);return
            if self.path=='/api/translate': self.translate(data);return
            self.send_json(404,{'error':'API not found'})
        except Exception as e:self.send_json(500,{'error':str(e)[:500]})
    def transcript(self,data):
        url=str(data.get('url','')).strip();vid=video_id(url)
        ytdlp=shutil.which('yt-dlp')
        if not ytdlp:self.send_json(503,{'error':'尚未安裝 yt-dlp。執行：python3 -m pip install -r requirements.txt'});return
        with tempfile.TemporaryDirectory(prefix='englishtube-') as td:
            cmd=[ytdlp,'--no-warnings','--skip-download','--write-auto-subs','--write-subs','--sub-langs','en.*,en','--sub-format','vtt/best','-o',str(Path(td)/'%(id)s.%(ext)s'),url]
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
            files=list(Path(td).glob('*.vtt'))
            if not files:
                # Try machine-readable JSON3 if vtt isn't available
                cmd[cmd.index('--sub-format')+1]='json3/vtt/best'
                p=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
                files=list(Path(td).glob('*.vtt'))+list(Path(td).glob('*.json3'))
            if not files:
                msg=(p.stderr or '影片沒有可取得的英文字幕，或 YouTube 暫時限制存取。')[-700:]
                self.send_json(422,{'error':msg});return
            f=files[0]
            if f.suffix=='.vtt': cues=parse_vtt(f.read_text(encoding='utf-8',errors='replace'))
            else:
                raw=json.loads(f.read_text(encoding='utf-8',errors='replace'));cues=[]
                for e in raw.get('events',[]):
                    txt=''.join(seg.get('utf8','') for seg in e.get('segs',[])).strip()
                    if txt:cues.append({'start':e.get('tStartMs',0)/1000,'duration':e.get('dDurationMs',0)/1000,'text':txt})
            if not cues:self.send_json(422,{'error':'字幕檔存在，但沒有可用句子。'});return
            self.send_json(200,{'videoId':vid,'language':f.stem.split('.')[-1],'cues':cues[:3000]})
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
