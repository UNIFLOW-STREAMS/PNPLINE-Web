import bpy,json
from mathutils import Vector
s=bpy.context.scene;s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];di=D.matrix_world.inverted()
for o in s.objects:
 if o.type=='EMPTY'and(o.name.startswith(('DT_','NA_HOUSE','SF_HIGHRISE','SF_SPHERE_TOWER','SF_OPEN_TOWER','SF_STEP_TOWER','SF_TALLEST_TOWER'))):
  p=di@o.matrix_world.translation
  print(o.name,[round(v,2)for v in p])
