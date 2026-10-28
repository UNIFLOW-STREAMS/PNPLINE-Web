import bpy,ast,sys,json,hashlib
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];label=args[0];reproduced=bpy.data.filepath;candidate=R/args[1]
tree=ast.parse((R.parent/'s2-styleframe-match-v001/scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','actions','objects'}],type_ignores=[]),'<pure helpers>','exec'))
def snapshot():
 s=bpy.context.scene;s.frame_set(156);o=objects();a=actions();geometry={x.name:digest([[list(v.co)for v in x.data.vertices],[list(p.vertices)for p in x.data.polygons]])for x in s.objects if x.type=='MESH'};states=[]
 names=['CAM_MASTER','CAM_LOOK_TARGET','A02_SHIP','A01_CONTAINER','P01_SPREADER','CN_FRAME','US_FRAME','CR_SUSPENSION_HEAD']
 for f in range(1393):
  s.frame_set(f);states.append([list(row)for n in names for row in s.objects[n].matrix_world])
 return o,a,geometry,np.array(states)
first=snapshot();bpy.ops.wm.open_mainfile(filepath=str(candidate));second=snapshot();err=float(np.max(abs(first[3]-second[3])))
checks={'objects_equal':first[0]==second[0],'actions_equal':first[1]==second[1],'mesh_vertices_faces_equal':first[2]==second[2],'all_frame_evaluation_equal':err<.00001}
report={'candidate':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'reproduced':reproduced,'reproduced_sha256':hashlib.sha256(Path(reproduced).read_bytes()).hexdigest(),'checks':checks,'max_error':err,'sample_frames':[0,1392],'step':1}
(R/'review'/f'{label}-reproduction.json').write_text(json.dumps(report,indent=2));print(checks);assert all(checks.values()),checks
bpy.ops.wm.open_mainfile(filepath=reproduced);p=R/'scripts/render.py';sys.argv=['blender','--','reproduced-'+label,'156,216,456,648'];exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
