const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const cssPath = path.join(root, 'src', 'concept.css');
const capturePaths = [path.join(root, 'src', 'capture.cjs'), path.join(root, 'src', 'capture-1920.cjs')];
const readmePath = path.join(root, 'README.md');
const backupDir = path.join(root, 'review', 'before-faq-quote-gap');
const recordPath = path.join(root, 'faq-quote-gap.json');

fs.mkdirSync(backupDir, { recursive: true });
for (const file of [cssPath, ...capturePaths]) {
  const backup = path.join(backupDir, path.basename(file));
  if (!fs.existsSync(backup)) fs.copyFileSync(file, backup);
}

let css = fs.readFileSync(cssPath, 'utf8');
const marker = '/* 64px light gap before full-bleed quote */';
if (!css.includes(marker)) {
  css += `\n${marker}\n.quote{background:linear-gradient(180deg,#F3F8FA 0,#F3F8FA 32px,#082A45 32px,#082A45 100%)}\n`;
  fs.writeFileSync(cssPath, css);
}

for (const capturePath of capturePaths) {
  let source = fs.readFileSync(capturePath, 'utf8');
  source = source.replace(
    /footerOverlayBlendMode: getComputedStyle\(document\.querySelector\('\.footer \.scene-content'\), '::after'\)\.mixBlendMode,/,
    `footerOverlayBlendMode: getComputedStyle(document.querySelector('.footer .scene-content'), '::after').mixBlendMode,\n      faqQuoteGap: Math.round(document.querySelector('#quote .scene-content').getBoundingClientRect().top - document.querySelector('#faq .scene-content').getBoundingClientRect().bottom),\n      quoteBackgroundImage: getComputedStyle(document.querySelector('#quote')).backgroundImage,`,
  );
  source = source.replace(
    /if \(report\.layout\.footerBackground !== 'rgb\(8, 42, 69\)' \|\| report\.layout\.footerOverlayColor !== 'rgb\(8, 42, 69\)' \|\| report\.layout\.footerOverlayBlendMode !== 'lighten'\) report\.failures\.push\('Footer #082A45 treatment mismatch'\);/,
    `if (report.layout.footerBackground !== 'rgb(8, 42, 69)' || report.layout.footerOverlayColor !== 'rgb(8, 42, 69)' || report.layout.footerOverlayBlendMode !== 'lighten') report.failures.push('Footer #082A45 treatment mismatch');\n    if (report.layout.faqQuoteGap !== 64 || !report.layout.quoteBackgroundImage.includes('rgb(243, 248, 250)') || !report.layout.quoteBackgroundImage.includes('rgb(8, 42, 69)')) report.failures.push('FAQ-to-quote 64px light gap mismatch');`,
  );
  fs.writeFileSync(capturePath, source);
}

fs.writeFileSync(recordPath, JSON.stringify({
  task: 'Remove the navy bar above the quote section and set the FAQ-to-quote gap to 64px.',
  createdAt: new Date().toISOString(),
  faqBottomPadding: 32,
  quoteTopPadding: 32,
  totalGap: 64,
  gapColor: '#F3F8FA',
  quoteBottomPaddingColor: '#082A45',
  backupDir: 'review/before-faq-quote-gap',
}, null, 2) + '\n');

let readme = fs.readFileSync(readmePath, 'utf8');
const heading = '## FAQ–입력폼 64px 간격';
if (!readme.includes(heading)) {
  readme += `\n\n${heading}\n\nFAQ와 입력폼 사이에 보이던 긴 네이비 바를 제거했습니다. FAQ 하단 32px과 입력폼 상단 32px을 같은 아이스 블루(#F3F8FA)로 연결해 콘텐츠 간 간격을 정확히 64px로 설정했습니다. 입력폼 하단 여백은 #082A45로 유지해 푸터 전환은 보존합니다.\n\n- 전체 페이지: [00-fullpage.png](00-fullpage.png)\n- 입력폼 검토: [review/quote-1920.png](review/quote-1920.png)\n- 검증 기록: [review/capture-report.json](review/capture-report.json)\n- 작업 기록: [faq-quote-gap.json](faq-quote-gap.json)\n`;
  fs.writeFileSync(readmePath, readme);
}

console.log(JSON.stringify({ cssPath, capturePaths, backupDir, recordPath }, null, 2));
