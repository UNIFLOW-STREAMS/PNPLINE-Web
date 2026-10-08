import bpy,sys,json,argparse,hashlib,numpy as np
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--other',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);first=bpy.data.filepath
def fingerprint(path):
 bpy.ops.wm.open_mainfile(filepath=path);s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s;objects=sorted(s.objects,key=lambda o:o.name);h=hashlib.sha256()
 for j in range(1392*4+1):
  s.frame_set(j//4,subframe=j%4/4);h.update(np.array([list(map(list,o.matrix_world)) for o in objects],dtype=np.float32).tobytes());h.update(np.float32(s.camera.data.lens).tobytes())
 return h.hexdigest()
left=fingerprint(first);right=fingerprint(str(Path(a.other).resolve()));result={'pass_all':left==right,'first':first,'second':str(Path(a.other).resolve()),'evaluated_sha256':left,'second_evaluated_sha256':right,'samples':5569,'step':.25,'scope':'All304 object world matrices + lens, entire0..1392 timeline, fresh process; identical evaluated digest required.'};Path(a.output).write_text(json.dumps(result,indent=2));print(result);assert left==right
