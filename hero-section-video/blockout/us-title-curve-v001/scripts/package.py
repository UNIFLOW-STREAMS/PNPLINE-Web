"""Publish only hash-matched verification and review artifacts; seal pointer on request."""
import argparse,json,hashlib,shutil,html,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];V=R/'review'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
arg=argparse.ArgumentParser();arg.add_argument('--seal',action='store_true');args=arg.parse_args()
d=read(R/'delivery.json');g=read(V/'geometry-verification.json');a=read(V/'preservation-verification.json')
assert sha(d['file'])==g['candidate_sha256']==a['sha256']==d['sha256']
assert sha(d['source'])==g['source_sha256']==a['source_sha256']==d['source_sha256']
assert g['pass']and a['pass']and all(g['checks'].values())and all(a['checks'].values())
before=read(V/'before-diagnostic/metadata.json');after=read(V/'after-diagnostic/metadata.json');actual=read(V/'after-actual/metadata.json')
assert before['sha256']==d['source_sha256']and after['sha256']==actual['sha256']==d['sha256']
assert all(not r['source_saved']for r in [before,after,actual])
for b,c in zip(before['rendered'],after['rendered']):assert b['name']==c['name']and b['camera']==c['camera']
assets=V/'assets';assets.mkdir(exist_ok=True);shutil.copyfile(R.parents[1]/'concept-design/usa-miniature.png',assets/'reference.png')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',19)
im=Image.new('RGB',(1280,800),'#e7ebed');dr=ImageDraw.Draw(im)
dr.text((20,10),'기존 카메라 검토 · 315 / 390 / 530 / 720 / 989 프레임',font=font,fill='#223843')
for i,row in enumerate(actual['rendered']):
 p=Image.open(row['file']).convert('RGB');p.thumbnail((400,225));x=20+(i%3)*420;y=55+(i//3)*355
 im.paste(p,(x,y));dr.text((x,y+235),f"f{row['frame']:04d} · {row['frame']/30:.2f}초",font=font,fill='#223843')
im.save(V/'actual-camera-contact.jpg',quality=95)
count=len(g['checks'])+len(a['checks'])
summary={'file':d['file'],'sha256':d['sha256'],'source':d['source'],'source_sha256':d['source_sha256'],'pass':True,'checks':count,
 'letter_height':d['design']['height'],'glyph_width_height_ratio_increase_percent':60,'curve_degrees':d['design']['arc_degrees'],
 'removed_visible_letter_plinths':3,'relocated_building_assemblies':len(d['relocations']),'preserved_original_actions':101,
 'all_990_frame_motion_and_camera_exact':True,'no_new_camera_actor_or_static_intersections':True,
 'visual_review':['matched front before/after','matched top before/after','actual frames 315,390,530,720,989'],
 'preview_mode':'Workbench material-color previews; no production camera/render settings changed'}
write(V/'verification-summary.json',summary)
cards=''.join(f'<a href="review/after-actual/f{f:04d}.png"><img src="review/after-actual/f{f:04d}.png" alt="기존 카메라 {f}프레임"><span>{f} 프레임 · {f/30:.2f}초</span></a>'for f in [315,390,530,720,989])
comparisons=''.join(f'''<section><h2>{label}</h2><div class="pair"><figure><a href="review/before-diagnostic/{view}.png"><img src="review/before-diagnostic/{view}.png" alt="수정 전 {label}"></a><figcaption>수정 전</figcaption></figure><figure><a href="review/after-diagnostic/{view}.png"><img src="review/after-diagnostic/{view}.png" alt="수정 후 {label}"></a><figcaption>수정 후</figcaption></figure></div></section>'''for view,label in [('front','도시 정면'),('top','도시 안의 곡선 배치')])
page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>USA 글자 비율·곡률 수정 v001</title>
<style>body{{margin:0;background:#edf0f1;color:#193441;font:16px/1.65 system-ui,sans-serif}}main{{max-width:1550px;margin:auto;padding:42px 26px}}h1{{font-size:35px;line-height:1.25}}h2{{font-size:23px;margin-top:40px}}a{{color:#006a83}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0}}img{{width:100%;display:block;border-radius:8px}}figcaption,span{{display:block;margin:8px 0;color:#45616c}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}code{{overflow-wrap:anywhere}}details{{padding:15px 0}}.chip{{display:inline-block;padding:6px 14px;margin-right:8px;border:1px solid #a5bdc6;border-radius:22px}}@media(max-width:760px){{.pair,.cards{{grid-template-columns:1fr}}}}</style>
<main><h1>도시를 감싸는 USA</h1><p>글자 비율을 넓게 조정하고 큰 받침을 제거했습니다. 지구의 곡면에 맞춘 지면 위에서 세 글자가 하나의 완만한 호로 이어집니다.</p>
<p><span class="chip">가로/세로 비율 +60%</span><span class="chip">곡률 {d['design']['arc_degrees']:.1f}°</span><span class="chip">검증 {count}/{count} 통과</span></p>
<p><a href="pnpline-us-title-curve-v001.blend">최신 Blender 파일</a> · <a href="README.md">수정 내역</a> · <a href="review/verification-summary.json">검증 결과</a></p>
{comparisons}<section><h2>컨셉 참고 이미지</h2><a href="review/assets/reference.png"><img src="review/assets/reference.png" style="max-width:1000px" alt="USA 미니어처 도시 컨셉"></a></section>
<section><h2>기존 카메라 시점</h2><p>0–989프레임의 카메라·이동 오브젝트 변환과 카메라 설정이 원본과 같습니다. 아래는 대표 프레임의 형태 검토 이미지입니다.</p><div class="cards">{cards}</div></section>
<details><summary>배치·보존 정보</summary><p>주변 건물 여섯 동은 전체 구조를 유지한 채 옮겼습니다. 스페이스 니들의 큰 광장 받침은 도시 내부에 맞는 낮은 기단으로 조정했습니다. 기존 글자와 받침 원본은 삭제하지 않고 숨겨 보관했습니다.</p><p>중국 구역·항만·선박·도로·창고·원본 재질·101개 액션을 보존했습니다. 글자와 재배치 건물의 접촉 검사, 실제 지면 접지 검사, 990프레임 동작 비교를 통과했습니다. 미국 구간은 반 프레임 간격으로 카메라·이동 장비 충돌도 검사했습니다.</p><p>미리보기는 Workbench 형태·재질 색상 검토용이며 최종 조명 렌더가 아닙니다.</p><p>결과 SHA-256: <code>{d['sha256']}</code></p><p>원본 SHA-256: <code>{d['source_sha256']}</code></p></details></main></html>'''
(R/'review.html').write_text(page,encoding='utf-8')
text=f'''# USA 글자 비율·곡률 수정 v001

작업 파일은 `pnpline-us-title-curve-v001.blend`입니다. `review.html`에서 같은 시점의 전후 비교와 기존 카메라 시점을 볼 수 있습니다.

## 변경 내용

- 기존 글자의 가로/세로 비율을 60% 넓혔습니다. 글자 높이는 27에서 23.5, 두께는 약 3.93에서 2.5 장면 단위로 조정했습니다. 은색 테두리와 남색 전면 재질을 유지했습니다.
- 높이가 약 10.3이던 글자 받침 세 개와 관련 기초를 숨기고, 글자 하단을 실제 도시 지면에 맞췄습니다.
- 세 글자에 반지름 80, 전체 회전각 {d['design']['arc_degrees']:.2f}도의 연속 곡률을 적용했습니다. 글자 자체가 휘며, 지구 곡면과 해당 위치의 법선에 맞춰 서 있습니다.
- 주변 건물 여섯 동은 조립 구조와 모델 수를 유지한 채 재배치했습니다. 보조 랜드마크인 스페이스 니들은 도시 내부에 배치하고 낮은 기단으로 지면을 연결했습니다.
- 새 글자는 `UST_CURVED_CITY_TITLE` 컬렉션의 `UST_LETTER_U`, `UST_LETTER_S`, `UST_LETTER_A`로 구분됩니다. 기존 글자와 받침은 삭제하지 않고 숨겨 보관했습니다.

## 검증

총 {count}/{count} 검사를 통과했습니다. 중국 구역, 항만, 선박, 도로, 창고와 원본 재질·101개 액션을 보존했습니다. 카메라와 이동 오브젝트 100개의 990프레임 변환 및 카메라 설정 오차가 0입니다. 글자·재배치 건물과 기존 오브젝트의 교차 접촉이 없으며, 카메라와 하역 장비 동선에도 새 충돌이 없습니다.

타임라인은 0–989프레임, 30fps, 33초입니다. `time-map.json`의 기존 카메라·시간 매핑을 유지했습니다.

`scripts/build.py`는 원본에서 결과를 재생성합니다. `scripts/verify_geometry.py`와 `scripts/audit_preservation.py`는 읽기 전용 검증입니다. 미리보기는 Workbench 형태·재질 색상 검토용이며 제작 카메라나 렌더 설정은 변경하지 않았습니다.

원본: `{d['source']}`

원본 SHA-256: `{d['source_sha256']}`

결과 SHA-256: `{d['sha256']}`
'''
(R/'README.md').write_text(text,encoding='utf-8')
tm=read(Path(d['source']).parent/'time-map.json');tm.update(output_sha256=d['sha256'],modeling_parent=d['source'],modeling_parent_sha256=d['source_sha256'],camera_and_timing_changed=False);write(R/'time-map.json',tm)
d.update(verification=str(V/'verification-summary.json'),review=str(R/'review.html'),status='Verified current working master'if args.seal else'Verified, awaiting review packaging');write(R/'delivery.json',d)
if args.seal:
 pointer=R.parent/'latest-previz.json';backup=V/'previous-latest-previz.json'
 if not backup.exists():shutil.copyfile(pointer,backup)
 p=read(backup);p.update(file=d['file'],sha256=d['sha256'],adopted_on='2026-11-01',choice='USA lettering with reference proportions, no tall plinths, continuous city-wrapping curvature',delivery=str(R/'delivery.json'),verification=str(V/'verification-summary.json'),review=str(R/'review.html'),status='Current working master; USA title proportions and curved placement verified')
 p.setdefault('source_files_preserved',{})['us_city_density']=d['source'];write(pointer,p)
print(json.dumps(summary,ensure_ascii=False))
