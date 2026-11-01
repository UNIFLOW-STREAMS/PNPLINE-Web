import bpy,sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from state import sha,snapshot,presentation,hashed
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;label=sys.argv[-1]
record=json.loads((R/'build-verification.json').read_text())[label];source=json.loads((R/'audit'/('source-'+label+'.json')).read_text())
assert sha(bpy.data.filepath)==record['sha256']
verification_path=R/'audit'/f'final-{label}-verification.json'
if '--render-only' not in sys.argv:
 now=snapshot();present=presentation()
 checks={k:hashed(now[k])==hashed(source['snapshot'][k]) for k in ['objects','geometry','non_dof_actions','slots','materials','camera_990','timing']}
 checks['dof_990_exact']=hashed(now['dof_990'])==record['dof_990_hash'];checks['presentation_exact']=hashed(present)==record['presentation_hash']
 assert all(checks.values()),checks
 verification_path.write_text(json.dumps(dict(checks=checks,passed=True,file=bpy.data.filepath,sha256=record['sha256']),indent=2));print('REOPEN VERIFIED',label,'990 frames',flush=True)
else:
 verification=json.loads(verification_path.read_text());assert verification['passed'] and verification['sha256']==record['sha256']
if '--verify-only' in sys.argv:sys.exit(0)
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=40;S.cycles.use_denoising=True;S.cycles.denoiser='OPENIMAGEDENOISE';S.cycles.seed=29;S.cycles.use_animated_seed=False;S.cycles.adaptive_min_samples=32;S.cycles.adaptive_threshold=.02;S.render.use_persistent_data=True;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.use_border=False;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8'
dest=R/'review'/label;dest.mkdir(parents=True,exist_ok=True);stats=[]
for f in [32,132,200,332,630,842]:
 S.frame_set(f);S.render.filepath=str(dest/f'f{f:04d}.png');start=time.time();bpy.ops.render.render(write_still=True);stats.append(dict(frame=f,seconds=round(time.time()-start,3)));(dest/'render.json').write_text(json.dumps(stats,indent=2));print('RENDER',label,f,stats[-1]['seconds'],flush=True)
