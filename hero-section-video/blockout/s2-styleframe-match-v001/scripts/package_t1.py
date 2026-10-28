"""Package measured preflight evidence; never alter reference pixels or blend."""
import json,hashlib,subprocess,html
from pathlib import Path
R=Path(__file__).resolve().parents[1];BASE=R/'inputs/base.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
inv=json.loads((R/'review/baseline-inventory.json').read_text())['objects']
# Manually read pixel bounds from the ORIGINAL 2048x1156 reference. Not fitted
# to Blender output. Approximate boundaries, 5px measurement uncertainty.
features={
 'C':{'bounds':[382,222,659,580]},'H':{'bounds':[655,169,919,535]},
 'I':{'bounds':[954,166,1069,445]},'N':{'bounds':[1104,182,1374,537]},
 'A':{'bounds':[1345,284,1590,652]},
 'cloud_left':{'bounds':[154,349,432,594]},'cloud_right':{'bounds':[1548,459,1650,598]},
 'sphere_spire':{'point':[742,279]},'sphere_upper':{'point':[742,356]},'sphere_lower':{'point':[741,517]},
 'open_top':{'point':[920,212]},'open_aperture':{'bounds':[904,225,938,250]},
 'stepped_spire':{'point':[936,283]},'tallest_tower':{'point':[1036,108]},
 'bridge_left':{'point':[480,688]},'bridge_right':{'point':[657,718]},
 'crane':{'bounds':[1238,550,1477,781]},'crane_apex':{'point':[1341,550]},
 'ship_bow_left':{'point':[969,911]},'ship_stern_right':{'point':[1554,872]},
 'ship':{'bounds':[964,683,1555,1010]},'ship_bridge':{'bounds':[1431,684,1517,866]},
 'cargo':{'bounds':[984,762,1458,925]},'hull_logo':{'bounds':[1246,907,1404,956]},
 'front_buildings':{'bounds':[277,597,1141,902]},'garden_pavilion':{'bounds':[457,694,575,809]},
 'small_vehicle_left':{'bounds':[581,847,624,887]},'small_vehicle_front':{'bounds':[711,830,794,871]},
 'small_vehicle_right':{'bounds':[1626,749,1699,785]},
 'internal_water':{'polygon':[[479,583],[620,549],[802,608],[1048,602],[1221,544],[1307,573],[1256,649],[1046,696],[882,704],[658,710],[490,650]]},
 'white_coast':{'polygon':[[216,710],[295,913],[1023,874],[1652,782],[1787,808],[1653,829],[1022,932],[270,969],[110,1080],[40,1137],[59,938]]},
 'waves_left':{'bounds':[1,639,283,1156]},'waves_right':{'bounds':[1550,556,2048,1156]},
 'low_roofs':{'bounds':[814,662,1232,826]}}
for f in features.values():
 if 'bounds'in f:f['normalized_bounds']=[x/(2048 if i%2==0 else 1156) for i,x in enumerate(f['bounds'])]
 if 'point'in f:f['normalized_point']=[f['point'][0]/2048,f['point'][1]/1156]
 if 'polygon'in f:f['normalized_polygon']=[[x/2048,y/1156] for x,y in f['polygon']]
rows=[
 ('D01','전체 구성',['internal_water','front_buildings','crane','ship'],['CN_LAND_TERRACE','CN_PROXY_ROOT'],'현재 수로가 없고 건물군이 직선으로 나열됨. 전체 배치 재구성 필요.'),
 ('D02','CHINA',['C','H','I','N','A'],[f'CHINA_{i}_{c}'for i,c in enumerate('CHINA')],'기존 글자 비례·간격·곡률과 도시 중첩이 다름.'),
 ('D03','구름',['cloud_left','cloud_right'],[],'좌우 조형물이 모두 없음. 3D 나선과 입체 덩어리 필요.'),
 ('D04','고층군',['sphere_spire','sphere_upper','sphere_lower','open_top','open_aperture','stepped_spire','tallest_tower'],[n for n in inv if n.startswith('CN_LM_') and inv[n]['type']=='EMPTY'],'대표 모티프는 있으나 상대 높이·배치·밀도와 입면 상세가 다름.'),
 ('D05','수로·교량',['internal_water','bridge_left','bridge_right'],[],'실제 수로와 아치형 교량 없음. 해안과 동작 보호를 함께 검토해야 함.'),
 ('D06','수변 건축·정원',['front_buildings','garden_pavilion','low_roofs','small_vehicle_left','small_vehicle_front','small_vehicle_right'],['CN_WATERFRONT_GROUP','CN_LOWRISE_GROUP'],'석조 입면·돔·밀집 지붕·조경·차량을 새로 대응해야 함.'),
 ('D07','항만',['crane','crane_apex'],[n for n in inv if n.startswith('P01_')],'UNRESOLVED C02: 케이블 상단이 높음. 허용된 새 지지 구조·가림 설계 검토 필요; 리그 변경 필수로 단정하지 않음.'),
 ('D08','선박·화물',['ship','ship_bow_left','ship_stern_right','ship_bridge','cargo','hull_logo'],['A02_SHIP','SHIP_HULL','SHIP_DECK','SHIP_BRIDGE','A01_CONTAINER'],'BLOCKED C01: 참조의 왼쪽 선수와 기존 카메라/전진 방향이 반대. 큰 선체 로고도 미구현.'),
 ('D09','흰 해안',['white_coast'],['CN_LAND_TERRACE'],'참조의 높은 흰 경사부·접힌 곡면과 원본 회색 지형이 다름.'),
 ('D10','바다·빛',['waves_left','waves_right'],['EARTH_CONTINUOUS_OCEAN'],'굵은 밝은 파동선·청록 색면·재질·주간광 구현 필요.')]
save('reference-map.json',{'reference_sha256':sha(R/'inputs/s2-styleframe-001.png'),'dimensions':[2048,1156],'coordinates':'top-left origin, normalized x/2048,y/1156; bounds x0,y0,x1,y1','measurement':'manual reading of original source; approximate visible boundaries +/-5px; no post-failure tolerance widening','important':'correspondences and screen boxes are diagnostic; NOT a similarity score or final art acceptance','features':features,'designs':[{'id':i,'role':role,'reference_features':fs,'existing_objects':obs,'status':'not implemented; preflight','gap':gap}for i,role,fs,obs,gap in rows],'occlusion_order':['CHINA behind towers','tower island behind internal water','internal water behind foreground stone/roof district','front quay behind foreground ship'],'assumptions':['Hidden island rear, water depth, material identity, unseen structure unknown.','No new canal outlet inferred.','Reference wave pattern is not an instruction to animate waves.']})
allowed=[n for n,v in inv.items() if n.startswith(('CN_LM_','CN_HR_','CN_WF_','CN_LR_','CHINA_','P01_LEG_','P01_BOOM_')) or v['props'].get('cn_proxy_owner') or v['props'].get('s2_reveal_owner') or n in ['CN_LAND_TERRACE','SHIP_HULL','SHIP_DECK','SHIP_BRIDGE','SHIP_BRIDGE_GLASS']]
save('allowed-changes.json',{'status':'T1 proposed object scope, no production edits applied','visual_only_candidates':allowed,'all_existing_actions':'protected, including visual objects with animation','protected_explicit':['CAM_MASTER','CAM_LOOK_TARGET','CN_FRAME','US_FRAME','A02_SHIP','A01_CONTAINER','P01_TROLLEY','P01_SPREADER','P01_CABLE_0','P01_CABLE_1','P01_CABLE_2','P01_CABLE_3'],'protected_global':['camera data all frames','all action data and evaluated root motion','fps/markers/scene events','earth center/radius','unrelated US meshes/materials/actions'],'pending_approval':['C01 camera viewpoint or ship motion must be reconsidered to preserve left bow','C02 unresolved: investigate replacement visible support geometry/occlusion within current motion lock; rig exception not yet justified'],'shared_data_rule':'Existing white/navy/yellow materials shared with unrelated objects. Copy or create dedicated materials; never recolor shared blocks.'})
save('scene-config.json',{'status':'preflight only; no accepted art parameters','source_sha256':sha(BASE),'camera':'CAM_MASTER','frame':156,'fps':12,'render_diagnostic':'BLENDER_WORKBENCH','design_renderer':'not selected or executed: scope conflict found before T2','image_target':'inputs/s2-styleframe-001.png','hidden_space_assumptions':'pending actual 3D implementation; no reconstruction claim'})
save('object-map.json',{'status':'no production replacements/new objects yet','baseline_inventory':'review/baseline-inventory.json','render_only_trials':['review/trial-exterior-reversed.png','review/trial-static-crane-lowered.png'],'trial_blend_saved':False})
save('inputs/manifest.json',{'branch':'main','head':'2426c437c105ceb32c34c32edded828a471c1ac1','source':'../s2-city-reveal-china-v001/master-s2-city-reveal-china-v001.blend','source_sha256':sha(BASE),'reference_sha256':sha(R/'inputs/s2-styleframe-001.png'),'gui':{'window':593466,'unsaved_marker':True,'saved_or_closed':False,'contents_compared':False},'model':'unknown','reasoning_effort':'unknown','blender':'5.1.0 adfe2921d5f3','isolation':'new output directory, immutable copied input; no branch mutation','git_status':'git-status-before.txt'})
rows_html=''.join(f'<tr><td>{i} {html.escape(role)}</td><td>{html.escape(gap)}</td></tr>'for i,role,fs,obs,gap in rows)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>S2 스타일프레임 정합 — 잠금 충돌 검토</title><style>
body{font:16px/1.6 system-ui,sans-serif;background:#edf0f2;color:#172b39;margin:32px}h1{font-size:29px}.note{background:#fff4dc;padding:16px;border-left:5px solid #bd811e}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}figure{margin:0;background:white;padding:12px}img{width:100%;aspect-ratio:16/9;object-fit:contain;background:#eee}figcaption{font-weight:600}table{width:100%;border-collapse:collapse;background:white}td,th{padding:10px;border:1px solid #ccd4d9;text-align:left}a{color:#00688c}.diagram{background:white;padding:18px}code{font-size:14px}.small{font-size:14px;color:#415260}</style>
<h1>S2 스타일프레임 정합: 동작 잠금 충돌 확인</h1>
<p class="note"><b>완료본이 아닙니다.</b> T1에서 확인한 선박 방향 충돌과 크레인 구조의 미결 사항입니다. 원본 이미지·Blender·미저장 창을 보존했습니다. 아래 시험 렌더는 원인을 확인하기 위한 것으로 최종 모델이나 디자인 제안이 아닙니다.</p>
<div class="grid"><figure><img src="inputs/s2-styleframe-001.png"><figcaption>고정 기준 이미지 · 원본 전체, 자르기/왜곡 없음</figcaption></figure><figure><img src="review/baseline-frames/0156.png"><figcaption>현재 저장본 · 새 CAM_MASTER f156 렌더</figcaption></figure></div>
<h2>C01 · 왼쪽 선수와 고정된 전진 방향</h2>
<p>지시서 D08은 왼쪽을 선수, 오른쪽을 선미/선교로 명시합니다. 기존의 선수 방향 항해를 유지한다는 전제로, 현재 f156 카메라에서 선박의 전진 축(+X)은 화면 오른쪽입니다. 외형만 반대로 만들면 항해가 선미 방향으로 진행됩니다.</p>
<div class="diagram"><svg viewBox="0 0 960 140" width="100%"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3z" fill="#c22"/></marker></defs><text x="50" y="30" font-size="20">기존 f156: 선미/선교 (화면 X≈0.50)</text><text x="600" y="30" font-size="20">전진축 끝 (X≈0.70)</text><line x1="460" y1="65" x2="675" y2="65" stroke="#c22" stroke-width="6" marker-end="url(#arrow)"/><text x="50" y="116" font-size="20">참조: 왼쪽 선수 ← [ 컨테이너 ] 오른쪽 선미/선교</text></svg></div>
<p class="small">f155.75→156.25 이동 벡터와 선박 +X 내적≈1.000. 같은 문제를 f170/216/278에서도 조사했습니다. 화면 화살표는 카메라 이동을 포함한 픽셀 속도가 아니라 f156 고정 카메라로 투영한 세계 공간 전진 방향입니다.</p>
<h2>C02 · 낮은 크레인과 고정된 인양 지지점</h2><p>참조의 크레인 꼭대기는 원본 y≈550/1156=0.476입니다. 기존 작동 케이블 상단은 y≈0.42–0.43이며 더 위에 있습니다. 기존 기둥/붐만 낮추는 시험에서는 트롤리와 케이블 상단의 실제 지지가 끊어집니다. 새 지지 형상·가림 관계로 해결할 가능성은 미검증이며 리그 변경이 필수라고 단정하지 않습니다. 보이지 않는 원본 구조를 남겨 검사를 통과시키지 않았습니다.</p>
<div class="grid"><figure><img src="review/trial-exterior-reversed.png"><figcaption>시험 1: 외형만 180° 반전 · 동작 그대로</figcaption><p>방향 충돌을 해결하지 못합니다. 기존 적재물과 우측 선교의 중첩도 남습니다. 최종 채택 안 함.</p></figure><figure><img src="review/trial-static-crane-lowered.png"><figcaption>시험 2: 정적 기둥/붐만 낮춤 · 작동 리그 그대로</figcaption><p>위에 남은 트롤리와 낮아진 구조가 분리됩니다. 실제 지지 연결 실패. 최종 채택 안 함.</p></figure></div>
<h2>승인 대상으로 제시하는 범위</h2><table><tr><th>안</th><th>내용과 비용</th></tr><tr><td>A · 기준 이미지 보존 (권장)</td><td>S2 내부 카메라·타깃 시점의 별도 최소 조정안 작성을 허용합니다. 중국 인양 장치는 우선 현 동작을 유지한 새 지지 구조로 검토하며, 리그 변경은 이번 승인 요청에서 제외합니다. 우선 기존 항로·총길이·FPS·이벤트 시점을 유지하는 방향으로 조사하고, S1→S2→S3 및 S4 하역을 재검증합니다. 아직 새 카메라 안의 성립을 검증한 것은 아닙니다. 추가 항로 변경이 필요하면 다시 보고합니다.</td></tr><tr><td>B · 카메라·동작 잠금 유지</td><td>선수/선교 좌우에 한정하여 디자인 변경 승인이 필요합니다. 크레인은 추가 구조 검토 사항입니다. 기존 이미지는 보존하고 별도 변경 기준을 만들며, 양쪽 동기화 전에는 완료할 수 없습니다. 현재 어느 디자인 변경도 승인/적용하지 않았습니다.</td></tr></table>
<h2>D01–D10 차이 목록</h2><table>'''+rows_html+'''</table>
<h2>실행 증거</h2><p>기존 회귀 35/35 통과. 방향/지지 전제 검사 2/2 RED(각각 확정된 방향 충돌 / 미결 구조 진단). 새 디자인 존재 검사 5/5 RED. 보존 어댑터는 별도 mutation 및 전 구간 검사로 검증합니다. 기준 스틸 16장 새 출력. 디자인 구현·연속 영상·최종 마스터·재현 검사는 아직 수행하지 않았습니다.</p><p><a href="report.md">상세 보고서</a> · <a href="reference-map.json">참조 좌표 및 대응표</a> · <a href="review/protected-constraint-probes.json">실제 좌표/속도</a> · <a href="review/locked-feasibility.json">RED 증거</a></p></html>'''
(R/'review.html').write_text(page,encoding='utf-8')
print('PACKAGED T1 REVIEW',R/'review.html')
if __name__=='__main__':pass
