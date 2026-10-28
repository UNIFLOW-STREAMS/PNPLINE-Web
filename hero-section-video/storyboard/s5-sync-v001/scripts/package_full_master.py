import json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout/full-layout-master-v001';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rec=json.loads((B/'render-full.json').read_text());identity=sha(B/'master-full-layout-v001.blend')
assert rec['status']=='complete' and rec['blend_sha256']==identity
assert [x['frame'] for x in rec['frames']]==list(range(1393))
for r in rec['frames']:assert sha(r['path'])==r['sha256']
run=Path(rec['frames'][0]['path']).parent
cmd=['ffmpeg','-y','-framerate','12','-start_number','0','-i',str(run/'%04d.png'),'-frames:v','1393','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(B/'preview/full.mp4')]
with (B/'logs/encode-full.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True)
subcmd=['ffmpeg','-y','-framerate','12','-start_number','408','-i',str(run/'%04d.png'),'-frames:v','625','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(B/'preview/transitions.mp4')]
with (B/'logs/encode-transitions.log').open('w') as log:subprocess.run(subcmd,stdout=log,stderr=log,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(B/'preview/full.mp4')],text=True));st=probe['streams'][0];assert int(st['nb_frames'])==1393 and st['r_frame_rate']=='12/1';(B/'review/video-probe.json').write_text(json.dumps(probe,indent=2),encoding='utf8')
contact=Image.new('RGB',(1440,5*292),'white');d=ImageDraw.Draw(contact);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
frames=[0,216,360,456,532,552,648,720,766,900,948,1008,1158,1260,1392]
for i,f in enumerate(frames):
 x=i%3*480;y=i//3*292;im=Image.open(run/f'{f:04d}.png').resize((480,270));contact.paste(im,(x,y));d.text((x+8,y+271),f'f{f}  ·  {f/12:.2f}s',font=font,fill='black')
contact.save(B/'review/contact.png')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>PNPLINE 전체 통합 마스터</title><style>body{margin:24px auto;max-width:1100px;background:#16191d;color:#eee;font:17px/1.6 sans-serif}h1{font-size:27px}video,img{width:100%;display:block;margin:18px 0}a{color:#9ed5ff}video{max-height:68vh}button{padding:10px 16px;font:inherit}.note{padding:14px;background:#243c46}</style><h1>S1–S7 전체 통합 마스터</h1><p>S4-05 기준으로 채택한 배치와 동선을 전체 영상에 연결했습니다. 전체 f0–1392 · 12fps · 1분 56.08초.</p><p class="note">S1·S2 구도 유지 → S3 항로 연결 → S4 하역·S5 주행·접안 → S6 창고 작업 → S7 출고.</p><button onclick="const v=document.getElementById('full');v.currentTime=0;v.playbackRate=1;v.dataset.started=performance.now();v.onended=()=>v.dataset.elapsed=(performance.now()-Number(v.dataset.started))/1000;v.play()">전체 원속도 재생</button><video id="full" controls preload="metadata" src="preview/full.mp4"></video><p><a href="master-full-layout-v001.blend">전체 Blender 마스터</a> · <a href="report.md">검증 보고서</a></p><p>연결부 확인: f408–1032 (영상 0초 = 본편 34초)</p><video controls preload="metadata" src="preview/transitions.mp4"></video><p>f692–700에서는 크레인 기둥이 차량 일부를 잠깐 가립니다.</p><img src="review/contact.png"></html>'''
(B/'review.html').write_text(html,encoding='utf8')
(B/'package-record.json').write_text(json.dumps({'master_sha256':identity,'render_record_sha256':sha(B/'render-full.json'),'full_video_sha256':sha(B/'preview/full.mp4'),'transition_video_sha256':sha(B/'preview/transitions.mp4'),'full_frames':1393,'fps':12,'duration_s':float(st['duration']),'source_frame_start':0,'transition_range':[408,1032],'encode_command':cmd,'transition_command':subcmd,'contact_sha256':sha(B/'review/contact.png'),'package_script_sha256':sha(__file__)},indent=2),encoding='utf8');print('FULL_MASTER_PACKAGED',identity)
