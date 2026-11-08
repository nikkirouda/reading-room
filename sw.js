/* The Reading Room — offline worker. Shell: network first, cache fallback. Books: cache first. */
const SHELL = 'rr-shell-v1', BOOKS = 'rr-books-v1';
const PRECACHE = ['./', 'index.html', 'shelf.json', 'manifest.webmanifest', 'fonts/fonts.css',
  'fonts/Literata-normal-400-700-latin.woff2', 'fonts/Literata-italic-400-700-latin.woff2',
  'fonts/IBMPlexSans-normal-400-latin.woff2', 'fonts/IBMPlexSans-normal-500-latin.woff2', 'fonts/IBMPlexSans-normal-600-latin.woff2',
  'icons/icon.svg', 'icons/icon-192.png', 'icons/icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(SHELL).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== SHELL && k !== BOOKS).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin || e.request.method !== 'GET') return;
  if (url.pathname.includes('/books/')) {
    e.respondWith(caches.open(BOOKS).then(async c => {
      const hit = await c.match(e.request); if (hit) return hit;
      const r = await fetch(e.request); if (r.ok) c.put(e.request, r.clone()); return r;
    }));
    return;
  }
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok) { const copy = r.clone(); caches.open(SHELL).then(c => c.put(e.request, copy)); }
    return r;
  }).catch(() => caches.match(e.request).then(h => h || (e.request.mode === 'navigate' ? caches.match('index.html') : Response.error()))));
});
