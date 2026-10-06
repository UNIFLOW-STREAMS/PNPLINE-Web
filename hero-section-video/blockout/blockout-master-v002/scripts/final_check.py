import json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
B='C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={f:Image.open(ROOT/'review'/f'camera-f{f:04}.png').convert('RGB').copy() for f in [0,96]}
with (ROOT/'logs/reopen-final.log').open('w',encoding='utf-8') as log:
    subprocess.run([B,'--background','--factory-startup',str(ROOT/'master-v002.blend'),'--python-exit-code','1','--python',str(ROOT/'scripts/render_s1.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
pixels={f:ImageChops.difference(before[f],Image.open(ROOT/'review'/f'camera-f{f:04}.png').convert('RGB')).getbbox() is None for f in before}
assert all(pixels.values()),pixels
reopen={'frame0_pixels_identical':pixels[0],'frame96_pixels_identical':pixels[96],'note':'Compare RGB pixels; PNG bytes contain changing render metadata. Initial byte-hash comparison was not the pixel test.'}
(ROOT/'review/reopen-check.json').write_text(json.dumps(reopen,indent=2),encoding='utf-8')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(ROOT/'preview/master-v002.mp4')],text=True))
v=next(x for x in probe['streams'] if x['codec_type']=='video');assert int(v['nb_read_frames'])==1393
base=sha(ROOT/'inputs/base-user-saved-v001.blend')
assert sha(ROOT.parent/'blockout-master-v001/master-v001.blend')==base,'Original saved file changed'
result={'reopen':reopen,'video':{'frames':int(v['nb_read_frames']),'fps':v['r_frame_rate'],'duration':probe['format']['duration']},'original_file_preserved':True,'base_sha256':base,'tests':json.loads((ROOT/'logs/test-result.json').read_text()),'s1_tests':json.loads((ROOT/'logs/s1-test-result.json').read_text())}
(ROOT/'review/final-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1280,390),(235,239,241));d=ImageDraw.Draw(sheet)
for x,f,label in [(0,0,'FRAME 0 / LOW ANGLE'),(640,96,'FRAME 96 / HIGH ANGLE')]:
    sheet.paste(Image.open(ROOT/'review'/f'camera-f{f:04}.png').resize((640,360)),(x,30));d.text((x+12,10),label,fill=(25,35,45))
sheet.save(ROOT/'review/S1-before-after.png')
print(json.dumps(result,indent=2))
