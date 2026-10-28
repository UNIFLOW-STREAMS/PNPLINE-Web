import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists();candidate=bpy.data.filepath
bpy.ops.wm.open_mainfile(filepath=str(R/'review/layout-proposal-v021.blend'));original={n:bpy.data.objects[n].location.copy()for n in ['SF_HIGHRISE_'+str(i)for i in range(8,14)]}
bpy.ops.wm.open_mainfile(filepath=candidate)
for name,p in original.items():bpy.data.objects[name].location=p+Vector((0,2.05,0))
bpy.context.scene.frame_set(156);bpy.context.view_layer.update()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA'
ver=out.stem.rsplit('-',1)[-1];(R/f'review/title-arc-{ver}-config.json').write_text((R/'review/title-arc-v026-config.json').read_text())
bpy.ops.wm.save_as_mainfile(filepath=str(out))
