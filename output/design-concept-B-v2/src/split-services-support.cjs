const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const record=JSON.parse(fs.readFileSync(path.join(root,'services-support-split.json'),'utf8'));
const backup=path.join(root,record.backup);
if(!fs.existsSync(backup))fs.copyFileSync(path.join(root,'02-services-details.png'),backup);
const dims={};
for(const item of record.outputs){
  const b=fs.readFileSync(item.source);
  dims[item.output]={width:b.readUInt32BE(16),height:b.readUInt32BE(20)};
  fs.writeFileSync(path.join(root,item.output),b);
}
const details=dims['02-services-details.png'],support=dims['02-services-support.png'];
const indexPath=path.join(root,'index.html');
let index=fs.readFileSync(indexPath,'utf8');
index=index.replace(/<section id="service-support"[\s\S]*?<\/section>\s*/,'');
index=index.replace(/<section id="service-details"[\s\S]*?<\/section>/,
  `<section id="service-details" class="scene" aria-label="四项核心服务的详细内容与适用需求"><img class="scene-image" src="02-services-details.png" width="${details.width}" height="${details.height}" alt="四张核心服务卡片，分别说明一件代发、FBA中转与补货、头程运输、IOR与进口清关咨询的服务内容、适合对象、作业内容与咨询入口。"></section>\n<section id="service-support" class="scene" aria-label="更多服务与仓内作业流程"><img class="scene-image" src="02-services-support.png" width="${support.width}" height="${support.height}" alt="仓储与库存、退货换标与检品、美国B2B配送、其他物流需求四项入口，以及入库验收、上架与库存管理、订单拣选与包装、出库配送或FBA补货四阶段仓内作业流程。"></section>`);
fs.writeFileSync(indexPath,index);
const reviewPath=path.join(root,'review.html');
let review=fs.readFileSync(reviewPath,'utf8');
review=review.replace(/<figure><a href="02-services-support.png"[\s\S]*?<\/figure>\s*/,'');
review=review.replace(/<figure><a href="02-services-details.png"[\s\S]*?<\/figure>/,
  '<figure><a href="02-services-details.png"><img src="02-services-details.png" alt="02-B · S4 핵심 서비스 상세 카드"><figcaption>02-B · S4 핵심 서비스 상세 카드</figcaption></a></figure>\n<figure><a href="02-services-support.png"><img src="02-services-support.png" alt="02-C · S4 추가 서비스·창고 작업 흐름"><figcaption>02-C · S4 추가 서비스·창고 작업 흐름</figcaption></a></figure>');
fs.writeFileSync(reviewPath,review);
const capturePath=path.join(root,'src/capture.cjs');
let capture=fs.readFileSync(capturePath,'utf8');
capture=capture.replace('report.layout.scenes!==11','report.layout.scenes!==12');
if(!capture.includes("'#service-support'"))capture=capture.replace("await shot('review/service-details-1440.png','#service-details');","await shot('review/service-details-1440.png','#service-details');await shot('review/service-support-1440.png','#service-support');");
fs.writeFileSync(capturePath,capture);
const readmePath=path.join(root,'README.md');
let readme=fs.readFileSync(readmePath,'utf8').replaceAll('11개','12개');
if(!readme.includes('| 02-services-support.png |'))readme=readme.replace('| 02-services-details.png | 이미지 없는 2×2 상세 카드 / 보조 링크 4개 / 창고 작업 절차 |','| 02-services-details.png | 이미지 없는 2×2 핵심 서비스 상세 카드 |\n| 02-services-support.png | 추가 서비스 링크 4개 / 4단계 창고 작업 타임라인 |');
const heading='## S4 추가 서비스·창고 작업 흐름 독립';
if(!readme.includes(heading))readme+='\n\n'+heading+'\n\n핵심 서비스 상세 카드에서 추가 서비스와 창고 작업 흐름을 제거하고, 이를 넉넉한 상하 여백을 가진 별도의 16:9 섹션으로 분리했습니다. 전체 페이지에서는 사진 아코디언, 핵심 서비스 상세 카드, 추가 서비스·창고 작업 흐름 순서로 연결합니다.\n\n- 핵심 서비스 상세: [02-services-details.png](02-services-details.png)\n- 독립 보조 섹션: [02-services-support.png](02-services-support.png)\n- 분리 전 보존본: [review/02-services-details-before-support-split.png](review/02-services-details-before-support-split.png)\n- 생성 기록: [services-support-split.json](services-support-split.json)\n';
fs.writeFileSync(readmePath,readme);
console.log(JSON.stringify({dims,scenes:(index.match(/<section[^>]+class="scene/g)||[]).length},null,2));
