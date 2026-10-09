const CACHE_NAME = 'munkoyo-musique-v2';
const urlsToCache = [
  '/'
];

// Installation du Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Interception des requêtes pour le mode hors ligne basique
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});