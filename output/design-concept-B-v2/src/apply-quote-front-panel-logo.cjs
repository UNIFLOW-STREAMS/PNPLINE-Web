const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const generated = 'C:\\Users\\KIM TAEHYUNG\\.codex\\generated_images\\01a09feb-ecf2-74e2-8dec-635a9efd2663\\exec-ceafcc15-7930-475c-b701-be08f1a169b4.png';
const target = path.join(root, '08-quote.png');
const backup = path.join(root, 'review', '08-quote-before-front-panel-logo.png');
const indexPath = path.join(root, 'index.html');
const readmePath = path.join(root, 'README.md');
const recordPath = path.join(root, 'quote-front-panel-logo.json');

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

fs.writeFileSync(recordPath, JSON.stringify({
  task: 'Move the official PNPLINE logo into the user-marked area on the broad front box panel.',
  createdAt: new Date().toISOString(),
  inputSection: '08-quote.png',
  placementGuide: 'codex-clipboard-86524487-b72c-499a-9e45-4a506718f65f.png',
  officialLogoReference: '../../resources/logo/PNP-LINE.webp',
  generatedSource: generated,
  output: '08-quote.png',
  backup: 'review/08-quote-before-front-panel-logo.png',
  dimensions: { width, height },
  placement: 'Broad front cardboard panel, left of the vertical blue tape; direct-print treatment.',
  exclusions: ['upper-left logo plate', 'right-side-face logo', 'red placement annotation'],
}, null, 2) + '\n');

let readme = fs.readFileSync(readmePath, 'utf8');
const heading = '## 견적 섹션 상자 전면 로고 위치 확정';
if (!readme.includes(heading)) {
  readme += `\n\n${heading}\n\n사용자가 표시한 영역에 맞춰 공식 PNPLINE 로고를 전경 상자의 넓은 전면으로 이동했습니다. 로고는 파란 테이프 왼쪽의 골판지 면에 인쇄되며, 좌측 상단 플레이트와 오른쪽 측면 로고, 빨간 위치 표시는 제거했습니다.\n\n- 현재 이미지: [08-quote.png](08-quote.png)\n- 오른쪽 측면 배치 보존본: [review/08-quote-before-front-panel-logo.png](review/08-quote-before-front-panel-logo.png)\n- 공식 로고 원본: [../../resources/logo/PNP-LINE.webp](../../resources/logo/PNP-LINE.webp)\n- 생성 기록: [quote-front-panel-logo.json](quote-front-panel-logo.json)\n`;
  fs.writeFileSync(readmePath, readme);
}

console.log(JSON.stringify({ target, backup, width, height, recordPath }, null, 2));
