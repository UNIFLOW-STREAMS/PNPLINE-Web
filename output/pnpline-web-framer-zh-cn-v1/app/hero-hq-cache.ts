const cacheName = "pnpline-hero-hq";
const workerPath = "/hero-hq-worker.js";

export async function hasStoredHq(asset: string) {
  try {
    return Boolean(await window.caches.match(`${asset}?hero-hq=complete`, {cacheName}));
  } catch {
    return false;
  }
}

export async function enableHqWorker(signal: AbortSignal) {
  const workers = navigator.serviceWorker;
  if (!workers || signal.aborted) return false;
  const hasControl = () => workers.controller?.scriptURL === new URL(workerPath, location.href).href;
  if (hasControl()) return true;

  return new Promise<boolean>(resolve => {
    const finish = (ready: boolean) => {
      clearTimeout(timeout);
      signal.removeEventListener("abort", onAbort);
      workers.removeEventListener("controllerchange", onControl);
      resolve(ready);
    };
    const onControl = () => {
      if (hasControl()) finish(true);
    };
    const onAbort = () => finish(false);
    const timeout = window.setTimeout(onAbort, 4000);
    signal.addEventListener("abort", onAbort, {once: true});
    workers.addEventListener("controllerchange", onControl);
    workers.register(workerPath).then(onControl, onAbort);
    onControl();
  });
}

export async function fillHqCache(asset: string, signal: AbortSignal) {
  let offset: number | null = 0;
  while (offset !== null && !signal.aborted) {
    try {
      const response: Response = await fetch(`${asset}?hero-hq=fill&offset=${offset}`, {
        signal,
        cache: "no-store",
        priority: "low",
      });
      if (response.status === 502 || response.status === 507) return false;
      if (!response.ok) throw new Error("HQ download interrupted");
      const next: number | null = (await response.json()).next;
      if (next !== null && (!Number.isSafeInteger(next) || next <= offset)) return false;
      offset = next;
    } catch {
      if (signal.aborted) return false;
      // Retry the same block after transient network failures.
      await new Promise(resolve => window.setTimeout(resolve, 3000));
    }
  }
  return offset === null;
}
