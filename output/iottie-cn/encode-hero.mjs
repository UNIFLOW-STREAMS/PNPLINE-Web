import { spawnSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const directory = new URL('./media/hero/', import.meta.url);
const input = fileURLToPath(new URL('./media/treker-original.mp4', import.meta.url));
mkdirSync(directory, { recursive: true });

// Reframe the cabin sequence per display. The bottom crop also removes the
// English captions embedded in the source frames.
const variants = [
  { name: 'desktop', crop: '1760:990:80:0', size: '1600:900', level: '4.0', crf: '23', maxRate: '2600k', buffer: '5200k' },
  { name: 'tablet', crop: '1320:990:260:0', size: '1024:768', level: '3.2', crf: '24', maxRate: '1600k', buffer: '3200k' },
  { name: 'mobile', crop: '792:990:374:0', size: '576:720', level: '3.1', crf: '25', maxRate: '950k', buffer: '1900k' },
];

function ffmpeg(args) {
  const result = spawnSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-nostdin', '-y', ...args], { stdio: 'inherit' });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`FFmpeg exited with status ${result.status}.`);
}

for (const variant of variants) {
  const mp4 = fileURLToPath(new URL(`treker-${variant.name}.mp4`, directory));
  const poster = fileURLToPath(new URL(`treker-${variant.name}.jpg`, directory));
  ffmpeg([
    '-ss', '22.4', '-i', input, '-t', '10.4', '-map', '0:v:0', '-an',
    '-vf', `crop=${variant.crop},fps=25,scale=${variant.size}:flags=lanczos,setsar=1`,
    '-c:v', 'libx264', '-preset', 'slow', '-profile:v', 'main', '-level:v', variant.level,
    '-pix_fmt', 'yuv420p', '-tag:v', 'avc1', '-crf', variant.crf,
    '-maxrate', variant.maxRate, '-bufsize', variant.buffer, '-g', '50',
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
    '-movflags', '+faststart', mp4,
  ]);
  ffmpeg(['-i', mp4, '-frames:v', '1', '-q:v', '3', '-update', '1', poster]);
  console.log(`Encoded ${variant.name}: ${variant.size.replace(':', ' × ')}`);
}
