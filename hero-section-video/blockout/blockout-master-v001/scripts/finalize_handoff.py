"""Attach provenance to the generated manifest; compare reopened pixels; hash deliverables."""
import hashlib, json, subprocess
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

expected={
    '../plan/master-codex-instructions.md':'c06c52d7484dfd6bdfad4c7de37a708e4b4341bbe65b41cb2b27bf0a58ce19af',
    '../plan/inputs/asset-inventory-source-v0.1.txt':'f38e8b2ab711197bd92ba5aa6aea8d45c0e307bdf96ec09c342e0d097d8e55db',
    '../plan/README.md':'f50752ba73322d3da84538ad7a44d3dd677aa3c29268cf24fb98d1665d0bc07a',
}
source_checks={name:{'expected':digest,'actual':sha(ROOT/name)} for name,digest in expected.items()}
assert all(x['expected']==x['actual'] for x in source_checks.values()),'Original input changed'
write(ROOT/'review'/'input-preservation.json',source_checks)

same=ImageChops.difference(Image.open(ROOT/'review/main-f0900.png').convert('RGB'),Image.open(ROOT/'review/reopen-f0900.png').convert('RGB')).getbbox() is None
assert same,'Reopened render differs'
write(ROOT/'review/reopen-check.json',{'frame':900,'resolution':[960,540],'separate_factory_startup_process':True,'pixel_identical':same,'log':'logs/reopen-final.log'})
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(ROOT/'preview/master-v001.mp4')],text=True))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_read_frames']))==(768,432,'12/1',1392)
assert abs(float(probe['format']['duration'])-116)<.001
write(ROOT/'review/ffprobe.json',probe)

details={
'A-01':('S1 S2 S3 S4 S5 S6 S7','동일 컨테이너·내부·양문·식별면','상세 문 잠금장치·외관'),
'A-02':('S1 S2 S3 S4','동일 강체 선박·선수·선미·선교·갑판','최종 선형·적재 디테일'),
'A-03':('S4 S5 S6 S7','트랙터·트레일러 연결점과 별도 회전','실차 회전반경·차종·동역학'),
'A-04':('S6 S7','주 출고 차량 1대·상차·문·독립 경로','차종·리깅'),
'A-05':('S6 S7','미리 대기한 보조 차량 1대·시차 합류','최종 수량·차종'),
'E-01':('S2 S3 S4 S7','고정 구형 세계의 단순 육지 테라스','최종 대륙 실루엣'),
'E-02':('S1 S2 S3 S4','연속된 구형 수면','수면 룩·유체 효과'),
'E-03':('S1 S2','중국 부두·야드·출항 수로·도로','항만 디자인'),
'E-04':('S2','중국 도시 건물 덩어리','랜드마크·외관'),
'E-05':('S3 S4','미국 접안부·야드·하역 공간','항만 디자인'),
'E-06':('S4 S7','미국 도시 건물 덩어리','랜드마크·외관'),
'E-07':('S4 S5','고정 진입 도로·타원 선회 구간','정밀 차량 궤적'),
'E-08':('S4 S5 S6 S7','단일 창고·항상 열린 전면·부분 지붕','건축 상세·최종 개방 구조'),
'E-09':('S5 S6','입고 마당·도크·바닥 연결판','실시설비 치수'),
'E-10':('S6 S7','출고 대기 마당·상차 연결판','상차 설비 상세'),
'E-11':('S7','공통 도로·두 분기·보조 합류로','최종 배송망 형상'),
'E-12':('S7','목적지를 암시하는 4개 건물','도시·지역 미정'),
'P-01':('S1 S2','중국 크레인·트롤리·케이블·스프레더','정밀 장비 기구·잠금'),
'P-02':('S4','별도 미국 크레인·트롤리·케이블·스프레더','정밀 장비 기구·잠금'),
'P-03':('S1 S2 S4','갑판 적재열·양국 야드 반복 프록시','배치 밀도·외관'),
'W-01':('S5 S6','신규·보관·컨테이너 잔류 팔레트 별도 개체','포장 단위·상세 적재'),
'W-02':('S6','입고·보관용 팔레트 잭 점유 및 이동','장비 선정·작업자 조작'),
'W-03':('S6','보관 랙·통로·상품 지지 선반','랙 규격·안전 간격'),
'W-04':('S6','선반 상품과 이미 피킹된 주문 별도 개체','손 집기·상품 디테일'),
'W-05':('S6','피킹 카트·접근 경로','운반 수단 확정'),
'W-06':('S6','포장대·작업 위치','설비 상세'),
'W-07':('S6','내용물 있는 열린 포장 상자','플랩 접기·봉함 연기'),
'W-08':('S6 S7','기봉함 상자·마지막 상차·기적재 화물','손 인계·봉함 표시'),
'W-09':('S6','출고 카트·이송 경로','운반 수단 확정'),
'W-10':('S6','입고·출고 대기 영역','작업 용량·간격'),
'CH-01':('S6','3개 작업자 점유 프록시·상차 팔/지지 프록시','얼굴·복장·손가락·정교한 연기'),
'FX-01':('S2 S3 S4','곡면을 따르는 두 항적 띠','수면 효과·유체'),
}
manifest=read(ROOT/'manifest.json')
inventory=read(ROOT/'review/scene-inventory.json')
assert set(details)=={a['asset_id'] for a in manifest['assets']}
for a in manifest['assets']:
    segments,rep,follow=details[a['asset_id']]
    objects=[o for o in inventory if o['asset_id']==a['asset_id']]
    a.update({'segments':segments.split(),'representation':rep,'detail_followup':follow,'status':'proxy','objects':[o['object'] for o in objects],'instances':sorted({o['instance_id'] for o in objects}),'collections':sorted({c for o in objects for c in o['collections']})})
manifest['source_hashes']=source_checks
for source in manifest['sources']:
    snapshot=ROOT/'inputs'/f"{source['id']}.json"
    source.update({'snapshot':str(snapshot.relative_to(ROOT)).replace('\\','/'),'sha256':sha(snapshot),'body_scope':'full returned page body; linked N1-N7 fetched separately','retrieved_date':'2026-10-06','source_version':'text direction v0.1'})
manifest['settings']['inbound_reverse_distance_test_units']=5.2
manifest['settings']['inbound_turn']={'type':'half ellipse, arc-length sampled','radii':[6,10],'center':[29.4,19],'final_aligned_trailer':[29.2,29],'dock_trailer':[34.4,29],'short_reverse_criterion':'<= one 5.5-unit articulated proxy length; not a real truck standard'}
manifest['segments']=[{'id':s,'start_frame':a,'end_frame':b,'shared_boundary':True} for s,a,b in [('S1',1,96),('S2',96,216),('S3',216,456),('S4',456,648),('S5',648,900),('S6',900,1200),('S7',1200,1392)]]
manifest['events']={'ship_seated':72,'ship_departs':145,'ship_docked':510,'US_lift':532,'trailer_seated':632,'inbound_departs':649,'doors_open':[811,842],'reverse':[849,890],'new_pallet_unload':[908,966],'outbound_primary':1201,'outbound_secondary':1261}
manifest['verification']={'tests':read(ROOT/'logs/test-result.json'),'all_frames':'validation.json','boundary_states':'boundary-states.json','reopen':'review/reopen-check.json','playback':'review/playback-check.json','acceptance':'report.md','scope':'sampled spatial blockout review only'}
manifest['authoritative_source']='scripts/build_master.py generates the editable master; scripts/finalize_handoff.py enriches metadata. Saved blend contains baked keys and requires no Python handlers. No manual scene edits.'
manifest['file_hashes']='hashes.json'
write(ROOT/'manifest.json',manifest)

required=['master-v001.blend','manifest.json','boundary-states.json','validation.json','report.md','README.md','progress.md','preview/master-v001.mp4']
paths=[ROOT/n for n in required]
paths+=list((ROOT/'scripts').glob('*'))+list((ROOT/'inputs').glob('*.json'))
paths+=[p for p in (ROOT/'review').rglob('*') if p.is_file()]
paths+=[ROOT/'logs'/n for n in ['build-final.log','validation-final.log','reopen-final.log','playback-final.log','review-final.log','animation-final.log','encode-final.log','test-result.json','boundary-reopen-check.json']]
entries={str(p.relative_to(ROOT)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(paths)) if p.is_file()}
frames=sorted((ROOT/'preview/frames').glob('frame-*.png'))
assert len(frames)==1392
aggregate=hashlib.sha256(''.join(f'{p.name} {sha(p)}\n' for p in frames).encode()).hexdigest()
write(ROOT/'hashes.json',{'algorithm':'SHA-256','version':'v001','files':entries,'frame_sequence':{'count':len(frames),'digest_method':'SHA256 of ordered filename + space + file SHA256 + LF','aggregate_sha256':aggregate},'excluded':'hashes.json itself, old candidate logs/backups/smoke files and transient HTTP server log'})
print(json.dumps({'original_inputs_unchanged':True,'reopen_pixel_identical':same,'video_frames':video['nb_read_frames'],'hashed_deliverables':len(entries),'blend_sha256':sha(ROOT/'master-v001.blend'),'video_sha256':sha(ROOT/'preview/master-v001.mp4')},indent=2))
