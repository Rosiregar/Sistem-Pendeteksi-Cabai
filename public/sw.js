/**
 * Service Worker untuk Sistem Informasi Patologi Cabai
 * Menggunakan strategi Stale-While-Revalidate untuk performa instan dan dukungan offline.
 */

const CACHE_NAME = "chili-v1-cache";
const OFFLINE_URL = "/index.html";

// Aset statis inti yang selalu didefinisikan secara eksplisit
const INITIAL_ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
  "/icon.svg"
];

// Pasang Service Worker (Install)
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[Service Worker] Mencadangkan cangkang aplikasi awal...");
      return cache.addAll(INITIAL_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Aktifkan Service Worker (Activate & bersihkan cache lama jika ada)
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log("[Service Worker] Menghapus cache lama:", key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Tangani Penarikan Data (Fetch)
self.addEventListener("fetch", (event) => {
  // Hanya proses permintaan GET
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);

  // Jangan cache permintaan API, Firebase, Google Authentication, atau modul eksternal
  if (
    url.pathname.startsWith("/api") ||
    url.hostname.includes("firebase") ||
    url.hostname.includes("googleapis") ||
    url.hostname.includes("vercel.app") ||
    url.hostname.includes("doubleclick")
  ) {
    return;
  }

  // Menggunakan strategi Stale-While-Revalidate
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Ambil versi terbaru di latar belakang untuk memperbarui cache
        fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse.status === 200) {
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(event.request, networkResponse);
              });
            }
          })
          .catch((err) => {
            console.warn("[Service Worker] Gagal sinkronisasi latar belakang offline:", err);
          });

        return cachedResponse;
      }

      // Jika tidak di cache, ambil langsung dari jaringan internet
      return fetch(event.request)
        .then((networkResponse) => {
          // Jangan simpan respons tidak valid
          if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== "basic") {
            return networkResponse;
          }

          // Klon respons dan simpan ke cache
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });

          return networkResponse;
        })
        .catch(() => {
          // Jika sepenuhnya luring (offline) dan user membuka halaman utama
          if (event.request.mode === "navigate") {
            return caches.match(OFFLINE_URL);
          }
        });
    })
  );
});
