const fs = require('fs');

async function main() {
  const pages = await (await fetch('http://127.0.0.1:9332/json')).json();
  const page = pages.find((entry) => entry.type === 'page');
  if (!page) throw new Error('No renderable page found.');

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  const pending = new Map();
  let nextId = 0;

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (!message.id || !pending.has(message.id)) return;
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(message.error.message));
    else resolve(message.result);
  };

  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });

  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });

  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', {
    width: 1920,
    height: 1080,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await send('Page.reload', { ignoreCache: true });
  await new Promise((resolve) => setTimeout(resolve, 1800));

  const metrics = await send('Page.getLayoutMetrics');
  const height = Math.ceil(metrics.cssContentSize.height);
  const shot = await send('Page.captureScreenshot', {
    format: 'png',
    captureBeyondViewport: true,
    fromSurface: true,
    clip: { x: 0, y: 0, width: 1920, height, scale: 1 },
  });

  fs.writeFileSync('pnpline-home-concept-revised-v3.png', Buffer.from(shot.data, 'base64'));
  ws.close();
  console.log(`Rendered 1920x${height}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
