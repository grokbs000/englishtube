// ENGLISHTUBE Service Worker v151
const CACHE='englishtube-v151';
const STATIC=[
  './',
  './index.html',
  './manifest.webmanifest',
  './icon.svg',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png',
  './songs_100.json',
  './songs_50.json',
  './uncollected_curated_library.json'
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

// Fetch: HTML/Navigation=Network-First (immediate updates), API=network-only, Static Assets=stale-while-revalidate
self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET')return;
  const url=new URL(req.url);
  if(url.pathname.startsWith('/api/'))return;
  if(url.origin!==self.location.origin)return;

  // HTML / Navigation -> Network-First (always fresh, offline fallback)
  if(req.mode==='navigate'||url.pathname==='/'||url.pathname.endsWith('index.html')){
    event.respondWith(
      fetch(req).then(res=>{
        if(res.ok){
          const clone=res.clone();
          caches.open(CACHE).then(c=>c.put(req,clone));
        }
        return res;
      }).catch(()=>caches.match('./index.html'))
    );
    return;
  }

  // Other static assets -> stale-while-revalidate
  event.respondWith(caches.open(CACHE).then(async cache=>{
    const cached = await cache.match(req);
    const netFetch=fetch(req).then(res=>{if(res.ok)cache.put(req,res.clone());return res}).catch(()=>null);
    if(cached){event.waitUntil(netFetch);return cached;}
    const fresh=await netFetch;
    if(fresh)return fresh;
  }));
});