import { access, copyFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

const [filmArgument, ...extra] = process.argv.slice(2);
if (extra.length) throw new Error('Usage: node build.mjs [path-to-full-film.mp4]');

const dist = new URL('./dist/', import.meta.url);
const film = filmArgument ? resolve(filmArgument) : new URL('./media/treker-original.mp4', import.meta.url);
const files = ['index.html', 'styles.css', 'player.js', 'assets/iottie-logo.png', 'assets/iottie-icon.png', 'assets/treker-cabin.webp', 'assets/treker-tray.webp']
  .map((name) => [new URL(`./site/${name}`, import.meta.url), name]);

for (const device of ['desktop', 'tablet', 'mobile']) {
  for (const extension of ['mp4', 'jpg']) {
    const name = `treker-${device}.${extension}`;
    files.push([new URL(`./media/hero/${name}`, import.meta.url), `assets/${name}`]);
  }
}
files.push([film, 'assets/treker.mp4']);

await Promise.all(files.map(([source]) => access(source)));
await mkdir(new URL('assets/', dist), { recursive: true });
for (const [source, destination] of files) await copyFile(source, new URL(destination, dist));
console.log(`Built ${fileURLToPath(dist)} with three hero renditions and full film.`);
