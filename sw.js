// ENGLISHTUBE Service Worker v26
const CACHE='englishtube-v27';
const STATIC=[
  './',
  './index.html',
  './manifest.webmanifest',
  './icon.svg',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png',
  './video_lessons.js',
  './video_lessons.json',
  './songs_50.json'
];

// Install: pre-cache static shell & skip waiting immediately
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(STATIC)));
  self.skipWaiting();
});

// Activate: purge ALL stale caches & claim clients, then notify pages
self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
      .then(()=>self.clients.matchAll({type:'window'}))
      .then(clients=>clients.forEach(c=>c.postMessage({type:'SW_UPDATED',version:CACHE})))
  );
});

// Fetch: API=network-only, cross-origin=passthrough, static=stale-while-revalidate
self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET')return;
  const url=new URL(req.url);
  if(url.pathname.startsWith('/api/'))return;
  if(url.origin!==self.location.origin)return;
  event.respondWith(caches.open(CACHE).then(async cache=>{
    // For video_lessons files: ignore query string when matching cache
    const isLessons = url.pathname.endsWith('/video_lessons.js') || url.pathname.endsWith('/video_lessons.json');
    const cached = isLessons
      ? await cache.match(url.pathname.replace(/.*\//,'./'+url.pathname.split('/').pop()), {ignoreSearch:true})
      : await cache.match(req);
    const netFetch=fetch(req).then(res=>{if(res.ok)cache.put(req,res.clone());return res}).catch(()=>null);
    if(cached){event.waitUntil(netFetch);return cached;}
    const fresh=await netFetch;
    if(fresh)return fresh;
    if(req.mode==='navigate')return cache.match('./index.html');
  }));
});