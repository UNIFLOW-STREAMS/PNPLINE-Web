const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const report=JSON.parse(fs.readFileSync(path.join(root,'review/capture-report.json'),'utf8'));
const full=report.outputs.find(x=>x.file==='00-fullpage.png');
const p=path.join(root,'README.md');
let t=fs.readFileSync(p,'utf8');
t=t.replace(/\[전체 페이지 PNG — 1440 × \d+\]/,`[전체 페이지 PNG — 1440 × ${full.height}]`);
fs.writeFileSync(p,t);
console.log(JSON.stringify({height:full.height,scenes:report.layout.scenes,failures:report.failures}));
