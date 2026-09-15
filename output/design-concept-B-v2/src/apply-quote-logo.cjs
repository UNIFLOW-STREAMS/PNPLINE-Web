const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const generated = 'C:\\Users\\KIM TAEHYUNG\\.codex\\generated_images\\01a09feb-ecf2-74e2-8dec-635a9efd2663\\exec-210a360a-172f-4378-a1e5-0c2c8118ac1b.png';
const target = path.join(root, '08-quote.png');
const backup = path.join(root, 'review', '08-quote-before-logo.png');
const indexPath = path.join(root, 'index.html');
const readmePath = path.join(root, 'README.md');
const recordPath = path.join(root, 'quote-logo-addition.json');

fs.mkdirSync(path.dirname(backup), { recursive: true });
if (!fs.existsSync(backup)) fs.copyFileSync(target, backup);
fs.copyFileSync(generated, target);

const png = fs.readFileSync(target);
if (png.toString('ascii', 1, 4) !== 'PNG') throw new Error('Generated output is not a PNG.');
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);

let index = fs.readFileSync(indexPath, 'utf8');
index = index.replace(
  /(<img class="scene-image" src="08-quote\.png" width=")\d+(" height=")\d+(" alt=")/,
  `$1${width}$2${height}$3`,
);
fs.writeFileSync(indexPath, index);

const prompt = `Edit IMAGE 1 only, the PNPLINE Chinese quote form section. IMAGE 2 is the official PNPLINE logo and must be used exactly as the visual source.

Preserve IMAGE 1's exact canvas, aspect ratio, warehouse photograph, blue-taped box, all Chinese headline and body copy, every form field and label, consent/privacy copy, CTA, positions, spacing, and colors. Make no other changes.

Add exactly one PNPLINE logo in the upper-left dark safe area, above “获取报价”. Place it on a compact white rounded-rectangle plate, approximately 11–13% of the canvas width, with comfortable inner padding, left-aligned with “获取报价”. Preserve the official logo's aspect ratio and its original PNP blue and LINE gray colors. Do not redraw, retype, recolor, stretch, crop, or alter the logo.

The logo plate must not overlap the eyebrow or headline. Do not add a second logo, a typed wordmark, a logo on the box, tape, or form, or any footer element. Output only the complete updated quote-section image.`;

fs.writeFileSync(recordPath, JSON.stringify({
  task: 'Add the official PNPLINE logo to the v2 quote section image.',
  createdAt: new Date().toISOString(),
  inputSection: '08-quote.png',
  officialLogoReference: '../../resources/logo/PNP-LINE.webp',
  generatedSource: generated,
  output: '08-quote.png',
  backup: 'review/08-quote-before-logo.png',
  dimensions: { width, height },
  prompt,
}, null, 2) + '\n');

let readme = fs.readFileSync(readmePath, 'utf8');
const heading = '## 견적 섹션 공식 PNPLINE 로고 추가';
if (!readme.includes(heading)) {
  readme += `\n\n${heading}\n\n첨부된 공식 PNP-LINE.webp를 참조해 견적 섹션 좌측 상단의 어두운 여백에 흰색 로고 플레이트를 추가했습니다. 로고는 한 번만 배치했으며 기존 창고 이미지, 중국어 카피, 폼 구성과 개인정보 문구는 유지했습니다.\n\n- 현재 이미지: [08-quote.png](08-quote.png)\n- 수정 전 보존본: [review/08-quote-before-logo.png](review/08-quote-before-logo.png)\n- 공식 로고 원본: [../../resources/logo/PNP-LINE.webp](../../resources/logo/PNP-LINE.webp)\n- 생성 기록: [quote-logo-addition.json](quote-logo-addition.json)\n`;
  fs.writeFileSync(readmePath, readme);
}

console.log(JSON.stringify({ target, backup, width, height, recordPath }, null, 2));
