const fs=require('node:fs'),path=require('node:path');
const p=path.resolve(__dirname,'..','README.md');
let t=fs.readFileSync(p,'utf8');
const h='## S4 하단 정보 구조 개선';
if(!t.includes(h)){
  t+='\n\n'+h+'\n\n추가 서비스 4개를 번호가 있는 독립 링크 타일로 구성하고, 창고 작업 절차를 연결선과 단계 번호가 있는 4단계 타임라인으로 변경했습니다. 적용 조건 문구는 흐름에서 분리해 별도 각주로 배치했습니다.\n\n- 현재 이미지: [02-services-details.png](02-services-details.png)\n- 수정 전 보존본: [review/02-services-details-before-bottom-redesign.png](review/02-services-details-before-bottom-redesign.png)\n- 생성 기록: [services-details-bottom-redesign.json](services-details-bottom-redesign.json)\n';
  fs.writeFileSync(p,t);
}
console.log(JSON.stringify({updated:t.includes(h)}));
