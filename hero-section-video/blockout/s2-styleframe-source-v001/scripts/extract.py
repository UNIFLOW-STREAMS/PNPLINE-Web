import subprocess,json,hashlib,shutil
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];repo=R.parents[2]
source=R.parent/'s2-city-reveal-china-v001/master-s2-city-reveal-china-v001.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(source);assert before=='b043cfbbc048cfeb90d16808852424ddaaf5c16c1dd60057fe98d73cf18132d2'
final=R/'S2_city_CHINA_f0156_1920x1080.png';assert not final.exists()
commands=[]
for label,width in [('full',1920),('qa',960),('repeat',1920)]:
 folder=R/'verification'/label;folder.mkdir(parents=True,exist_ok=False)
 cmd=['C:/Program Files/Blender Foundation/Blender 5.1/blender.exe','--background',str(source),'--python-exit-code','1','--python',str(R/'scripts/render_source.py'),'--','--output',str(folder),'--frames','156','--width',str(width)]
 with (folder/'run.log').open('w',encoding='utf-8') as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 commands.append({'argv':cmd,'exit_code':p.returncode});assert p.returncode==0
shutil.copyfile(R/'verification/full/0156.png',final)
im=Image.open(final);assert im.size==(1920,1080) and im.mode=='RGB' and im.format=='PNG';im.load()
repeat=Image.open(R/'verification/repeat/0156.png');assert im.tobytes()==repeat.tobytes()
qa=Image.open(R/'verification/qa/0156.png').convert('RGB');old=Image.open(R.parent/'s2-city-reveal-china-v001/preview/final-frames/0156.png').convert('RGB');assert qa.tobytes()==old.tobytes()
after=sha(source);assert before==after
git=lambda *a:subprocess.check_output(['git','-c','safe.directory=F:/pnpline-landing','-C','F:/pnpline-landing',*a],text=True).strip()
manifest={'source':str(source),'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':True,'branch':git('branch','--show-current'),'commit':git('rev-parse','HEAD'),'scene_metadata':json.loads((R/'scene-metadata.json').read_text()),'engine':'BLENDER_WORKBENCH','lighting':'STUDIO / MATERIAL / shadows and cavity / WORLD(.18,.18,.18), reused previous render.py','final_png':str(final),'size':list(im.size),'mode':im.mode,'sha256':sha(final),'commands':commands,'qa_960_rgb_exact':True,'repeat_1920_rgb_exact':True,'gui':'Existing source GUI has unsaved asterisk; preserved without saving/closing. Explicitly specified on-disk hash used. Unsaved GUI content not compared.','model_effort':'Not changed or independently verified this task','visual_review':'pending','git_status_after':git('status','--short')}
(R/'source-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps({'path':str(final),'sha256':sha(final),'source_unchanged':True,'qa_exact':True,'repeat_exact':True}))
