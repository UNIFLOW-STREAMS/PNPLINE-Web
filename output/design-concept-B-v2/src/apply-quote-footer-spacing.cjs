const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.resolve(__dirname, '..');
const generatedQuote = 'C:\\Users\\KIM TAEHYUNG\\.codex\\generated_images\\01a09feb-ecf2-74e2-8dec-635a9efd2663\\exec-f606eb56-311a-4dc6-b6b6-7229f55f20ca.png';
const quote = path.join(root, '08-quote.png');
const footer = path.join(root, '08-footer.png');
const quoteBackup = path.join(root, 'review', '08-quote-before-footer-blend.png');
const footerBackup = path.join(root, 'review', '08-footer-before-compact-spacing.png');
const footerTemp = path.join(root, '08-footer-compact.tmp.png');
const indexPath = path.join(root, 'index.html');
const cssPath = path.join(root, 'src', 'concept.css');
const readmePath = path.join(root, 'README.md');
const recordPath = path.join(root, 'quote-footer-blend-spacing.json');

fs.mkdirSync(path.dirname(quoteBackup), { recursive: true });
if (!fs.existsSync(quoteBackup)) fs.copyFileSync(quote, quoteBackup);
if (!fs.existsSync(footerBackup)) fs.copyFileSync(footer, footerBackup);

fs.copyFileSync(generatedQuote, quote);

const crop = { x: 0, y: 255, width: 1672, height: 455 };
const ffmpeg = spawnSync('ffmpeg', [
  '-hide_banner', '-loglevel', 'error', '-y',
  '-i', footerBackup,
  '-vf', `crop=${crop.width}:${crop.height}:${crop.x}:${crop.y}`,
  '-frames:v', '1',
  footerTemp,
], { encoding: 'utf8' });
if (ffmpeg.status !== 0) throw new Error(ffmpeg.stderr || 'ffmpeg footer crop failed');
fs.copyFileSync(footerTemp, footer);
fs.unlinkSync(footerTemp);

function pngSize(file) {
  const png = fs.readFileSync(file);
  if (png.toString('ascii', 1, 4) !== 'PNG') throw new Error(`${file} is not a PNG.`);
  return { width: png.readUInt32BE(16), height: png.readUInt32BE(20) };
}

const quoteSize = pngSize(quote);
const footerSize = pngSize(footer);

let index = fs.readFileSync(indexPath, 'utf8');
index = index.replace(
  /(<img class="scene-image" src="08-quote\.png" width=")\d+(" height=")\d+(" alt=")/,
  `$1${quoteSize.width}$2${quoteSize.height}$3`,
);
index = index.replace(
  /(<img class="scene-image" src="08-footer\.png" width=")\d+(" height=")\d+(" alt=")/,
  `$1${footerSize.width}$2${footerSize.height}$3`,
);
fs.writeFileSync(indexPath, index);

let css = fs.readFileSync(cssPath, 'utf8');
css = css.replace(
  /\.footer \.official-footer-logo\{[^}]+\}/,
  '.footer .official-footer-logo{left:2.75%;top:31.85%;width:20.7%;height:22.75%;border-radius:.65vw;padding:.55% 1%;}',
);
fs.writeFileSync(cssPath, css);

fs.writeFileSync(recordPath, JSON.stringify({
  task: 'Reduce footer whitespace and blend the quote section into the footer.',
  createdAt: new Date().toISOString(),
  quote: {
    input: '08-quote.png',
    backup: 'review/08-quote-before-footer-blend.png',
    generatedSource: generatedQuote,
    output: '08-quote.png',
    dimensions: quoteSize,
    treatment: 'Lower 15–18% transitions to #082A45 at the bottom edge.',
  },
  footer: {
    input: '08-footer.png',
    backup: 'review/08-footer-before-compact-spacing.png',
    output: '08-footer.png',
    crop,
    dimensions: footerSize,
    logoOverlay: { left: '2.75%', top: '31.85%', width: '20.7%', height: '22.75%' },
  },
}, null, 2) + '\n');

let readme = fs.readFileSync(readmePath, 'utf8');
const heading = '## 입력폼–푸터 블렌딩과 푸터 여백 조정';
if (!readme.includes(heading)) {
  readme += `\n\n${heading}\n\n입력폼 이미지 하단을 푸터의 딥 네이비(#082A45)로 점진 전환해 수평 경계를 완화했습니다. 푸터는 기존 텍스트와 5개 정보 그룹을 유지하면서 상하 빈 영역을 제거해 1672 × 455px로 축소했습니다. 공식 로고 오버레이도 새 크롭 좌표에 맞춰 이동했습니다.\n\n- 블렌딩된 입력폼: [08-quote.png](08-quote.png)\n- 압축된 푸터: [08-footer.png](08-footer.png)\n- 입력폼 수정 전: [review/08-quote-before-footer-blend.png](review/08-quote-before-footer-blend.png)\n- 푸터 수정 전: [review/08-footer-before-compact-spacing.png](review/08-footer-before-compact-spacing.png)\n- 작업 기록: [quote-footer-blend-spacing.json](quote-footer-blend-spacing.json)\n`;
  fs.writeFileSync(readmePath, readme);
}

console.log(JSON.stringify({ quoteSize, footerSize, crop, recordPath }, null, 2));
