import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];file=Path(bpy.data.filepath);ver=file.stem.rsplit('-',1)[-1]
def capture():
 s=bpy.context.scene;s.frame_set(156);data={}
 for o in s.objects:
  if o.name.startswith('CR_')or o.name=='P01_SPREADER':continue
  row={'parent':o.parent.name if o.parent else None,'matrix':list(map(list,o.matrix_basis)),'hide':o.hide_render,'materials':[m.name if m else None for m in o.data.materials]if hasattr(o.data,'materials')else []}
  if o.type=='MESH':row['vertices']=[list(v.co)for v in o.data.vertices];row['faces']=[list(p.vertices)for p in o.data.polygons]
  if o.type=='CURVE':row['points']=[[[*p.co]for p in sp.points]for sp in o.data.splines];row['bevel']=o.data.bevel_depth
  if o.type=='CAMERA':row['lens']=o.data.lens;row['shift']=[o.data.shift_x,o.data.shift_y]
  data[o.name]=hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()
 return data
after=capture();bpy.ops.wm.open_mainfile(filepath=str(R/'review/crane-style-proposal-v019.blend'));before=capture();changed=[k for k in before.keys()|after.keys()if before.get(k)!=after.get(k)]
result={'file':str(file),'original_noncrane_objects':len(before),'changed_noncrane_geometry_transforms_at_f156':changed,'passed':not changed}
(R/f'review/crane-scope-{ver}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert not changed
