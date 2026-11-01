import bpy,json
from pathlib import Path
S=bpy.context.scene;S.frame_set(780);D=bpy.context.evaluated_depsgraph_get();c=S.camera.evaluated_get(D);origin=c.matrix_world.translation;direction=c.matrix_world.to_quaternion() @ __import__('mathutils').Vector((0,0,-1))
hit,loc,n,idx,obj,matrix=S.ray_cast(D,origin,direction)
rows=[]
for m in bpy.data.materials:
 if m.node_tree and any(n.type in {'BSDF_TRANSPARENT','HOLDOUT','MIX_SHADER','LIGHT_PATH'} for n in m.node_tree.nodes):
  rows.append(dict(name=m.name,nodes=[(n.name,n.type) for n in m.node_tree.nodes]))
print('HIT',obj.name if obj else None, 'MATS',[m.name for m in obj.data.materials] if obj else [])
print('SPECIAL',json.dumps(rows))
Path(__file__).resolve().parents[1].joinpath('review/visibility.json').write_text(json.dumps(rows,indent=2))

