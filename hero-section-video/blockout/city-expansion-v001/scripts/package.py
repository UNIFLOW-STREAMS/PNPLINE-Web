"""Package only complete, hash-matched 30fps renders of the accepted master."""
import hashlib,json,re,subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
master=R/'pnpline-city-expansion-v001.blend'
sha=hashlib.sha256(master.read_bytes()).hexdigest()
build=json.loads((R/'review/build.json').read_text())
geometry=json.loads((R/'review/geometry.json').read_text())
preservation=json.loads((R/'review/preservation.json').read_text())
assert geometry['passed'] and preservation['passed']
assert preservation['output_sha256']==sha
frames=R/'preview/frames'
assert sorted(p.name for p in frames.glob('f*.png'))==[f'f{f:04}.png' for f in range(990)]
for start,end in [(0,494),(495,989)]:
 report=json.loads((R/f'review/render-{start}-{end}.json').read_text())
 assert report['sha256']==sha and report['frames']==list(range(start,end+1))
 assert report['fps']==30 and report['resolution']==[1280,720]
video=R/'preview/pnpline-city-expansion-v001.mp4'
subprocess.run(['ffmpeg','-hide_banner','-y','-loglevel','error','-framerate','30','-start_number','0','-i',str(frames/'f%04d.png'),'-frames:v','990','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames,duration','-of','json',str(video)],text=True))['streams'][0]
assert probe['nb_read_frames']=='990' and probe['r_frame_rate']=='30/1' and abs(float(probe['duration'])-33)<.001
assert [probe['width'],probe['height']]==[1280,720]
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
timings={}
for a,b in [(0,494),(495,989)]:
 lines=(R/f'review/render-{a}-{b}.log').read_text(errors='replace').splitlines()
 stamps=[]
 for line in lines:
  if 'Saved:' not in line:continue
  m=re.match(r'(\d+):(\d+\.\d+)',line)
  if m:stamps.append(int(m[1])*60+float(m[2]))
 timings[f'{a}-{b}']={'rendered_frames':len(stamps),'elapsed_seconds':stamps[-1] if stamps else None}
paths=[master,video,R/'review.html',R/'README.md']+list((R/'scripts').glob('*.py'))+[R/'scripts/dense_layout.json']+[R/'preview'/f'{n}.png' for n in ['overview-top','overview-oblique','chrysler-detail','pyramid-detail','willis-detail','bridge-detail']]
files=[{'path':str(p.relative_to(R)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
delivery={'version':'city-expansion-v001','source':build['source'],'source_sha256':build['source_sha256'],'master_sha256':sha,'video':probe,'geometry_passed':True,'preservation_passed':True,'protected_original_objects':preservation['protected_original_objects'],'camera_exact_frames':preservation['camera_sample_count'],'buildings':len(build['buildings']),'landmarks':len(build['landmarks']),'surrounding_buildings':len(build['buildings'])-len(build['landmarks']),'trees':build['tree_count'],'new_objects':build['new_objects'],'new_vertices':build['new_vertices'],'new_polygons':build['new_polygons'],'render_backend':'Blender 5.1 WORKBENCH','gpu_timing':'not measured','render_wall_time':timings,'files':files}
(R/'delivery.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'master_sha256':sha,'video':probe,'files':len(files)},indent=2))
