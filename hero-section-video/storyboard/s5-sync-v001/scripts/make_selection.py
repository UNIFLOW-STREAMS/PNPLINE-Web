import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=json.loads((R/'inputs/source.json').read_text(encoding='utf8'))
setting=json.loads((R/'review/source-comparison.json').read_text(encoding='utf8'))['current']['saved_settings']
cfg=json.loads((R/'config.json').read_text(encoding='utf8'))
items=[('S5-01',672,'부두 출발','같은 적재 차량이 출발. 크레인·연결 도로·목적지 관계를 유지.','keep',672),('S5-02',720,'연결 도로 추적','부두에서 멀어지고 같은 물류센터로 접근. 문은 닫힘.','keep',720),('S5-03',732,'입고 마당 접근','본격 선회 직전. 마당과 도크, 방향을 바꿀 공간을 관찰.','replace',766),('S5-03A',766,'마당 선회·정렬 중','실제 전진 선회 중. 견인부와 트레일러의 자세가 계속 변함.','replace',810),('S5-04',842,'후면 정렬·문 개방','정지·문 개방 완료. 후진 전이며 도크까지 빈 간격이 남음.','keep',842),('S5-05',900,'도크 도착·창고로 시선 연결','접안·정지. 문은 열리고 화물은 내부. 카메라는 입고 바닥으로 이동.','keep',900)]
out={'source_sha256':src['source_sha256'],'fps':setting['fps'],'fps_base':setting['fps_base'],'preview_start':cfg['preview_start'],'time_origin':'master frame 0','baseline_adoption':'pending user review','panels':[]}
for ident,f,role,note,decision,old in items:
 out['panels'].append({'id':ident,'frame':f,'subframe':0,'role':role,'action':note,'status':'candidate','master_seconds':f*out['fps_base']/out['fps'],'preview_seconds':(f-out['preview_start'])*out['fps_base']/out['fps'],'old_board':{'frame':old,'decision':decision,'reason':'Keep matching actual state' if decision=='keep' else 'Replace role mismatch; f810 retained only as stopped diagnostic'},'user_approval':None})
(R/'storyboard-selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
