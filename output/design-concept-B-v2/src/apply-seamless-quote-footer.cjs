const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const generated = 'C:\\Users\\KIM TAEHYUNG\\.codex\\generated_images\\01a09feb-ecf2-74e2-8dec-635a9efd2663\\exec-c45ed8ae-4851-41ce-81d2-b318ec796d18.png';
const quote = path.join(root, '08-quote.png');
const backup = path.join(root, 'review', '08-quote-before-seamless-join.png');
const indexPath = path.join(root, 'index.html');
const cssPath = path.join(root, 'src', 'concept.css');
const readmePath = path.join(root, 'README.md');
const recordPath = path.join(root, 'quote-footer-seamless-join.json');

fs.mkdirSync(path.dirname(backup), { recursive: true });
if (!fs.existsSync(backup)) fs.copyFileSync(quote, backup);
fs.copyFileSync(generated, quote);

const png = fs.readFileSync(quote);
if (png.toString('ascii', 1, 4) !== 'PNG') throw new Error('Generated output is not a PNG.');
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);

let index = fs.readFileSync(indexPath, 'utf8');
index = index.replace(
  /(<img class="scene-image" src="08-quote\.png" width=")\d+(" height=")\d+(" alt=")/,
  `$1${width}$2${height}$3`,
);
fs.writeFileSync(indexPath, index);

let css = fs.readFileSync(cssPath, 'utf8');
const marker = '/* seamless quote-to-footer join */';
if (!css.includes(marker)) {
  css += `\n${marker}\n.quote::after{content:"";position:absolute;z-index:2;left:0;right:0;bottom:-1px;height:10%;pointer-events:none;background:linear-gradient(180deg,rgba(8,42,69,0) 0%,rgba(8,42,69,.22) 26%,rgba(8,42,69,.62) 66%,#082A45 100%)}\n.footer{margin-top:-1px;background:#082A45}.footer::before{content:"";position:absolute;z-index:1;left:0;right:0;top:-1px;height:13%;pointer-events:none;background:#082A45}.footer .official-footer-logo{z-index:2}\n`;
  fs.writeFileSync(cssPath, css);
}

fs.writeFileSync(recordPath, JSON.stringify({
  task: 'Eliminate the visible quote-to-footer seam at image and browser-rendering levels.',
  createdAt: new Date().toISOString(),
  input: '08-quote.png',
  backup: 'review/08-quote-before-seamless-join.png',
  generatedSource: generated,
  output: '08-quote.png',
  dimensions: { width, height },
  joinColor: '#082A45',
  assemblyTreatment: {
    quoteBottomGradientHeight: '10%',
    footerTopSolidHeight: '13%',
    footerOverlap: '-1px',
  },
}, null, 2) + '\n');

let readme = fs.readFileSync(readmePath, 'utf8');
const heading = '## 입력폼–푸터 이음선 제거';
if (!readme.includes(heading)) {
  readme += `\n\n${heading}\n\n입력폼 하단의 장면을 더 긴 범위에서 딥 네이비로 전환하고, 브라우저 조립 단계에서 양쪽 경계를 동일한 #082A45로 고정했습니다. 입력폼 하단 10%에는 투명도 그라데이션을 적용하고 푸터 상단 13%는 같은 단색으로 덮었으며, 분수 픽셀 리사이징으로 생기는 선을 막기 위해 두 섹션을 1px 겹쳤습니다.\n\n- 현재 입력폼: [08-quote.png](08-quote.png)\n- 현재 푸터: [08-footer.png](08-footer.png)\n- 수정 전 입력폼: [review/08-quote-before-seamless-join.png](review/08-quote-before-seamless-join.png)\n- 작업 기록: [quote-footer-seamless-join.json](quote-footer-seamless-join.json)\n`;
  fs.writeFileSync(readmePath, readme);
}

console.log(JSON.stringify({ quote, backup, width, height, cssPath, recordPath }, null, 2));
