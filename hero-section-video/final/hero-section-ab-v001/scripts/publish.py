"""Publish the approved A/B files and current-file pointers after verification."""
import json,hashlib,shutil,importlib.util,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];H=R.parents[1]
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
records=json.loads((R/'build-verification.json').read_text());variants={}
for label,description in [('A','Original architectural colors'),('B','White and gray architectural materials with cyan brand landmarks and crane heads')]:
 rec=records[label];v=json.loads((R/'audit'/f'final-{label}-verification.json').read_text());assert v['passed'] and all(v['checks'].values())
 src=Path(rec['file']);assert sha(src)==rec['sha256']
 assert sha(rec['material_source'])==rec['material_source_sha256']
 assert sha(rec['presentation_source'])==rec['presentation_source_sha256']
 assert not rec['missing_images'],rec['missing_images']
 images=[R/'review'/label/f'f{f:04d}.png' for f in [32,132,200,332,630,842]];assert all(p.is_file() for p in images)
 canonical=H/f'hero-section-{label}.blend'
 if canonical.exists() and sha(canonical)!=rec['sha256']:raise RuntimeError('Existing canonical file requires version archive: '+str(canonical))
 shutil.copy2(src,canonical);assert sha(canonical)==rec['sha256']
 variants[label]=dict(file=str(canonical),versioned_copy=str(src),sha256=rec['sha256'],description=description,material_source=rec['material_source'],verification=str(R/'audit'/f'final-{label}-verification.json'))
spec=importlib.util.spec_from_file_location('review_package',H/'lookdev/white-cyan-study-v002/scripts/package_review.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.SHOTS=tuple(f'{f:04d}' for f in [32,132,200,332,630,842])
for key in p.SHOTS:
 for label,prefix in [('A','before'),('B','after')]:shutil.copy2(R/'review'/label/f'f{key}.png',R/'review'/f'{prefix}-{key}.png')
p.build(R/'review/index.html','PNPLINE · Hero Section A / B','A는 원래 컬러, B는 흰색·회색과 브랜드 청록색입니다. 두 버전은 daylight v002 라이팅, 최종 DOF v006(최초 강도의 40%), 화면 좌표 그라데이션 배경을 동일하게 적용했습니다.','A · 컬러','B · White & Cyan',R/'review','before',R/'review','after','../../../hero-section-A.blend','../delivery.json')
index=R/'review/index.html';text=index.read_text(encoding='utf-8');buttons=''.join(f'<button data-shot="{key}">{name} · {int(key)}</button>' for key,name in zip(p.SHOTS,['중국 선적','중국 항만','해상 전환','미국 입항','창고 진입','출고 작업']))
text=re.sub(r'<nav aria-label="비교 장면">.*?</nav>','<nav aria-label="비교 장면">'+buttons+'</nav>',text).replace('실험 Blender 파일','A Blender 파일').replace('재질 설정과 검증 기록','채택 파일과 검증 기록').replace('</footer>',' · <a href="../../../hero-section-B.blend">B Blender 파일</a></footer>').replace('40 samples · 기존 지형·카메라·애니메이션 유지','40 samples · 1280×720 검토 렌더 · 기존 지형·카메라·애니메이션 유지');index.write_text(text,encoding='utf-8')
delivery=dict(adopted_on='2026-11-02',variants=variants,presentation_source=records['A']['presentation_source'],presentation_sha256=records['A']['presentation_source_sha256'],lighting='daylight-v002',dof='hero-focus-v006; aperture diameter 40 percent of v004, exact 990-frame animation',background=dict(top_srgb='#DFEAF3',bottom_srgb='#F3F6F8',screen_space=True,packed=True),color_management=dict(view='AgX',look='AgX - Medium High Contrast',exposure=.3),fps=30,frame_start=0,frame_end=989,review=str(index),verification=str(R/'build-verification.json'),archive=str(R),canonical_default='A',status='Adopted A/B masters; full scene preservation and exact presentation transfer verified on reopen; six actual-camera frames per variant reviewed.')
(R/'delivery.json').write_text(json.dumps(delivery,indent=2));(H/'latest-hero-section.json').write_text(json.dumps(delivery,indent=2))
ptr=H/'lookdev/latest-lookdev.json';prior=json.loads(ptr.read_text());backup=R/'previous-latest-lookdev.json'
if not backup.exists():backup.write_text(json.dumps(prior,indent=2))
next_ptr=dict(file=variants['A']['file'],versioned_copy=variants['A']['versioned_copy'],sha256=variants['A']['sha256'],variants=variants,source=records['A']['material_source'],source_sha256=records['A']['material_source_sha256'],presentation_source=records['A']['presentation_source'],fps=30,frame_start=0,frame_end=989,delivery=str(R/'delivery.json'),review=str(index),status='Adopted Hero Section A (color) and B (white/cyan), both with final lighting, DOF and gradient. Default file is A; select variants.B for white/cyan.')
ptr.write_text(json.dumps(next_ptr,indent=2))
(R/'README.md').write_text('''# PNPLINE Hero Section A / B · adopted 2026-11-02

최신 작업 파일:
- `F:/pnpline-landing/hero-section-video/hero-section-A.blend`: 원래 컬러 재질.
- `F:/pnpline-landing/hero-section-video/hero-section-B.blend`: 최신 White & Cyan v005. 랜드마크와 중국 항만 크레인 3대 상부의 청록색을 포함한다.

두 파일의 공통 라이팅·DOF·배경은 “hero section 영상 라이팅 제안” 세션의 최종 `hero-focus-v006` 파일에서 그대로 가져왔다. daylight-v002 라이팅, v006 DOF(최초 v004 조리개 지름의 40%), 화면 상단 #DFEAF3·하단 #F3F6F8 그라데이션이다. AgX / Medium High Contrast / exposure +0.3도 동일하다.

기존 컬러 및 흰색 버전과 형상·재질·슬롯·배치·리그·비 DOF 액션을 대조했다. 카메라 위치·회전·렌즈와 DOF는 각각 0–989프레임 전체를 검증했고, 최종 파일을 다시 열어서 검사를 반복했다. 라이팅·월드·합성 노드·배경 이미지 내장도 대조했다. 두 버전은 재질 외에는 동일하다.

review/index.html에 같은 실제 카메라의 6개 프레임을 나란히 비교할 수 있다. 이미지를 HTML에 포함했다. 검토 렌더는 Cycles OPTIX / 40 samples / 1280×720이다. 저장된 제작 설정은 원래의 Cycles / 128 samples / 1920×1080이다. 전체 990프레임 영상은 이 통합 작업에서 렌더하지 않았다.

원본 lookdev 및 모든 실험 파일을 보존했다. 이 폴더는 채택 시점의 버전 보관본이다. `latest-hero-section.json`에 A/B 경로를 기록했고, `lookdev/latest-lookdev.json`의 기본 파일은 A이며 variants.B에 B를 기록했다. blockout/latest-previz.json은 블록아웃 이력으로 남겨두었다.

렌더 명령 예시(PowerShell, A):
```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' -b 'F:/pnpline-landing/hero-section-video/hero-section-A.blend' -E CYCLES -o 'F:/pnpline-landing/hero-section-video/renders/A/hero-' -F PNG -s 0 -e 989 -a
```
B는 파일명과 출력 폴더의 A를 B로 바꾸면 된다. GPU가 필요하면 Blender Preferences의 Cycles Render Devices에서 OptiX GPU를 선택한다. 검토 렌더의 GPU 선택은 scripts/review.py에 명시되어 있다.
''',encoding='utf-8')
print('ADOPTED canonical A/B and updated latest pointers',flush=True)
