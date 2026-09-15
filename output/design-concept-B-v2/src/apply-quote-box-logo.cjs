const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const generated = 'C:\\Users\\KIM TAEHYUNG\\.codex\\generated_images\\01a09feb-ecf2-74e2-8dec-635a9efd2663\\exec-7f04a861-9978-4866-9105-872c9b158153.png';
const target = path.join(root, '08-quote.png');
const backup = path.join(root, 'review', '08-quote-before-box-logo-correction.png');
const indexPath = path.join(root, 'index.html');
const readmePath = path.join(root, 'README.md');
const recordPath = path.join(root, 'quote-box-logo-correction.json');

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

const prompt = `Edit only the PNPLINE Chinese quote-form section image. Remove the white logo plate from the upper-left and restore the dark warehouse background. Add exactly one official PNPLINE logo directly to the foreground box, on the front vertical cardboard face to the right of the blue tape. Render it as printing on cardboard with correct perspective, texture, lighting, wide aspect ratio, PNP blue and LINE gray. Do not use a sticker or place another logo elsewhere. Preserve every other visual and text element.`;

fs.writeFileSync(recordPath, JSON.stringify({
  task: 'Correct the PNPLINE logo placement by printing it on the foreground box.',
  createdAt: new Date().toISOString(),
  inputSection: '08-quote.png',
  officialLogoReference: '../../resources/logo/PNP-LINE.webp',
  generatedSource: generated,
  output: '08-quote.png',
  backup: 'review/08-quote-before-box-logo-correction.png',
  dimensions: { width, height },
  prompt,
}, null, 2) + '\n');

let readme = fs.readFileSync(readmePath, 'utf8');
const heading = '## 견적 섹션 상자 로고 배치 수정';
if (!readme.includes(heading)) {
  readme += `\n\n${heading}\n\n좌측 상단의 로고 플레이트를 제거하고 공식 PNPLINE 로고를 전경 상자의 전면에 인쇄된 포장 그래픽으로 옮겼습니다. 로고는 파란 테이프 오른쪽의 골판지 면에 원근, 표면 질감, 조명을 반영해 한 번만 배치했습니다.\n\n- 현재 이미지: [08-quote.png](08-quote.png)\n- 좌측 상단 배치 보존본: [review/08-quote-before-box-logo-correction.png](review/08-quote-before-box-logo-correction.png)\n- 최초 무로고 보존본: [review/08-quote-before-logo.png](review/08-quote-before-logo.png)\n- 공식 로고 원본: [../../resources/logo/PNP-LINE.webp](../../resources/logo/PNP-LINE.webp)\n- 생성 기록: [quote-box-logo-correction.json](quote-box-logo-correction.json)\n`;
  fs.writeFileSync(readmePath, readme);
}

console.log(JSON.stringify({ target, backup, width, height, recordPath }, null, 2));
