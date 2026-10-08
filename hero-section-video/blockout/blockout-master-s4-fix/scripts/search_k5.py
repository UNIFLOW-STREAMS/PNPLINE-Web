"""Read-only camera feasibility search; surface rays, then render ranked poses."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import bounds
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;U=bpy.data.objects['US_FRAME'].matrix_world.copy()
C.animation_data_clear();C.data.animation_data_clear();S.frame_set(648)
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
dg=bpy.context.evaluated_depsgraph_get();up=U.to_3x3()@Vector((0,0,1))
names=['TRACTOR_CAB','A01_SIDE_L','A01_SIDE_R','A01_FRONT','A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF','P02_SPREADER_FRAME','SHIP_HULL','TRAILER_CHASSIS']
surfaces={}
for name in names:
 o=bpy.data.objects[name];surfaces[name]=[]
 for face in o.data.polygons:
  normal=(o.matrix_world.to_3x3().inverted().transposed()@face.normal).normalized()
  for point in [face.center]+[face.center.lerp(o.data.vertices[i].co,.75) for i in face.vertices]:
   surfaces[name].append((o.matrix_world@point,normal))
print('US centers', {n:list(U.inverted()@bpy.data.objects[n].matrix_world.translation) for n in names})
def pose(p,t,l):
 wp=U@Vector(p);wt=U@Vector(t);z=(wp-wt).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized()
 C.location=wp;C.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion();C.data.lens=l;bpy.context.view_layer.update()
def visibility(name):
 counts={'front':0,'inframe':0,'visible':0,'pole':0};origin=C.matrix_world.translation
 for p,normal in surfaces[name]:
  if normal.dot(origin-p)<=0:continue
  counts['front']+=1;uv=world_to_camera_view(S,C,p)
  if not(uv.z>0 and .015<uv.x<.985 and .015<uv.y<.985):continue
  counts['inframe']+=1;ray=p-origin
  hit,loc,n,idx,obj,mat=S.ray_cast(dg,origin,ray.normalized(),distance=ray.length+.03)
  if hit and obj.name==name and (loc-p).length<.08:counts['visible']+=1
  elif hit and obj.name.startswith('P02_'):counts['pole']+=1
 return counts
rows=[]
for side,ys in [('north',[22,26,30,34]),('south',[-18,-14,-10,-6])]:
 for x in [-12,-8,-4,0,4,8,12,16]:
  for y in ys:
   for z in [11,14,17]:
    for l in [32,38]:
     p=(x,y,z);t=(5,7,3) if side=='south' else (6,8,2.5);pose(p,t,l)
     cab=visibility('TRACTOR_CAB');cargo=[visibility(n) for n in names if n.startswith('A01_')]
     v=sum(d['visible'] for d in cargo);front=sum(d['front'] for d in cargo);pole=sum(d['pole'] for d in cargo)
     truck=bounds('A03_TRACTOR');box=bounds('A01_CONTAINER');ship=visibility('SHIP_HULL');spreader=visibility('P02_SPREADER_FRAME')
     road=[]
     for q in [(18,9,.74),(22,9,.74),(26,9,.74),(30,14,.74)]:
      wp=U@Vector(q);uv=world_to_camera_view(S,C,wp);road.append(uv.z>0 and .025<uv.x<.975 and .025<uv.y<.975)
     if min(truck+box)<.005 or max(truck+box)>.995:continue
     if cab['visible']<6 or v<9 or ship['visible']<2 or not any(road):continue
     score=3*cab['visible']/max(cab['front'],1)+2*v/max(front,1)-2*(cab['pole']+pole)/max(front+cab['front'],1)+.3*sum(road)+.06*ship['visible']+.8*(box[2]-box[0])
     rows.append({'p':p,'t':t,'lens':l,'score':score,'cab':cab,'cargo_visible':v,'cargo_front':front,'cargo_pole':pole,'ship':ship,'road':road,'spreader':spreader,'truck_bounds':truck,'cargo_bounds':box,'side':side})
rows.sort(key=lambda r:-r['score']);out=R/'review/k5-search';out.mkdir(exist_ok=True)
(out/'ranked.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
selected=[]
for r in rows:
 if any((Vector(r['p'])-Vector(s['p'])).length<5 for s in selected):continue
 selected.append(r)
 if len(selected)==9:break
for i,r in enumerate(selected):
 pose(r['p'],r['t'],r['lens']);S.render.filepath=str(out/f'rank-{i:02d}.png');bpy.ops.render.render(write_still=True);print('RANK',i,json.dumps(r))
(out/'selected.json').write_text(json.dumps(selected,indent=2),encoding='utf-8')
