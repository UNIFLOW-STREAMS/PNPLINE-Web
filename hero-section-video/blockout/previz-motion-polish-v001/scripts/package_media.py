"""Verify frame provenance, encode without additional speed multipliers."""
from pathlib import Path
import hashlib,json,subprocess,sys,shutil
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encode(folder,fps,out,count):
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(fps),'-start_number','0','-i',str(folder/'%04d.png'),'-frames:v',str(count),'-c:v','libx264','-crf','20','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)]))
 st=probe['streams'][0];assert int(st['nb_read_frames'])==count and st['r_frame_rate']==f'{fps}/1'
 assert abs(float(probe['format']['duration'])-count/fps)<.002
 subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
 return {'path':str(out),'sha256':sha(out),'frames':count,'fps':fps,'duration':float(probe['format']['duration']),'decode':'PASS','probe':probe}
preview=R/'preview';preview.mkdir(exist_ok=True)
for variant in sys.argv[1:] or ['baseline','A','B']:
 if variant=='baseline':
  base=R.parent/'previz-s1-s7-2x-v001';rec=json.loads((base/'render-record.json').read_text());folder=base/'frames'
  for item in rec['images']:
   assert sha(folder/f"{item['frame']:04d}.png")==item['sha256']
  assert sha(rec['source'])==rec['source_sha256'] and sha(rec['video_path'])==rec['video_sha256']
  result=encode(folder,12,preview/'source-12fps.mp4',1393)
  shutil.copy2(rec['video_path'],preview/'existing-24fps.mp4')
  result['baseline_render_record_sha256']=sha(base/'render-record.json');result['existing24_sha256']=sha(preview/'existing-24fps.mp4')
 else:
  rec=json.loads((R/f'render-record-{variant}.json').read_text());assert rec['status']=='complete' and sha(rec['blend_path'])==rec['blend_sha256']
  folder=Path(rec['output_dir'])
  for item in rec['images']:assert sha(folder/f"{item['frame']:04d}.png")==item['sha256']
  result=encode(folder,24,preview/f'candidate-{variant}.mp4',rec['frame_end']+1)
  result['blend_sha256']=rec['blend_sha256'];result['render_record_sha256']=sha(R/f'render-record-{variant}.json')
 (R/'review'/f'media-{variant}.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('ENCODED',variant,result['duration'],flush=True)

