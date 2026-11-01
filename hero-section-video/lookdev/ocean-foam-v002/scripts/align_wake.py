import bpy,sys,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r.parent/'ocean-foam-v001/scripts'))
from resources import chart
s=bpy.context.scene
initial=s.frame_current
tree=bpy.data.node_groups['Pacific | Stern wash']
tree.nodes.clear()
source=(r.parent/'ocean-foam-v001/scripts/build.py').read_text()
exec(source[source.index('def node('):source.index("F='Float'")])
i=node('NodeGroupInput').outputs
stern_e=value('Hull stern east');stern_n=value('Hull stern north')
forward_e=value('Hull forward east');forward_n=value('Hull forward north')
for frame in range(990):
 s.frame_set(frame)
 matrix=s.objects['A02_SHIP'].matrix_world
 origin=chart(matrix@Vector((-7.15,-.17,0)))
 front=chart(matrix@Vector((-6.15,-.17,0)))
 dx,dy=front[0]-origin[0],front[1]-origin[1]
 length=math.hypot(dx,dy)
 for socket,val in zip([stern_e,stern_n,forward_e,forward_n],[*origin,dx/length,dy/length]):
  socket.default_value=val
  socket.keyframe_insert('default_value',frame=frame)
for layer in tree.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for key in fc.keyframe_points:key.interpolation='LINEAR'
dx=sub(i['East'],stern_e);dy=sub(i['North'],stern_n)
aft=mul(add(mul(dx,forward_e),mul(dy,forward_n)),-1)
across=sub(mul(dy,forward_e),mul(dx,forward_n))
uv=vec(mul(add(aft,1),1/12),mul(add(across,4),1/8))
cloud,foam,ridge=sep(tex(bpy.data.images['Wake - restrained cargo shoulders'],uv))
done({'Cloud':mul(cloud,i['Power']),'Lace':mul(foam,i['Power']),'Ridge':mul(ridge,i['Power'])})
s.frame_set(initial)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(r/'pnpline-ocean-foam-v002.blend'),compress=True)
