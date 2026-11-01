"""Seal the reviewed US city model and advance the local current-master pointer."""
import json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=read(R/'delivery.json');candidate=Path(d['file']);source=Path(d['source'])
assert sha(candidate)==d['sha256'] and sha(source)==d['source_sha256']
g=read(R/'review/geometry-verification.json');a=read(R/'review/preservation-verification.json')
assert g['candidate_sha256']==a['sha256']==d['sha256']
assert g['source_sha256']==a['source_sha256']==d['source_sha256']
assert g['pass'] and all(c['pass']for c in g['checks'])
assert a['pass'] and all(a['checks'].values())
for folder in ['after-diagnostic','after-front-diagnostic','after-actual']:
    assert read(R/'review'/folder/'metadata.json')['sha256']==d['sha256']
assert d['sha256']in(R/'review.html').read_text(encoding='utf-8')
heroes=[r for r in d['replacements']if r['kind']in {'empire','onewtc'}]
frontages=[r for r in d['replacements']if r['kind']not in {'empire','onewtc'}]
count=len(g['checks'])+len(a['checks'])
summary={'file':str(candidate),'sha256':d['sha256'],'source':str(source),'source_sha256':d['source_sha256'],'pass':True,
 'checks':count,'geometry_checks':len(g['checks']),'preservation_checks':len(a['checks']),
 'landmark_replacements':len(heroes),'refined_existing_frontages':len(frontages),'new_infill_buildings':d['building_count'],
 'new_trees':d['tree_count'],'rear_height_adjustments':len(d['height_changes']),
 'china_terrain_port_ship_warehouse_unchanged':True,'all_990_frame_motion_and_camera_exact':True,
 'new_geometry_road_and_actor_intersections':0,
 'visual_review':{'diagnostics':['city','skyline','streets','top','front'],'actual_frames':[315,390,530,720,989],
  'mode':'Workbench material-color shape and layout review; source production camera unchanged'}}
write(R/'review/verification-summary.json',summary)
d.update(status='Verified current working master',hero_count=len(heroes),refined_frontage_count=len(frontages),
 verification=str(R/'review/verification-summary.json'),review=str(R/'review.html'))
write(R/'delivery.json',d)
tm=read(source.parent/'time-map.json');tm.update(output_sha256=d['sha256'],modeling_parent=str(source),modeling_parent_sha256=d['source_sha256'],camera_and_timing_changed=False)
write(R/'time-map.json',tm)
pointer=R.parent/'latest-previz.json';backup=R/'review/previous-latest-previz.json'
if not backup.exists():shutil.copyfile(pointer,backup)
p=read(backup);p.update(file=str(candidate),sha256=d['sha256'],adopted_on='2026-11-01',
 choice='US city reference design, focal Empire State/One WTC, dense architecture and gap planting',
 delivery=str(R/'delivery.json'),verification=str(R/'review/verification-summary.json'),review=str(R/'review.html'),
 status='Current working master; US city modeling revision verified')
p.setdefault('source_files_preserved',{})['shanghai_density']=str(source)
write(pointer,p)
text=f'''# 미국 상징 도시 밀도·디자인 보강 v001

최신 작업 파일: `pnpline-us-city-density-v001.blend`

## 모델링

- 엠파이어 스테이트 빌딩: 석회석 계열 외벽, 수직 기둥과 창 배열, 여러 단의 후퇴형 상부, 첨탑, 미국 국기. 전체 높이32 장면 단위.
- 원 월드 트레이드 센터: 정사각형 기단에서 회전된 상부 평면으로 연결되는8개 삼각 외벽, 유리 격자, 모서리 리브, 옥상 링과 분절 안테나. 전체 높이36 장면 단위.
- 기존 WTC가 도로·작업 구역과 겹치던 자리는 피하고, 도시 내부의 빈 구획으로 이동. 도로와 작업 구역 형상은 그대로 유지.
- 후방 고층 건물 {len(d['height_changes'])}동의 높이를 조정해 중심 랜드마크가 가장 뚜렷하게 보이도록 구성.
- 일반 건물 {d['building_count']}동 추가, 기존 전면 상업 건물 {len(frontages)}동 외관 개선. 코니스·아치형 입구·비상계단·옥상 물탱크와 유리 외벽 변형을 사용.
- 건물 틈새에 나무 {d['tree_count']}그루 추가. 기존 도로와 물류 동선을 확보하고 구면 지형의 법선에 맞춰 배치.

원본 모델은 삭제하지 않고 교체 대상의 표시만 비활성화했습니다. 추가 모델은 `USD_US_CITY_DENSITY` 컬렉션에서 편집할 수 있습니다.

## 보존과 검증

중국 전체 구역, 지형, 항만, 선박, 창고, 도로와 기존 재질·액션을 보존했습니다. 카메라와 이동 오브젝트의990프레임 변환 및 카메라 설정 오차0. 새 모델과 도로·물류 동선의 충돌 없음. 총 {count}/{count} 검증 통과.

타임라인: 0–989프레임,30fps,33초. `time-map.json`의 시간 매핑 유지.

`review.html`에는 같은 시점의 전후 비교, 정면·스카이라인·거리·평면 이미지, 실제 카메라5개 프레임을 담았습니다. 이미지는 Workbench 형태·재질 색상 검토용이며 최종 조명 렌더가 아닙니다.

원본: `{source}`

결과 SHA-256: `{d['sha256']}`

재생성: Blender5.1에서 `scripts/build.py`. 독립 검증: `scripts/verify_geometry.py`, `scripts/audit_preservation.py`. `scripts/finalize.py`는 작업 파일·검증·이미지의 해시 일치와 통과를 확인한 뒤 최신 작업본 포인터를 갱신합니다.
'''
(R/'README.md').write_text(text,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
