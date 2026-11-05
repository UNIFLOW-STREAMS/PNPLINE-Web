import bpy,json,hashlib,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];H=R.parents[1];S=bpy.context.scene
sys.path.insert(0,str(R.parent/'hero-section-ab-v001/scripts'))
from state import sha,hashed,curves
source=bpy.data.filepath;sourcehash=sha(source);actions={a.name:hashed(curves(a)) for a in bpy.data.actions};timing=[S.frame_start,S.frame_end,S.render.fps,S.render.fps_base]
cfg=json.loads((H.parent/'output/scroll-previz-pacing-v001/pacing.json').read_text());cfg.update(version='hero-section-b-scroll-v001',media='assets/hero-section-b-previz.mp4',poster='assets/poster.jpg',blenderSource='hero-section-B.blend',application='web-only; source animation unchanged',previewRenderer='BLENDER_WORKBENCH')
(R/'pacing.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
for name,body in [('PNPLINE_SCROLL_PACING.json',json.dumps(cfg,ensure_ascii=False,indent=2)),('PNPLINE_SCROLL_README.md','Scroll pacing is applied in the web player only. 13 viewport heights across S1-S7. Animation remains 0-989 at 30 fps. Do not bake this map into source animation or apply a second time to an already retimed video. Configuration is also exported beside this blend.')]:
 t=bpy.data.texts.get(name) or bpy.data.texts.new(name);t.clear();t.write(body)
S['scroll_world_mode']='web_only';S['scroll_world_total_viewport_heights']=sum(x['scrollVh'] for x in cfg['sections']);S['scroll_world_config']='PNPLINE_SCROLL_PACING.json';S['scroll_world_source_sha256']=sourcehash
assert actions=={a.name:hashed(curves(a)) for a in bpy.data.actions};assert timing==[S.frame_start,S.frame_end,S.render.fps,S.render.fps_base]
bpy.context.preferences.filepaths.save_version=0;out=R/'hero-section-B.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'verification.json').write_text(json.dumps(dict(source=source,source_sha256=sourcehash,file=str(out),sha256=sha(out),animation_unchanged=True,action_count=len(actions),timing=timing,camera=S.camera.name,application='web-only',A_unchanged_sha256=sha(H/'hero-section-A.blend')),indent=2));print('SAVED B metadata only',flush=True)
# Preview settings are not saved into the production blend.
S.render.engine='BLENDER_WORKBENCH';S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100;S.render.use_border=False;S.display.shading.light='STUDIO';S.display.shading.color_type='MATERIAL';S.display.shading.show_shadows=True;S.display.shading.show_cavity=True;S.display.shading.cavity_type='BOTH';S.display.shading.show_specular_highlight=True;S.display.shading.background_type='WORLD';S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8';S.render.image_settings.compression=15
dest=R/'frames';dest.mkdir(exist_ok=True);S.frame_start=0;S.frame_end=989;S.frame_step=1;S.render.filepath=str(dest/'f')
def progress(scene,*args):
 if scene.frame_current%30==0:print('FRAME',scene.frame_current,flush=True)
bpy.app.handlers.render_post.append(progress);bpy.ops.render.render(animation=True)
print('PREVIEW COMPLETE',flush=True)
