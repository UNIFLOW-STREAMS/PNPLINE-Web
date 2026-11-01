import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'city-expansion-v002/pnpline-city-expansion-v002.blend'))
s=bpy.context.scene;s.frame_set(349);U=s.objects['US_FRAME'];I=U.matrix_world.inverted()
ground=[]
for o in s.objects:
 if o.type=='MESH' and (o.name in ['US_LAND_TERRACE','US_QUAY','US_YARD_ROAD'] or o.name.startswith('CV_PORT')):
  print(o.name)
  M=I@o.matrix_world;ground.append((o.name,BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])))
res=[]
for y in [5.5,6.3,10.9,12.8,14,15.5,17.5,19]:
 for x in [-26,-22,-18,-14,-10,-6,0,6,10,14,18,22]:
  hits=[]
  for name,bvh in ground:
   p,n,idx,d=bvh.ray_cast(Vector((x,y,20)),Vector((0,0,-1)))
   if p is not None:hits.append((name,[round(v,3) for v in p],[round(v,3) for v in n]))
  res.append({'xy':[x,y],'hits':hits})
(R/'review/ground-survey.json').write_text(json.dumps(res,indent=2))
camdata=bpy.data.cameras.new('SURVEY');cam=bpy.data.objects.new('SURVEY',camdata);s.collection.objects.link(cam);s.camera=cam
s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
def capture(name,eye,target,scale):
 eye=Vector(eye);target=Vector(target);q=(target-eye).to_track_quat('-Z','Y');cam.matrix_world=U.matrix_world@Matrix.Translation(eye)@q.to_matrix().to_4x4();camdata.type='ORTHO';camdata.ortho_scale=scale
 s.render.filepath=str(R/'preview'/f'{name}.png');bpy.ops.render.render(write_still=True)
capture('port-before',(-28,-40,33),(0,9,4),65)
capture('port-top-before',(0,12,65),(0,12,0),62)
