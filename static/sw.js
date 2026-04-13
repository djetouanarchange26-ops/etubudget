const CACHE = 'etubudget-v1'
const STATIC = [
    '/auth/login',
    '/static/style.css',
    '/static/app.js',
]

self.addEventListener('install', e => {
    e.waitUntil(
        caches.open(CACHE).then(cache => cache.addAll(STATIC))
    )
    self.skipWaiting()
})

self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
        )
    )
    self.clients.claim()
})

self.addEventListener('fetch', e => {
    // Pour les requêtes API — toujours réseau
    if (e.request.url.includes('/auth/') ||
        e.request.url.includes('/transactions') ||
        e.request.url.includes('/categories') ||
        e.request.url.includes('/stats')) {
        return
    }
    // Pour le reste — cache first
    e.respondWith(
        caches.match(e.request).then(r => r || fetch(e.request))
    )
})