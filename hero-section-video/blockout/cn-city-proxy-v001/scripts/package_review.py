"""Encode exact frame ranges; metadata and complete decode, then local review UI."""
import json,hashlib,subprocess,platform
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
commands=[];media={}
def run(cmd,log):
 with (R/'review/logs'/log).open('w',encoding='utf8') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 commands.append({'command':cmd,'exit_code':r.returncode,'log':'review/logs/'+log});r.check_returncode()
for version in ['before','after']:
 for kind,start,count in [('connection',84,397),('s2',96,121)]:
  out=R/'preview'/f'{version}-{kind}.mp4'
  if not out.exists():run(['ffmpeg','-v','warning','-framerate','12','-start_number',str(start),'-i',str(R/'preview'/f'{version}-frames'/'%04d.png'),'-frames:v',str(count),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],out.stem+'-encode.log')
  p=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)]));stream=p['streams'][0]
  assert int(stream['nb_read_frames'])==count and stream['avg_frame_rate']=='12/1'
  assert stream['width']==960 and stream['height']==540 and abs(float(p['format']['duration'])-count/12)<.001
  run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],out.stem+'-decode.log')
  media[out.name]={'sha256':sha(out),'frames':[start,start+count-1],'frame_count':count,'fps':12,'seconds':float(p['format']['duration']),'ffprobe':p,'full_decode':'PASS'}
(R/'review/media.json').write_text(json.dumps(media,indent=2))
(R/'review/media-commands.json').write_text(json.dumps(commands,indent=2))
frames=[96,124,148,180,216,278,330,450,456]
im=Image.new('RGB',(960,300*len(frames)),(235,237,238));d=ImageDraw.Draw(im)
for i,f in enumerate(frames):
 d.text((8,i*300+5),f'f{f} BEFORE                                      AFTER (same CAM_MASTER)',fill=(10,20,25))
 for j,v in enumerate(['before','after']):
  with Image.open(R/'preview'/f'{v}-frames'/f'{f:04}.png') as src:im.paste(src.resize((480,270)),(j*480,i*300+25))
im.save(R/'review/comparison.jpg',quality=93)
manifest={'date':'2026-10-28','branch':'main','head':'4993e2f5ce299e7e119eb7b57a4098d7922a7c1f','source_path':str(R.parent/'s5-integration-v001/master-s5-integration-v001.blend'),'source_sha256':sha(R/'inputs/base.blend'),'reference_sha256':sha(R/'inputs/reference.png'),'spec_sha256':sha(R/'inputs/task-spec.md'),'model_selector':'unknown','reasoning_setting':'unknown','environment':platform.platform(),'blender':'5.1.0 adfe2921d5f3','output':str(R/'master-cn-city-proxy-v001.blend'),'output_sha256':sha(R/'master-cn-city-proxy-v001.blend'),'source_unchanged':sha(R/'inputs/base.blend')==sha(R.parent/'s5-integration-v001/master-s5-integration-v001.blend')}
(R/'inputs/manifest.json').write_text(json.dumps(manifest,indent=2))
print('MEDIA_VERIFIED',list(media))
