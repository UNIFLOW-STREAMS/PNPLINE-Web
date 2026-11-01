"""Hash-bound review page and contact sheets; no Blender source mutations."""
import argparse,hashlib,html,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'review'
SOURCE=ROOT.parent/'cn-unified-curvature-v001/pnpline-cn-unified-curvature-v001.blend'
SOURCE_SHA='f0f07fcbbd00f9f3c2d3402092684e6326610ffcf65678a33490ad5d86f4b978'
FRAMES=[57,96,132,165,253]

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(size,bold=False):
 for p in ['C:/Windows/Fonts/malgunbd.ttf'if bold else'C:/Windows/Fonts/malgun.ttf','C:/Windows/Fonts/arial.ttf']:
  if Path(p).exists():return ImageFont.truetype(p,size)
 return ImageFont.load_default()

def contact(rows,output,title,subtitle,cols=4):
 w,h=430,242;gap=16;cap=34;header=78
 canvas=Image.new('RGB',(cols*w+(cols+1)*gap,header+math.ceil(len(rows)/cols)*(h+cap+gap)+gap),'#eef1ed')
 draw=ImageDraw.Draw(canvas)
 draw.text((gap,13),title,font=font(25,True),fill='#18383d')
 draw.text((gap,47),subtitle,font=font(15),fill='#53676a')
 for i,row in enumerate(rows):
  group_count=min(cols,len(rows)-(i//cols)*cols)
  offset=(canvas.width-(group_count*w+(group_count-1)*gap))/2
  x=int(offset+(i%cols)*(w+gap));y=header+(i//cols)*(h+cap+gap)
  im=Image.open(row['file']).convert('RGB');im.thumbnail((w,h),Image.Resampling.LANCZOS)
  canvas.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))
  label=row.get('caption',f"f{row.get('frame',0):04d} · {row.get('frame',0)/30:.2f}s")
  draw.text((x+4,y+h+7),label,font=font(17),fill='#29464a')
 canvas.save(output,quality=95,subsampling=0)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--draft',action='store_true');args=parser.parse_args()
 delivery=read(ROOT/'delivery.json');candidate=Path(delivery['file']);candidate_sha=sha(candidate)
 assert candidate_sha==delivery['sha256']
 assert sha(SOURCE)==SOURCE_SHA
 before=read(REVIEW/'before-diagnostic/metadata.json');after=read(REVIEW/'after-diagnostic/metadata.json')
 before_actual=read(REVIEW/'before-actual/metadata.json');actual=read(REVIEW/'after-actual/metadata.json')
 assert before['sha256']==before_actual['sha256']==SOURCE_SHA
 assert after['sha256']==actual['sha256']==candidate_sha
 assert all(m['source_saved']is False for m in [before,after,before_actual,actual])
 assert [r['frame']for r in actual['rendered']]==FRAMES
 assert [r['frame']for r in before_actual['rendered']]==FRAMES
 assert all(a['camera']==b['camera']for a,b in zip(actual['rendered'],before_actual['rendered'])),'Actual camera changed between source and candidate'
 before_views={r['name']:r for r in before['rendered']};after_views={r['name']:r for r in after['rendered']}
 assert set(before_views)==set(after_views)=={'shanghai','island','bund_oldtown','top'}
 for name in before_views:
  assert before_views[name]['camera']==after_views[name]['camera'],('Mismatched comparison pose',name)
 verify_path=REVIEW/'density-verification.json';verification=read(verify_path)if verify_path.exists()else None
 verified=bool(verification and verification['candidate_sha256']==candidate_sha and verification.get('source_sha256')==SOURCE_SHA and verification.get('pass')and verification['checks']and all(r['pass'] for r in verification['checks']))
 animation_path=REVIEW/'preservation-verification.json'
 animation=read(animation_path)if animation_path.exists()else None
 animation_verified=bool(animation and animation['sha256']==candidate_sha and animation.get('source_sha256')==SOURCE_SHA and animation.get('pass')and all(animation['checks'].values()))
 if not args.draft:
  assert verified,'Current candidate must pass density verification before final review packaging'
  assert animation_verified,'Current candidate must pass preservation verification before final review packaging'
 check_count=len(verification['checks'])if verified else 0
 animation_check_count=len(animation['checks'])if animation_verified else 0
 contact(actual['rendered'],REVIEW/'actual-camera-contact.jpg','실제 영상 카메라 · 5개 검토 프레임',
         '저장된 카메라에서 촬영 · 30 fps 타임라인 · 렌더 과정에서 원본 파일 저장 없음',cols=3)
 labels={'shanghai':'상하이 전체 · 건축 밀도','island':'스카이라인 섬 · 고층 건물','bund_oldtown':'와이탄 · 석고문 주거지','top':'평면 · 수로와 배치 비교'}
 contact([dict(after_views[n],caption=labels[n])for n in ['shanghai','island','bund_oldtown','top']],REVIEW/'diagnostic-contact.jpg',
         '상하이 밀도 보강 · 배치 검토','임시 진단 카메라 · 재질 색상과 형상 확인용 Workbench 렌더',cols=2)
 cards=''.join(f'<figure><a href="review/after-diagnostic/{n}.png" target="_blank"><img src="review/after-diagnostic/{n}.png" alt="{labels[n]}" loading="lazy"></a><figcaption><strong>{labels[n]}</strong><a href="review/before-diagnostic/{n}.png" target="_blank">수정 전 보기</a></figcaption></figure>'for n in ['island','bund_oldtown','top'])
 frames=''.join(f'<a href="review/after-actual/f{f:04d}.png" target="_blank">f{f:04d}<span>{f/30:.2f}s</span></a>'for f in FRAMES)
 links=[('Blender 작업 파일',candidate.name),('구성 명세','delivery.json')]
 if verification:links.append(('밀도·지면 접촉 검증','review/density-verification.json'))
 for path in sorted(REVIEW.glob('*preservation*verification*.json')):
  links.append(('수로·카메라·애니메이션 보존 검증',path.relative_to(ROOT).as_posix()))
 resources=''.join(f'<a href="{html.escape(url)}">{html.escape(label)}</a>'for label,url in links)
 template='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>상하이 건축 밀도 보강 · 검토</title>
<style>
:root{color-scheme:light;--ink:#193b40;--muted:#5d7274;--line:#d3ddd6;--accent:#166c78;--split:50%}*{box-sizing:border-box}body{margin:0;background:#f3f5ef;color:var(--ink);font-family:"Malgun Gothic",sans-serif;line-height:1.7}main{max-width:1460px;margin:auto;padding:48px 36px 68px}header{display:flex;justify-content:space-between;gap:24px;align-items:flex-start}h1{font-size:37px;letter-spacing:-.05em;line-height:1.25;margin:10px 0 16px}h2{font-size:24px;letter-spacing:-.03em;margin:0 0 16px}p{margin:0;color:var(--muted)}.eyebrow{font-size:12px;letter-spacing:.13em;text-transform:uppercase}.status{padding:7px 15px;border:1px solid #aec8b7;background:#e4eee5;border-radius:30px;font-size:12px;white-space:nowrap}section{margin-top:44px}a{color:var(--accent);text-underline-offset:4px}.compare{position:relative;isolation:isolate;overflow:hidden;line-height:0;border:1px solid var(--line);border-radius:12px;background:#bac5c5}.compare img{width:100%;display:block}.before{position:absolute;inset:0;clip-path:inset(0 calc(100% - var(--split)) 0 0)}.divider{position:absolute;inset:0 auto 0 var(--split);width:2px;background:#fff;pointer-events:none}.tag{position:absolute;top:18px;line-height:1.5;color:#fff;background:#183b40df;border-radius:4px;padding:5px 13px;font-size:12px}.tag.left{left:18px}.tag.right{right:18px}.controls{display:flex;gap:12px;align-items:center;margin-top:14px}.controls input{flex:1;accent-color:var(--accent)}button{border:1px solid var(--line);background:#fff;border-radius:6px;padding:8px 15px;color:var(--ink);font:inherit;font-size:12px;cursor:pointer}button:hover{background:#e8efea}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #d79a3d;outline-offset:4px}.fine{font-size:12px;margin-top:12px}.changes{padding:20px 24px;background:#e8efea;border-left:3px solid var(--accent);margin-top:24px;font-size:14px;color:var(--ink)}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}figure{margin:0;border:1px solid var(--line);border-radius:12px;background:white;overflow:hidden}figure:last-child{grid-column:1/-1}figure img{display:block;width:100%}figcaption{padding:16px 20px;display:flex;justify-content:space-between;gap:20px}figcaption a{font-size:12px;white-space:nowrap}.contact{width:100%;display:block;border:1px solid var(--line);border-radius:12px}.frames{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:16px}.frames a{padding:9px 12px;border:1px solid var(--line);border-radius:6px;background:#fff;text-decoration:none;font-size:13px}.frames span{display:block;font-size:11px;color:var(--muted)}.resources{display:flex;flex-wrap:wrap;gap:14px 25px;margin-top:20px;font-size:14px}footer{margin-top:45px;border-top:1px solid var(--line);padding-top:20px;font-size:11px;color:var(--muted);word-break:break-all}.sr-only{position:absolute;clip:rect(0,0,0,0);width:1px;height:1px;overflow:hidden}@media(max-width:800px){main{padding:30px 18px}h1{font-size:29px}header{display:block}.status{display:inline-block;margin-top:20px}.grid{grid-template-columns:1fr}.frames{grid-template-columns:repeat(4,1fr)}figcaption{display:block}.controls{flex-wrap:wrap}.controls input{flex-basis:100%}}
</style></head><body><main>
<header><div><p class="eyebrow">Shanghai architecture density / v001</p><h1>상하이 중심부를 더 촘촘하게</h1><p>수로와 구면 지형을 유지하면서 상하이의 스카이라인, 와이탄, 전통 주거지의 건축 밀도를 높였습니다.</p></div><span class="status">__STATUS__</span></header>
<section><h2>같은 시점에서 비교</h2><div class="compare" id="compare"><img src="review/after-diagnostic/shanghai.png" alt="밀도를 보강한 상하이 중심부"><img class="before" src="review/before-diagnostic/shanghai.png" alt="수정 전 도시와 지형"><div class="divider"></div><span class="tag left">수정 전</span><span class="tag right">수정 후</span></div>
<div class="controls"><button type="button" data-split="100">수정 전</button><button type="button" data-split="50">비교</button><button type="button" data-split="0">수정 후</button><label class="sr-only" for="split">수정 전후 비교선 위치</label><input id="split" type="range" min="0" max="100" value="50" aria-valuetext="수정 전후 절반씩 표시"></div>
<p class="fine">동일한 임시 진단 카메라로 촬영했습니다. 검토 렌더 과정에서는 저장된 카메라와 Blender 파일을 수정하지 않았습니다. <a href="review/after-diagnostic/shanghai.png" target="_blank">수정 후 원본 이미지</a> · <a href="review/before-diagnostic/shanghai.png" target="_blank">수정 전 원본 이미지</a></p>
<div class="changes">건물 __BUILDING_COUNT__개와 수목 __TREE_COUNT__그루를 추가했습니다. 상징적인 고층 타워를 키우고, 주변 유리 건물과 낮은 돔 문화시설을 보강했습니다. 와이탄에는 장식이 풍부한 석조 건물을, 전통 주거지에는 회색 기와와 흰 벽의 석고문 건물을 촘촘히 배치했습니다.</div></section>
<section><h2>구역별 건축 밀도와 지면 접촉</h2><div class="grid">__CARDS__</div></section>
<section><h2>실제 영상 카메라</h2><a href="review/actual-camera-contact.jpg" target="_blank"><img class="contact" src="review/actual-camera-contact.jpg" alt="적재, 도시 전경, 출항과 전환을 보여주는 실제 카메라 5개 프레임" loading="lazy"></a><div class="frames">__FRAMES__</div><p class="fine">저장된 영상 카메라에서 촬영한 대표 프레임입니다. 각 번호를 선택하면 원본 이미지를 열 수 있습니다. 전체 타임라인은 30 fps이며, 이 페이지에는 검토용 정지 이미지를 담았습니다. 카메라 구도는 그대로 유지되어, 확대된 상하이 중앙 타워의 상단은 f96·f132에서 화면 위로 벗어납니다. 위의 진단 이미지는 전체 높이를 확인하기 위한 별도 구도입니다.</p></section>
<section><h2>작업 파일과 검증 기록</h2><p>미리보기는 재질 색상과 형태를 확인하는 Workbench 렌더입니다. 최종 조명 렌더는 별도 작업입니다.</p><div class="resources">__RESOURCES__</div></section>
<footer>후보 파일 SHA256: __HASH__<br>수정 전 파일 SHA256: __SOURCE_HASH__<br>모든 검토 이미지는 표시된 파일 해시와 연결되어 있으며, 렌더 후 원본 파일이 변경되지 않았음을 확인했습니다.</footer>
</main><script>const range=document.getElementById('split');const compare=document.getElementById('compare');function split(value){range.value=value;compare.style.setProperty('--split',value+'%');range.setAttribute('aria-valuetext','수정 전 '+value+'%, 수정 후 '+(100-value)+'% 표시')}range.addEventListener('input',()=>split(Number(range.value)));document.querySelectorAll('[data-split]').forEach(button=>button.addEventListener('click',()=>split(Number(button.dataset.split))));</script></body></html>'''
 status=f'배치·보존 검증 {check_count+animation_check_count}개 통과'if verified and animation_verified else'검토 이미지 · 검증 진행 중'
 for key,value in {'STATUS':status,'CARDS':cards,'FRAMES':frames,'RESOURCES':resources,'HASH':candidate_sha,'SOURCE_HASH':SOURCE_SHA,'BUILDING_COUNT':str(delivery['building_count']),'TREE_COUNT':str(delivery['tree_count'])}.items():template=template.replace('__'+key+'__',value)
 (ROOT/'review.html').write_text(template,encoding='utf-8')
 manifest={'candidate_sha256':candidate_sha,'source_sha256':SOURCE_SHA,'source_unchanged':True,'source_saved_by_renderer':False,
           'diagnostic_views':list(after_views),'matching_diagnostic_camera_poses':True,'actual_frames':FRAMES,'preview_only':True,
           'sampled_actual_camera_states_exact':True,
           'building_count':delivery['building_count'],'tree_count':delivery['tree_count'],'building_counts':delivery['building_counts'],
           'framing_observations':[{'frames':[96,132],'observation':'Enlarged Shanghai tallest tower extends above the unchanged actual-camera image; diagnostic views show full height.'}],
           'density_verification_passed':verified,'density_check_count':check_count,'draft':args.draft,
           'preservation_verification_passed':animation_verified,'preservation_check_count':animation_check_count,
           'html':str(ROOT/'review.html'),'actual_contact_sheet':str(REVIEW/'actual-camera-contact.jpg'),
           'diagnostic_contact_sheet':str(REVIEW/'diagnostic-contact.jpg')}
 (REVIEW/'package.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 print('SHANGHAI_REVIEW_PACKAGED',json.dumps(manifest),flush=True)

if __name__=='__main__':main()
