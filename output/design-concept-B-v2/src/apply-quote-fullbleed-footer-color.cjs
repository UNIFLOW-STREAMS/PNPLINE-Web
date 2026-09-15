const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const cssPath = path.join(root, 'src', 'concept.css');
const capturePaths = [path.join(root, 'src', 'capture.cjs'), path.join(root, 'src', 'capture-1920.cjs')];
const readmePath = path.join(root, 'README.md');
const backupDir = path.join(root, 'review', 'before-quote-fullbleed-footer-color');
const recordPath = path.join(root, 'quote-fullbleed-footer-color.json');

fs.mkdirSync(backupDir, { recursive: true });
for (const file of [cssPath, ...capturePaths]) {
  const target = path.join(backupDir, path.basename(file));
  if (!fs.existsSync(target)) fs.copyFileSync(file, target);
}

let css = fs.readFileSync(cssPath, 'utf8');
const marker = '/* quote full-bleed and exact footer navy */';
if (!css.includes(marker)) {
  css += `\n${marker}\n.quote{padding-left:0;padding-right:0}.quote .scene-content{width:1920px}.quote .scene-image{width:1920px}.footer{background:#082A45}.footer .scene-content::after{content:"";position:absolute;z-index:2;inset:0;pointer-events:none;background:#082A45;mix-blend-mode:lighten}.footer .official-footer-logo{z-index:3}\n`;
  fs.writeFileSync(cssPath, css);
}

for (const capturePath of capturePaths) {
  let source = fs.readFileSync(capturePath, 'utf8');
  source = source.replace(
    /const geometryFailure = report\.layout\.sceneGeometry\.some\(scene =>[\s\S]*?\n    \);/,
    `const geometryFailure = report.layout.sceneGeometry.some(scene => {\n      const fullBleedQuote = scene.id === 'quote';\n      const expectedContentWidth = fullBleedQuote ? 1920 : 1440;\n      const expectedContentLeft = fullBleedQuote ? 0 : 240;\n+      return scene.outerWidth !== 1920 ||\n+        scene.contentWidth !== expectedContentWidth ||\n+        scene.contentLeft !== expectedContentLeft ||\n+        scene.imageWidth !== expectedContentWidth ||\n+        scene.paddingTop !== 32 ||\n+        scene.paddingBottom !== 32;\n+    });`,
  );
  source = source.replace(
    /if \(report\.images\.some\(image => !image\.loaded \|\| image\.renderedWidth !== 1440\)\) report\.failures\.push\('Image load or content-width failure'\);/,
    `if (report.images.some(image => !image.loaded || image.renderedWidth !== (image.src === '08-quote.png' ? 1920 : 1440))) report.failures.push('Image load or content-width failure');`,
  );
  source = source.replace(
    /logoSources: \[\.\.\.document\.querySelectorAll\('\.brand img,\.official-footer-logo img'\)\]\.map\(element => element\.getAttribute\('src'\)\),/,
    `logoSources: [...document.querySelectorAll('.brand img,.official-footer-logo img')].map(element => element.getAttribute('src')),\n      footerBackground: getComputedStyle(document.querySelector('.footer')).backgroundColor,\n      footerOverlayColor: getComputedStyle(document.querySelector('.footer .scene-content'), '::after').backgroundColor,\n      footerOverlayBlendMode: getComputedStyle(document.querySelector('.footer .scene-content'), '::after').mixBlendMode,`,
  );
  source = source.replace(
    /if \(report\.layout\.solid\.some\(item => item\.color !== 'rgb\(0, 127, 168\)'\)\) report\.failures\.push\('CTA token mismatch'\);/,
    `if (report.layout.solid.some(item => item.color !== 'rgb(0, 127, 168)')) report.failures.push('CTA token mismatch');\n    if (report.layout.footerBackground !== 'rgb(8, 42, 69)' || report.layout.footerOverlayColor !== 'rgb(8, 42, 69)' || report.layout.footerOverlayBlendMode !== 'lighten') report.failures.push('Footer #082A45 treatment mismatch');`,
  );
  fs.writeFileSync(capturePath, source);
}

fs.writeFileSync(recordPath, JSON.stringify({
  task: 'Render the quote image full-bleed at 1920px and make the footer background #082A45.',
  createdAt: new Date().toISOString(),
  quote: { outerWidth: 1920, contentWidth: 1920, imageWidth: 1920, horizontalPadding: 0, verticalPadding: 32 },
  footer: { outerWidth: 1920, contentWidth: 1440, horizontalPadding: 240, background: '#082A45', imageBlendMode: 'lighten' },
  backupDir: 'review/before-quote-fullbleed-footer-color',
}, null, 2) + '\n');

let readme = fs.readFileSync(readmePath, 'utf8');
const heading = '## 입력폼 1920px 풀블리드와 푸터 색상';
if (!readme.includes(heading)) {
  readme += `\n\n${heading}\n\n입력폼 섹션은 1440px 콘텐츠 제한의 예외로 처리해 배경 이미지가 1920px 전체 폭을 채우도록 변경했습니다. 상하 32px 여백은 유지합니다. 푸터 외곽과 내부 이미지 배경은 #082A45로 통일했으며, 텍스트·구분선·공식 로고의 밝기는 유지합니다.\n\n- 전체 페이지: [00-fullpage.png](00-fullpage.png)\n- 입력폼 검토: [review/quote-1920.png](review/quote-1920.png)\n- 푸터 검토: [review/footer-1920.png](review/footer-1920.png)\n- 검증 기록: [review/capture-report.json](review/capture-report.json)\n- 작업 기록: [quote-fullbleed-footer-color.json](quote-fullbleed-footer-color.json)\n`;
  fs.writeFileSync(readmePath, readme);
}

console.log(JSON.stringify({ cssPath, capturePaths, backupDir, recordPath }, null, 2));
