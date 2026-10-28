from pathlib import Path
import json,subprocess,hashlib
R=Path(__file__).resolve().parents[1];ver='v021';qa=json.loads((R/f'review/crane-motion-verified-{ver}.json').read_text());scope=json.loads((R/f'review/crane-scope-{ver}.json').read_text());assert all(qa['checks'].values())and scope['passed']
folder=R/f'preview/crane-motion-{ver}-frames';meta=json.loads((folder/'metadata.json').read_text());fps=meta['source_fps']/meta['fps_base'];frames=meta['frames'];lines=['ffconcat version 1.0']
for i,f in enumerate(frames):
 p=folder/f'f{f:04d}.png';assert p.exists();duration=(frames[i+1]-f)/fps if i<len(frames)-1 else 1/fps;lines += ["file '"+p.as_posix()+"'",f'duration {duration:.12f}']
lines += ["file '"+(folder/f'f{frames[-1]:04d}.png').as_posix()+"'"]
listing=R/f'preview/crane-motion-{ver}.ffconcat';listing.write_text('\n'.join(lines)+'\n');video=R/f'preview/crane-motion-{ver}.mp4'
duration=(frames[-1]-frames[0]+1)/fps
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-r',str(fps/2),'-f','concat','-safe','0','-i',str(listing),'-frames:v',str(frames[-1]-frames[0]+1),'-r',str(fps),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,r_frame_rate,nb_frames:format=duration','-of','json',str(video)]));assert abs(float(probe['format']['duration'])-duration)<.01;assert int(probe['streams'][0]['nb_frames'])==217
(R/f'preview/crane-motion-{ver}-metadata.json').write_text(json.dumps({'render':meta,'video':probe,'speed':'original 12 fps timing; sampled every 2 frames and held, not sped up'},indent=2))
report='''# 크레인 외형 및 S1 동작 연결 v021

작업 파일: `review/layout-proposal-v021.blend`.
사용자 승인: v019 외형을 기준으로 S1 인양 경로·높이·케이블과 필요한 근접카메라 연결까지 수정.
기준 체인: v014 C 도시 → v017 NA 도시 → v019 소형 크레인 외형 → v021 동작 통합. 이전 파일은 보존.

## 변경 사항
- 부두에 접지된 흰 수직 기둥 4개, 짧은 청색 수평 붐과 삼각 지지 구조를 유지했다.
- 기둥 상부에 회전 받침을 추가해 짧은 붐이 S1의 기존 컨테이너 위치에 닿도록 했다. 붐은 약 79도 안팎의 초기 작업 방향에서 참조 대기 방향으로 돌아온다. 정확한 값은 crane-integration-v021.json의 initial_slew_degrees.
- 트롤리가 레일을 따라 이동하고 인양 장치는 안착 후 접혀 회수된다. 4개 케이블은 새 상부 장치와 실제 인양 프레임에 연결된다.
- S1 초기 컨테이너 높이를 약 1.8m 낮췄다. 카메라와 타깃도 같은 만큼 이동해 기존 각도와 렌즈를 유지했다. 변경 구간은 f0–71이다.
- f72에 원본과 같은 위치에 안착한다. f78 이후 장치를 올리고 f100–138에 붐을 회전시켜 f156에 대기 위치로 내린다.
- v019에서 기둥 주변을 비우기 위해 가옥 4동·나무 2그루를 이동한 내용을 포함한다. 건물 개수·디자인은 유지했다.

## 검증 결과
Blender 5.1.0에서 저장본을 별도 재개방했다. 동작 검사 8/8 및 비크레인 객체 범위 검사 통과.
- f72–1392 모든 정수 프레임에서 컨테이너·선박·카메라·타깃의 원본 대비 행렬 오차 0.
- 원본 48개 액션 중 승인된 컨테이너·카메라·타깃·중국 인양 장치 4개만 변경. 새 기구 액션 19개.
- f0–156의 0.5프레임 표본에서 케이블 끝점 오차 최대 약 0.036mm, 최소 케이블 길이 약 0.20m.
- 안착 프레임과 인양 프레임/컨테이너 높이 간격 유지. 회수 중 건축물 외곽과의 겹침 및 카메라의 건물 내부 진입 검사는 발견 없음.
- f156의 비크레인 객체 7,001개 형상·변환·재질 연결 차이 없음(v019 대비).
- f0/24/48/72/96/112/128/144/156/216 Cycles 스틸 및 f156 확대 렌더 확인.
- f0–216 Workbench 검토 영상: 2프레임마다 렌더한 후 원본 12fps 타이밍으로 유지. 재생시간 약 18.08초이며 2배속이 아니다.

검사 첫 실행에서 실제 선형 보간된 접이식 장치 대신 해석식 easing 값을 비교하여 케이블 끝점 오차를 과대 계산했다. 검사를 실제 트위스트락 형상의 접속점 기준으로 수정하고 다시 실행했다. 허용 오차는 변경하지 않았다.

## 한계와 남은 차이
이번 완료 범위는 크레인 외형과 승인된 S1 연결이다. 전체 스타일프레임의 모든 요소를 최종 승인한 것은 아니다. 기존 선박 색면, 넓은 흰 지형, f104 부근의 기존 카메라 전환 등은 이번 변경과 별개다.
크레인의 회전 받침과 접이식 인양 장치는 단일 참조 이미지에서 보이지 않는 동작을 연결하기 위한 간략한 기계 구성이다. 구조공학 검증을 의미하지 않는다.
0.5프레임 표본 및 건물 외곽 검사이며 모든 연속시간/미세 메시 충돌에 대한 수학적 증명은 아니다. 검토 영상은 형태·동작용이고 재질 비교는 Cycles 스틸을 기준으로 한다.

## 재현
`crane-style-proposal-v019.blend`를 열어 `scripts/integrate_compact_crane.py -- <새 출력 경로>` 실행.
`verify_crane_motion.py`, `verify_crane_scope.py`로 동작 및 범위 확인.
`render_crane_motion.py -- stills`, `render_crane_motion.py -- workbench-video`, `render_na_detail.py -- <PNG>`로 검토 자료 생성.
'''
(R/f'review/crane-integration-{ver}.md').write_text(report,encoding='utf-8')
p=R/'review.html';html=p.read_text(encoding='utf-8');start=html.index('<section ')
section='''<section id="crane-v021" style="background:white;padding:24px;border:3px solid #278195;margin-bottom:30px"><h1>크레인 수정 + S1 동작 연결 — v021</h1>
<p>흰 수직 기둥과 짧은 청색 수평 붐을 유지하면서, 컨테이너 인양·안착·장치 회수·대기 위치 복귀를 연결했습니다. f72 안착과 이후 컨테이너·선박·카메라는 원본과 동일합니다.</p>
<div class="grid"><figure><img src="review/na-detail-v017.png" style="aspect-ratio:auto"><figcaption>수정 전 v017</figcaption></figure><figure><img src="review/crane-detail-v021.png" style="aspect-ratio:auto"><figcaption>동작 연결 완료 v021 · 동일 f156</figcaption></figure></div>
<video controls preload="metadata" style="width:100%;max-width:1100px" src="preview/crane-motion-v021.mp4"></video><p>S1–S2 f0–216 · 원래 동작 시간 · Workbench 검토 영상</p>
<p><a href="review/layout-proposal-v021.blend"><b>작업 Blender 파일: layout-proposal-v021.blend</b></a> · <a href="review/crane-motion-v021/f0156.png">전체 렌더</a> · <a href="review/crane-motion-verified-v021.json">동작 검사 8/8</a> · <a href="review/crane-scope-v021.json">보호 범위 검사</a> · <a href="review/crane-integration-v021.md">작업 기록</a></p>
<details><summary>초기 인양·안착·대기 프레임</summary><div class="grid"><img src="review/crane-motion-v021/f0000.png"><img src="review/crane-motion-v021/f0072.png"><img src="review/crane-motion-v021/f0156.png"></div></details>
<p>초기 높이와 S1 카메라 이동은 승인 범위에서 수정했습니다. 도시·CHINA·구름·수로를 포함한 이전 수정이 누적되어 있습니다. 이전 정지 제안 v019는 아래 이력으로 남겨 둡니다.</p></section>'''
if 'id="crane-v021"' in html:
 oldstart=html.index('<section id="crane-v021"');oldend=html.index('</section>',oldstart)+len('</section>');html=html[:oldstart]+html[oldend:];start=html.index('<section ')
p.write_text(html[:start]+section+html[start:],encoding='utf-8')
paths=['review/layout-proposal-v021.blend','review/crane-style-proposal-v019.blend','review/crane-detail-v021.png','review/crane-motion-v021/f0156.png','preview/crane-motion-v021.mp4']
(R/'review/crane-delivery-v021.json').write_text(json.dumps({'status':'crane geometry and approved S1 motion integrated','hashes':{f:hashlib.sha256((R/f).read_bytes()).hexdigest()for f in paths},'motion':qa,'scope':scope,'video':probe},indent=2))
if '## 크레인 v021 동작 통합'not in (R/'decision-log.md').read_text(encoding='utf-8'):
 with (R/'decision-log.md').open('a',encoding='utf-8')as f:f.write('\n\n## 크레인 v021 동작 통합\n사용자가 S1 인양·카메라 연결까지 승인하여 v019 외형을 실제 기구 동작에 연결했다. f72 이후 컨테이너·선박·카메라 보존 확인. 최종 작업 파일 review/layout-proposal-v021.blend, 상세 기록 review/crane-integration-v021.md.\n')
print(json.dumps({'file':qa['file'],'checks':qa['checks'],'scope':scope,'video':probe},indent=2))
