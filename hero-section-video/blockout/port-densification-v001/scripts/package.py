"""Package a complete 33-second preview only after all final-scene audits pass."""
import hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
master=R/'pnpline-port-densification-v001.blend';sha=hashlib.sha256(master.read_bytes()).hexdigest()
build=json.loads((R/'review/build.json').read_text());assert build['output_sha256']==sha
reports={}
for name,field in [('preservation','output_sha256'),('clearance','sha256'),('static-clearance','sha256'),('camera-passage','sha256')]:
 report=json.loads((R/'review'/f'{name}.json').read_text());assert report['passed'] and report[field]==sha,name
 reports[name]=report
frames=R/'preview/final-frames'
assert sorted(p.name for p in frames.glob('f*.png'))==[f'f{f:04}.png' for f in range(990)]
for start,end in [(0,494),(495,989)]:
 report=json.loads((R/f'review/render-{start}-{end}.json').read_text())
 assert report['sha256']==sha and report['frames']==list(range(start,end+1))
 assert report['fps']==30 and report['resolution']==[1280,720]
video=R/'preview/pnpline-port-densification-v001.mp4'
subprocess.run(['ffmpeg','-hide_banner','-y','-loglevel','error','-framerate','30','-start_number','0','-i',str(frames/'f%04d.png'),'-frames:v','990','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames,duration','-of','json',str(video)],text=True))['streams'][0]
assert probe['nb_read_frames']=='990' and probe['r_frame_rate']=='30/1' and abs(float(probe['duration'])-33)<.001
assert [probe['width'],probe['height']]==[1280,720]
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
paths=[master,video,R/'review.html',R/'README.md']+list((R/'scripts').glob('*.py'))+list((R/'preview').glob('*.png'))+list((R/'review').glob('*.json'))+list((R/'review/views').glob('*.png'))
files=[{'path':str(p.relative_to(R)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
delivery={'version':'port-densification-v001','source':build['source'],'source_sha256':build['source_sha256'],'master_sha256':sha,'video':probe,
 'preservation_passed':True,'moving_clearance_passed':True,'static_clearance_passed':True,'camera_passage_passed':True,
 'protected_original_objects':reports['preservation']['protected_original_objects'],'exact_camera_frames':990,
 'new_containers':build['new_containers'],'new_stack_blocks':build['new_stack_blocks'],'additional_cranes':2,'enhanced_existing_cranes':1,
 'new_objects':build['new_objects'],'new_vertices':build['new_vertices'],'new_polygons':build['new_polygons'],
 'render_backend':'Blender 5.1 WORKBENCH','gpu_timing':'not measured','files':files}
(R/'delivery.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'master_sha256':sha,'video':probe,'files':len(files)},indent=2))
