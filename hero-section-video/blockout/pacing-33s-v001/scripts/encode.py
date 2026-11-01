"""Encode exactly990 independently rendered frames at30fps and verify the media."""
import hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
frames=R/'preview/frames'
expected=[frames/f'f{i:04}.png' for i in range(990)]
assert all(p.exists() for p in expected),'Render is incomplete'
assert len(list(frames.glob('f*.png')))==990
meta=[json.loads((R/'review'/name).read_text()) for name in ['render-0-494.json','render-495-989.json']]
assert len({m['blend_sha256'] for m in meta})==1
assert all(m['fps']==30 and m['resolution']==[1280,720] for m in meta)
out=R/'preview/pnpline-33s-30fps-v001.mp4';assert not out.exists()
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-framerate','30','-start_number','0','-i',str(frames/'f%04d.png'),'-frames:v','990','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)]))
v=probe['streams'][0]
assert v['r_frame_rate']==v['avg_frame_rate']=='30/1'
assert int(v['nb_frames'])==int(v['nb_read_frames'])==990
assert abs(float(probe['format']['duration'])-33)<.0001
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
digest=hashlib.sha256(out.read_bytes()).hexdigest()
(R/'review/video.json').write_text(json.dumps({'blend_sha256':meta[0]['blend_sha256'],'video_sha256':digest,'probe':probe},indent=2))
print(out,'30fps,990frames,33seconds; full decode passed')
