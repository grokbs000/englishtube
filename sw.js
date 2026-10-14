// ENGLISHTUBE Service Worker v13
const CACHE='englishtube-v13';
const STATIC=[
  './',
  './index.html',
  './manifest.webmanifest',
  './icon.svg',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png',
  './video_lessons.js',
  './video_lessons.json'
];

// Install: pre-cache static shell & skip waiting immediately
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(STATIC)));
  self.skipWaiting();
});

// Activate: purge ALL stale caches & claim clients immediately
self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

// Fetch: API=network-only, cross-origin=passthrough, static=stale-while-revalidate, nav fallback=index.html
self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET')return;
  const url=new URL(req.url);
  // API routes: never cache
  if(url.pathname.startsWith('/api/'))return;
  // Cross-origin (YouTube, CDN): passthrough
  if(url.origin!==self.location.origin)return;
  event.respondWith(caches.open(CACHE).then(async cache=>{
    const cached=await cache.match(req);
    const netFetch=fetch(req).then(res=>{if(res.ok)cache.put(req,res.clone());return res}).catch(()=>null);
    if(cached){event.waitUntil(netFetch);return cached;}
    const fresh=await netFetch;
    if(fresh)return fresh;
    if(req.mode==='navigate')return cache.match('./index.html');
  }));
});