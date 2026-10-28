import json,shutil,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];review=R/'review';preview=R/'preview';preview.mkdir(exist_ok=True);before=review/'before';before.mkdir(exist_ok=True)
frames=list(range(0,673,3));src=R.parent/'route-b-a-side-v001/review/city-final'
for f in frames:
 assert (review/'after-final'/f'f{f:04d}.png').exists(),f
 shutil.copy2(src/f'f{f:04d}.png',before/f'f{f:04d}.png')
for label in ['before','after']:
 files=[review/('after-final' if label=='after' else label)/f'f{f:04d}.png' for f in frames];lst=preview/f'{label}.txt'
 lst.write_text(''.join(f"file '{p.as_posix()}'\nduration 0.25\n" for p in files)+f"file '{files[-1].as_posix()}'\n",encoding='utf-8')
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(lst),'-t',str(673/12),'-r','24','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(preview/f'{label}.mp4')],check=True)
 probes=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration','-of','json',str(preview/f'{label}.mp4')],text=True))
 (preview/f'{label}-metadata.json').write_text(json.dumps({'frames':frames,'sample_step':3,'source_fps':12,'encoded_fps':24,'source_interval':[0,672],'ffprobe':probes,'file_sha256':hashlib.sha256((preview/f'{label}.mp4').read_bytes()).hexdigest()},indent=2))
chosen=[72,156,222,450,477,672];im=Image.new('RGB',(1280,390*len(chosen)),(25,25,25));draw=ImageDraw.Draw(im)
for i,f in enumerate(chosen):
 for j,label in enumerate(['before','after']):
  im.paste(Image.open(review/('after-final' if label=='after' else label)/f'f{f:04d}.png'),(640*j,390*i));draw.text((640*j+16,390*i+365),f'{label.upper()}  f{f}',fill='white')
im.save(review/'before-after.jpg')
print('REVIEW_PACKAGED',len(frames))
