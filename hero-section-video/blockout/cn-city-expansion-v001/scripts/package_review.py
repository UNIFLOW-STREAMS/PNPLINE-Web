"""Package hash-bound final renders into a local review page and contact sheet."""
import hashlib
import html
import json
import math
from pathlib import Path

from PIL import Image,ImageChops,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'review'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size,bold=False):
    paths=['C:/Windows/Fonts/malgunbd.ttf'if bold else'C:/Windows/Fonts/malgun.ttf',
           'C:/Windows/Fonts/arialbd.ttf'if bold else'C:/Windows/Fonts/arial.ttf']
    for path in paths:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default()


def contact_sheet(rows,output):
    cols=4
    w,h=430,242
    gap=16
    caption=34
    header=75
    total_w=cols*w+(cols+1)*gap
    total_h=header+math.ceil(len(rows)/cols)*(h+caption+gap)+gap
    canvas=Image.new('RGB',(total_w,total_h),'#eef0ef')
    draw=ImageDraw.Draw(canvas)
    draw.text((gap,13),'기존 카메라 · 13개 검토 프레임',font=font(25,True),fill='#18393f')
    draw.text((gap,45),'30 fps  |  카메라 경로·렌즈 유지  |  각 이미지는 원본 PNG로 확인할 수 있습니다',font=font(15),fill='#51666a')
    for i,row in enumerate(rows):
        group=i//cols
        group_count=min(cols,len(rows)-group*cols)
        offset=(total_w-(group_count*w+(group_count-1)*gap))/2
        x=int(offset+(i%cols)*(w+gap))
        y=header+group*(h+caption+gap)
        image=Image.open(row['file']).convert('RGB')
        image.thumbnail((w,h),Image.Resampling.LANCZOS)
        canvas.paste(image,(x+(w-image.width)//2,y+(h-image.height)//2))
        draw.text((x+4,y+h+8),f"f{row['frame']:04d}  ·  {row['frame']/30:.2f}s",font=font(17),fill='#29474c')
    canvas.save(output,quality=95,subsampling=0)


def main():
    delivery=read(ROOT/'delivery.json')
    candidate=Path(delivery['file'])
    candidate_hash=sha(candidate)
    assert candidate_hash==delivery['sha256']
    before=read(REVIEW/'before-actual/metadata.json')
    after=read(REVIEW/'after-actual/metadata.json')
    before_hero=read(REVIEW/'before-hero-diagnostic/metadata.json')
    after_hero=read(REVIEW/'after-hero-diagnostic/metadata.json')
    diagnostic=read(REVIEW/'after-diagnostic/metadata.json')
    verification=read(REVIEW/'expansion-verification.json')
    assert before['sha256']==before_hero['sha256']==delivery['source_sha256']
    assert after['sha256']==after_hero['sha256']==diagnostic['sha256']==verification['candidate_sha256']==candidate_hash
    assert all(verification['checks'].values()),'Scene verification must pass before packaging final proof'
    assert before_hero['width']==after_hero['width']==1800
    assert before_hero['height']==after_hero['height']==1200
    assert before_hero['rendered'][0]['camera']==after_hero['rendered'][0]['camera'],'Hero before/after camera mismatch'
    assert len(before['rendered'])==len(after['rendered'])==13
    pose_results=[]
    pixel_results=[]
    for a,b in zip(after['rendered'],before['rendered']):
        assert a['frame']==b['frame']
        same=a['camera']==b['camera']
        pose_results.append({'frame':a['frame'],'camera_exact':same})
        assert same
        diff=ImageChops.difference(Image.open(a['file']).convert('RGB'),Image.open(b['file']).convert('RGB'))
        pixel_results.append({'frame':a['frame'],'pixel_exact':diff.getbbox()is None})
    preserve={'candidate_sha256':candidate_hash,'source_sha256':delivery['source_sha256'],
              'all_sampled_camera_poses_optics_exact':True,'poses':pose_results,'pixel_comparison':pixel_results,
              'note':'China-frame pixel changes are expected geometry additions. All sampled camera pose and optics are exactly preserved.'}
    (REVIEW/'render-camera-preservation.json').write_text(json.dumps(preserve,indent=2),encoding='utf-8')
    counts=delivery['building_counts']
    support=sum(counts[key]for key in ['hutong_roof_buildings','lowrise_houses','qilou','midrise'])
    assert support==247 and delivery['landmark_count']==13
    contact_sheet(after['rendered'],REVIEW/'actual-camera-contact.jpg')
    frames=''.join(f'<a class="frame-link" href="review/after-actual/f{r["frame"]:04d}.png" target="_blank">f{r["frame"]:04d}<span>{r["frame"]/30:.2f}s</span></a>'for r in after['rendered'])
    verify_count=len(verification['checks'])
    template='''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>중국 도시 확장 · 최종 검토</title>
<style>
:root{color-scheme:light;--ink:#17383e;--muted:#607174;--paper:#f4f4ef;--line:#d7ded9;--accent:#17667a;--split:50%}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;line-height:1.65}main{max-width:1440px;margin:auto;padding:54px 38px 70px}a{color:var(--accent);text-underline-offset:4px}header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;margin-bottom:32px}.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}h1{font-size:38px;line-height:1.2;margin:12px 0 15px;letter-spacing:-.04em}h2{font-size:24px;margin:0 0 12px;letter-spacing:-.03em}p{margin:0;color:var(--muted)}.status{display:inline-block;border:1px solid #aec4b8;border-radius:20px;background:#e6eee7;color:#315a45;padding:7px 15px;font-size:13px;white-space:nowrap}.stats{display:flex;gap:36px;margin:28px 0 32px}.stat strong{display:block;font-size:27px;line-height:1.2}.stat span{font-size:12px;color:var(--muted)}section{margin-top:52px}.section-title{display:flex;align-items:baseline;justify-content:space-between;gap:24px;margin-bottom:18px}.section-title p{font-size:13px}.compare{position:relative;isolation:isolate;line-height:0;overflow:hidden;border:1px solid var(--line);border-radius:12px;background:#c9cdcd}.compare img{width:100%;display:block}.compare .before{position:absolute;inset:0;clip-path:inset(0 calc(100% - var(--split)) 0 0)}.divider{position:absolute;inset:0 auto 0 var(--split);width:2px;background:white;box-shadow:0 0 12px #17383e66;pointer-events:none}.tag{position:absolute;top:18px;line-height:1.5;padding:5px 13px;background:#17383ee3;color:white;border-radius:4px;font-size:12px}.tag.left{left:18px}.tag.right{right:18px}.controls{display:flex;align-items:center;gap:14px;margin-top:14px}.controls input{flex:1;accent-color:var(--accent)}button{border:1px solid var(--line);border-radius:6px;background:white;color:var(--ink);padding:8px 14px;font:inherit;font-size:12px;cursor:pointer}button:hover{background:#e7efeb}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #e2a442;outline-offset:4px}.fine{font-size:12px;margin-top:12px;color:var(--muted)}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.card{margin:0;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}.card img{display:block;width:100%}.card figcaption{padding:18px 21px}.card strong{display:block;font-size:17px;margin-bottom:3px}.card p{font-size:13px}.wide{margin-top:24px}.contact{width:100%;display:block;border:1px solid var(--line);border-radius:12px}.frame-links{display:grid;grid-template-columns:repeat(7,1fr);gap:8px;margin-top:16px}.frame-link{padding:10px 12px;border:1px solid var(--line);border-radius:6px;background:white;text-decoration:none;font-size:13px}.frame-link span{display:block;color:var(--muted);font-size:11px}.note{padding:19px 23px;border-left:3px solid var(--accent);background:#e9efeb;margin-top:24px;font-size:14px}.resources{display:flex;flex-wrap:wrap;gap:13px 24px;margin-top:20px;font-size:14px}footer{border-top:1px solid var(--line);margin-top:48px;padding-top:22px;font-size:11px;color:var(--muted);word-break:break-all}.sr-only{position:absolute;clip:rect(0,0,0,0);width:1px;height:1px;overflow:hidden}@media(max-width:800px){main{padding:30px 18px}h1{font-size:30px}header{display:block}.status{margin-top:16px}.grid{grid-template-columns:1fr}.section-title{display:block}.section-title p{margin-top:7px}.stats{gap:26px}.frame-links{grid-template-columns:repeat(4,1fr)}.controls{flex-wrap:wrap}.controls input{flex-basis:100%}}
</style></head><body><main>
<header><div><div class="eyebrow">China city expansion / v001</div><h1>상하이에서 베이징·광저우까지</h1><p>기존 항만과 도시를 유지하고, 지구 곡면을 따라 두 도시 구역을 확장했습니다.</p></div><span class="status">최종 씬 검증 __CHECK_COUNT__개 통과</span></header>
<div class="stats"><div class="stat"><strong>13</strong><span>신규 랜드마크</span></div><div class="stat"><strong>247</strong><span>신규 주변 건물</span></div><div class="stat"><strong>423</strong><span>신규 가로수</span></div></div>
<section style="margin-top:0"><div class="section-title"><h2>같은 위치에서 비교</h2><p>선택한 진단 카메라 · 1800 × 1200</p></div>
<div class="compare" id="compare"><img src="review/after-hero-diagnostic/hero.png" alt="베이징과 광저우가 확장된 최종 중국 도시"><img class="before" src="review/before-hero-diagnostic/hero.png" alt="확장 전 상하이와 항만"><div class="divider"></div><span class="tag left">수정 전</span><span class="tag right">수정 후</span></div>
<div class="controls"><button type="button" data-split="100">수정 전</button><button type="button" data-split="50">비교</button><button type="button" data-split="0">수정 후</button><label class="sr-only" for="split">수정 전후 비교선 위치</label><input id="split" type="range" min="0" max="100" value="50" aria-valuetext="수정 전후 절반씩 표시"></div>
<p class="fine">이 전체 보기에는 검토용 임시 카메라를 사용했습니다. 저장된 영상 카메라의 경로·각도·렌즈는 변경하지 않았습니다. <a href="review/after-hero-diagnostic/hero.png" target="_blank">수정 후 원본 이미지</a> · <a href="review/before-hero-diagnostic/hero.png" target="_blank">수정 전 원본 이미지</a></p></section>
<section><div class="section-title"><h2>지역별 모델링</h2><p>이미지를 선택하면 원본 크기로 열립니다.</p></div><div class="grid">
<figure class="card"><a href="review/after-diagnostic/beijing.png" target="_blank"><img src="review/after-diagnostic/beijing.png" alt="CCTV, 중국존, 천단, 자금성 및 후퉁 건물이 배치된 베이징 구역" loading="lazy"></a><figcaption><strong>베이징</strong><p>CCTV · 중국존 · 국가체육장 · 천단 · 자금성·천안문 · 만리장성</p></figcaption></figure>
<figure class="card"><a href="review/after-diagnostic/guangzhou.png" target="_blank"><img src="review/after-diagnostic/guangzhou.png" alt="광저우 타워와 고층 건물, 전통 사원과 치러우가 배치된 광저우 구역" loading="lazy"></a><figcaption><strong>광저우</strong><p>광저우 타워와 고층 스카이라인, 전통 건축, 치러우 거리</p></figcaption></figure></div>
<figure class="card wide"><a href="review/after-diagnostic/beijing_rear.png" target="_blank"><img src="review/after-diagnostic/beijing_rear.png" alt="부드러운 타원형 언덕 위 만리장성, 경기장과 베이징 후면 구역" loading="lazy"></a><figcaption><strong>만리장성 공원과 후면 도시</strong><p>언덕 경계를 완만하게 연결하고, 도시 외곽과 기존 도시 사이의 건물 밀도를 보완했습니다.</p></figcaption></figure></section>
<section><div class="section-title"><h2>배치와 연결</h2><p>기존 항만의 선박 동선과 적재 동작 유지</p></div><figure class="card"><a href="review/after-diagnostic/top.png" target="_blank"><img src="review/after-diagnostic/top.png" alt="상하이를 중심으로 베이징과 광저우가 연결된 전체 평면 배치" loading="lazy"></a><figcaption><strong>전체 평면</strong><p>주변 건물 247개: 후퉁 지붕 건물 48개, 소형 저층 건물 82개, 치러우 40개, 중층 건물 77개. 후퉁 단지 수와 개별 건물 수를 중복 집계하지 않았습니다.</p></figcaption></figure></section>
<section><div class="section-title"><h2>실제 영상 카메라</h2><p>13개 대표 프레임 · 기존 30 fps 타임라인</p></div><a href="review/actual-camera-contact.jpg" target="_blank"><img class="contact" src="review/actual-camera-contact.jpg" alt="기존 카메라의 적재, 도시 전경, 출항, 미국 도착, 물류 구간을 검토한 13프레임 모음" loading="lazy"></a><div class="frame-links">__FRAMES__</div>
<div class="note">990개 프레임에서 기존 카메라와 주요 동작의 변환값·카메라 광학 설정이 원본과 일치합니다. 새 외곽 랜드마크 일부는 현재 영상 구도에서 잘립니다. 확대 구역 전체는 위 조감도와 지역별 뷰에서 확인할 수 있습니다.</div></section>
<section><h2>파일과 검증 기록</h2><p>미리보기는 재질 색상과 형태를 확인하기 위한 Workbench 렌더입니다. 최종 조명 렌더를 의미하지 않습니다.</p><div class="resources"><a href="pnpline-cn-city-expansion-v001.blend">Blender 작업 파일</a><a href="delivery.json">구성 명세</a><a href="review/expansion-verification.json">씬 보존·충돌 검증</a><a href="review/contact-verification.json">지형 접촉 검증</a><a href="review/site-verification.json">배치 검증</a><a href="review/render-camera-preservation.json">렌더 카메라 비교</a></div></section>
<footer>최종 파일 SHA256: __HASH__<br>원본 SHA256: __SOURCE_HASH__<br>검토 이미지는 위 최종 파일에서 생성했으며, 렌더 과정에서 Blender 파일을 저장하지 않았습니다.</footer>
</main><script>const slider=document.getElementById('split');const compare=document.getElementById('compare');function setSplit(value){slider.value=value;compare.style.setProperty('--split',value+'%');slider.setAttribute('aria-valuetext','수정 전 '+value+'%, 수정 후 '+(100-value)+'% 표시')}slider.addEventListener('input',()=>setSplit(Number(slider.value)));document.querySelectorAll('[data-split]').forEach(button=>button.addEventListener('click',()=>setSplit(Number(button.dataset.split))));</script></body></html>'''
    template=template.replace('__CHECK_COUNT__',str(verify_count)).replace('__FRAMES__',frames).replace('__HASH__',candidate_hash).replace('__SOURCE_HASH__',delivery['source_sha256'])
    (ROOT/'review.html').write_text(template,encoding='utf-8')
    manifest={'candidate_sha256':candidate_hash,'source_sha256':delivery['source_sha256'],
              'html':str(ROOT/'review.html'),'contact_sheet':str(REVIEW/'actual-camera-contact.jpg'),
              'landmarks':13,'support_buildings':support,'support_breakdown':counts,
              'hero_dimensions':[1800,1200],'actual_frames':[r['frame']for r in after['rendered']],
              'all_13_sampled_camera_states_exact':True,'all_scene_checks_pass':True,
              'scene_check_count':verify_count,'source_blend_unchanged':sha(Path(delivery['source']))==delivery['source_sha256']}
    assert manifest['source_blend_unchanged']
    (REVIEW/'package.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('CITY_REVIEW_PACKAGED',json.dumps(manifest),flush=True)


if __name__=='__main__':
    main()
