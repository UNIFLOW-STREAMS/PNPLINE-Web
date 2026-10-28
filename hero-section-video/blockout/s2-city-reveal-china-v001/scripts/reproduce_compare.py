import bpy,sys,json,hashlib,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('pres',R.parent/'cn-city-proxy-v001/scripts/preservation.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
frames=[0,84,96,97,97.25,124,144,156,170,192,214.75,215,216,278,330,450,456,900,1392]
names,a,af,ae=m.snapshot(R/'master-s2-city-reveal-china-v001.blend',frames=frames)
rn,b,bf,be=m.snapshot(R/'review/reproduced.blend',frames=frames)
result={'objects':len(names),'structure_equal':a==b,'names_equal':names==rn,'sampled_evaluation_equal':af==bf,'frames':frames,'static_errors':ae+be,'original_sha256':hashlib.sha256((R/'master-s2-city-reveal-china-v001.blend').read_bytes()).hexdigest(),'reproduced_sha256':hashlib.sha256((R/'review/reproduced.blend').read_bytes()).hexdigest()}
(R/'review/reproduced-structure.json').write_text(json.dumps(result,indent=2));print(result)
assert a==b and af==bf and names==rn and not ae and not be
