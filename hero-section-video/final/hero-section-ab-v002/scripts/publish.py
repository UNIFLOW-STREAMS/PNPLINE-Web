import json,hashlib,shutil,importlib.util,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];H=R.parents[1]
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
recs={k:json.loads((R/f'{k}-changes.json').read_text()) for k in ['A','B']}
assert recs['A']['foliage_selected']==recs['B']['foliage_selected']
for label,rec in recs.items():
 assert sha(rec['source'])==rec['source_sha256']
 assert sha(rec['file'])==rec['sha256']
 assert rec['presentation_preserved'] and rec['untouched_actions_preserved']
 for f in [132,822,842]:assert (R/'review'/label/f'f{f:04d}.png').is_file()
frames=R/'review/B/motion';assert all((frames/f'f{f:04d}.png').is_file() for f in range(800,921))
video=R/'loading-adjusted-30fps.mp4'
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-start_number','800','-i',str(frames/'f%04d.png'),'-frames:v','121','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,r_frame_rate,width,height','-of','json',str(video)],text=True))['streams'][0];assert probe['nb_frames']=='121' and probe['r_frame_rate']=='30/1'
ptr=H/'latest-hero-section.json';delivery=json.loads(ptr.read_text());(R/'previous-latest-hero-section.json').write_text(json.dumps(delivery,indent=2))
for label,rec in recs.items():
 canonical=H/f'hero-section-{label}.blend';shutil.copy2(rec['file'],canonical);assert sha(canonical)==rec['sha256']
 delivery['variants'][label].update(file=str(canonical),versioned_copy=rec['file'],sha256=rec['sha256'],verification=str(R/f'{label}-changes.json'))
spec=importlib.util.spec_from_file_location('review_package',H/'lookdev/white-cyan-study-v002/scripts/package_review.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);p.SHOTS=('0132','0822','0842')
for key in p.SHOTS:
 for label,prefix in [('A','before'),('B','after')]:shutil.copy2(R/'review'/label/f'f{key}.png',R/'review'/f'{prefix}-{key}.png')
p.build(R/'review/index.html','PNPLINE · Hero Section A / B · v002','적재 동작을 늦추고 트럭 출발을 1초 늦췄습니다. 양국 가로수 수관 395개에 청록색을 적용했습니다.','A · 컬러','B · White & Cyan',R/'review','before',R/'review','after','../../../hero-section-A.blend','../delivery.json')
path=R/'review/index.html';text=path.read_text(encoding='utf-8');text=re.sub(r'<nav aria-label="비교 장면">.*?</nav>','<nav aria-label="비교 장면"><button data-shot="0132">도시·수목 · 132</button><button data-shot="0822">적재 준비 · 822</button><button data-shot="0842">적재 작업 · 842</button></nav>',text);text=text.replace('40 samples · 1600px','24 samples · 1280px').replace('</footer>',' · <a href="../../../hero-section-B.blend">B Blender 파일</a> · <a href="../loading-adjusted-30fps.mp4">적재 동작 30fps 영상</a></footer>');path.write_text(text,encoding='utf-8')
delivery.update(archive=str(R),review=str(path),verification=str(R/'B-changes.json'),motion_review=str(video),revision='v002',changes=dict(carry_duration_frames=[23,45],truck_departure_frames=[870,900],foliage_crowns=395,foliage_selection='35 percent fixed hash per tree; crown material slot only'),status='Latest adopted A/B; loading motion slowed with coordinated cargo/support/worker/truck timing; crown-only cyan selection. Existing lighting, DOF and gradient retained.')
(R/'delivery.json').write_text(json.dumps(delivery,indent=2));ptr.write_text(json.dumps(delivery,indent=2))
look=H/'lookdev/latest-lookdev.json';old=json.loads(look.read_text());(R/'previous-latest-lookdev.json').write_text(json.dumps(old,indent=2));old.update(file=delivery['variants']['A']['file'],versioned_copy=delivery['variants']['A']['versioned_copy'],sha256=delivery['variants']['A']['sha256'],variants=delivery['variants'],review=str(path),delivery=str(R/'delivery.json'),status=delivery['status']);look.write_text(json.dumps(old,indent=2))
(R/'README.md').write_text('''# Hero Section A/B v002

A와 B에 동일한 적재 동작 조정을 적용했다. 캐릭터·손·받침·상자·카트의 키프레임을 함께 리타이밍했다. 주 적재 이동은 기존 약 23프레임에서 45프레임으로 늘렸고, 트럭 출발은 870에서 900프레임으로 늦췄다. 후속 이동은 989프레임의 원래 종점으로 연결한다. 캐릭터 다리에 작은 교대 발 들기를 추가했다. 무거운 상자를 운반하던 기존의 웅크린 자세는 유지한다.

가로수 WC 모델의 수관 슬롯(1)만 개체 이름의 고정 해시로 35% 선택해 브랜드 청록색을 적용했다. 총 395개이며 A/B에 동일하다. 줄기·화단·나머지 수관은 그대로다.

카메라·라이팅·DOF·배경 그라데이션과 기타 애니메이션은 보존했다. 변경 대상의 원본 액션은 남기고 사본 액션으로 수정했다. 이전 채택 버전은 final/hero-section-ab-v001에 보존했다. 최신 루트 A/B와 latest 포인터를 갱신했다.

review/index.html: A/B의 3개 실제 카메라 시점. loading-adjusted-30fps.mp4: 800–920 프레임, 30fps, 480×270 저해상도 동작 검토. 제작 파일은 1920×1080 설정을 유지한다. A/B-changes.json에 정확한 대상과 해시를 기록했다.
''',encoding='utf-8');print('PUBLISHED latest A/B',probe)
