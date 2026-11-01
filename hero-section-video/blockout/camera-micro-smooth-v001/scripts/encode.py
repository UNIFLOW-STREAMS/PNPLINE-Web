"""Render replacement is limited to f331..f365; every other frame is reused."""
import hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text())
ship=(R/cfg['source']).resolve().parent;ship_cfg=json.loads((ship/'config.json').read_text())
truck=(ship/ship_cfg['source']).resolve().parent;truck_cfg=json.loads((truck/'config.json').read_text())
base=(truck/truck_cfg['source']).resolve().parent
proof=json.loads((R/'review/preservation.json').read_text());digest=hashlib.sha256((R/cfg['output']).read_bytes()).hexdigest()
assert proof['passed'] and proof['output_sha256']==digest
for folder,config in [(R,cfg),(ship,ship_cfg),(truck,truck_cfg)]:
 assert hashlib.sha256((folder/config['source']).resolve().read_bytes()).hexdigest()==config['source_sha256']
for folder,expected in [(ship,cfg['source_sha256']),(truck,ship_cfg['source_sha256'])]:
 p=json.loads((folder/'review/preservation.json').read_text());assert p['passed'] and p['output_sha256']==expected
groups=[(base,['render-0-494.json','render-495-989.json'],'blend_sha256',truck_cfg['source_sha256']),
 (truck,['render-441-529.json','render-530-619.json'],'sha256',ship_cfg['source_sha256']),
 (ship,['render-211-279.json','render-280-349.json'],'sha256',cfg['source_sha256']),
 (R,['render-331-365.json'],'sha256',digest)]
for folder,names,key,expected in groups:
 for name in names:
  m=json.loads((folder/'review'/name).read_text())
  assert m[key]==expected and m['fps']==30 and m['resolution']==[1280,720]
assert json.loads((R/'review/render-331-365.json').read_text())['frames']==list(range(331,366))

def frame(f,before=False):
 folder=base
 if 210<f<350:folder=ship
 if 440<f<620:folder=truck
 if not before and 330<f<366:folder=R
 return folder/'preview/frames'/f'f{f:04}.png'

def encode(name,frames):
 paths=list(frames);assert all(p.is_file() for p in paths)
 listing=R/'review'/(name+'.ffconcat')
 listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{p.as_posix()}'\noption framerate 30\nduration 0.03333333333333333\n" for p in paths),encoding='utf-8')
 out=R/'preview'/(name+'.mp4');assert not out.exists()
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-r','30','-frames:v',str(len(paths)),'-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)]));v=probe['streams'][0]
 assert v['r_frame_rate']==v['avg_frame_rate']=='30/1'
 assert int(v['nb_frames'])==int(v['nb_read_frames'])==len(paths)
 assert abs(float(probe['format']['duration'])-len(paths)/30)<.001
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
 return {'file':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'frame_count':len(paths),'fps':30,'duration':float(probe['format']['duration']),'full_decode_passed':True}
reports=[encode('pnpline-33s-camera-micro-smooth-v001',(frame(f) for f in range(990))),
 encode('before-f330-f366',(frame(f,True) for f in range(330,367))),
 encode('after-f330-f366',(frame(f) for f in range(330,367)))]
(R/'review/video.json').write_text(json.dumps({'blend_sha256':digest,'videos':reports,'rerendered_frames':[331,365],
 'unchanged_frames':[[0,330],[366,989]],'reused_frame_count':955},indent=2))
print(json.dumps(reports,indent=2),flush=True)
