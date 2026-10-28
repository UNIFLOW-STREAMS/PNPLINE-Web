import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;file=Path(bpy.data.filepath);label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else file.stem
s.frame_set(72);cargo=s.objects['A01_CONTAINER'];pallet=s.objects['W01_NEW_PALLET'];relative=cargo.matrix_world.inverted()@pallet.matrix_world;outside=[];drift=0;max_top=-1e9
payload=[pallet]+list(pallet.children_recursive)
for k in range(289):
 f=k/4;s.frame_set(int(f),subframe=f%1);I=cargo.matrix_world.inverted();delta=I@pallet.matrix_world
 drift=max(drift,max(abs(delta[i][j]-relative[i][j]) for i in range(4) for j in range(4)))
 for o in payload:
  if o.type!='MESH':continue
  for v in o.data.vertices:
   p=I@o.matrix_world@v.co;max_top=max(max_top,p.z)
   if abs(p.x)>1.49 or abs(p.y)>.68 or p.z<-.77 or p.z>.77:
    outside.append([f,o.name,list(p)]);break
s.frame_set(0);D=s.objects['SF_CN_LAYOUT'].matrix_world.inverted();start=(D@cargo.matrix_world.translation).z;beam=(D@s.objects['CR_SLEW_JIB'].matrix_world.translation).z
checks={'payload_inside_container_all_289_samples':not outside,'payload_relative_pose_constant_during_lowering':drift<.0001,'raised_start_height':start>7.4,'raised_crane_height':beam>9.4}
result={'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'checks':checks,'payload_outside_count':len(outside),'outside_examples':outside[:12],'max_relative_drift':drift,'payload_top_relative_z':max_top,'container_start_height':start,'boom_height':beam}
(R/'review'/f'{label}-lift.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert all(checks.values())
