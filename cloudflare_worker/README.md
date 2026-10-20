# YouTube Transcript Proxy — Cloudflare Worker

## 為什麼需要這個？

Render (AWS) 的 IP 位址被 YouTube ASN 黑名單封鎖，無法直接抓取字幕。
這個 Cloudflare Worker 部署在 Cloudflare Edge（非 AWS），YouTube 不封鎖 Cloudflare IP，
讓 EnglishTube 後端可以透過它繞過 IP 封鎖取得字幕。

## 部署步驟（5 分鐘完成）

### 方法 A：Cloudflare Dashboard（最簡單）

1. 登入 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 左側選單 → **Workers & Pages** → **Create Application** → **Create Worker**
3. 點 **Edit Code**，把 `yt_transcript_worker.js` 的內容完整貼上
4. 點 **Deploy** → 複製 Worker URL（格式：`https://xxx.workers.dev`）
5. 到 Render 後台 → **Environment** → 新增環境變數：
   ```
   YT_WORKER_URL = https://xxx.workers.dev
   ```
6. 完成！Render 重啟後所有新影片都能自動取得字幕

### 方法 B：Wrangler CLI

```bash
npm install -g wrangler
wrangler login
cd cloudflare_worker
wrangler deploy yt_transcript_worker.js --name yt-transcript-proxy
```

## 免費額度

Cloudflare Workers 免費方案：**每天 100,000 次請求**，對 EnglishTube 完全足夠。

## 測試

```bash
curl "https://YOUR_WORKER_URL.workers.dev/?v=09R8_2nJtjg&lang=en" | python3 -c "import sys,json; d=json.load(sys.stdin); print('cues:', len(d.get('cues',[])), '| title:', d.get('title','')[:30])"
```

## 使用時機

`server.py` 的優先順序：
- Priority 0: 本地快取
- Priority 1: youtube-transcript-api（有代理時用代理）  
- **Priority 1.5: 此 CF Worker（設定 YT_WORKER_URL 後啟用）← 推薦**
- Priority 2: yt-dlp 多客戶端
- Priority 3: 原生 CC 降級
