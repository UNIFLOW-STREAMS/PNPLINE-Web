import json, hashlib
from pathlib import Path
B=Path('F:/pnpline-landing/hero-section-video/blockout/full-layout-master-v001')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
mh=sha(B/'master-full-layout-v001.blend')
pkg=read(B/'package-record.json')
assert mh==pkg['master_sha256']
assert sha(B/'preview/full.mp4')==pkg['full_video_sha256']
write(B/'review/playback.json', {'master_sha256':mh,'video_sha256':pkg['full_video_sha256'],'method':'CUA browser click on full-speed playback button; read media element at start, mid-run and end','source':'http://127.0.0.1:8768/preview/full.mp4','current_time_s':116.083333,'duration_s':116.083333,'ended':True,'paused_at_end':True,'playback_rate':1,'elapsed_wall_seconds':116.0858999999985,'media_error':None,'pass':True,'observed_frames':'Mid-run driving view and final two-vehicle outbound view; representative renders inspected separately.'})
records=['full-acceptance','master-regression','layout-acceptance','preservation','handoffs','space-validation','final-review','playback']
for n in records:
 d=read(B/f'review/{n}.json')
 if 'master_sha256' in d: assert d['master_sha256']==mh,n
 if 'pass' in d: assert d['pass'],n
 if 'pass_all' in d: assert d['pass_all'],n
 if n=='master-regression': assert d['tests']==23 and not d['errors'] and not d['failures']
wheel=(B/'logs/wheel-tests.log').read_text(encoding='utf-8')
assert 'Ran 5 tests' in wheel and '\nOK' in wheel
source=B.parent/'s5-integration-v001/master-s5-integration-v001.blend'
assert sha(source)=='8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665'
manifest={'master_sha256':mh,'source_unchanged':True,'pass':True,'frame_range':[0,1392],'fps':12,'records':{n:{'path':f'review/{n}.json','sha256':sha(B/f'review/{n}.json')} for n in records},'wheel_log_sha256':sha(B/'logs/wheel-tests.log'),'collision_scope':{'handoff':[216,624],'dock_sat':[720,948],'step':0.25,'continuous_time_claim':False},'package_record_sha256':sha(B/'package-record.json'),'known_visual_limitation':'f692–700 brief crane occlusion retained from adopted proposal.'}
write(B/'review/validation-manifest.json',manifest)
with (B/'report.md').open('a',encoding='utf-8') as f: f.write('\n브라우저 원속도 재생은 실제 116.086초 동안 진행되어 영상 끝 116.083333초에 도달했다. 미디어 오류는 없었고 마지막 두 출고 차량 장면을 확인했다. 결과와 출처는 `review/playback.json`, 최종 검증 묶음은 `review/validation-manifest.json`에 기록했다.\n')
paths=[B/'master-full-layout-v001.blend',B/'README.md',B/'report.md',B/'review.html',B/'build-record.json',B/'render-full.json',B/'package-record.json',B/'preview/full.mp4',B/'preview/transitions.mp4',B/'review/contact.png',B/'review/validation-manifest.json',B/'logs/wheel-tests.log']+[B/f'review/{n}.json' for n in records]
write(B/'hashes.json',{str(p.relative_to(B)).replace('\\','/'):sha(p) for p in paths})
print('PASS: final master, original preservation, playback, validation manifest and deliverable hashes')
