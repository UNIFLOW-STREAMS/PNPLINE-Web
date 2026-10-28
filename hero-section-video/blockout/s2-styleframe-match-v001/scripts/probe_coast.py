import bpy,json
from mathutils import Vector
s=bpy.context.scene;s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];di=D.matrix_world.inverted();o=s.objects['SF_COAST_FOLDED_FACE'];n=len(o.data.vertices)//2
print('COAST',json.dumps([list(o.data.vertices[i].co) for i in range(0,n,16)]))
for o in s.objects:
 if (('HULL' in o.name or 'OCEAN' in o.name) and o.type=='MESH'):
  ps=[di@o.matrix_world@Vector(c)for c in o.bound_box]
  print(o.name,o.hide_render,'bbox',[[min(p[j]for p in ps),max(p[j]for p in ps)]for j in range(3)])
