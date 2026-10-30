/* OptiMOB — service worker.
 *
 * NÃO editar o sw.js gerado: este é o modelo. O vite.config.ts (plugin
 * optimobPwa) preenche a versão e a lista de ficheiros nas duas constantes
 * abaixo no fim de cada build — a versão é um hash do conteúdo, então um
 * build novo = cache novo.
 *
 * Estratégia:
 *  - tudo o que o build gerou é pré-carregado na instalação (o app inteiro
 *    abre offline, incluindo fontes e a página do relatório);
 *  - navegação: rede primeiro (pega a versão nova), cache se estiver offline;
 *  - resto: cache primeiro.
 * A atualização NÃO é automática: o worker novo espera (waiting) até o
 * utilizador clicar em "Atualizar" no aviso do app (mensagem SKIP_WAITING) —
 * assim ninguém perde um modelo aberto a meio por um reload surpresa.
 */
const VERSION = "457f791e39"
const CACHE = 'optimob-' + VERSION
const PRECACHE = [
  "./assets/html2canvas-D6u0_z7V.js",
  "./assets/index.es-Dt4q_L_e.js",
  "./assets/main-q6vjKo2Q.js",
  "./assets/pdfBrand-D2-tpTYf.js",
  "./assets/pdfBrand-FJ_Vzwkt.css",
  "./assets/purify.es-7fJ1DZ6H.js",
  "./assets/report-BMD4B06x.css",
  "./assets/report-Bvyw2irI.js",
  "./favicon.svg",
  "./icons/apple-touch-icon.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/maskable-512.png",
  "./index.html",
  "./manifest.webmanifest",
  "./report.html"
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE.map((url) => new Request(url, { cache: 'reload' })))),
  )
})

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      for (const key of await caches.keys()) {
        if (key.startsWith('optimob-') && key !== CACHE) await caches.delete(key)
      }
      await self.clients.claim()
    })(),
  )
})

self.addEventListener('fetch', (event) => {
  const request = event.request
  if (request.method !== 'GET') return
  const url = new URL(request.url)
  if (url.origin !== self.location.origin) return

  if (request.mode === 'navigate') {
    event.respondWith(
      // no-cache: revalida sempre (o GitHub Pages serve as páginas com max-age=600 e a
      // página velha ficaria até 10 min a apontar para ficheiros antigos).
      fetch(request, { cache: 'no-cache' })
        .then((response) => {
          const copy = response.clone()
          caches.open(CACHE).then((cache) => cache.put(request, copy))
          return response
        })
        .catch(async () => {
          const exact = await caches.match(request, { ignoreSearch: true })
          if (exact) return exact
          const fallback = url.pathname.endsWith('report.html') ? './report.html' : './index.html'
          return caches.match(fallback)
        }),
    )
    return
  }

  event.respondWith(
    caches.match(request).then(
      (hit) =>
        hit ||
        fetch(request).then((response) => {
          if (response.ok) {
            const copy = response.clone()
            caches.open(CACHE).then((cache) => cache.put(request, copy))
          }
          return response
        }),
    ),
  )
})
