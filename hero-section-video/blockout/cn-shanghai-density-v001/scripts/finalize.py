"""Publish only the hash-verified Shanghai modeling revision to the local master pointer."""
import hashlib,json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

delivery=read(ROOT/'delivery.json')
candidate=Path(delivery['file']);source=Path(delivery['source'])
assert sha(candidate)==delivery['sha256'] and sha(source)==delivery['source_sha256']
geometry=read(ROOT/'review/density-verification.json')
preservation=read(ROOT/'review/preservation-verification.json')
assert geometry['candidate_sha256']==preservation['sha256']==delivery['sha256']
assert geometry['source_sha256']==preservation['source_sha256']==delivery['source_sha256']
assert geometry['pass'] and all(r['pass']for r in geometry['checks'])
assert preservation['pass'] and all(preservation['checks'].values())
for directory in ['after-diagnostic','after-actual']:
    assert read(ROOT/'review'/directory/'metadata.json')['sha256']==delivery['sha256']
assert (ROOT/'review.html').exists() and delivery['sha256'] in (ROOT/'review.html').read_text(encoding='utf-8')

total=len(geometry['checks'])+len(preservation['checks'])
summary={
 'file':str(candidate),'sha256':delivery['sha256'],'source':str(source),'source_sha256':delivery['source_sha256'],
 'pass':True,'check_count':total,'geometry_checks':len(geometry['checks']),'preservation_checks':len(preservation['checks']),
 'new_buildings':delivery['building_count'],'new_trees':delivery['tree_count'],'building_types':delivery['building_counts'],
 'original_meshes_materials_actions_preserved':True,'river_banks_bridge_exact':True,'camera_and_actor_990_frames_exact':True,
 'new_geometry_water_and_architecture_intersections':0,
 'visual_review':{'diagnostic_views':['shanghai','island','bund_oldtown','top'],'actual_camera_frames':[57,96,132,165,253],
  'observation':'The enlarged Shanghai Tower top is outside the unchanged camera frame at96 and132. Diagnostic views show the complete skyline. Camera reframing was not part of this modeling revision.'}}
write(ROOT/'review/verification-summary.json',summary)
delivery.update(status='Verified current working master',verification=str(ROOT/'review/verification-summary.json'),review=str(ROOT/'review.html'),
                visual_observation=summary['visual_review']['observation'])
write(ROOT/'delivery.json',delivery)
time_map=read(source.parent/'time-map.json')
time_map.update(output_sha256=delivery['sha256'],modeling_parent=str(source),modeling_parent_sha256=delivery['source_sha256'],camera_and_timing_changed=False)
write(ROOT/'time-map.json',time_map)
pointer=ROOT.parent/'latest-previz.json';backup=ROOT/'review/previous-latest-previz.json'
if not backup.exists():shutil.copyfile(pointer,backup)
previous=read(backup)
previous.update(file=str(candidate),sha256=delivery['sha256'],adopted_on='2026-11-01',
                choice='Shanghai density, enlarged central landmarks and gap planting with exact waterway and animation preservation',
                delivery=str(ROOT/'delivery.json'),verification=str(ROOT/'review/verification-summary.json'),review=str(ROOT/'review.html'),
                status='Current working master; Shanghai modeling revision verified')
previous.setdefault('source_files_preserved',{})['unified_curvature']=str(source)
write(pointer,previous)
text=f'''# 상하이 건축 밀도 보강 v001

작업 파일: `pnpline-cn-shanghai-density-v001.blend`

- 추가 건물 {delivery['building_count']}동: 고층 33동, 와이탄풍 19동, 석고문 주거 74동, 문화시설 1동.
- 중앙 랜드마크 3동 높이 1.6배. SWFC 폭 1.30배, 진마오 폭 1.25배, 상하이 타워 폭 1.35배. 두 보조 고층은 겹침을 피하도록 재배치.
- 건물 사이와 정원에 나무 {delivery['tree_count']}그루 추가. 오른쪽 빈터의 과밀 식재와 보행로에 걸친 나무는 제외.
- 기존 수로, 양안, 섬, 다리, 통합 구면 지형 보존. 새 건물과 나무는 해당 위치의 지구 법선에 정렬.
- 항만, 선박, 하역 애니메이션, 미국 구역과 기존 카메라를 보존. 0–989프레임, 30 fps, 총 33초.

`review.html`에서 같은 시점의 전후 비교와 실제 카메라 5개 프레임을 확인할 수 있습니다. 진단 이미지는 Workbench 검토용입니다.

확대된 상하이 타워 상단은 기존 카메라 f96, f132에서 화면 밖으로 나갑니다. 이번 모델링 수정에서는 카메라 구도를 변경하지 않았습니다.

검증 {total}/{total} 통과. 원본 오브젝트·메시·재질·액션 보존, 990프레임 카메라/이동 오차 0, 추가 건축의 수로 침범 및 구조물 교차 없음.

원본: `{source}`

결과 SHA-256: `{delivery['sha256']}`

재생성: Blender 5.1에서 `scripts/build.py` 실행. 검증은 `scripts/verify_density.py`, `scripts/audit_preservation.py`로 수행합니다. `scripts/finalize.py`는 현재 파일 해시와 검증·렌더 해시가 모두 일치할 때만 최신 작업 포인터를 갱신합니다.
'''
(ROOT/'README.md').write_text(text,encoding='utf-8')
print(json.dumps({'file':str(candidate),'sha256':delivery['sha256'],'checks':total,'buildings':delivery['building_count'],'trees':delivery['tree_count'],'published_pointer':str(pointer)},ensure_ascii=False))
