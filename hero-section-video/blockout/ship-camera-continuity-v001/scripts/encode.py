"""Encode the ship-camera edit while preserving the accepted truck-camera edit."""
import hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text())
truck=(R/cfg['source']).resolve().parent
truck_cfg=json.loads((truck/'config.json').read_text())
base=(truck/truck_cfg['source']).resolve().parent
proof=json.loads((R/'review/preservation.json').read_text())
truck_proof=json.loads((truck/'review/preservation.json').read_text())
current_hash=hashlib.sha256((R/cfg['output']).read_bytes()).hexdigest()
assert proof['passed'] and proof['output_sha256']==current_hash
assert truck_proof['passed'] and truck_proof['output_sha256']==cfg['source_sha256']
assert hashlib.sha256((R/cfg['source']).resolve().read_bytes()).hexdigest()==cfg['source_sha256']
assert hashlib.sha256((truck/truck_cfg['source']).resolve().read_bytes()).hexdigest()==truck_cfg['source_sha256']
base_meta=[json.loads((base/'review'/name).read_text()) for name in ('render-0-494.json','render-495-989.json')]
truck_meta=[json.loads((truck/'review'/name).read_text()) for name in ('render-441-529.json','render-530-619.json')]
new_meta=[json.loads((R/'review'/name).read_text()) for name in ('render-211-279.json','render-280-349.json')]
assert all(m['blend_sha256']==truck_cfg['source_sha256'] for m in base_meta)
assert all(m['sha256']==cfg['source_sha256'] for m in truck_meta)
assert all(m['sha256']==current_hash for m in new_meta)
assert all(m['fps']==30 and m['resolution']==[1280,720] for m in base_meta+truck_meta+new_meta)
assert sorted(f for m in new_meta for f in m['frames'])==list(range(211,350))

def frame(f,before=False):
 folder=base
 if 440<f<620:folder=truck
 if not before and 210<f<350:folder=R
 return folder/'preview/frames'/f'f{f:04}.png'

def encode(name,frames):
 paths=list(frames);assert all(p.is_file() for p in paths)
 listing=R/'review'/(name+'.ffconcat')
 listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{p.as_posix()}'\noption framerate 30\nduration 0.03333333333333333\n" for p in paths),encoding='utf-8')
 out=R/'preview'/(name+'.mp4');assert not out.exists()
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-r','30','-frames:v',str(len(paths)),'-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)]))
 v=probe['streams'][0]
 assert v['r_frame_rate']==v['avg_frame_rate']=='30/1'
 assert int(v['nb_frames'])==int(v['nb_read_frames'])==len(paths)
 assert abs(float(probe['format']['duration'])-len(paths)/30)<.001
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
 return {'file':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'frame_count':len(paths),'fps':30,'duration':float(probe['format']['duration']),'full_decode_passed':True}

reports=[encode('pnpline-33s-ship-camera-v001',(frame(f) for f in range(990))),
 encode('before-f200-f360',(frame(f,True) for f in range(200,361))),
 encode('after-f200-f360',(frame(f) for f in range(200,361)))]
(R/'review/video.json').write_text(json.dumps({'blend_sha256':current_hash,'videos':reports,'rerendered_frames':[211,349],
 'verified_reused_frames':{'pacing':[[0,210],[350,440],[620,989]],'truck_camera':[[441,619]]}},indent=2))
print(json.dumps(reports,indent=2),flush=True)
