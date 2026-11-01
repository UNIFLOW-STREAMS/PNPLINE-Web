"""Encode actual Blender review frames and assemble a local Korean comparison page."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review'
still_metadata_paths = {}
for label in ['before', 'after']:
    frames = REVIEW / f'{label}-hoist-frames'
    metadata = json.loads((frames / 'metadata.json').read_text(encoding='utf-8'))
    source = Path(metadata['source'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == metadata['sha256'], label + ' stale source'
    candidates = [REVIEW / f'{label}-{mode}-metadata.json' for mode in ['stills', 'all']]
    matching = [p for p in candidates if p.exists() and json.loads(p.read_text(encoding='utf-8'))['sha256'] == metadata['sha256']]
    assert matching, label + ' stale stills'
    still_meta_path = max(matching, key=lambda p: p.stat().st_mtime)
    still_meta = json.loads(still_meta_path.read_text(encoding='utf-8'))
    still_metadata_paths[label] = still_meta_path.name
    paths = [frames / f'f{f:04d}.png' for f in metadata['frames']]
    assert all(p.is_file() and p.stat().st_size for p in paths)
    concat = REVIEW / f'{label}-hoist-concat.txt'
    concat.write_text(''.join("file '" + p.as_posix().replace("'", "'\\''") + "'\nduration 0.166666666667\n" for p in paths)
                      + "file '" + paths[-1].as_posix() + "'\n", encoding='utf-8')
    video = REVIEW / f'{label}-hoist.mp4'
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                    '-i', str(concat), '-vf', 'fps=12', '-t', str(len(paths) / 6), '-c:v', 'libx264',
                    '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video)], check=True)
    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height,r_frame_rate,nb_frames:format=duration',
                                     '-of', 'json', str(video)], text=True)
    (REVIEW / f'{label}-hoist-video.json').write_text(probe, encoding='utf-8')

concept = ROOT.parents[1] / 'concept-design' / 'china-shanghai-miniature.png'
assert concept.is_file(), concept
shutil.copy2(concept, REVIEW / 'concept.png')
html = '''<!doctype html>
<html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>중국 미니어처 전면 항만 · 수정 전후</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101820;color:#f0f4f7;font:16px/1.65 system-ui,sans-serif}main{max-width:1650px;margin:auto;padding:36px 24px 70px}h1{font-size:30px;line-height:1.3;margin:0 0 10px}h2{font-size:23px;margin:40px 0 14px}p{color:#bbcad4;margin:8px 0}a{color:#81d9ec}button,select{font:inherit;background:#223641;color:#f0f4f7;border:1px solid #486573;border-radius:7px;padding:7px 14px;cursor:pointer}button.active{background:#166274;border-color:#82d6e7}.toolbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:18px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0;min-width:0}figcaption{font-size:19px;font-weight:600;margin:0 0 8px}img,video{width:100%;height:auto;display:block;border-radius:8px;background:#1b2931}.note{border-left:3px solid #45b8ce;padding:12px 18px;background:#182832;margin:24px 0}.small{font-size:14px}.concept{max-width:1300px}.meta{word-break:break-all;font-size:13px;color:#8fa6b6}details{padding:12px 0}summary{cursor:pointer}@media(max-width:850px){.grid{grid-template-columns:1fr}main{padding:22px 14px}h1{font-size:25px}}
</style><main>
<h1>중국 미니어처 전면 항만</h1>
<p>기존 도시 앞쪽에 긴 부두, 컨테이너 127개로 구성한 4열 적재 구역과 크레인 3기를 배치한 작업본입니다.</p>
<p><a href="../master-cn-port-layout-v001.blend">master-cn-port-layout-v001.blend</a> · <a href="concept.png" target="_blank">컨셉 이미지 원본</a></p>
<div class="note">이 페이지의 카메라는 배치와 인양 동작을 확인하기 위한 임시 검토 카메라입니다. Blender 마스터의 기존 카메라 애니메이션은 유지했으며, 최종 카메라·앵글·동선 조정은 다음 작업에 해당합니다.</div>
<h2>같은 검토 시점에서 비교</h2>
<div class="toolbar" id="views"><button class="active" data-view="overview">전체 도시</button><button data-view="port">항만 확대</button><button data-view="top">위에서 보기</button></div>
<div class="grid"><figure><figcaption>수정 전</figcaption><a id="beforeLink" href="before-overview.png" target="_blank"><img id="beforeImg" src="before-overview.png" alt="수정 전 전체 도시와 항만"></a></figure><figure><figcaption>수정 후</figcaption><a id="afterLink" href="after-overview.png" target="_blank"><img id="afterImg" src="after-overview.png" alt="수정 후 전체 도시와 항만"></a></figure></div>
<p class="small">이미지를 클릭하면 원본 크기로 열립니다. 수정 전후에는 동일한 임시 카메라를 사용했습니다.</p>
<h2>S1 하강·안착 동작 확인</h2>
<div class="toolbar"><button id="play">두 영상 재생</button><button id="pause">일시정지</button><button id="reset">처음으로</button><label>재생 속도 <select id="speed"><option value="0.5">0.5배</option><option selected value="1">1배</option><option value="2">2배</option><option value="3.5">3.5배</option></select></label></div>
<div class="grid"><figure><figcaption>수정 전</figcaption><video id="beforeVideo" controls muted playsinline preload="metadata" poster="before-hoist-frames/f0000.png" src="before-hoist.mp4"></video></figure><figure><figcaption>수정 후 · 이동한 인양 위치 기준</figcaption><video id="afterVideo" controls muted playsinline preload="metadata" poster="after-hoist-frames/f0000.png" src="after-hoist.mp4"></video></figure></div>
<p>f0–156 · 원본 12fps 시간축 · 2프레임 간격 샘플. 수정 후 영상은 기존 카메라를 항만 이동량만큼 평행 이동해 촬영했습니다. 이 임시 이동은 마스터 파일에 저장하지 않았습니다.</p>
<h2>항만 컨셉 기준</h2><a href="concept.png" target="_blank"><img class="concept" src="concept.png" alt="청색과 백색 컨테이너, 3기 크레인과 긴 부두가 있는 중국 미니어처 컨셉"></a>
<details><summary>검증 자료</summary><p><a href="verification.json">원본 액션·카메라·하강 동작 보존 및 항만 교차 검사</a><br><a href="after-stills-metadata.json">이미지 기준 파일과 해시</a><br><a href="after-hoist-frames/metadata.json">영상 기준 파일과 해시</a></p></details>
</main><script>
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-view]').forEach(x=>x.classList.toggle('active',x===b));['before','after'].forEach(k=>{const p=k+'-'+b.dataset.view+'.png';document.getElementById(k+'Img').src=p;document.getElementById(k+'Link').href=p})});
const vs=[document.getElementById('beforeVideo'),document.getElementById('afterVideo')];document.getElementById('play').onclick=()=>{const t=vs[0].currentTime;vs.forEach(v=>{v.currentTime=t;v.play()})};document.getElementById('pause').onclick=()=>vs.forEach(v=>v.pause());document.getElementById('reset').onclick=()=>vs.forEach(v=>{v.pause();v.currentTime=0});document.getElementById('speed').onchange=e=>vs.forEach(v=>v.playbackRate=+e.target.value);
</script></html>'''
html = html.replace('after-stills-metadata.json', still_metadata_paths['after'])
(REVIEW / 'review.html').write_text(html, encoding='utf-8')
print('PACKAGED', REVIEW / 'review.html')
