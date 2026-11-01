import sys,json,bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parents[1]/'scripts'))
import guangzhou
c=bpy.data.collections.new('GZ_NORMAL_CHECK');bpy.context.scene.collection.children.link(c)
checks={}
for kind in ['box','tube','loft','solid_arch','open_arch']:
 b=guangzhou._Builder(kind,None,c,{},2,2,2)
 if kind=='box':b.box((0,0,1),(2,2,2),'x')
 if kind=='tube':b.tube([(0,0,0),(0,0,2)],1,'x',sides=16)
 if kind=='loft':b.loft([guangzhou._chamfer(2,2,z)for z in [0,2]],'x')
 if kind=='solid_arch':b.arch(0,0,0,1,2,.3,'x')
 if kind=='open_arch':b.arch(0,0,0,1,2,.3,'x',thickness=.1)
 volume=0
 for verts,faces,_ in b.batches.values():
  for face in faces:
   a=Vector(verts[face[0]])
   for i in range(1,len(face)-1):
    volume+=a.dot(Vector(verts[face[i]]).cross(Vector(verts[face[i+1]])))/6
 checks[kind]=volume
 assert volume>0,(kind,volume)
(R/'normals-report.json').write_text(json.dumps(checks,indent=2))
print('OUTWARD_NORMALS_PASS',checks)
