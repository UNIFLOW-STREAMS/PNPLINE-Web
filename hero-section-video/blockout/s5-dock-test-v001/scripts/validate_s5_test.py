"""Saved-scene contracts; evaluates Blender, never the path generator."""
import bpy,sys,json,math,argparse
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
def angle(a,b):return math.degrees(a.angle(b,0))
def validate(cfg):
 s=bpy.data.scenes[cfg['test_scene']];bpy.context.window.scene=s;U=bpy.data.objects['S5T__US_FRAME'].matrix_world.inverted();P='S5T__';th=cfg['thresholds'];errors=[];rows=[]
 def check(ok,label,f,value):
  if not ok:errors.append(dict(check=label,frame=f,value=value))
 def local(n):return U@bpy.data.objects[P+n].matrix_world
 prev=None;maximum=dict(hitch_m=0,tangent_deg=0,yaw_degrees_per_frame=0,steering_deg=0,support_m=0,relative_error=0)
 src=bpy.data.scenes[cfg['source_scene']];source_objects=set(src.objects);source_actions={o.animation_data.action for o in src.objects if o.animation_data and o.animation_data.action}
 for o in s.objects:
  check(o not in source_objects,'independent object',0,o.name);check(not o.parent or o.parent in set(s.objects),'parent reference',0,o.name)
  if o.animation_data:check(o.animation_data.action not in source_actions,'independent action',0,o.name)
  check(not o.constraints and not(o.animation_data and (o.animation_data.drivers or o.animation_data.nla_tracks)),'no external runtime',0,o.name)
 wheels=[o for o in s.objects if '_WHEEL_' in o.name];wheel_start={};wheel_end={};wheel_prev={};steer_error=0
 vertices=[];faces=[]
 for name in ['US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
  o=bpy.data.objects[P+name];offset=len(vertices);vertices.extend(U@o.matrix_world@v.co for v in o.data.vertices);faces.extend([offset+i for i in p.vertices] for p in o.data.polygons)
 ground=BVHTree.FromPolygons(vertices,faces)
 for i in range(648*4,900*4+1):
  f=i/4;s.frame_set(int(f),subframe=f%1);t=local('A03_TRAILER');h=local('A03_TRACTOR');c=local('A01_CONTAINER');F=t.to_3x3()@Vector((1,0,0));H=h.to_3x3()@Vector((1,0,0))
  hitch=(local('TRAILER_HITCH').translation-local('TRACTOR_HITCH').translation).length;maximum['hitch_m']=max(maximum['hitch_m'],hitch);check(hitch<th['hitch_m'],'hitch',f,hitch)
  relation=t.inverted()@c;expected=Matrix.Translation((0,0,2.55));relative=max(abs(relation[r][k]-expected[r][k]) for r in range(4) for k in range(4));maximum['relative_error']=max(maximum['relative_error'],relative);check(relative<th['relative_transform'],'container fixed',f,relative)
  check(abs(F.z)<.0001 and abs(H.z)<.0001,'regional planar heading',f,[F.z,H.z])
  doors=[bpy.data.objects[P+'A01_DOOR_'+x].rotation_euler.z for x in ['L','R']]
  row=dict(frame=f,trailer=list(t.translation),tractor=list(h.translation),trailer_forward=list(F),tractor_forward=list(H),doors=doors,camera=[list(r) for r in local('CAM_OBLIQUE')],lens=bpy.data.objects[P+'CAM_OBLIQUE'].data.lens,target=list(local('LOOK_TARGET').translation))
  if prev:
   for root,forward in [('trailer','trailer_forward'),('tractor','tractor_forward')]:
    d=Vector(row[root])-Vector(prev[root]);mean=Vector(row[forward])+Vector(prev[forward]);yaw=angle(Vector(row[forward]),Vector(prev[forward]))/.25;maximum['yaw_degrees_per_frame']=max(maximum['yaw_degrees_per_frame'],yaw);check(yaw<th['body_degrees_per_frame'],'continuous yaw',f,yaw)
    if 649<f<=810 and d.length>.0001:
     e=angle(d,mean);maximum['tangent_deg']=max(maximum['tangent_deg'],e);check(e<th['tangent_degrees'],'forward axle tangent',f,[root,e])
    if 810<f<=849:check(d.length<th['stationary_m'],'stop for doors',f,d.length)
    if 849<f<=890:check(d.dot(mean)<=.00001,'reverse sign',f,d.dot(mean))
   if f>=849:check(max(abs(doors[j]-prev['doors'][j]) for j in range(2))<.0001,'doors locked during reverse',f,doors)
  for o in wheels:
   pts=[U@o.matrix_world@v.co for v in o.data.vertices];bottom=min(p.z for p in pts);center=(U@o.matrix_world).translation;hit=ground.ray_cast(center+Vector((0,0,2)),Vector((0,0,-1)),5)[0];support=abs(bottom-hit.z) if hit else 999;maximum['support_m']=max(maximum['support_m'],support);check(support<th['support_height_m'],'wheel support height',f,[o.name,bottom,hit.z if hit else None])
   if 'TRACTOR_WHEEL' in o.name:
    wheel_forward=h.to_3x3()@Vector((math.cos(o.rotation_euler.z),math.sin(o.rotation_euler.z),0))
    if o.name in wheel_prev:
     oldp,oldf=wheel_prev[o.name];v=center-oldp
     if v.length>.0001:
      e=min(angle(v,wheel_forward+oldf),angle(-v,wheel_forward+oldf));steer_error=max(steer_error,e);check(e<th['tangent_degrees'],'steered wheel tangent',f,[o.name,e])
    wheel_prev[o.name]=(center,wheel_forward)
   maximum['steering_deg']=max(maximum['steering_deg'],abs(math.degrees(o.rotation_euler.z)));check(abs(math.degrees(o.rotation_euler.z))<th['steering_degrees'],'steering bound',f,o.name)
   if f==849:wheel_start[o.name]=o.rotation_euler.y
   if f==890:wheel_end[o.name]=o.rotation_euler.y
  rows.append(row);prev=row
 for n in wheel_start:check(wheel_end[n]>wheel_start[n]+1,'reverse wheel roll',890,[n,wheel_start[n],wheel_end[n]])
 end=rows[-1];check(abs(end['trailer'][0]+1.6-36)<.03 and abs(end['trailer'][1]-29)<.03,'dock alignment',900,end['trailer'])
 maximum['steered_wheel_tangent_deg']=steer_error
 return dict(pass_all=not errors,errors=errors,maximum=maximum,sample_count=len(rows),states=rows)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--scene',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(Path(a.config).read_text());assert a.scene==cfg['test_scene'];result=validate(cfg);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);(out/'motion-validation.json').write_text(json.dumps(result),encoding='utf8');print('MOTION',result['pass_all'],'errors',len(result['errors']),'maximum',result['maximum']);print('FIRST_ERRORS',result['errors'][:5]);assert result['pass_all']
