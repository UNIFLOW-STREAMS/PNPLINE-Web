"""Encode contiguous review chunks only after exact-frame/hash verification."""
from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[1]
model=R/'candidate-warehouse-v008.blend';sha=hashlib.sha256(model.read_bytes()).hexdigest()
expected=[('a',744,911),('b',912,1079),('c',1080,1248)]
all_frames=[];parts=[]
for part,first,last in expected:
 folder=R/'preview'/f'warehouse-v008-{part}';meta=json.loads((folder/'metadata.json').read_text())
 frames=list(range(first,last+1));assert meta['sha256']==sha and meta['frames']==frames and meta['fps']==12
 assert sorted(p.name for p in folder.glob('f*.png'))==[f'f{f:04d}.png' for f in frames]
 all_frames+=frames;out=R/'preview'/f'warehouse-v008-{part}.mp4';assert not out.exists()
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-n','-framerate','12','-start_number',str(first),'-i',str(folder/'f%04d.png'),'-frames:v',str(len(frames)),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
 parts.append(out.name)
assert all_frames==list(range(744,1249))
listing=R/'preview/concat-v008.txt';listing.write_text(''.join(f"file '{name}'\n" for name in parts))
final=R/'preview/warehouse-v008.mp4';assert not final.exists()
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-n','-f','concat','-safe','1','-i',str(listing),'-c','copy','-movflags','+faststart',str(final)],check=True)
report={'source_sha256':sha,'frames':all_frames,'parts':parts,'videos':{}}
for filename in ['baseline-v010.mp4','warehouse-v008.mp4']:
 path=R/'preview'/filename
 raw=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,r_frame_rate,width,height','-show_entries','format=duration','-of','json',str(path)],text=True)
 probe=json.loads(raw);stream=probe['streams'][0];assert int(stream['nb_frames'])==505 and stream['r_frame_rate']=='12/1'
 assert stream['width']==640 and stream['height']==360 and abs(float(probe['format']['duration'])-505/12)<.001
 subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True)
 report['videos'][filename]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'probe':probe}
(R/'review/video-verification.json').write_text(json.dumps(report,indent=2))
print('Verified and encoded 505 contiguous frames at 12fps; both videos decode without errors.')
