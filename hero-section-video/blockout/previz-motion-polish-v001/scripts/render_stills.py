import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from motion import TimeMap
cfg=json.loads((R/'config.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
frames=sorted(set(cfg['storyboard_source_frames']+[0,95,96,215,216,455,456,647,648,649,700.5450141107419,708.75,776.5,899,900,1199,1200,1392]))
for variant in ['source','A','B']:
 path=R/'inputs/source.blend' if variant=='source' else R/f'master-motion-polish-{variant}.blend'
 if variant!='source':
  validation=json.loads((R/'review'/f'validation-{variant}.json').read_text());assert validation['pass_all'] and validation['blend_sha256']==sha(path)
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_border=False
 s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
 folder=R/'review/stills'/variant;folder.mkdir(parents=True,exist_ok=True);m=TimeMap(1392,cfg['easing'],cfg['compression_B'] if variant=='B' else []);rows=[]
 for f in frames:
  t=f if variant=='source' else m.forward(f);s.frame_set(int(t),subframe=t%1);out=folder/f'source-{f:g}.png';s.render.filepath=str(out);bpy.ops.render.render(write_still=True);rows.append({'source_frame':f,'output_frame':t,'path':str(out),'sha256':sha(out)})
 (R/'review'/f'stills-{variant}.json').write_text(json.dumps({'blend_sha256':sha(path),'script_sha256':sha(__file__),'images':rows},indent=2))
