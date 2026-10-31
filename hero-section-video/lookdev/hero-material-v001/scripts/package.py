import json,hashlib,subprocess,re,statistics,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageStat
R=Path(__file__).resolve().parents[1];V=R/'review';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pack=V/'packaging.json';render_sha=json.loads(pack.read_text())['render_source_sha256'] if pack.exists() else sha(R/'pnpline-hero-material-v001.blend')
clips=[('water-glass',105,'중국 항만 · 유리와 수면'),('us-port',330,'미국 항만 이동'),('warehouse',710,'창고 내부')]
results=[]
for label,start,title in clips:
 folder=V/label;metrics=folder/'render-metrics.json'
 if not metrics.exists() or len(json.loads(metrics.read_text()))!=30:continue
 data=json.loads(metrics.read_text());assert all(x['source_sha256']==render_sha for x in data)
 frames=sorted(folder.glob('f*.png'));assert len(frames)==30
 for suffix,crf in [('review',12),('web',24)]:
  out=V/f'{label}-{suffix}.mp4'
  cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','30','-start_number',str(start),'-i',str(folder/'f%04d.png'),'-frames:v','30','-c:v','libx264','-preset','slow','-crf',str(crf),'-pix_fmt','yuv420p','-movflags','+faststart','-an',str(out)]
  subprocess.run(cmd,check=True)
 # Full decoded comparison against original PNG, with the same YUV conversion.
 check=subprocess.run(['ffmpeg','-hide_banner','-i',str(V/f'{label}-web.mp4'),'-framerate','30','-start_number',str(start),'-i',str(folder/'f%04d.png'),'-lavfi','[0:v]setpts=PTS-STARTPTS[a];[1:v]format=yuv420p,setpts=PTS-STARTPTS[b];[a][b]ssim','-frames:v','30','-f','null','-'],capture_output=True,text=True)
 (V/f'{label}-compression.log').write_text(check.stderr)
 ssim=re.findall(r'All:([0-9.]+)',check.stderr)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(V/f'{label}-web.mp4')],text=True))
 means=[];highlight=[]
 for f in frames:
  im=Image.open(f).convert('RGB');means.append(ImageStat.Stat(im.convert('L')).mean[0]);hist=im.convert('L').histogram();highlight.append(sum(hist[250:])/sum(hist))
 steps=[abs(b-a) for a,b in zip(means,means[1:])]
 rec=dict(label=label,title=title,start=start,end=start+29,frames=30,fps=30,duration=1.0,web_crf=24,web_bytes=(V/f'{label}-web.mp4').stat().st_size,ssim_vs_png=float(ssim[-1]) if ssim else None,probe=probe,mean_luma=means,max_adjacent_global_luma_step=max(steps),median_adjacent_global_luma_step=statistics.median(steps),highlight_fraction_range=[min(highlight),max(highlight)],temporal_note='Global luminance is a diagnostic only: camera motion changes the image. Consecutive-frame crops were inspected; real-time playback review remains pending because Computer Use could not verify the Windows browser URL.')
 results.append(rec)
 # Filmstrip including consecutive samples at the middle and widely spaced endpoints.
 strip=Image.new('RGB',(1440,6*290),'#eef1f4');draw=ImageDraw.Draw(strip)
 for row,idx in enumerate([0,6,13,14,15,29]):
  im=Image.open(frames[idx]);strip.paste(im.resize((512,288)),(0,row*290));crop=im.crop((700,260,1400,700));crop.thumbnail((700,288));strip.paste(crop,(540,row*290));draw.text((1260,row*290+12),frames[idx].stem,fill='black')
 strip.save(V/f'{label}-temporal.jpg',quality=92)
(V/'temporal-compression.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf8')
# All evidence, labels, and images correspond to actual scene-camera renders.
frames=[45,110,200,315,390,530,720,820];titles=['중국 하역 접점','중국 도시 · 항만','해상 전환','미국 도시 · 항만','미국 크레인 이동','트럭 인입','창고 입고 · 랙','창고 피킹 · 이동']
sheet=Image.new('RGB',(1280,4*390),'#edf0f4');d=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
 im=Image.open(V/'after'/f'f{f:04}.png');sheet.paste(im.resize((640,360)),((i%2)*640,(i//2)*390+25));d.text(((i%2)*640+12,(i//2)*390+6),f'CAM_MASTER / f{f:04} / Cycles 128',fill='black')
sheet.save(V/'styleframes-contact.jpg',quality=94)
for f in [110,315]:
 im=Image.open(V/'after'/f'f{f:04}.png');im.resize((1440,810)).save(V/f'hero-1440-f{f}.jpg',quality=94);im.resize((390,219)).save(V/f'hero-390-f{f}.jpg',quality=94)
options=''.join(f'<option value="{f}">{f:04} · {t}</option>' for f,t in zip(frames,titles))
videos=''.join(f'<article><h3>{title}</h3><p>프레임 {start}–{start+29} · 30fps · 1초 · 1920×1080</p><video id="{label}" controls muted loop playsinline preload="metadata" src="review/{label}-web.mp4"></video><p><a href="review/{label}-review.mp4">고품질 검토 영상</a> · <a href="review/{label}-web.mp4">웹 압축 영상</a> · <a href="review/{label}-temporal.jpg">연속 프레임</a></p></article>' for label,start,title in clips)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>PNPLINE · Material lookdev v001</title><style>body{font:16px/1.65 system-ui,sans-serif;margin:0;background:#101a25;color:#edf3f7}main{max-width:1440px;margin:auto;padding:36px 24px}h1{font-size:32px}p{color:#bbc9d5}a{color:#79d9ee}select,button{padding:10px;font:inherit}img,video{width:100%;display:block}article{margin:32px 0;padding:20px;background:#1b2937;border-radius:12px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}.label{font-weight:bold;padding:8px 0}.small{max-width:390px}code{word-break:break-all}label{margin-right:16px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><main><p>PNPLINE / BLENDER LOOK DEVELOPMENT / v001</p><h1>정교한 미니어처, 일관된 재료와 빛</h1><p>Cycles OptiX · AgX · 실제 CAM_MASTER · 0–989 / 30fps 보존</p><p>현재 결과 SHA256: <code>SHA</code></p><p>원본 형상·카메라·타이밍을 보존하고 재질, 조명, 월드, 색 관리를 변경했습니다. 전후 모두 동일 카메라·동일 프레임의 Cycles 렌더입니다. 원본은 저장하지 않고 렌더 엔진과 출력 품질만 검토용으로 맞췄습니다.</p><article><h2>동일 프레임 전후 비교</h2><select id="frame">OPTIONS</select><div class="pair"><div><div class="label">원본 재질·조명</div><img id="before" src="review/before/f0045.png"></div><div><div class="label">보강 결과</div><img id="after" src="review/after/f0045.png"></div></div><p>원본 크기로 확인하려면 이미지를 새 탭에서 여세요.</p></article><article><h2>1440px / 390px 표시 검토</h2><p>가로 영상의 축소 가독성을 검토합니다. 현재 배포 설정이 가리키는 웹페이지 파일은 없으므로, 실제 운영 페이지 합성 검증으로 표시하지 않습니다.</p><img src="review/hero-1440-f110.jpg"><div class="small"><img src="review/hero-390-f110.jpg"></div></article><h2>연속 구간 · 실제 속도</h2><p>각 구간은 원래 30fps로 재생됩니다. 1초 검토 구간이므로 반복 경계의 점프는 원본 영상의 컷이 아닙니다.</p>VIDEOS<article><h2>대표 스타일 프레임</h2><img src="review/styleframes-contact.jpg"></article><p><a href="README.md">설정 · 렌더 방법</a> · <a href="review/preservation-verification.json">990프레임 보존 검증</a> · <a href="review/material-manifest.json">재질 명세</a> · <a href="review/temporal-compression.json">영상/압축 측정</a></p></main><script>document.querySelector('#frame').addEventListener('change',e=>{let f=String(e.target.value).padStart(4,'0');for(let k of ['before','after'])document.getElementById(k).src=`review/${k}/f${f}.png`;});</script></html>'''
page=page.replace('OPTIONS',options).replace('VIDEOS',videos)
# Replace explicit hash token without modifying the SHA256 label.
page=page.replace('<code>SHA</code>','<code>'+sha(R/'pnpline-hero-material-v001.blend')+'</code>')
(R/'review.html').write_text(page,encoding='utf8')
print('PACKAGED_CLIPS',len(results),flush=True)
