import json,hashlib,shutil,subprocess,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];H=R.parents[1];W=H.parent/'output/hero-section-b-scroll-v001';old=H.parent/'output/scroll-previz-pacing-v001';W.mkdir(exist_ok=True);(W/'assets').mkdir(exist_ok=True);(W/'data').mkdir(exist_ok=True)
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for name in ['app.mjs','mapping.mjs','style.css','server.mjs','package.json']:shutil.copy2(old/name,W/name)
config=json.loads((R/'pacing.json').read_text(encoding='utf-8'));(W/'pacing.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
html=(old/'index.html').read_text(encoding='utf-8').replace('PNPLINE · Scroll pacing review','PNPLINE · Hero Section B scroll').replace('SCROLL PACING / 01','HERO B / SCROLL').replace('LATEST SCENE · WORKBENCH PREVIZ','HERO SECTION B · WORKBENCH PREVIZ').replace('최신 통합 장면의 실제 카메라','최신 Hero Section B의 실제 카메라').replace('위 영상은 동선과 스크롤 속도를 확인하는 제작용 프리비즈입니다.','위 영상은 최신 B 장면의 스크롤 동선과 속도를 확인하는 제작용 프리비즈입니다.').replace('0–989프레임 · 30fps.','0–989프레임 · 30fps. B.blend의 애니메이션 타이밍은 변경하지 않았습니다.').replace('<a href="review/mapping.svg">매핑 그래프</a>','').replace('프레임 매핑 CSV','프레임 매핑 CSV')
(W/'index.html').write_text(html,encoding='utf-8')
if '--prepare' in sys.argv:print('Prepared standalone web player');sys.exit(0)
frames=R/'frames';assert all((frames/f'f{f:04d}.png').is_file() for f in range(990))
mp4=W/'assets/hero-section-b-previz.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-framerate','30','-start_number','0','-i',str(frames/'f%04d.png'),'-frames:v','990','-c:v','libx264','-preset','fast','-crf','18','-g','8','-keyint_min','8','-sc_threshold','0','-bf','0','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(mp4)],text=True))['streams'][0];assert probe['nb_frames']=='990' and probe['r_frame_rate']=='30/1'
from PIL import Image
for name,f in [('poster',32),('s1',32),('s2',118),('s3',230),('s4',390),('s5',600),('s6',780),('s7',930)]:Image.open(frames/f'f{f:04d}.png').convert('RGB').save(W/'assets'/f'{name}.jpg',quality=91)
verify=json.loads((R/'verification.json').read_text());canonical=H/'hero-section-B.blend';assert sha(canonical)==verify['source_sha256'];assert sha(verify['file'])==verify['sha256'];assert sha(H/'hero-section-A.blend')==verify['A_unchanged_sha256'];shutil.copy2(verify['file'],canonical)
manifest=dict(source=str(canonical),source_sha256=verify['sha256'],animation_unchanged=True,renderer='BLENDER_WORKBENCH',quality='Scroll timing preview; final Cycles material/light/DOF not represented',stream=probe,media=str(mp4),media_sha256=sha(mp4),pacing=str(W/'pacing.json'),total_viewport_heights=13,web=str(W),application='Scroll maps to currentTime; no animation retime; no double easing')
(W/'data/media-manifest.json').write_text(json.dumps(manifest,indent=2));(R/'delivery.json').write_text(json.dumps(manifest,indent=2))
pointer=H/'latest-hero-section.json';p=json.loads(pointer.read_text());(R/'previous-latest-hero-section.json').write_text(json.dumps(p,indent=2));p['variants']['B'].update(versioned_copy=verify['file'],sha256=verify['sha256'],scroll_config=str(W/'pacing.json'),scroll_player=str(W/'index.html'),verification=str(R/'verification.json'));p['scroll_world']=manifest;pointer.write_text(json.dumps(p,indent=2))
look=H/'lookdev/latest-lookdev.json';lp=json.loads(look.read_text());(R/'previous-latest-lookdev.json').write_text(json.dumps(lp,indent=2));lp['variants']['B']=p['variants']['B'];look.write_text(json.dumps(lp,indent=2))
readme='''# Hero Section B · web scroll pacing

최신 B.blend에는 PNPLINE_SCROLL_PACING.json과 적용 설명을 Text 데이터로 내장했다. 액션 키프레임과 0–989 / 30fps 타이밍은 그대로이며 A도 그대로다. 재생 속도 변경은 웹 플레이어에서만 한다.

기존 승인 설정을 그대로 사용한다. S1–S7 거리는 각각 1.2 / 1.6 / 1.3 / 1.9 / 2.3 / 3.0 / 1.7 화면 높이이며 합계 13이다. 1080px 높이에서는 14,040px이다. 컨테이너 안착, 도시 공개, 하역, 도크 정렬, 피킹·포장·상차, 배송 분기 감속 지점도 동일하다.

실행: 이 폴더에서 `node server.mjs` (기본 3096). 별도 실행은 PowerShell `$env:PORT='3098'; node server.mjs`. 서버는 127.0.0.1에만 바인딩한다. 스크롤이 영상 시간만 제어한다. 선형/감속 비교, 장면 이동, 측정 보기, reduced-motion 정적 대체를 제공한다. 빠른 스크롤에 대한 최소 관람 시간 보장은 포함하지 않는다.

미디어는 최신 B의 990프레임을 모두 새로 출력한 Workbench 프리비즈(960×540 / 30fps / GOP 8)다. 최종 라이팅·투명도·DOF·재질 반응은 Cycles 렌더와 다르다. 최종 Cycles 0–989 / 30fps MP4로 assets/hero-section-b-previz.mp4를 교체해도 프레임 구간과 설정은 그대로 사용할 수 있다. 타이밍을 다시 굽거나 웹 매핑을 중복 적용하지 않는다.

원래 검토 페이지 output/scroll-previz-pacing-v001은 보존했다. 운영 사이트는 변경하지 않았고, 이 폴더는 독립 실행·이식용 웹 플레이어다. Blender 제작 렌더 설정은 바꾸지 않았다.
'''
(W/'README.md').write_text(readme,encoding='utf-8');(R/'README.md').write_text(readme,encoding='utf-8');print('PACKAGED',json.dumps(manifest),flush=True)
