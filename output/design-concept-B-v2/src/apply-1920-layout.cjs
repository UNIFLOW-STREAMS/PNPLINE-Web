const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const indexPath = path.join(root, 'index.html');
const cssPath = path.join(root, 'src', 'concept.css');
const capturePath = path.join(root, 'src', 'capture.cjs');
const capture1920Path = path.join(root, 'src', 'capture-1920.cjs');
const syncPath = path.join(root, 'src', 'sync-readme-capture.cjs');
const readmePath = path.join(root, 'README.md');
const backupDir = path.join(root, 'review', 'layout-before-1920');

fs.mkdirSync(backupDir, { recursive: true });
for (const file of [indexPath, cssPath, capturePath, syncPath]) {
  const target = path.join(backupDir, path.basename(file));
  if (!fs.existsSync(target)) fs.copyFileSync(file, target);
}

let index = fs.readFileSync(indexPath, 'utf8');
if (!index.includes('class="scene-content"')) {
  index = index.replace(/(<section\b[^>]*>)([\s\S]*?)(<\/section>)/g, '$1\n<div class="scene-content">$2</div>\n$3');
  fs.writeFileSync(indexPath, index);
}

let css = fs.readFileSync(cssPath, 'utf8');
const marker = '/* fixed 1920 canvas with 1440 content */';
if (!css.includes(marker)) {
  css += `\n${marker}\nhtml,body{width:100%;min-width:1920px}body{background:#DDE7EC}.landing{width:1920px;min-width:1920px;margin:0 auto}.scene{width:1920px;margin:0;padding:32px 240px;background:#F3F8FA}.scene-content{position:relative;width:1440px;margin:0;line-height:0}.scene-image{width:1440px;max-width:none}.hero{background:#FFFFFF}.quote,.footer{background:#082A45}.solid,.outline{font-size:19.872px;border-radius:9.36px}.official-header nav{gap:59.76px}.official-header nav a{font-size:18px}.quote-cta{font-size:21.024px}.footer{margin-top:0}.quote::after,.footer::before{content:none}.quote .scene-content::after{content:"";position:absolute;z-index:2;left:0;right:0;bottom:-1px;height:10%;pointer-events:none;background:linear-gradient(180deg,rgba(8,42,69,0) 0%,rgba(8,42,69,.22) 26%,rgba(8,42,69,.62) 66%,#082A45 100%)}.footer .scene-content::before{content:"";position:absolute;z-index:1;left:0;right:0;top:-1px;height:13%;pointer-events:none;background:#082A45}.footer .official-footer-logo{z-index:2}\n`;
  fs.writeFileSync(cssPath, css);
}

fs.copyFileSync(capture1920Path, capturePath);

let sync = fs.readFileSync(syncPath, 'utf8');
sync = sync.replace(/1440 ×/g, '1920 ×');
sync = sync.replace(/`\[전체 페이지 PNG — 1440 × \$\{full\.height\}\]`/g, '`[전체 페이지 PNG — 1920 × ${full.height}]`');
fs.writeFileSync(syncPath, sync);

let readme = fs.readFileSync(readmePath, 'utf8');
const heading = '## 1920px 전체 페이지 레이아웃';
if (!readme.includes(heading)) {
  readme += `\n\n${heading}\n\n전체 페이지 캔버스를 1920px로 확장하고, 모든 섹션에 1440px 콘텐츠 래퍼를 적용했습니다. 콘텐츠는 좌우 240px 중앙 여백 안에서 가로폭을 빈 공간 없이 채우며, 각 섹션에는 상단 32px과 하단 32px 여백을 둡니다. CTA와 공식 로고 오버레이는 1440px 콘텐츠 좌표계를 유지합니다.\n\n- 전체 페이지: [00-fullpage.png](00-fullpage.png)\n- 브라우저 시안: [index.html](index.html)\n- 검증 기록: [review/capture-report.json](review/capture-report.json)\n- 적용 전 소스: [review/layout-before-1920](review/layout-before-1920)\n`;
  fs.writeFileSync(readmePath, readme);
}

console.log(JSON.stringify({ indexPath, cssPath, capturePath, syncPath, backupDir }, null, 2));
