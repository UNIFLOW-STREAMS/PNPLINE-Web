import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('F:/pnpline-landing/hero-section-video/blockout/curvature-rework-v001')
for file in [root/'inputs/warehouse-v008.blend',root/'candidate-curvature-v003.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene
 for f in [600,930,1075]:
  s.frame_set(f);carrier=s.objects['A01_CONTAINER']; inv=carrier.matrix_world.inverted()
  for o in s.objects:
   if o.name.startswith('W01_REMAINING_CONTAINER_CARGO'):
    print('CARGO',file.stem,f,o.name,'parent',o.parent.name if o.parent else None,'hide',o.hide_render,'scale',list(o.scale),'relative',list(inv@o.matrix_world.translation),'radius',o.matrix_world.translation.length)
