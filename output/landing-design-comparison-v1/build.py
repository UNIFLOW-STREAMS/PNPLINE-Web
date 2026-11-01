from pathlib import Path
import re, html, json, hashlib

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1]/'docs/pnpline-china-source-content/pnpline-landing-mvp-copy-v4.zh-CN.md'
raw = SOURCE.read_text(encoding='utf-8-sig')
chunks = re.split(r'<a id="([^"]+)"></a>',raw)
sections = dict(zip(chunks[1::2],chunks[2::2]))

def inline(s):
    s=html.escape(s)
    s=re.sub(r'\*\*(.*?)\*\*',r'<strong>\1</strong>',s)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',s)

def md(s):
    blocks=[]
    for b in s.strip().split('\n\n'):
        if b.startswith('- '):blocks.append('<ul>'+''.join('<li>'+inline(x[2:])+'</li>' for x in b.splitlines())+'</ul>')
        elif b.startswith('### '):blocks.append('<h3>'+inline(b[4:])+'</h3>')
        elif b.startswith('## '):blocks.append('<h2>'+inline(b[3:])+'</h2>')
        elif b.startswith('# '):blocks.append('<h1>'+inline(b[2:])+'</h1>')
        else:blocks.append('<p>'+inline(b)+'</p>')
    return '\n'.join(blocks)

arrow='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6"/></svg>'
shapes=[
'<path d="m3 7 9-5 9 5v10l-9 5-9-5zM3 7l9 5 9-5M12 12v10M7.5 4.5l9 5v5"/>',
'<path d="M2 6h12v11H2zM14 10h4l4 5v2h-8M6 17v0M18 17v0"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>',
'<path d="M5 3h10l4 4v14H5zM15 3v5h4M8 12h8M8 16h6"/>',
'<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 3v18M8 9h13M13 14h4M13 17h4"/>'
]
icons=['<svg viewBox="0 0 24 24" aria-hidden="true">'+x+'</svg>' for x in shapes]
hero_blocks=sections['journey'].strip().split('\n\n')
headline=hero_blocks[0][2:]
head_first,head_last=headline.split('，',1)
description=[x for x in hero_blocks if not x.startswith(('#','[','PNPLINE'))]
hero_description=''.join('<p>'+inline(x)+'</p>' for x in description)
service_chunks=re.split(r'\n### ',sections['services'])
service_intro=md(service_chunks[0])
service_modules=[]
for i,block in enumerate(service_chunks[1:]):
    title,body=block.strip().split('\n',1)
    body=re.sub(r'\n\[获取物流报价\]\(#quote\)\s*$', '',body).strip()
    service_modules.append('<article class="service-module service-'+str(i)+'"><div class="service-title"><span class="service-icon">'+icons[i]+'</span><h3>'+inline(title)+'</h3></div><div class="service-copy">'+md(body)+'</div></article>')
quote_intro=md(sections['quote'].split('| 信息')[0])
form='''<form novalidate><div class="form-fields">
<label for="product">产品类目<input id="product" name="product" autocomplete="off" placeholder="商品名称或所属类目。"></label>
<label for="shipping">发货方式<span class="select-wrap"><select id="shipping" name="shipping"><option>未定</option><option>海运整柜（FCL）</option><option>海运拼箱（LCL）</option><option>空运</option></select></span></label>
<label for="volume">月出货量<input id="volume" name="volume" placeholder="未定" aria-describedby="volume-hint"><span class="field-hint" id="volume-hint">预计货量并注明单位，例如体积、重量或订单数；也可填写“未定”。</span></label>
<label for="destination">目的地<span class="select-wrap"><select id="destination" name="destination"><option>未定</option><option>FBA仓</option><option>PNPLINE美国自营仓</option><option>最终消费者</option><option>美国企业或零售收货点</option></select></span></label>
<label for="ior">是否需要IOR服务<span class="select-wrap"><select id="ior" name="ior"><option>不清楚</option><option>需要</option><option>不需要</option></select></span></label>
<label for="email">联系邮箱<input id="email" name="email" type="email" autocomplete="email" placeholder="用于本次询价联系的邮箱。"></label>
</div><label class="consent"><input type="checkbox" name="consent"><span>我已阅读<a href="privacy.html">《隐私政策》</a>，同意为处理本次询价使用所填信息。</span></label>
<div class="form-submit"><button type="submit" class="button primary">提交询价需求 '''+arrow+'''</button><p>报价与执行条件将在资料及服务范围确认后沟通。</p></div><p class="form-status" role="status"></p></form>'''

for variant in ['a','b']:
    doc='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PNPLINE · '''+variant.upper()+'''</title><link rel="stylesheet" href="assets/font.css"><link rel="stylesheet" href="design.css"></head><body class="variant-'''+variant+'''">
<a class="skip-link" href="#services">查看服务范围</a>
<header class="site-header"><a class="brand" href="#journey" aria-label="PNPLINE"><img src="assets/PNP-LINE.webp" alt="PNPLINE" width="1500" height="400"></a><span class="brand-description">跨境物流服务</span><nav aria-label="主导航"><a href="#services">服务范围</a><a href="#quote" class="nav-quote">获取物流报价 '''+arrow+'''</a></nav></header>
<main><section id="journey" class="journey"><div class="hero-pin"><div class="hero-heading"><h1><span>'''+inline(head_first)+'，</span><span>'+inline(head_last)+'''</span></h1></div><div class="hero-media"><img class="hero-poster" src="assets/hero-poster.jpg" alt="" fetchpriority="high"><video muted playsinline preload="auto" poster="assets/hero-poster.jpg" aria-label="物流旅程画面" src="assets/hero-scrub.mp4"></video></div><div class="hero-bottom"><div class="hero-description">'''+hero_description+'''</div><div class="hero-actions"><a href="#quote" class="button primary">获取物流报价 '''+arrow+'''</a><a href="#services" class="text-link">查看服务范围 '''+arrow+'''</a></div></div></div></section>
<section id="services" class="services section"><div class="container"><div class="section-intro">'''+service_intro+'''</div><div class="service-list">'''+''.join(service_modules)+'''</div><a class="text-link service-cta" href="#quote">获取物流报价 '''+arrow+'''</a></div></section>
<section id="quote" class="quote section"><div class="container quote-layout"><div class="quote-intro">'''+quote_intro+'''</div>'''+form+'''</div></section></main>
<footer><a class="footer-brand" href="#journey">PNPLINE</a><p>美国自营海外仓与跨境物流服务</p><a href="privacy.html">隐私政策</a></footer><script src="design.js"></script></body></html>'''
    (ROOT/f'{variant}.html').write_text(doc,encoding='utf-8')

manifest={'source':str(SOURCE.relative_to(ROOT.parents[1])).replace('\\','/'),'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'variants':['a.html','b.html'],'scope':['journey','services','quote'],'video':{'source':'hero-section-video/blockout/pacing-33s-v001/preview/pnpline-33s-30fps-v001.mp4','derived':'assets/hero-scrub.mp4','duration':33,'keyframeIntervalFrames':6},'status':'design-comparison-not-final-selection'}
(ROOT/'content-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Built A and B from Chinese V4; same copy, three sections each')
