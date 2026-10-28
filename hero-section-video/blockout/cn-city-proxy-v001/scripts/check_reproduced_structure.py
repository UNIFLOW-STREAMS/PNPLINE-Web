import sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from preservation import snapshot,digest
master=R/'master-cn-city-proxy-v001.blend';other=R/'review/reproduced.blend'
names,a,af,ae=snapshot(master,frames=[0,96,148,216,278,330,456,648,900,1200,1392])
nn,b,bf,be=snapshot(other,frames=[0,96,148,216,278,330,456,648,900,1200,1392])
result={'same_names':names==nn,'all_object_mesh_material_action_scene_signatures_equal':a==b,'sampled_states_equal':af==bf,'static_errors':ae+be,'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'reproduced_sha256':hashlib.sha256(other.read_bytes()).hexdigest(),'semantic_digest':digest(a)}
(R/'review/structural-reproduction.json').write_text(json.dumps(result,indent=2));print(result)
assert names==nn and a==b and af==bf and not ae and not be
