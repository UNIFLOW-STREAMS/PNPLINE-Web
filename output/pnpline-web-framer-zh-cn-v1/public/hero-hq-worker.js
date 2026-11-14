const cacheName = "pnpline-hero-hq";
const blockSize = 512 * 1024;
const pendingBlocks = new Map();

self.addEventListener("install", event => event.waitUntil(self.skipWaiting()));
self.addEventListener("activate", event => event.waitUntil(self.clients.claim()));

self.addEventListener("fetch", event => {
  const {request} = event;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin ||
      !/^\/assets\/video\/hero-scroll-(desktop|tablet|mobile)-hq-v\d+\.mp4$/.test(url.pathname)) return;

  const operation = url.searchParams.get("hero-hq");
  const asset = new URL(url.pathname, url.origin).href;
  if (operation === "play") {
    event.respondWith(play(asset, request.headers.get("range")).catch(unavailable));
  } else if (operation === "fill") {
    const offset = Number(url.searchParams.get("offset"));
    if (!Number.isSafeInteger(offset) || offset < 0 || offset % blockSize) {
      event.respondWith(new Response(null, {status: 400}));
      return;
    }
    event.respondWith(fill(asset, offset).catch(error =>
      error instanceof InvalidRange ? new Response(null, {status: 502}) : unavailable()));
  }
});

function unavailable() {
  return new Response(null, {status: 503});
}

class InvalidRange extends Error {}

async function getBlock(asset, offset, priority) {
  const key = `${asset}?hero-hq=block&offset=${offset}`;
  const existing = pendingBlocks.get(key);
  if (existing) return existing;

  const load = async () => {
    const cache = await caches.open(cacheName).catch(() => undefined);
    const saved = await cache?.match(key).catch(() => undefined);
    if (saved) {
      return {blob: await saved.blob(), total: Number(saved.headers.get("x-hero-size")), stored: true};
    }

    const end = offset + blockSize - 1;
    const response = await fetch(asset, {
      headers: {Range: `bytes=${offset}-${end}`},
      cache: "no-store",
      priority,
    });
    const range = /^bytes (\d+)-(\d+)\/(\d+)$/.exec(response.headers.get("content-range") || "");
    const total = Number(range?.[3]);
    if (response.status !== 206 || !range || Number(range[1]) !== offset ||
        !Number.isSafeInteger(total) || total <= offset || Number(range[2]) !== Math.min(end, total - 1)) {
      await response.body?.cancel();
      if (response.status === 200 || response.status === 206 || response.status === 416) {
        throw new InvalidRange("Invalid HQ video range");
      }
      throw new Error("HQ video request failed");
    }
    const blob = await response.blob();
    if (blob.size !== Math.min(blockSize, total - offset)) throw new Error("Incomplete HQ video range");

    // Store the payload under its own key because Cache Storage rejects HTTP 206 responses.
    const stored = await cache?.put(key, new Response(blob, {headers: {"x-hero-size": String(total)}}))
      .then(() => true, () => false);
    return {blob, total, stored};
  };

  const block = load().finally(() => pendingBlocks.delete(key));
  pendingBlocks.set(key, block);
  return block;
}

function parseRange(header, size) {
  if (!header) return {start: 0, end: size - 1};
  const match = /^bytes=(\d*)-(\d*)$/.exec(header);
  if (!match || (!match[1] && !match[2])) return null;
  const start = match[1] ? Number(match[1]) : Math.max(0, size - Number(match[2]));
  const end = match[1] && match[2] ? Math.min(Number(match[2]), size - 1) : size - 1;
  return Number.isSafeInteger(start) && start <= end ? {start, end} : null;
}

async function play(asset, rangeHeader) {
  const first = await getBlock(asset, 0, "high");
  const range = parseRange(rangeHeader, first.total);
  if (!range) {
    return new Response(null, {status: 416, headers: {"Content-Range": `bytes */${first.total}`}});
  }

  const {start} = range;
  const end = rangeHeader && /^bytes=\d+-$/.test(rangeHeader)
    ? Math.min(range.end, (Math.floor(start / blockSize) + 1) * blockSize - 1)
    : range.end;
  let position = start;
  let cancelled = false;
  const stream = new ReadableStream({
    async pull(controller) {
      const offset = Math.floor(position / blockSize) * blockSize;
      const block = offset === 0 ? first : await getBlock(asset, offset, "high");
      if (cancelled) return;
      if (block.total !== first.total) throw new Error("HQ video size changed");
      const limit = Math.min(end + 1, offset + block.blob.size);
      const bytes = await block.blob.slice(position - offset, limit - offset).arrayBuffer();
      if (cancelled) return;
      controller.enqueue(new Uint8Array(bytes));
      position = limit;
      if (position > end) controller.close();
    },
    cancel() {
      cancelled = true;
    },
  });
  const headers = new Headers({
    "Accept-Ranges": "bytes",
    "Content-Type": "video/mp4",
    "Content-Length": String(end - start + 1),
  });
  if (rangeHeader) headers.set("Content-Range", `bytes ${start}-${end}/${first.total}`);
  return new Response(stream, {status: rangeHeader ? 206 : 200, headers});
}

async function fill(asset, offset) {
  const block = await getBlock(asset, offset, "low");
  if (!block.stored) return new Response(null, {status: 507});
  const next = offset + blockSize;
  if (next < block.total) return Response.json({next});

  const cache = await caches.open(cacheName);
  // Each fill starts at zero and advances only after a block is committed.
  const committed = await cache.put(`${asset}?hero-hq=complete`, new Response(null))
    .then(() => true, () => false);
  if (!committed) return new Response(null, {status: 507});
  return Response.json({next: null});
}
