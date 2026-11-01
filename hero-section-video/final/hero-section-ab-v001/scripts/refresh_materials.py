import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from state import tree,clean,hashed,presentation
bpy.context.scene.frame_set(0);path=Path(__file__).resolve().parents[1]/'audit'/(sys.argv[-1]+'.json');record=json.loads(path.read_text())
used={sl.material for o in bpy.context.scene.objects for sl in o.material_slots if sl.material}
record['snapshot']['materials']={m.name:hashed([clean(m.diffuse_color),tree(m.node_tree)]) for m in used}
record['presentation']=presentation();path.write_text(json.dumps(record));print('REFRESHED',sys.argv[-1],flush=True)
