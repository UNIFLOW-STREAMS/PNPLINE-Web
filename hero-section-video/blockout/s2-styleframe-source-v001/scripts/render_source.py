import bpy,sys,runpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene;s.frame_set(156)
assert s.name=='PNPLINE_MASTER_v005' and s.camera.name=='CAM_MASTER' and s.camera.data.lens==40
meta={'scene':s.name,'camera':s.camera.name,'frame':156,'fps':s.render.fps,'fps_base':s.render.fps_base,'lens_mm':s.camera.data.lens,'frame_range':[s.frame_start,s.frame_end],'camera_matrix':list(map(list,s.camera.matrix_world)),'blender':bpy.app.version_string}
s.render.image_settings.color_mode='RGB'
(R/'scene-metadata.json').write_text(json.dumps(meta,indent=2))
runpy.run_path(str(R.parent/'cn-city-proxy-v001/scripts/render.py'),run_name='__main__')
