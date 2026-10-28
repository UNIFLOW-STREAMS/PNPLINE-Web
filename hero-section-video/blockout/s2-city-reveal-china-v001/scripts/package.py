import json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
records=[]
for name in ['source','titlebase','limited','final']:
 folder=R/'preview'/f'{name}-frames'
 if len(list(folder.glob('*.png')))!=397:continue
 out=R/'preview'/f'{name}.mp4'
 cmd=['ffmpeg','-y','-v','error','-framerate','12','-start_number','84','-i',str(folder/'%04d.png'),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
 p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 probe=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,duration','-of','json',str(out)],capture_output=True,text=True,check=True)
 decode=subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],capture_output=True,text=True)
 records.append({'name':name,'command':cmd,'exit_code':p.returncode,'decode_exit':decode.returncode,'probe':json.loads(probe.stdout),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
(R/'review/media.json').write_text(json.dumps(records,indent=2))
frames=[96,124,144,156,170,180,192,204,216,240,278,330]
out=Image.new('RGB',(960,180*len(frames)//3),(30,30,30));draw=ImageDraw.Draw(out)
for i,f in enumerate(frames):
 im=Image.open(R/('preview/final-frames' if (R/'preview/final-frames').exists() else 'preview/limited-frames')/f'{f:04}.png').resize((320,180));out.paste(im,((i%3)*320,(i//3)*180));draw.text(((i%3)*320+8,(i//3)*180+8),str(f),fill='white',stroke_width=2,stroke_fill='black')
out.save(R/'review/sequence.png')
manifest={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in (R/'inputs').iterdir() if p.is_file() and p.name!='manifest.json'}
(R/'inputs/manifest.json').write_text(json.dumps(manifest,indent=2))
