import bpy,sys,json,argparse,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(Path(a.config).read_text());out={}
for role,scene_name,prefix in [('master',cfg['source_scene'],''),('test',cfg['test_scene'],'S5T__')]:
 s=bpy.data.scenes[scene_name];bpy.context.window.scene=s;inv=bpy.data.objects[prefix+'US_FRAME'].matrix_world.inverted();rows=[]
 names=['A03_TRAILER','A03_TRACTOR','A01_CONTAINER','A01_DOOR_L','A01_DOOR_R', 'CAM_MASTER' if role=='master' else 'CAM_OBLIQUE','CAM_LOOK_TARGET' if role=='master' else 'LOOK_TARGET']
 for f in [647.75,648,648.25,899.75,900,900.25]:
  s.frame_set(math.floor(f),subframe=f%1);row=dict(frame=f,objects={})
  for n in names:
   o=bpy.data.objects[prefix+n];mat=inv@o.matrix_world;row['objects'][n]=dict(matrix=[list(r) for r in mat],location=list(mat.translation),quaternion=list(mat.to_quaternion()),lens=o.data.lens if o.type=='CAMERA' else None)
  rows.append(row)
 for index in [1,4]:
  row=rows[index]
  for n,ob in row['objects'].items():
   before=rows[index-1]['objects'][n];after=rows[index+1]['objects'][n];ob['central_velocity_m_per_frame']=[(after['location'][j]-before['location'][j])/.5 for j in range(3)]
   ob['quaternion_rate_per_frame']=[(after['quaternion'][j]-before['quaternion'][j])/.5 for j in range(4)]
   if ob['lens'] is not None:ob['lens_rate_per_frame']=(after['lens']-before['lens'])/.5
 out[role]=rows
Path(a.output).write_text(json.dumps(out,indent=2),encoding='utf8');print('BOUNDARIES saved')
