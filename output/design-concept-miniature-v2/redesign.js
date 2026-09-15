// The original hero is intentionally untouched. All revisions target the other nine sections.
const smArrow='<span aria-hidden="true">→</span>';
const smButton=(label,target,secondary=false)=>'<a class="sm-button'+(secondary?' secondary':'')+'" href="#'+target+'">'+label+smArrow+'</a>';
const smLink=(label,target)=>'<a class="sm-link" href="#'+target+'">'+label+smArrow+'</a>';
const smPhoto=(file,W,H,x,y,w,h,alt)=>crop(file,W,H,x,y,w,h,alt,'sm-photo');
const smIcon=name=>'<span class="sm-icon-tile">'+icon(name)+'</span>';
const smSet=(id,height,body)=>{const el=document.getElementById(id);el.className='frame sm-section sm-'+id;el.style.setProperty('--height',height+'px');el.querySelector('.inner').innerHTML=body;};
const oldForm=document.querySelector('#quote .form-panel').outerHTML;
smSet('journey',920,'<div class="sm-heading"><h2>从中国到美国，每一步都清楚</h2>'+smButton('了解运输方案','services',true)+'</div><div class="sm-route-panel">'+
smPhoto('02-journey',1774,887,48,286,1678,340,'中国工厂、国际运输、美国清关、自营仓与末端配送')+
'<ol class="sm-stages">'+['中国工厂','头程运输','美国清关','美国自营海外仓','美国配送'].map((t,i)=>'<li><span>0'+(i+1)+'</span><h3>'+t+'</h3></li>').join('')+'</ol><p class="sm-note">路线与服务范围，以确认方案为准 · 流程示意</p></div>');
const smCustomers=[
['Amazon卖家','FBA补货 · FBM出库',63,244,524,361,'查看方案'],
['独立站 / TikTok Shop','本地订单配送',655,244,503,361,'Shopify'],
['工厂与贸易商','整柜运输 · B2B交付',1227,244,524,361,'了解B2B配送']];
smSet('customers',920,'<div class="sm-heading"><h2>找到适合您业务的方案</h2></div><div class="sm-customer-grid">'+smCustomers.map((v,i)=>'<article class="sm-customer-card">'+smPhoto('03-customers',1811,868,v[2],v[3],v[4],v[5],v[0]+'的微缩物流场景')+'<div class="sm-card-copy"><h3>'+v[0]+'</h3><p>'+v[1]+'</p><div class="sm-links">'+smLink(v[6],'services')+(i===1?smLink('TikTok Shop','services'):'')+'</div></div></article>').join('')+'</div>');
const smServices=[
['一件代发','拣货 · 包装 · 出库',77,194,410,233],
['FBA中转补货','验收 · 贴标 · 补货',884,194,394,233],
['头程运输','FCL · LCL · 空运',77,483,410,236],
['IOR与清关咨询','资料 · 角色 · 责任',884,483,394,236]];
smSet('services',1100,'<div class="sm-heading"><h2>按任务，选择需要的服务</h2></div><div class="sm-service-grid">'+smServices.map(v=>'<a class="sm-service-card" href="#quote">'+smPhoto('04-services',1704,923,v[2],v[3],v[4],v[5],v[0]+'微缩示意')+'<div><h3>'+v[0]+'</h3><p>'+v[1]+'</p><span class="sm-service-arrow" aria-hidden="true">→</span></div></a>').join('')+'</div><div class="sm-secondary-services">'+smLink('仓储与库存','operations')+smLink('退货与检品','quote')+smLink('B2B配送','quote')+smLink('其他需求','quote')+'</div><div class="sm-cta-band"><h3>从您的需求开始。</h3>'+smButton('咨询物流方案','quote')+'</div>');
smSet('operations',980,'<div class="sm-heading"><h2>自营仓库，清晰管理</h2></div><div class="sm-operation-grid"><div class="sm-warehouse">'+smPhoto('05-operations',1704,923,75,186,993,535,'美国自营仓作业模型，概念示意')+'</div><div class="sm-feature-list">'+[['warehouse','入库记录'],['search','库存查询'],['truck','出库指令']].map(v=>'<a href="#quote" class="sm-feature">'+smIcon(v[0])+'<h3>'+v[1]+'</h3><span aria-hidden="true">→</span></a>').join('')+'<p class="sm-note">系统概念示意 · 功能以实际方案为准</p></div></div><div class="sm-info-band"><h3>PNPLINE直接运营美国仓库</h3><div>'+smButton('了解WMS','quote',true)+smButton('确认服务责任','customs')+'</div></div>');
smSet('customs',780,'<div class="sm-customs-panel"><div><h2>发货前，<br>先确认清楚</h2><div class="sm-check-chips">'+[['document','商品资料'],['person','IOR需求'],['list','责任范围']].map(v=>'<span>'+smIcon(v[0])+v[1]+'</span>').join('')+'</div>'+smButton('了解清关与合规','quote')+'</div><div class="sm-document-photo">'+smPhoto('06-customs',1942,809,1021,183,812,468,'商品资料、IOR需求与责任范围的微缩资料图')+'</div></div>');
const smCosts=[['头程运输',91,229,291,211],['清关与合规',426,230,285,211],['仓储',754,230,268,211],['仓内操作',1064,230,284,211],['美国配送',1389,230,292,211]];
smSet('costs',960,'<div class="sm-heading"><h2>费用透明，从构成开始</h2></div><div class="sm-cost-panel">'+smCosts.map(v=>'<div>'+smPhoto('07-costs',1774,887,v[1],v[2],v[3],v[4],v[0]+'费用示意')+'<i aria-hidden="true"></i><h3>'+v[0]+'</h3></div>').join('')+'</div><div class="sm-scenarios"><a href="#quote">'+smIcon('box')+'<div><h3>FBA · 20 CBM</h3><p>运输、清关、暂存与补货</p></div><span>›</span></a><a href="#quote">'+smIcon('truck')+'<div><h3>独立站 · 每月500单</h3><p>库存、拣配与美国配送</p></div><span>›</span></a></div><div class="sm-cost-bottom"><p class="sm-note">询价场景示意，不代表客户案例或价格承诺</p>'+smButton('获取报价','quote')+'</div>');
smSet('faq',1080,'<div class="sm-faq-grid"><div><p class="sm-eyebrow">FAQ</p><h2>咨询前，<br>先了解</h2><div class="sm-faq-photo">'+smPhoto('08-faq',1704,923,80,273,606,484,'微缩货车与仓库工作人员')+'</div>'+smLink('联系我们','quote')+'</div><div class="sm-faq-list">'+faq.map((v,i)=>'<details name="sm-faq"'+(i===0?' open':'')+'><summary>'+v[0]+'</summary><p>'+v[1]+'</p></details>').join('')+'</div></div>');
smSet('quote',1060,'<div class="sm-quote-shell"><div class="sm-quote-inner"><div class="sm-quote-intro"><h2>让我们了解<br>您的需求</h2><div class="sm-contact-steps">'+[['document','提交需求'],['search','确认范围'],['person','沟通报价']].map(v=>'<span>'+smIcon(v[0])+'<b>'+v[1]+'</b></span>').join('')+'</div><div class="sm-quote-photo">'+smPhoto('09-inquiry',1717,916,116,451,627,339,'微缩仓库配送车辆与包裹')+'</div></div><div class="sm-quote-form">'+oldForm+'<p class="sm-note">设计预览 · 不发送数据</p></div></div></div>');
document.querySelector('#quote .form-panel .button').className='sm-button';
document.querySelector('#quote .form-panel .arrow').textContent='→';
smSet('footer',660,'<div class="sm-footer-grid"><div><a class="brand" href="#hero"><img src="PNP-LINE.webp" alt="PNPLINE"></a><p>美国自营海外仓与跨境物流</p><div class="sm-footer-photo">'+smPhoto('10-footer',2172,724,101,260,548,246,'微缩配送车与包裹')+'</div>'+smButton('免费获取报价','quote')+'</div>'+footerLinks.map(g=>'<div><h3>'+g[0]+'</h3><ul>'+g[1].map(v=>'<li><a href="#'+v[1]+'">'+v[0]+'</a></li>').join('')+'</ul></div>').join('')+'</div><div class="sm-footer-bottom"><span>PNPLINE</span><a href="#footer">隐私政策</a></div>');
document.querySelectorAll('#faq details').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)document.querySelectorAll('#faq details').forEach(other=>{if(other!==d)other.open=false})}));
resize();

