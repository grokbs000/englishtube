/**
 * Cloudflare Worker: YouTube Transcript Proxy
 * 部署到 Cloudflare Workers 後，server.py 透過此 Worker 取得 YouTube 字幕
 * 解決 Render (AWS) IP 被 YouTube ASN 封鎖問題
 * 
 * 使用方式：GET /?v=VIDEO_ID&lang=en
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const vid = url.searchParams.get('v')
  const lang = url.searchParams.get('lang') || 'en'

  if (!vid) {
    return new Response(JSON.stringify({ error: 'Missing ?v=VIDEO_ID' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    })
  }

  try {
    // Step 1: 從 YouTube watch 頁面取得 ytInitialPlayerResponse
    const watchUrl = `https://www.youtube.com/watch?v=${vid}`
    const watchResp = await fetch(watchUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
      }
    })

    if (!watchResp.ok) {
      return errorJson(502, `YouTube watch page returned ${watchResp.status}`)
    }

    const html = await watchResp.text()

    // Step 2: 解析 ytInitialPlayerResponse
    const match = html.match(/ytInitialPlayerResponse\s*=\s*(\{.+?\})\s*;/)
    if (!match) {
      return errorJson(502, 'ytInitialPlayerResponse not found in page')
    }

    const playerResponse = JSON.parse(match[1])
    const captions = playerResponse?.captions?.playerCaptionsTracklistRenderer?.captionTracks || []

    if (captions.length === 0) {
      return new Response(JSON.stringify({ cues: [], error: 'no_captions' }), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      })
    }

    // Step 3: 找到英文字幕軌
    let track = captions.find(t => t.languageCode === lang)
      || captions.find(t => t.languageCode?.startsWith('en'))
      || captions[0]

    if (!track?.baseUrl) {
      return errorJson(502, 'No suitable caption track found')
    }

    // Step 4: 取得字幕 XML（Cloudflare IP 不被 YouTube 封鎖）
    const captionUrl = track.baseUrl + '&fmt=json3'
    const captionResp = await fetch(captionUrl)
    if (!captionResp.ok) {
      return errorJson(502, `Caption fetch failed: ${captionResp.status}`)
    }

    const captionData = await captionResp.json()
    const events = captionData.events || []

    const cues = []
    for (const e of events) {
      const text = (e.segs || []).map(s => s.utf8 || '').join('').trim()
      if (text && text.length > 1) {
        cues.push({
          start: Math.round(parseFloat(e.tStartMs || 0) / 10) / 100,
          duration: Math.max(0.5, Math.round(parseFloat(e.dDurationMs || 2000) / 10) / 100),
          text: text
        })
      }
    }

    return new Response(JSON.stringify({
      cues,
      lang: track.languageCode,
      title: playerResponse?.videoDetails?.title || ''
    }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    })

  } catch (err) {
    return errorJson(500, String(err))
  }
}

function errorJson(status, msg) {
  return new Response(JSON.stringify({ cues: [], error: msg }), {
    status,
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
  })
}
