import bpy,json,sys,argparse,math,hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=bpy.data.scenes[a.scene];bpy.context.window.scene=s;prefix='S5T__' if s.name.startswith('S5_DOCK') else '';U=s.objects[prefix+'US_FRAME'].matrix_world.copy();I=U.inverted()
def curves(o):
 ad=o.animation_data
 return [fc for l in ad.action.layers for st in l.strips for b in st.channelbags for fc in b.fcurves] if ad and ad.action else []
inv=[]
for o in sorted(s.objects,key=lambda o:o.name):
 inv.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,rotation=o.rotation_mode,scale=list(o.scale),location=list(o.location),constraints=[c.type for c in o.constraints],drivers=len(o.animation_data.drivers) if o.animation_data else 0,nla=len(o.animation_data.nla_tracks) if o.animation_data else 0,action=o.animation_data.action.name if o.animation_data and o.animation_data.action else None,action_users=o.animation_data.action.users if o.animation_data and o.animation_data.action else 0,keys=[(fc.data_path,fc.array_index,[(float(k.co.x),float(k.co.y)) for k in fc.keyframe_points]) for fc in curves(o)]))
roots=['A03_TRACTOR','A03_TRAILER','A01_CONTAINER','A01_DOOR_L','A01_DOOR_R','W01_NEW_PALLET','W01_REMAINING_CONTAINER_CARGO','DOCK_TARGET','DOCK_BRIDGE','CAM_MASTER','CAM_LOOK_TARGET']
roots.extend(o.name.removeprefix(prefix) for o in s.objects if 'JACK' in o.name or 'INBOUND' in o.name)
frames=[648,720,721,732,746,760,790,810,842,849,890,900,901,912,924,936,948,960,972,984,1008]
rows=[]
for f in frames:
 s.frame_set(f);row={'frame':f,'objects':{},'lens':s.camera.data.lens}
 for n in set(roots):
  o=s.objects.get(prefix+n)
  if o is None:continue
  m=I@o.matrix_world;row['objects'][n]={'p':list(m.translation),'matrix':[list(r) for r in m],'dims':list(o.dimensions),'local':list(o.location),'rotation':list(o.rotation_euler)}
 rows.append(row)
s.frame_set(900);shape={}
for n in ['A01_DOOR_L','A01_DOOR_R','A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF','A01_FLOOR','A01_ROOF','A01_SIDE_L','A01_SIDE_R','DOCK_BRIDGE','WAREHOUSE_FLOOR','TRAILER_CHASSIS']:
 o=s.objects.get(prefix+n)
 if o:shape[n]=dict(local=list(o.location),dims=list(o.dimensions),scale=list(o.scale),matrix=[list(r) for r in I@o.matrix_world])
out=dict(file=bpy.data.filepath,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),scene=s.name,frames=[s.frame_start,s.frame_end],fps=s.render.fps,markers={m.name:m.frame for m in s.timeline_markers},camera=s.camera.name,inventory=inv,rows=rows,shape=shape,version=bpy.app.version_string)
Path(a.output).write_text(json.dumps(out),encoding='utf8');print('SURVEY',s.name,len(inv),out['markers'])
for r in rows:
 print(r['frame'],{n:[round(v,3) for v in x['p']] for n,x in r['objects'].items() if n in ['A03_TRAILER','W01_NEW_PALLET','CAM_MASTER']})
