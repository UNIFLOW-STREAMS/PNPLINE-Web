from pathlib import Path
import re, html

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'docs/pnpline-china-source-content/pnpline-landing-mvp-copy-v4.zh-CN.md'
raw = SOURCE.read_text(encoding='utf-8-sig')
parts = re.split(r'<a id="([^"]+)"></a>', raw)
sections = dict(zip(parts[1::2], parts[2::2]))

def inline(s):
    s = html.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)

def md(s):
    out, lines, i = [], s.strip().splitlines(), 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1; continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+', x) for x in cells): rows.append(cells)
                i += 1
            out.append('<div class="table-wrap"><table><thead><tr>' + ''.join('<th scope="col">'+inline(c)+'</th>' for c in rows[0]) + '</tr></thead><tbody>')
            out.extend('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in row)+'</tr>' for row in rows[1:])
            out.append('</tbody></table></div>'); continue
        if line.startswith('- ') or re.match(r'\d+\. ', line):
            ordered = bool(re.match(r'\d+\. ', line)); tag = 'ol' if ordered else 'ul'
            out.append('<'+tag+'>')
            while i < len(lines) and (re.match(r'\d+\. ', lines[i]) if ordered else lines[i].startswith('- ')):
                out.append('<li>'+inline(re.sub(r'^(?:\d+\.|-) ', '', lines[i]))+'</li>'); i += 1
            out.append('</'+tag+'>'); continue
        heading = re.match(r'^(#{1,3}) (.*)', line)
        if heading:
            n = len(heading[1]); out.append(f'<h{n}>'+inline(heading[2])+f'</h{n}>')
        else: out.append('<p>'+inline(line)+'</p>')
        i += 1
    return '\n'.join(out)

nav = md(parts[0].split('---')[-1]).removeprefix('<p>').removesuffix('</p>')
hero = md(sections['journey'])
hero = hero.replace('<p>PNPLINE · 跨境物流服务</p>', '')
hero = '<p class="eyebrow">PNPLINE · 跨境物流服务</p>' + hero
hero = hero.replace('<p><a href=', '<p class="actions"><a href=')
content = []
labels = {'services':'서비스 범위', 'customers':'고객별 요구', 'evidence':'직영 창고·운영', 'process':'상담 절차', 'pricing':'비용 구성', 'faq':'자주 묻는 질문', 'quote':'단일 견적 폼'}
footer = sections['quote'].split('\n---')[1]
for sid in list(sections)[1:]:
    source = sections[sid].split('\n---')[0]
    if sid in ('services', 'evidence'):
        blocks = re.split(r'\n### ', source)
        intro = md(blocks[0]); cards = []
        for block in blocks[1:]:
            block = re.sub(r'\n\[获取物流报价\]\(#quote\)\s*$', '', block)
            cards.append('<article>'+md('### '+block)+'</article>')
        body = intro + '<div class="cards">' + ''.join(cards) + '</div><p class="actions"><a href="#quote">获取物流报价</a></p>'
    elif sid == 'faq':
        blocks = re.split(r'\n### ', source)
        body = md(blocks[0]) + '<div class="faq-list">'
        for b in blocks[1:]:
            title, answer = b.split('\n',1)
            body += '<details><summary>'+inline(title)+'</summary>'+md(answer)+'</details>'
        body += '</div>'
    elif sid == 'quote':
        body = md(source.split('| 信息')[0])
        body += '''<form novalidate><div class="form-grid">
<label>产品类目<input name="product" placeholder="商品名称或所属类目。"></label>
<label>发货方式<select name="shipping"><option>未定</option><option>海运整柜（FCL）</option><option>海运拼箱（LCL）</option><option>空运</option></select></label>
<label>月出货量<input name="volume" placeholder="未定" aria-describedby="volume-hint"><span id="volume-hint" class="field-hint">预计货量并注明单位，例如体积、重量或订单数；也可填写“未定”。</span></label>
<label>目的地<select name="destination"><option>未定</option><option>FBA仓</option><option>PNPLINE美国自营仓</option><option>最终消费者</option><option>美国企业或零售收货点</option></select></label>
<label>是否需要IOR服务<select name="ior"><option>不清楚</option><option>需要</option><option>不需要</option></select></label>
<label>联系邮箱<input type="email" name="email" placeholder="用于本次询价联系的邮箱。"></label>
</div><label class="consent"><input type="checkbox" name="consent"><span>我已阅读<a href="/privacy/">《隐私政策》</a>，同意为处理本次询价使用所填信息。</span></label>
<button type="submit">提交询价需求</button><p class="form-result" role="status"></p></form>
<p>报价与执行条件将在资料及服务范围确认后沟通。</p>'''
    else: body = md(source)
    content.append(f'<section id="{sid}" class="content-section"><div class="annotation">{labels[sid]} · #{sid}</div>{body}</section>')

svg = '''<svg viewBox="0 0 1200 720" aria-hidden="true" id="world"><defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#d7dcdf" stroke-width="1"/></pattern></defs><rect width="1200" height="720" fill="url(#grid)"/>
<g id="world-camera" fill="#e8ebed" stroke="#899399" stroke-width="2">
<ellipse cx="760" cy="420" rx="300" ry="190" fill="#f1f3f4"/><ellipse cx="760" cy="420" rx="150" ry="190" fill="none"/><path d="M460 420H1060M490 340H1030M490 500H1030" fill="none"/>
<path d="M520 280l80-35 72 55-24 70-100 25-43-63zM859 355l90-54 80 80-32 93-89 6-37-57z" fill="#d3d9dc"/>
<path id="route" d="M550 365C610 230 820 240 935 390S840 550 700 510" stroke="#68757d" stroke-width="3" stroke-dasharray="7 8" fill="none"/>
<g transform="translate(495 305)"><path d="M0 0V-65H80V0M-12-65H96M62-65V-20" fill="none"/><rect x="0" y="0" width="46" height="25"/><rect x="50" y="0" width="46" height="25"/><path d="M-22 30H120l-20 25H0z" fill="#b5bfc5"/></g>
<g transform="translate(890 380)"><path d="M0 0l55-35 95 0 35 35v75H0z" fill="#d1d8dc"/><path d="M0 0H185M65 0V75M15 30H50V75H15zM90 30H125V75H90zM140 30H175V75H140z" fill="none"/></g>
<g transform="translate(645 505)"><rect width="60" height="34"/><path d="M60 12h24l15 22H60z"/><circle cx="15" cy="40" r="9"/><circle cx="76" cy="40" r="9"/></g>
<g id="cargo" fill="#68757d" stroke="white" stroke-width="3"><rect x="-13" y="-13" width="26" height="26" rx="2"/><path d="M-7-7L7 7M7-7L-7 7"/></g></g></svg>'''

template = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PNPLINE · 单页线框 V4</title><link rel="stylesheet" href="wireframe.css"></head><body>
<div class="review-bar" lang="ko"><strong>PNPLINE <span>와이어프레임 / 중문 V4</span></strong><div><button id="overview" aria-pressed="false">전체 구조</button><button id="notes" aria-pressed="true">검토 패널 숨기기</button></div></div>
<aside class="inspector" lang="ko"><p class="rail-kicker">INTERACTION SPEC / 검토 전용</p><h2>스크롤 위치가<br>영상 시점을 결정합니다.</h2><p>히어로를 고정한 채 화면을 아래위로 스크롤해 보세요. 멈추면 해당 시점이 유지됩니다.</p>
<div class="readout"><span>스크롤 진행도</span><strong id="progress-value">0%</strong><progress id="progress" max="1" value="0"></progress><span>영상 위치</span><strong id="time-value">0.000 × T</strong></div>
<p class="formula">p = 스크롤 이동 / 고정 구간 길이<br>영상 시점 t = p × T</p><p class="small">T는 영상 길이입니다. 최종 영상이 없어 기본 화면은 위치 대응을 보여 주는 도식입니다.</p>
<div class="seek-buttons"><button data-seek="0">0%</button><button data-seek="0.25">25%</button><button data-seek="0.5">50%</button><button data-seek="0.75">75%</button><button data-seek="1">100%</button></div>
<label class="file-label">작업 영상 연결 · 선택 사항<input id="media-input" type="file" accept="video/*"></label><p class="small" id="media-status" role="status">파일은 브라우저 안에서만 사용합니다.</p>
<details><summary>S1–S7 제작 구간</summary><p class="small">중국 선적 → 출항 → 항해 → 미국 입항 → 창고 도착 → 창고 작업 → 출고·배송</p><p class="small">실제 구간 경계는 최종 미디어 명세로 확정합니다. 7등분이나 임의 초 단위를 확정하지 않습니다.</p></details>
<nav class="outline" aria-label="검토용 섹션 이동"><a href="#journey">히어로</a><a href="#services">서비스 범위</a><a href="#customers">고객별 요구</a><a href="#evidence">직영 창고·운영</a><a href="#process">상담 절차</a><a href="#pricing">비용 구성</a><a href="#faq">FAQ</a><a href="#quote">견적 폼</a></nav>
<p class="small">검토 패널과 청색 주석은 제작 참고용이며 공개 UI에 포함되지 않습니다. ‘전체 구조’에서는 긴 스크롤 구간을 접어 배치를 살펴봅니다.</p></aside>
<div class="site"><header><a class="brand" href="#journey">PNPLINE</a><nav aria-label="主导航">{{NAV}}</nav><a class="mobile-quote" href="#quote">获取物流报价</a></header>
<main><section id="journey"><div class="hero-pin"><div class="media-layer">{{SVG}}<video id="hero-video" muted playsinline preload="metadata" aria-label="物流旅程画面" hidden></video></div><div class="hero-copy">{{HERO}}</div><div class="annotation hero-note">영상 영역 · 스크롤 위치 → 시점 이동 · 문구와 CTA는 웹 UI로 고정</div></div></section>{{CONTENT}}</main>
<footer>{{FOOTER}}</footer></div>
<dialog id="privacy-preview" lang="ko"><h2>별도 개인정보 처리방침 페이지</h2><p>운영 사이트에서는 /privacy/로 연결합니다. 전문 작성·검수가 남아 있어 이 와이어프레임에는 정책 내용을 넣지 않았습니다.</p><button id="close-privacy">랜딩으로 돌아가기</button></dialog>
<script src="wireframe.js"></script></body></html>'''
for key, val in {'NAV':nav,'SVG':svg,'HERO':hero,'CONTENT':''.join(content),'FOOTER':md(footer)}.items():
    template = template.replace('{{'+key+'}}',val)
(HERE/'index.html').write_text(template,encoding='utf-8')
standalone = template.replace('<link rel="stylesheet" href="wireframe.css">', '<style>'+ (HERE/'wireframe.css').read_text(encoding='utf-8') + '</style>')
standalone = standalone.replace('<script src="wireframe.js"></script>', '<script>'+ (HERE/'wireframe.js').read_text(encoding='utf-8') + '</script>')
(HERE/'standalone.html').write_text(standalone,encoding='utf-8')
print('Built', HERE/'index.html')
