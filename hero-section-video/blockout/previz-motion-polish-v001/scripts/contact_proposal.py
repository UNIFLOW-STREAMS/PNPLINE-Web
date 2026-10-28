"""Review-only contact geometry proposal. Never adopts into A/B automatically."""
import bpy,sys,json,math,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from motion import TimeMap
cfg=json.loads((R/'config.json').read_text());m=TimeMap(1392,cfg['easing']);bpy.ops.wm.open_mainfile(filepath=str(R/'master-motion-polish-A.blend'));s=bpy.context.scene
U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted()
frame_before=m.forward(702);s.frame_set(int(frame_before),subframe=frame_before%1)
before_wheel_z={o.name:o.location.z for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name}
ramps=[('PROPOSAL_QUAY_ROAD_RAMP',(17,19,7.75,10.25,.899996,.73499),'x'),('PROPOSAL_ROAD_YARD_RAMP',(29,38,25.5,26,.73499,.759997),'y')]
for name,(x0,x1,y0,y1,z0,z1),axis in ramps:
 top=[(x0,y0,z0),(x1,y0,z1 if axis=='x' else z0),(x1,y1,z1),(x0,y1,z0 if axis=='x' else z1)]
 verts=top+[(x,y,z-.03) for x,y,z in top];faces=[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);o=bpy.data.objects.new(name,mesh);s.collection.objects.link(o);o.matrix_world=U
 if s.objects['E07_INBOUND_ROAD'].data.materials:o.data.materials.append(s.objects['E07_INBOUND_ROAD'].data.materials[0])
 o['proposal_only']='Pending user approval: road contact transition only'
# Swept turn needs a wider ribbon: the existing 2.5m road drops to terrace
# under the articulated tractor wheel during the approved ellipse turn.
oldroad=s.objects['E07_INBOUND_ROAD'];newverts=[]
for k in range(0,len(oldroad.data.vertices),2):
 a,b=[I@oldroad.matrix_world@oldroad.data.vertices[k+j].co for j in [0,1]];center=(a+b)/2
 for p in [center+(a-center)*2,center+(b-center)*2]:
  h=.899996 if p.x<=17 and p.y<12 else .73499
  if 17<p.x<19 and p.y<12:h=.899996+(.73499-.899996)*(p.x-17)/2
  if p.y>25.5:h=.73499+(.759997-.73499)*min(1,(p.y-25.5)/.5)
  newverts.append((p.x,p.y,h))
mesh=bpy.data.meshes.new('PROPOSAL_CONTINUOUS_ROAD');mesh.from_pydata(newverts,[],[list(p.vertices) for p in oldroad.data.polygons]);road=bpy.data.objects.new(mesh.name,mesh);s.collection.objects.link(road);road.matrix_world=U
for mat in oldroad.data.materials:mesh.materials.append(mat)
oldroad.hide_render=True
ground=[]
for n in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD','PROPOSAL_CONTINUOUS_ROAD']+[r[0] for r in ramps]:
 o=s.objects[n];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name];rows={o.name:[] for o in wheels};lo,hi=m.forward(649),m.forward(890)
times=sorted(set([lo,hi]+[j/128 for j in range(math.ceil(lo*128),math.floor(hi*128)+1)]+[m.forward(f) for f in cfg['storyboard_source_frames'] if 649<=f<=890]))
for t in times:
 s.frame_set(int(t),subframe=t%1)
 for o in wheels:
  wm=I@o.matrix_world;c=wm.translation;hits=[tree.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for tree in ground];z=max(p.z for p in hits if p is not None);bottom=min((wm@v.co).z for v in o.data.vertices);axis=I.to_3x3()@o.parent.matrix_world.to_3x3()@o.matrix_parent_inverse.to_3x3()@Vector((0,0,1));rows[o.name].append((t,o.location.z+(z-bottom)/axis.z))
for o in wheels:
 fc=next(fc for l in o.animation_data.action.layers for st in l.strips for bag in st.channelbags if bag.slot_handle==o.animation_data.action_slot.handle for fc in bag.fcurves if fc.data_path=='location' and fc.array_index==2)
 points=[tuple(k.co) for k in fc.keyframe_points if k.co.x<lo or k.co.x>hi]+rows[o.name];points.sort();fc.keyframe_points.clear();fc.keyframe_points.add(len(points));fc.keyframe_points.foreach_set('co',np.array(points).ravel())
 for k in fc.keyframe_points:k.interpolation='LINEAR'
 fc.update()
worst=[0,None,None]
for t in sorted(set(np.arange(lo,hi,.0625).tolist()+[m.forward(f) for f in np.arange(649,890,.0625)]+[float(f) for f in range(math.ceil(lo),math.floor(hi)+1)])):
 s.frame_set(int(t),subframe=t%1)
 for o in wheels:
  wm=I@o.matrix_world;c=wm.translation;hits=[tree.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for tree in ground];z=max(p.z for p in hits if p is not None);err=abs(min((wm@v.co).z for v in o.data.vertices)-z)
  if err>worst[0]:worst=[err,t,o.name]
s['contact_proposal_status']='User approval pending';s.frame_set(round(m.forward(702)));path=R/'review/master-contact-proposal.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
(R/'review/contact-proposal.json').write_text(json.dumps({'status':'proposal only; not adopted','ramps':ramps,'road_width_before':2.5,'road_width_proposed':5.0,'wheel_ground_error':worst,'geometry_scope':'continuous road overlay width5m and two transition strips; original meshes retained, truck roots, camera, S5 route and doors unchanged','blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},indent=2))
print('CONTACT_PROPOSAL',worst,flush=True)
# Matched actual scene views at the discontinuity, with an inspection camera.
camdata=bpy.data.cameras.new('REVIEW_CAMERA');cam=bpy.data.objects.new('REVIEW_CAMERA',camdata);s.collection.objects.link(cam);s.camera=cam;camdata.lens=48
p=U@Vector((20,3.0,4));target=U@Vector((17.4,9,.9));cam.location=p;cam.rotation_euler=(target-p).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=960;s.render.resolution_y=540;s.frame_set(int(m.forward(702)),subframe=m.forward(702)%1);s.render.filepath=str(R/'review/contact-proposal.png');bpy.ops.render.render(write_still=True)
for name,_,_ in ramps:s.objects[name].hide_render=True
road.hide_render=True;oldroad.hide_render=False
for name,z in before_wheel_z.items():s.objects[name].location.z=z
bpy.context.view_layer.update()
s.render.filepath=str(R/'review/contact-existing-ground.png');bpy.ops.render.render(write_still=True)
