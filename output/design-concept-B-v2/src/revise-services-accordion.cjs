const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const record = JSON.parse(fs.readFileSync(path.join(root, 'services-accordion-expanded-edit.json'), 'utf8'));
const backup = path.join(root, 'review/02-services-before-accordion-restoration.png');
if (!fs.existsSync(backup)) fs.copyFileSync(path.join(root, '02-services.png'), backup);
const bytes = fs.readFileSync(record.source);
const width = bytes.readUInt32BE(16), height = bytes.readUInt32BE(20);
fs.writeFileSync(path.join(root, record.variant), bytes);
fs.writeFileSync(path.join(root, record.output), bytes);
const indexPath = path.join(root, 'index.html');
let index = fs.readFileSync(indexPath, 'utf8');
if (!index.includes('src="02-services.png"')) throw new Error('Services image missing');
index = index.replace(/src="02-services.png" width="\d+" height="\d+"/, `src="02-services.png" width="${width}" height="${height}"`);
fs.writeFileSync(indexPath, index);
const reviewPath = path.join(root, 'review.html');
fs.writeFileSync(reviewPath, fs.readFileSync(reviewPath, 'utf8').replaceAll('02 · S4 핵심 서비스 완성형', '02 · S4 아코디언 + 전체 서비스 정보'));
const readmePath = path.join(root, 'README.md');
let readme = fs.readFileSync(readmePath, 'utf8');
readme = readme.replace('## S4 핵심 서비스 정보 완성', '## 이전 수정 기록 — S4 전체 카드 확장');
readme = readme.replace('서비스 카드 설명과 일부 폼 레이블은 이미지 해상도에 맞춰 축약했습니다.', '현재 S4는 서비스 전체 원고를 반영했으며, 일부 폼 레이블은 이미지 해상도에 맞춰 축약했습니다.');
const heading = '## S4 아코디언 복원과 높이 확장';
if (!readme.includes(heading)) readme += '\n\n' + heading + '\n\n' +
  '첫 카드가 넓게 펼쳐지고 나머지 세 카드가 좁게 놓인 기존 사진 아코디언 구도를 복원했습니다. 사진 아래에는 네 서비스의 설명·적합 대상·작업 요약·CTA를 단순한 텍스트 열로 배치했습니다. 보조 링크 4개와 창고 작업 절차는 하단에 분리했습니다.\n\n' +
  `새 이미지 크기는 ${width} × ${height}px입니다. 16:9에서 4:3으로 높이를 늘렸으며 사진은 비율을 유지합니다. 아코디언은 정적 시안으로, 펼침·접힘 동작은 구현하지 않았습니다.\n\n` +
  '- 현재 시안: [02-services.png](02-services.png)\n' +
  '- 별도 파일: [02-services-accordion-expanded.png](02-services-accordion-expanded.png)\n' +
  '- 이전 전체 카드 버전: [review/02-services-before-accordion-restoration.png](review/02-services-before-accordion-restoration.png)\n' +
  '- 전체 원고: [services-complete-content.zh-CN.md](services-complete-content.zh-CN.md)\n' +
  '- 전체 생성 프롬프트: [services-accordion-expanded-edit.json](services-accordion-expanded-edit.json)\n';
fs.writeFileSync(readmePath, readme);
console.log(JSON.stringify({width, height, variant:record.variant}));
