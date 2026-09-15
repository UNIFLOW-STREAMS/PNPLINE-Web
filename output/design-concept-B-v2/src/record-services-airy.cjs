const fs = require('node:fs');
const path = require('node:path');
const readmePath = path.resolve(__dirname, '..', 'README.md');
let text = fs.readFileSync(readmePath, 'utf8');
const heading = '## S4 상세 카드 여백·타이포 조정';
if (!text.includes(heading)) {
  text += '\n\n' + heading + '\n\n' +
    '2×2 상세 카드 구조와 전체 문구를 유지하면서 카드 사이의 간격과 내부 패딩을 확대했습니다. 서비스 제목·본문·필드명·값·CTA의 글자 크기와 무게를 낮추고, 그림자와 그라데이션 없이 얇은 테두리와 평면 CTA를 사용해 시각적 밀도를 줄였습니다.\n\n' +
    '- 현재 이미지: [02-services-details.png](02-services-details.png)\n' +
    '- 수정 전 보존본: [review/02-services-details-before-airy-spacing.png](review/02-services-details-before-airy-spacing.png)\n' +
    '- 생성 기록: [services-details-airy-edit.json](services-details-airy-edit.json)\n';
  fs.writeFileSync(readmePath, text);
}
console.log(JSON.stringify({updated: text.includes(heading)}));
