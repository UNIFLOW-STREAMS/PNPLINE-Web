"""Prepare the approved eight-image design brief; no image generation here."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'docs/pnpline-china-source-content/pnpline-landing-mvp-copy-v4.zh-CN.md'
source = SOURCE.read_text(encoding='utf-8-sig')
chunks = re.split(r'<a id="([a-z]+)"></a>', source)
copy = {chunks[i]: chunks[i + 1].strip() for i in range(1, len(chunks), 2)}

common = '''Use case: ui-mockup. Produce ONE high-fidelity horizontal website SECTION concept image, straight-on, no browser/device frame, no presentation annotations, no collage. This belongs to a consistent eight-section PNPLINE Chinese logistics landing site. Design a real premium corporate logistics website, restrained Swiss editorial precision inspired by United Carriers hierarchy, not generic SaaS cards.
DESIGN SYSTEM: requested canvas width exactly 1920px. Except hero media, content maximum width is exactly 1440px centered, x=240 through1680. Preserve this generous 240px blank gutter on each side; background surfaces can span1920. All body comps share Noto Sans SC-like Chinese sans serif, correct clear Chinese glyphs. H2 44px weight600, subgroup titles24px weight500, body18px line-height1.75, labels15px, helpers14px. H1 only hero64px weight600. White #FCFDFD, pale-neutral #F3F6F7, ink #102A33, secondary #536165, hairline #DCE3E6. Brand cyan #00ABE1 used sparingly on primary CTA with DARK #102A33 text, never white CTA text. Link #00799F underlined. Square corners, straight edges, no drop shadows, no gradients except readable hero scrim, no pills, no floating orbs, no glass. All headings and paragraphs on coherent axes, generous intentional whitespace, 96px outer vertical padding,32px column gaps. Primary CTA rectangular52px tall with optional slim diagonal arrow. No made-up numbers, guarantees, certifications, testimonials, partner logos, prices, warehouses, people, dashboard data, maps or operating evidence. No English section eyebrows or decorative section numbering. Only the real3-stepprocess uses small step numbers.
MEDIA: retain IMAGE placeholders at the instructed slots, flat muted random-color rectangles with dark centered IMAGE lettering. They are deliberate user-requested asset placeholders; do not replace them with AI illustrations or operational photographs. All Chinese copy must be accurately typeset, not summarized or invented. Do not show Markdown tokens or anchor IDs. Do not shrink whole composition into a centered postcard or surround it with a gray canvas. Render website pixels edge to edge. Exact source text follows; use the layout-specific visibility rules over incidental markdown structure. Never draw labels for canvas dimensions, margins or this brief.'''

plans = [
 ('01-hero','journey','1920x1080', '''Only hero plus its navigation, no lower section. Use supplied official PNPLINE logo unchanged in a white72px header, logo and nav aligned within1440 from x240 to1680. Nav: 服务范围 / 仓库与系统 / 费用说明 / 常见问题 then cyan 获取物流报价. The supplied second image is an EXISTING unfinished video frame: keep its recognizable crane/container subject and use it as a full-bleed hero media canvas x0..1920 under header. It is NOT evidence of a real facility. Do not redesign or photorealize the video content. Dark ink scrim behind a confident lower-left text composition, fading toward unobscured right. Large2line white H1 at x240: 美国自营海外仓， / 衔接出货与订单履约. At64px, body18px around560px wide; text/CTAgroup vertically aroundmiddle-lower but not touching bottom. Eyebrow PNPLINE · 跨境物流服务 above H1. Supporting paragraph only the one starting依托PNPLINE. The second paragraph starting从一件代发 is moved toservices and MUST NOT appear here. Two52px CTAs 获取物流报价 cyan with darktext, 查看服务范围 solidwhite with darktext. This static comp is a frozen point in a scroll-to-video-time hero: NO play button, controls, timeline, autoplay badges, scrolling invitations, concept labels, or S1-S7 captions. Keepvideo full1920width while text aligns content axis. Hero is image-as-canvas, not a textcolumn adjacent to an imagecolumn.'''),
 ('02-services','services','1920x1200', '''Onlyservices section on white. Top-left44px2line title with intro underneath; use full1440content. Include additional hero paragraph before serviceintro: 从一件代发、FBA补货到批量交付，先明确需要的服务，再确认作业条件与费用。 Below intro four editorial rows separated by fine horizontal rules, not cards. Title column x240..550, explanation x600..1330, supportingimage columnx1370..1680 for FIRST TWO rows only. First larger row 仓储与订单履约 with openingdescription then four named subworkitems in clear2x2 grouping, eachwith full explanation. First IMAGE placeholder about280x210, muted dustybluegray. Second transport row complete explanation plus smallerhorizontalIMAGE placeholder mutedstonegray. Final IOR and systemsrows are textonly, body spansrestwidth. Preserve allfourservices incl legal/acceptance qualification words, no numberedbadges. End cyan 获取物流报价. Fitallfourrows with readable18pxbody on1200highcanvas; no cropping or miniaturepage.'''),
 ('03-customers','customers','1920x824', '''Onlycustomer-types section, white. Clean compact editorial comparison. Title44px top-left on2lines. Below a wide ruledlist with3spaciousrows: left400px named saleschannel, central750px fullrequirements, right200px smallunderlined relevantservice link. Row1 Amazon FBA / FBM -> 仓储与订单履约; row2 Shopify独立站 / TikTok Shop -> 库存与系统对接; row3 工厂、贸易商与B2B供货方 -> 中国出货与美国境内运输. Show all3full explanations and platform-nonendorsementnote below. No platformlogos, photos, cardboxes or repeatedquoteCTA. Type and rules createinterest, no decoration.'''),
 ('04-evidence','evidence','1920x1080', '''Onlywarehouseand systems section. Pale #F3F6F7 fullbackground. Two-line44pxtitle top-left and full intro beneath. Two deliberate asymmetrical editorial media/textblocks: left atx240 width760, right atx1064 width616 starting64pxlower. Leftwide IMAGE rectangle lightbluegray about760x350, right IMAGE rectanglemutedlavendergray about616x300. Place heading and respective full explanatoryparagraph directly beloweach. Maintain depth from alignmentonly, no shadows. This offset is the site's single deliberate secondary visual motif. NO warehouse photo or fabricatedWMS screenshot; bothmustclearlyread IMAGE. Headings 仓库与货物交接 and 库存与出库管理. No quoteCTAhere. Clearlabels understandablewithoutimages.'''),
 ('05-process','process','1920x824', '''Onlyprocess section, understatedmini-editorialepisodewithamplewhitespace, white. Title44px2lines x240 near120. Threeequalcolumns across1440width belowtitle, thinrule atop each with smallcyan01,02,03. Titles24px 说明需求 / 核对条件 / 确认报价 and fullprovidedparagraphunder each18px. Do not make oversizeddisplaynumbers or3cards. NoCTA, illustrations, route map, shipmenttracking. Actual content fitsaround500px vertical; use remainingcanvas as breathingroom, notstretchspacebetweenwords. Easy toscaninoneglance.'''),
 ('06-pricing','pricing','1920x1080', '''Onlycostexplanation sectiononwhite, editorial ledgercomposition. Two-line44pxtitle top-left thenfullintroparagraph. Full1440wide2columntable below atx240..1680. Header费用项目 / 需要确认的条件, labelcolumn400px, wideconditionscolumn1040px;5rows with generouspadding and finehorizontalrules, fulltext. No verticalboxborders, pricingcards, numbers, currency, planbadgesorcalculator. Beneathtable longfulladditionalcostnoteleft and cyan 获取物流报价 alignedright. Preserve最低收费 andotherqualifiersclearly. Mostlytext, restrainedonecyanCTA.'''),
 ('07-faq','faq','1920x1080', '''OnlyFAQ sectiononwhite. Narrowlefttitlecolumn x240..640, heading44pxwithmeaningful2-3lines, lots ofintentionalwhiteunderit. Wideaccordion x760..1680 with8questionrows all visible. Onlyfirstrow open; display firstanswer in full. Subsequent7questiontitlesallreadablebutanswerscollapsednotshown. Thinrulesandrightalignedplusicons; firstusesminus. Question20pxmedium, answer18px withlineheight1.75. NoCTA, illustration, boxedcardsorbadges. Firstquestion美国仓库是自营的吗？ with its exactanswer. All8questionsandfirstanswerfitswithouttinytext. NoFAQ Englishdisplayheading.'''),
 ('08-quote','quote','1920x1080', '''Onlyfinalquote section withsubordinatefooterstrip. Pale #F3F6F7 background. Leftcolumn x240..700:44pxtitlemeaningful2linesandfullintro18px. Rightform x856..1680, two412-ishcolumns with24pxgap, threefieldrows. Sixfields inorder产品类目 / 发货方式 / 月出货量 / 目的地 / 是否需要IOR服务 / 联系邮箱. Fixedlabelsabove, input52pxtallwhite with1px#7B8B90squareborders, realisticdropdownchevrononly, nofilledPII. Selectdefaults 未定,未定,不清楚 respectively. Fullsmallhelpertextsforproduct,volume,email belowfields. Consentcheckboxandexactconsentsentencebelowform; underlined隐私政策link. Cyan 提交询价需求 beneathconsent, then exact报价与执行条件将在资料及服务范围确认后沟通。 No extra company/name/phone/servicefields, fakecontactsor submit-success. Lowheightfooteratbottom separatedbyhairline withofficiallogo and 美国自营海外仓与跨境物流服务, sixsmallfooterlinks. Footerbackgroundwhiteandcontentalso1440wide. Headernotrepeated.'''),
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT/'images').mkdir(exist_ok=True)
prompts=[]
for name,key,size,layout in plans:
    body=copy[key]
    if key in ('customers','evidence'):
        body=body.replace('[获取物流报价](#quote)','')
    if key=='journey':
        body=body.replace('从一件代发、FBA补货到批量交付，先明确需要的服务，再确认作业条件与费用。','')
    prompts.append({'id':name,'requestedSize':size,'conceptCanvasWidth':1920,'contentMaxWidth':1440,
                    'prompt':common+'\n\nRequested output size: '+size+' pixels, horizontal.\nLAYOUT: '+layout+'\n\nSOURCE COPY (Chinese, verbatim):\n'+body,
                    'output':'images/'+name+'.png'})
(OUT/'prompts.json').write_text(json.dumps(prompts,ensure_ascii=False,indent=2),encoding='utf-8')
brief='''# PNPLINE 1920 콘셉트 디자인 제작 명세

전체 섹션 계획과 디자인 방향 정의서 및 중문 V4를 사용한다. 이번 사용자 지정 1920px 전체 폭 / 1440px 본문 최대 폭은 이전 1320px 규칙보다 우선한다. 본문 여백은 240px씩, 히어로 영상은 전체 1920px를 사용한다. 헤더와 문구는 읽기 정렬선을 유지한다.

- 산출물: 한 섹션당 가로형 이미지 1개, 총 8개. 긴 전체 페이지 합성 이미지로 대체하지 않는다.
- 밝은 테마 / Noto Sans SC / 공식 #00ABE1 / 짙은 버튼 글자 / 직각 모서리.
- 핵심 구도: 영상 전체 면, 서비스 상세 행, 고객 비교 행, 비대칭 증빙 자료 배치, 짧은 상담 절차, 비용 표, FAQ, 6필드 폼.
- 공통 표현: 세로 간격과 구분선, 편집형 비대칭, 이미지 프레임, FAQ 접이식 행. 장식용 숫자와 가짜 대시보드는 사용하지 않는다.
- 모션 표현은 히어로 고정·시점 제어와 FAQ 열기에 한정. 정적 콘셉트 이미지가 실제 스크롤 동작을 증명하지 않는다.
- 비검증 이미지는 기존 IMAGE 자리표시자 유지. 실제 시설·장비·운영 실적을 새로 생성하지 않는다.
- 히어로 영상의 전진/역방향/정지 프레임 유지와 서비스·견적 즉시 접근 명세를 유지한다. 삭제된 스크롤 초대/콘셉트 표기는 넣지 않는다.
- 기존 V5 구현 파일은 이 작업으로 변경하지 않는다.

## 비용 승인

사용자는 이번 콘셉트 8장에 한해 사전 금액 미확정 상태의 내장 이미지 생성을 명시 승인했다. 기존 누적 비용/생성 수량 기록을 초기화하지 않는다. 이번 승인 외 추가 생성·유료 확대는 포함하지 않는다. 사전 견적을 제공하지 않는 도구이므로 $0 또는 특정 확정 금액으로 기재하지 않는다.

## 출처

- `docs/pnpline-single-page-section-plan-2026-11-01.ko.md`
- `docs/pnpline-design-direction-2026-11-01.ko.md`
- `docs/pnpline-china-source-content/pnpline-landing-mvp-copy-v4.zh-CN.md`
- `resources/logo/PNP-LINE.webp`
- `output/landing-reference-v5/assets/hero-poster.jpg`

정확한 생성 프롬프트는 `prompts.json`에 보존한다. 실제 반환 픽셀 크기는 생성 뒤 별도로 기록하며, 생성 모델의 레이아웃은 실행 코드의 치수 검증을 대체하지 않는다.
'''
(OUT/'BRIEF.md').write_text(brief,encoding='utf-8')
budget_path=ROOT/'docs/pnpline-generation-budget-2026-11-01.json'
budget=json.loads(budget_path.read_text(encoding='utf-8-sig'))
budget['currentPlan']={'newGenerationRequired':True,'estimatedAdditionalCostUsd':None,'estimatedAdditionalGeneratedImages':8,'reuseExistingMedia':True,'fabricateOperationalEvidence':False,'approval':'User explicitly approved these eight concept images with cost unknown, 2026-11-01; no additional variants authorized.'}
budget['totals']['reservedMaxUsd']=None
budget['totals']['reservedMaxImages']=8
budget['entries'].append({'id':'concept-1920-v1','timestamp':'2026-11-01','tool':'image_gen.imagegen','purpose':'Eight separate PNPLINE section concepts','pricingSource':'Built-in tool supplies no preflight USD estimate','maxCostUsd':None,'maxReturnedImages':8,'userConfirmationIfRequired':'이번 콘셉트 8장 생성 허용','status':'approved-reserved','actualCostUsd':None,'actualGeneratedImages':0,'outputPaths':[]})
budget_path.write_text(json.dumps(budget,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prompts':len(prompts),'out':str(OUT),'generationSubmitted':False}))
