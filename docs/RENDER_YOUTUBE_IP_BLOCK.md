# EnglishTube × Render 雲端部署技術手冊
## 🚨 YouTube 字幕抓取「雲端機房 IP 封鎖」完整解決方案

> **版本**：v1.0 · 2026-10-20  
> **適用範圍**：所有 Render / AWS / GCP / Azure / Fly.io / Railway / Vercel Serverless 部署

---

## 一、問題根源（Root Cause）

### 1.1 確診現象

在 Render 線上站台（`https://englishtube-tw.onrender.com`）嘗試收錄新影片時：

| 症狀 | 錯誤訊息 |
|---|---|
| `youtube-transcript-api` | `IpBlocked: YouTube is blocking requests from your IP...` |
| `yt-dlp` (Web client) | `Failed to extract any player response` |
| `yt-dlp` (Android client) | `Read timed out (read timeout=6.0)` |
| 舊版 CLI subprocess | `Command timed out after 15 seconds` |

### 1.2 為什麼會發生？

YouTube 維護一份 **雲端機房 IP 黑名單**（ASN-level block），涵蓋：

- **AWS** 全部 Region（Render 使用 AWS Oregon / US-East）
- **Google Cloud Platform / Azure / Hetzner / OVH / DigitalOcean**

> ⚠️ **本地端能正常抓取，部署到雲端就失敗** —— 100% 因為 IP 黑名單，不是程式碼錯誤。

---

## 二、已踩過的陷阱（Pitfalls）

### ❌ 陷阱 1：加大 subprocess timeout
```python
subprocess.run(cmd, timeout=15)   # 根本不夠
subprocess.run(cmd, timeout=60)   # 更長也無用，問題在 IP 不在時間
```
**教訓**：timeout 值再大都沒用，YouTube 根本不回應雲端 IP 的請求。

### ❌ 陷阱 2：多客戶端疊加（mweb + android + ios）
```python
# 三個客戶端會依序嘗試，每個都 timeout 6 秒 = 總共 18+ 秒掛死
extractor_args={'youtube': {'player_client': ['mweb', 'android', 'ios']}}
```
**教訓**：在雲端每個 client 都會 timeout，總等待時間線性疊加，前端 Cloudflare 先斷線。

### ❌ 陷阱 3：`en.*` 萬用字元語言選擇
```python
'subtitleslangs': ['en.*']   # 觸發 YouTube 429 Too Many Requests
```
**教訓**：只指定 `'en'`，或使用 `youtube-transcript-api` 精確查找。

### ❌ 陷阱 4：公開 Invidious 代理
```python
instances = ['inv.tux.pizza', 'invidious.nerdvpn.de', ...]
# 測試結果：全部失敗（timeout / 500 / SSL error）
```

### ❌ 絕對禁止：用 Google 帳號 cookie 繞過
```python
ydl_opts['cookiefile'] = 'cookies.txt'  # 帳號可能被永久封鎖！
```

---

## 三、最終架構（Production Solution）

### 3.1 後端字幕提取優先順序（server.py）

```
Priority 0: 本地快取優先
  └─ data/lessons/{vid}.json   → 秒出，完全免 YouTube 請求
  └─ songs_100.json            → 同上

Priority 1: youtube-transcript-api（帶代理支援）
  └─ 讀取 YOUTUBE_PROXY env → 走代理突破 IP 封鎖
  └─ 無代理時 → 本機有效，雲端被封

Priority 2: yt-dlp Android Client（帶代理支援）
  └─ socket_timeout=6, retries=1
  └─ 讀取 json3 格式字幕

Priority 3: Graceful Fallback（原生 CC 引導）
  └─ 返回 HTTP 200 + 原生 CC 提示 cue
  └─ 前端偵測 isFallbackOnly → 展開逐字稿貼上引導
```

### 3.2 前端智慧引導（isFallbackOnly 判斷）

```javascript
const isFallbackOnly = (cues.length === 1 && cues[0].text.includes('原生 CC'));
if (isFallbackOnly && !userTranscript) {
  // 顯示 3 步驟引導：YouTube「顯示文字稿」→ 複製 → 貼入
  // 按鈕：「📋 一鍵貼上逐字稿並建立」
  // 降級：「📺 依然以原生 CC 模式收錄」
}
```

### 3.3 parseCustomTranscript — 雙模式時間軸解析器

支援 YouTube「顯示文字稿」複製後的兩種格式：

```
格式 A：單行（時間戳 + 文字）
0:10 It is December 6, 2014.

格式 B：雙行（YouTube 標準複製格式）
0:10
It is December 6, 2014.
0:12
We are gonna drive across L.A.
```

---

## 四、根本修復：設定代理環境變數

### 4.1 在 Render 後台設定

1. 登入 [render.com](https://render.com) → 選擇 `englishtube-tw`
2. 進入 **Environment** 標籤
3. 新增：
   ```
   YOUTUBE_PROXY = http://username:password@proxy-host:port
   ```
4. **Save Changes** → 自動重啟容器

### 4.2 推薦代理服務商

| 服務 | 免費方案 | 備註 |
|---|---|---|
| [Webshare](https://www.webshare.io/) | 10 個住宅 IP 免費 | 最推薦 |
| 自建 VPS 代理 | 依 VPS 費用 | 台灣/日本節點最快 |
| Bright Data | 試用額度 | 高穩定，付費 |

### 4.3 代理讀取邏輯（server.py）

```python
yt_proxy = os.getenv('YOUTUBE_PROXY') or os.getenv('HTTPS_PROXY') or os.getenv('HTTP_PROXY')
proxies = {'http': yt_proxy, 'https': yt_proxy} if yt_proxy else None
api = YouTubeTranscriptApi(proxies=proxies) if proxies else YouTubeTranscriptApi()
if yt_proxy:
    ydl_opts['proxy'] = yt_proxy
```

---

## 五、影片類型對照表

| 類型 | 有字幕? | Render 可抓? | 建議 |
|---|---|---|---|
| TED / 演講 / 教學 | ✅ manual | ✅（有快取時） | 加入 `data/lessons/` |
| 音樂 MV（大廠） | ✅ manual | ❌ IP 封鎖 | 逐字稿 or 代理 |
| 個人 Vlog | ⚠️ auto CC | ❌ IP 封鎖 | 逐字稿 or 代理 |
| 電影片段 | ❌ 無 | ❌ | 原生 CC 模式 |

---

## 六、診斷工具

```bash
# 查看最近 10 次字幕請求日誌
curl https://englishtube-tw.onrender.com/api/transcript-recent

# 測試特定影片
curl -s -X POST https://englishtube-tw.onrender.com/api/transcript \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=VIDEO_ID"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('cues:', len(d.get('cues',[])), '| err:', d.get('debug',{}).get('yte_err','')[:80])"

# IpBlocked 在 yte_err = 確認 IP 封鎖
# Read timed out 在 ytdlp_err = yt-dlp 也被封鎖
```

---

## 七、修復 Commits 記錄

| Commit | 內容 |
|---|---|
| `e36234f` | in-process yt_dlp + Graceful Fallback 初版 |
| `86c3c4f` | 硬性 3.5s ThreadPool deadline + 單一 android client |
| `9a3d81a` | youtube-transcript-api 升為 Priority 1 |
| `96147cb` | `/api/transcript-recent` 診斷端點 |
| `3e1a833` | 正確保存 exception 字串 |
| `155f0db` | 代理 env var 支援 + 前端逐字稿貼上引導 |

---

## 八、核心守則（Engineering DNA）

> 1. YouTube IP 封鎖是 **ASN 級別**，唯一解是**代理**，無技術 hack 可繞過。
> 2. 所有網路請求必須設 **socket timeout ≤ 6s**，禁止無限等待。
> 3. 本地快取 `data/lessons/` 是最高優先，持續擴充常用英語教材庫。
> 4. 前端永遠不能因字幕失敗而卡死 UI，必須提供**至少一個可操作降級路徑**。
