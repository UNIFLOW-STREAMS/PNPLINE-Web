"""Review-only analytic tyre support: avoids dense-key subframe phase aliasing."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];path=R/'review/master-contact-proposal.blend';bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted()
wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]
for o in wheels:
 o.driver_remove('location',2)
 ctrl=bpy.data.objects.new('CONTACT_CTRL_'+o.name,None);s.collection.objects.link(ctrl);ctrl.hide_render=True;ctrl['roll']=0.;ctrl.keyframe_insert('["roll"]',frame=0)
 srcfc=next(fc for l in o.animation_data.action.layers for st in l.strips for b in st.channelbags if b.slot_handle==o.animation_data.action_slot.handle for fc in b.fcurves if fc.data_path=='rotation_euler' and fc.array_index==1)
 dstfc=next(fc for l in ctrl.animation_data.action.layers for st in l.strips for b in st.channelbags for fc in b.fcurves)
 dstfc.keyframe_points.clear();dstfc.keyframe_points.add(len(srcfc.keyframe_points))
 for a,b in zip(srcfc.keyframe_points,dstfc.keyframe_points):b.co=a.co;b.interpolation=a.interpolation
 dstfc.update()
 def make_driver(path,expression,variables,index=None,owner=None):
  owner=owner or ctrl
  fc=owner.driver_add(path) if index is None else owner.driver_add(path,index);d=fc.driver;d.type='SCRIPTED'
  for v in list(d.variables):d.variables.remove(v)
  for name,obj,prop in variables:
   v=d.variables.new();v.name=name;v.targets[0].id=obj
   if prop.startswith('TRANSFORM:'):
    v.type='TRANSFORMS';v.targets[0].transform_type=prop.split(':')[1];v.targets[0].transform_space='WORLD_SPACE';v.targets[0].rotation_mode='QUATERNION'
   else:v.type='SINGLE_PROP';v.targets[0].data_path=prop
  assert len(expression)<256,expression
  d.expression=expression
 wx,wy=o.location[:2]
 uq=s.objects['US_FRAME'].matrix_world.to_quaternion().inverted();uw,ux,uy,uz=uq
 qvars=[(n,o.parent,'TRANSFORM:ROT_'+axis) for n,axis in [('w','W'),('x','X'),('y','Y'),('z','Z')]]
 ctrl['qw']=0.;ctrl['qz']=0.;ctrl['yaw']=0.
 make_driver('["qw"]',f'({uw})*w-({ux})*x-({uy})*y-({uz})*z',qvars)
 make_driver('["qz"]',f'({uw})*z+({ux})*y-({uy})*x+({uz})*w',qvars)
 make_driver('["yaw"]','2*atan2(z,w)',[('z',ctrl,'["qz"]'),('w',ctrl,'["qw"]')])
 for j,label in enumerate(['contact_x','contact_y','contact_z']):
  ctrl[label]=0.;variables=[];parts=[]
  for i in range(3):
   if abs(I[j][i])<1e-7:continue
   parts.append(f'({I[j][i]:.8g})*p{i}');variables.append((f'p{i}',o.parent,'TRANSFORM:LOC_'+['X','Y','Z'][i]))
  expression='+'.join(parts)+f'+({I[j][3]:.8g})'
  if j<2:
   variables.append(('t',ctrl,'["yaw"]'));expression+=f'+({wx:.8g})*cos(t)-({wy:.8g})*sin(t)' if j==0 else f'+({wx:.8g})*sin(t)+({wy:.8g})*cos(t)'
  make_driver(f'["{label}"]',expression,variables)
 ctrl['contact_ground']=0.
 make_driver('["contact_ground"]','.899996-.165006*min(1,max(0,(x-17)/2)) if y<12 else .73499+.025007*min(1,max(0,(y-25.5)/.5))',[('x',ctrl,'["contact_x"]'),('y',ctrl,'["contact_y"]')])
 # Mesh axial z becomes horizontal after fixed X=pi/2; Z steering does not alter height.
 xy=sorted(set((round(v.co.x*o.scale.x,8),round(v.co.y*o.scale.y,8)) for v in o.data.vertices))
 radius=math.hypot(*xy[0]);phase=math.atan2(xy[0][1],xy[0][0]);n=len(xy);step=2*math.pi/n
 for i in range(1000):
  r=i*.019;analytic=radius*math.cos((r-math.pi/2-phase+step/2)%step-step/2);actual=-min(-math.sin(r)*x+math.cos(r)*y for x,y in xy)
  assert abs(analytic-actual)<1e-7
 make_driver('location',f'g-z+{radius:.10g}*cos((r-({math.pi/2+phase-step/2:.10g}))%({step:.10g})-({step/2:.10g}))',[('g',ctrl,'["contact_ground"]'),('z',ctrl,'["contact_z"]'),('r',ctrl,'["roll"]')],2,owner=o)
 o['contact_driver_note']='Safe math-only expression; parent transform and wheel roll inputs; no external driver namespace'
 bpy.context.view_layer.update()
ground=[]
for n in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD','PROPOSAL_CONTINUOUS_ROAD','PROPOSAL_QUAY_ROAD_RAMP','PROPOSAL_ROAD_YARD_RAMP']:
 o=s.objects[n];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
worst=[0,None,None];invalid=[]
for j in range(649*16,890*16+1):
 t=j/16;s.frame_set(int(t),subframe=t%1)
 for o in wheels:
  wm=I@o.matrix_world;c=wm.translation;hits=[b.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for b in ground]
  if not any(p is not None for p in hits):
   ctrl=s.objects['CONTACT_CTRL_'+o.name];print('DIAG',t,o.name,list(c),list(o.location),dict(ctrl.items()),[(f.driver.expression,f.driver.is_valid) for f in ctrl.animation_data.drivers],flush=True);raise ValueError('No support hit')
  height=max(p.z for p in hits if p is not None);err=abs(min((wm@v.co).z for v in o.data.vertices)-height)
  if err>worst[0]:worst=[err,t,o.name]
  if any(not fc.driver.is_valid for fc in o.animation_data.drivers):invalid.append(o.name)
s.frame_set(704);bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
out={'pass':worst[0]<.002 and not invalid,'worst_ground_error':worst,'invalid_drivers':sorted(set(invalid)),'blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest()};(R/'review/contact-driver-validation.json').write_text(json.dumps(out,indent=2));print('DRIVER_RESULT',json.dumps(out),flush=True)
