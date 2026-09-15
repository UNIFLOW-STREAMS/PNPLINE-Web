const icons={
box:'<path d="m4 9 12-6 12 6v14l-12 6-12-6z M4 9l12 6 12-6 M16 15v14 M10 6l12 6"/>',
truck:'<path d="M3 7h17v15H3z M20 12h6l4 6v4H20 M5 22a3 3 0 1 0 6 0 M22 22a3 3 0 1 0 6 0"/>',
warehouse:'<path d="M3 13 16 3l13 10v16H3z M10 29V17h12v12 M10 22h12"/>',
document:'<path d="M7 3h12l7 7v19H7z M19 3v8h7 M11 16h11 M11 21h11 M11 25h7"/>',
person:'<circle cx="16" cy="9" r="5"/><path d="M6 29v-5a10 10 0 0 1 20 0v5 M16 18v10 M12 19l4 4 4-4"/>',
search:'<circle cx="13" cy="13" r="9"/><path d="m20 20 9 9"/>',
list:'<path d="M8 5H5v24h23V5h-3 M11 3h11v6H11z M10 16l2 2 4-4 M19 16h5 M10 23h6 M19 23h5"/>'
};
const icon=(name)=>'<svg class="icon" viewBox="0 0 32 32" aria-hidden="true">'+icons[name]+'</svg>';
const arrow='<span class="arrow" aria-hidden="true">↗</span>';
const link=(text,to)=>'<a class="textlink" href="#'+to+'">'+text+arrow+'</a>';
const crop=(file,W,H,x,y,w,h,alt,cls='')=>'<div class="crop '+cls+'" style="aspect-ratio:'+w+'/'+h+'"><img alt="'+alt+'" src="studies/'+file+'.png" width="'+W+'" height="'+H+'" style="width:'+W/w*100+'%;left:'+(-x/w*100)+'%;top:'+(-y/h*100)+'%"></div>';
const section=(id,h,name,body,cls='')=>'<section class="frame '+cls+'" id="'+id+'" data-name="'+name+'" style="--height:'+h+'px"><div class="inner">'+body+'</div><div class="grid-guide" aria-hidden="true"><span>1440 px · 240 px margins</span></div></section>';
const faq=[
['报价前，需要准备什么？','商品、发货方式、月货量、目的地、IOR需求及联系方式。'],
['货量未定，可以咨询吗？','可以先说明商品、销售计划与发货节奏；未确定的项目可填写“未定”。'],
['一件代发与FBA补货有何区别？','一件代发逐单发往买家；FBA中转补货按计划发往亚马逊仓库。'],
['运输、清关与入仓能一起咨询吗？','可以一起提交需求，具体承接环节与各方责任在方案中确认。'],
['报价包含税费与附加费用吗？','以具体报价清单为准，请核对税费、最低收费与附加作业条件。'],
['不清楚是否需要IOR怎么办？','可选择“不清楚”，并提供商品与交易资料，进一步确认需求。'],
['美国仓库是自营的吗？','是的，PNPLINE直接运营美国仓库。可进一步了解场地资料与作业范围。'],
['如何查询库存与出库进度？','可先了解WMS的库存、订单与出库功能；可用范围以实际方案为准。']];
const frames=[];
frames.push(section('hero',1080,'히어로',
'<header class="header"><a class="brand" href="#hero" aria-label="PNPLINE"><img src="PNP-LINE.webp" alt="PNPLINE"></a><nav aria-label="主导航"><a href="#operations">美国海外仓</a><a href="#journey">头程运输</a><a href="#customs">清关与合规</a><a href="#customers">平台方案</a><a href="#operations">系统</a><a href="#operations">关于我们</a><a href="#faq">资讯</a></nav><a class="button" href="#quote">免费获取报价</a></header>'+
'<div class="hero-copy"><p class="eyebrow">PNPLINE · 跨境物流</p><h1>美国自营海外仓<br>从中国出货，到美国履约</h1><div class="hero-actions"><a class="button" href="#quote">免费获取报价'+arrow+'</a><a class="button secondary" href="#operations">查看自营仓库</a></div></div>'+
'<div class="hero-route"><span>'+icon('box')+'中国出货</span><i></i><span>'+icon('warehouse')+'美国自营仓</span><i></i><span>'+icon('truck')+'美国配送</span></div><span class="media-note">概念示意</span>','hero'));
frames.push(section('journey',960,'전체 물류 흐름','<div class="section-head"><h2>从中国到美国，<span class="accent">一条清晰的路径</span></h2>'+link('了解运输方案','services')+'</div>'+
crop('02-journey',1774,887,0,218,1774,430,'中国工厂、海运、美国清关、自营仓与美国配送的连续微缩流程','route-art')+
'<div class="journey-labels">'+['中国工厂','头程运输','美国清关','美国自营海外仓','美国境内配送'].map((t,i)=>'<div><b>0'+(i+1)+'</b><h3>'+t+'</h3></div>').join('')+'</div><div class="journey-bottom"><p class="note">路线与服务范围，以确认方案为准</p><p class="note">流程示意</p></div>','journey'));
frames.push(section('customers',1000,'고객 유형별 선택','<h2>您的业务，<span class="accent">走哪条路？</span></h2>'+
crop('03-customers',1774,887,0,166,1774,471,'同一批货物分向Amazon、独立站订单与B2B交付的三条路径','customer-art')+
'<div class="customer-grid"><article><h3>Amazon卖家</h3><p>FBA补货 · FBM出库</p>'+link('查看方案','services')+'</article><article><h3>独立站 / TikTok Shop</h3><p>本地订单配送</p><div class="links">'+link('Shopify','services')+link('TikTok Shop','services')+'</div></article><article><h3>工厂与贸易商</h3><p>整柜运输 · B2B交付</p>'+link('了解B2B配送','services')+'</article></div>','customers'));
const services=[
['一件代发','拣货 · 包装 · 出库',0,133,817,251,'微缩订单包装与出库作业'],
['FBA中转补货','验收 · 贴标 · 补货',846,135,826,249,'微缩托盘、贴标与集装箱'],
['头程运输','FCL · LCL · 空运',0,500,831,248,'微缩货船与飞机'],
['IOR与清关咨询','资料 · 角色 · 责任',844,505,828,239,'货物资料与清关角色的微缩示意']];
frames.push(section('services',1120,'핵심 서비스','<h2>需要哪一环，<span class="accent">我们就从哪里开始</span></h2><div class="services-grid">'+services.map(s=>'<article class="service">'+crop('04-services',1672,941,s[2],s[3],s[4],s[5],s[6])+'<h3>'+s[0]+'</h3><p class="sub">'+s[1]+'<a href="#quote" aria-label="咨询'+s[0]+'">↗</a></p></article>').join('')+'</div><div class="service-links">'+link('仓储与库存','operations')+link('退货与检品','quote')+link('B2B配送','quote')+link('其他需求','quote')+'</div>','services dark'));
frames.push(section('operations',1040,'직영창고·책임·시스템','<h2>美国仓库，<span class="accent">由PNPLINE直接运营</span></h2><div class="operations-grid"><div>'+
crop('05-operations',1672,941,9,232,1085,557,'美国仓库入库、库存、出库作业模型；概念示意','warehouse-art')+'<div class="warehouse-link">'+link('查看自营仓库','quote')+'</div></div><div class="ops-panels"><article class="ops-panel"><h3>责任清晰</h3><div class="roles">'+[['document','资料'],['person','IOR'],['box','服务范围']].map(v=>'<span>'+icon(v[0])+v[1]+'</span>').join('')+'</div>'+link('了解责任范围','customs')+'</article><article class="ops-panel"><h3>库存与出库，看得清</h3><div class="wms">'+[['search','库存查询'],['list','订单状态'],['truck','出库记录']].map(v=>'<div class="wms-row">'+icon(v[0])+'<span>'+v[1]+'</span><span>查看 ↗</span></div>').join('')+'</div><p class="note">系统概念示意</p><div class="panel-bottom">'+link('了解WMS','quote')+link('API对接','quote')+'</div></article></div></div>','operations'));
frames.push(section('customs',840,'발송 전 확인',
crop('06-customs',1896,830,0,70,1170,720,'商品资料、IOR需求与责任范围的箱内资料示意')+
'<div><h2>发货前，<br><span class="accent">先把条件确认清楚</span></h2><div class="checklist">'+[['document','商品资料'],['person','IOR需求'],['box','责任范围']].map(v=>'<div>'+icon(v[0])+v[1]+'</div>').join('')+'</div>'+link('了解清关与合规','quote')+'</div>','customs'));
frames.push(section('costs',1000,'비용 구성','<div class="section-head"><h2>费用拆开看，<span class="accent">报价更清楚</span></h2>'+link('查看费用说明','quote')+'</div>'+
crop('07-costs',1672,941,0,237,1672,266,'运输、清关、仓储、操作与配送的五项费用组成','cost-art')+
'<div class="cost-labels">'+['头程运输','清关与合规','仓储','仓内操作','美国配送'].map(t=>'<span>'+t+'</span>').join('')+'</div><div class="scenarios"><div class="scenario">'+icon('box')+'<div><h3>FBA · 20 CBM</h3><p>运输 / 清关 / 暂存 / 贴标 / 补货</p></div></div><div class="scenario">'+icon('truck')+'<div><h3>独立站 · 每月500单</h3><p>库存 / 拣配 / 包装 / 配送</p></div></div></div><div class="cost-notes"><p class="note">询价场景示意，不代表客户案例或价格承诺</p><p class="note">核对计费单位、包含项目与附加条件</p></div>','costs'));
frames.push(section('faq',1040,'FAQ','<div><p class="eyebrow">FAQ</p><h2>先解答，<br><span class="accent">再出发</span></h2>'+crop('08-faq',1672,941,92,241,622,595,'青色微缩集装箱与搬运工人')+link('还有问题？联系我们','quote')+'</div><div class="faq-list">'+faq.map((v,i)=>'<details'+(i===0?' open':'')+'><summary>'+v[0]+'</summary><p>'+v[1]+'</p></details>').join('')+'</div>','faq'));
frames.push(section('quote',1080,'견적 문의','<div><h2>下一程，<br>从您的<span class="accent">需求开始</span></h2><div class="contact-steps"><span>提交需求</span> → <span>确认范围</span> → <span>沟通报价</span></div>'+
crop('09-inquiry',1672,941,0,379,727,562,'微缩货车从仓库沿青色路线出发')+
'</div><div><div class="form-panel" role="group" aria-label="物流需求表单设计"><div class="form-grid"><label class="form-field">产品类目<input placeholder="商品名称或类目"></label><label class="form-field">发货方式<select><option>未定</option><option>海运整柜（FCL）</option><option>海运拼箱（LCL）</option><option>空运</option></select></label><label class="form-field">月出货量<input placeholder="预计货量及单位"></label><label class="form-field">目的地<select><option>PNPLINE美国自营仓</option><option>FBA仓</option><option>最终消费者</option><option>美国企业或零售收货点</option><option>未定</option></select></label><label class="form-field">是否需要IOR服务<select><option>不清楚</option><option>需要</option><option>不需要</option></select></label><label class="form-field">联系邮箱<input type="email" placeholder="请输入联系邮箱"></label></div><label class="consent"><input type="checkbox"><span>我已阅读并同意<a href="#footer">《隐私政策》</a></span></label><button class="button" type="button" aria-disabled="true" title="静态设计预览，不发送数据">提交需求'+arrow+'</button><p class="note">尚未确定的内容，可填写「未定」。</p></div><p class="form-caption">设计预览 · 不发送数据</p></div>','inquiry dark'));
const footerLinks=[['服务',[['美国海外仓','operations'],['头程运输','journey'],['清关与合规','customs']]],['了解PNPLINE',[['关于我们','operations'],['自营仓库资料','operations'],['资质与合规','customs']]],['报价与联系',[['价格与报价','costs'],['联系我们','quote'],['合作伙伴','quote']]],['语言',[['简体中文','hero'],['한국어','hero'],['English','hero']]]];
frames.push(section('footer',680,'푸터','<div class="footer-grid"><div><a href="#hero" class="brand"><img src="PNP-LINE.webp" alt="PNPLINE"></a><p class="footer-tagline">美国自营海外仓与跨境物流</p>'+crop('10-footer',2048,768,100,390,545,200,'蓝色微缩配送车与包裹')+'</div>'+footerLinks.map(g=>'<div><h3>'+g[0]+'</h3><ul>'+g[1].map(v=>'<li><a href="#'+v[1]+'">'+v[0]+'</a></li>').join('')+'</ul></div>').join('')+'</div><div class="footer-bottom"><span>PNPLINE</span><a href="#footer">隐私政策</a></div>','footer'));
document.querySelector('#sheet').innerHTML=frames.join('');
document.querySelector('.hero').insertAdjacentHTML('afterbegin','<img class="hero-background" src="hero-harbor.jpg" alt=""><div class="hero-shade"></div>');
const jump=document.querySelector('#jump');
document.querySelectorAll('.frame').forEach((f,i)=>jump.add(new Option(String(i+1).padStart(2,'0')+' · '+f.dataset.name,f.id)));
const isExport=new URLSearchParams(location.search).has('export');
document.body.classList.toggle('export',isExport);
let fit=!isExport;
function resize(){const available=innerWidth-(innerWidth<=760?20:48);const scale=fit?Math.min(available/1920,1):1;document.documentElement.style.setProperty('--scale',scale);const space=document.querySelector('.sheet-space');space.style.width=1920*scale+'px';space.style.height=document.querySelector('.sheet').offsetHeight*scale+'px';document.querySelector('#fit').setAttribute('aria-pressed',String(fit));document.querySelector('#actual').setAttribute('aria-pressed',String(!fit));}
document.querySelector('#fit').onclick=()=>{fit=true;resize()};
document.querySelector('#actual').onclick=()=>{fit=false;resize()};
document.querySelector('#guide').onchange=e=>document.body.classList.toggle('guides',e.target.checked);
jump.onchange=()=>{const target=document.getElementById(jump.value);window.scrollTo({top:scrollY+target.getBoundingClientRect().top-90,behavior:'smooth'});history.replaceState(null,'','#'+target.id)};
document.querySelectorAll('.faq details').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)document.querySelectorAll('.faq details').forEach(other=>{if(other!==d)other.open=false})}));
window.addEventListener('resize',resize);resize();
