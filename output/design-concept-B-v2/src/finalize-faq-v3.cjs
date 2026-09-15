const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const readmePath = path.join(root, 'README.md');
let readme = fs.readFileSync(readmePath, 'utf8');
readme = readme.replace(
  '| 07-faq.png | 현재 A안 FAQ 8개와 답변 |',
  '| 07-faq.png | v3 FAQ 8개 / 전체 답변 / 관련 서비스 링크 |'
);
fs.writeFileSync(readmePath, readme);
const content = JSON.parse(fs.readFileSync(path.join(root, 'content.zh-CN.json'), 'utf8'));
const questions = Object.keys(content).filter(key => /^FAQ\.\d+\.q$/.test(key));
const links = Object.keys(content).filter(key => /^FAQ\.\d+\.links$/.test(key));
console.log(JSON.stringify({ questions: questions.length, linkGroups: links.length }));
