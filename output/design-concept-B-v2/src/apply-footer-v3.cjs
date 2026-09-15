const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const record=JSON.parse(fs.readFileSync(path.join(root,'footer-v3-five-groups-edit.json'),'utf8'));
const backup=path.join(root,record.backup);
if(!fs.existsSync(backup))fs.copyFileSync(path.join(root,'08-quote.png'),backup);
const dims={};
for(const item of record.outputs){
 const b=fs.readFileSync(item.source);
 dims[item.output]={width:b.readUInt32BE(16),height:b.readUInt32BE(20)};
 fs.writeFileSync(path.join(root,item.output),b);
}
const q=dims['08-quote.png'],f=dims['08-footer.png'];
const indexPath=path.join(root,'index.html');
let index=fs.readFileSync(indexPath,'utf8');
index=index.replace(/<section id="footer"[\s\S]*?<\/section>\s*/,'');
index=index.replace(/<section id="quote"[\s\S]*?<\/section>/,
 `<section id="quote" class="scene quote" aria-label="物流需求表单初始状态与隐私说明">\n<img class="scene-image" src="08-quote.png" width="${q.width}" height="${q.height}" alt="所需服务、销售渠道、预计月业务量、联系邮箱、选填补充说明。隐私同意默认未勾选；说明咨询处理、邮件通知及最长12个月保留期限。">\n<a class="solid quote-cta" href="states.html" aria-label="查看咨询表单的交互状态设计">提交咨询 →</a>\n</section>\n<section id="footer" class="scene footer" aria-label="服务、PNPLINE介绍、报价与联系、政策和语言">\n<img class="scene-image" src="08-footer.png" width="${f.width}" height="${f.height}" alt="PNPLINE美国自营海外仓与跨境物流服务。服务、了解PNPLINE、报价与联系、政策、语言五个信息组。链接目的地为IA规划，语言目的地尚未确认。">\n<div class="official-footer-logo"><img src="assets/PNP-LINE.webp" alt="PNPLINE 官方标志"></div>\n</section>`);
fs.writeFileSync(indexPath,index);
const cssPath=path.join(root,'src/concept.css');
let css=fs.readFileSync(cssPath,'utf8');
if(!css.includes('.footer .official-footer-logo'))css += '\n.footer .official-footer-logo{left:2.75%;top:42.5%;width:20.7%;height:11%;border-radius:.65vw;padding:.55% 1%;}\n';
fs.writeFileSync(cssPath,css);
const reviewPath=path.join(root,'review.html');
let review=fs.readFileSync(reviewPath,'utf8');
review=review.replace(/<figure><a href="08-footer.png"[\s\S]*?<\/figure>\s*/,'');
review=review.replace(/<figure><a href="08-quote.png"[\s\S]*?<\/figure>/,
 '<figure><a href="08-quote.png"><img src="08-quote.png" alt="09 · 견적 폼 / 개인정보"><figcaption>09 · 견적 폼 / 개인정보</figcaption></a></figure>\n<figure><a href="08-footer.png"><img src="08-footer.png" alt="10 · 푸터 5개 정보 그룹"><figcaption>10 · 푸터 5개 정보 그룹 / 공식 로고는 전체 페이지 렌더링에서 적용</figcaption></a></figure>');
fs.writeFileSync(reviewPath,review);
const capturePath=path.join(root,'src/capture.cjs');
let capture=fs.readFileSync(capturePath,'utf8').replace('report.layout.scenes!==12','report.layout.scenes!==13');
if(!capture.includes("'#footer'"))capture=capture.replace("await shot('review/quote-1440.png','#quote');","await shot('review/quote-1440.png','#quote');await shot('review/footer-1440.png','#footer');");
fs.writeFileSync(capturePath,capture);
const mdPath=path.join(root,'content.zh-CN.md');
let md=fs.readFileSync(mdPath,'utf8');
const rows=[
 '| FOOT.brand | draft-visible | PNPLINE — 美国自营海外仓与跨境物流服务 |',
 '| FOOT.services.title | draft-visible | 服务 |',
 '| FOOT.services.links | planned-unpublished | 美国海外仓 → /warehouse/；头程运输 → /freight/；清关与合规 → /customs/ |',
 '| FOOT.about.title | draft-visible | 了解PNPLINE |',
 '| FOOT.about.links | planned-unpublished | 关于我们 → /about/；自营仓库资料 → /about/facilities/；资质与合规 → /about/compliance/ |',
 '| FOOT.contact.title | draft-visible | 报价与联系 |',
 '| FOOT.contact.links | planned-unpublished | 价格与报价 → /pricing/；联系我们 → /contact/；合作伙伴 → /partner/ |',
 '| FOOT.policy.title | draft-visible | 政策 |',
 '| FOOT.policy.links | planned-unpublished | 隐私政策 → /privacy/ |',
 '| FOOT.language.title | draft-visible | 语言 |',
 '| FOOT.language.items | destination-unconfirmed | 简体中文；한국어；English |'
].join('\n');
md=md.replace(/\| FOOT\.brand[\s\S]*?\| FOOT\.2[^\n]*\n?/,rows+'\n');
fs.writeFileSync(mdPath,md);
const jsonPath=path.join(root,'content.zh-CN.json');
const data=JSON.parse(fs.readFileSync(jsonPath,'utf8'));
for(const key of Object.keys(data))if(/^FOOT\./.test(key))delete data[key];
const foot={
 'FOOT.brand':{text:'PNPLINE — 美国自营海外仓与跨境物流服务',status:'draft-visible'},
 'FOOT.services.title':{text:'服务',status:'draft-visible'},
 'FOOT.services.links':{text:'美国海外仓 → /warehouse/；头程运输 → /freight/；清关与合规 → /customs/',status:'planned-unpublished'},
 'FOOT.about.title':{text:'了解PNPLINE',status:'draft-visible'},
 'FOOT.about.links':{text:'关于我们 → /about/；自营仓库资料 → /about/facilities/；资质与合规 → /about/compliance/',status:'planned-unpublished'},
 'FOOT.contact.title':{text:'报价与联系',status:'draft-visible'},
 'FOOT.contact.links':{text:'价格与报价 → /pricing/；联系我们 → /contact/；合作伙伴 → /partner/',status:'planned-unpublished'},
 'FOOT.policy.title':{text:'政策',status:'draft-visible'},
 'FOOT.policy.links':{text:'隐私政策 → /privacy/',status:'planned-unpublished'},
 'FOOT.language.title':{text:'语言',status:'draft-visible'},
 'FOOT.language.items':{text:'简体中文；한국어；English',status:'destination-unconfirmed'}
};
Object.assign(data,foot);
fs.writeFileSync(jsonPath,JSON.stringify(data,null,2)+'\n');
const readmePath=path.join(root,'README.md');
let readme=fs.readFileSync(readmePath,'utf8');
readme=readme.replace('본문은 12개 가로형 이미지','본문은 13개 가로형 이미지').replace('서로 다른 섹션 비율의 12개 이미지','서로 다른 섹션 비율의 13개 이미지').replace('확인 사항: 12개 본문 이미지 로딩','확인 사항: 13개 본문 이미지 로딩');
readme=readme.replace('| 08-quote.png | 5개 입력 그룹, 미선택 동의, 개인정보, 푸터 |','| 08-quote.png | 5개 입력 그룹, 미선택 동의, 개인정보 |\n| 08-footer.png | 서비스 / PNPLINE 소개 / 견적·연락 / 정책 / 언어 5개 그룹 |');
const heading='## 푸터 v3 5개 그룹 확장';
if(!readme.includes(heading))readme+='\n\n'+heading+'\n\n기존 견적 이미지 하단의 가격·연락·개인정보 3링크 푸터를 제거하고, 푸터를 별도 가로형 섹션으로 분리했습니다. 새 푸터는 서비스, PNPLINE 소개, 견적·연락, 정책, 언어의 5개 그룹을 포함합니다. 언어 목적지는 승인 전이라 URL을 표시하지 않았고 공개 연락처·법인정보·인증 배지도 추가하지 않았습니다. 전체 페이지에서는 공식 PNP-LINE.webp를 빈 로고 플레이트에 직접 렌더링합니다.\n\n- 견적 전용 이미지: [08-quote.png](08-quote.png)\n- 푸터 배경 이미지: [08-footer.png](08-footer.png)\n- 공식 로고 포함 푸터 캡처: [review/footer-1440.png](review/footer-1440.png)\n- 푸터 원고와 IA 경로: [footer-v3-content.zh-CN.md](footer-v3-content.zh-CN.md)\n- 분리 전 보존본: [review/08-quote-before-footer-split.png](review/08-quote-before-footer-split.png)\n- 생성 기록: [footer-v3-five-groups-edit.json](footer-v3-five-groups-edit.json)\n';
fs.writeFileSync(readmePath,readme);
console.log(JSON.stringify({dims,scenes:(index.match(/<section[^>]+class="scene/g)||[]).length},null,2));
