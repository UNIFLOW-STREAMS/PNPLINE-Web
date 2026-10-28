import bpy,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
right_only='--right-cloud-only' in sys.argv
water_only='--waterway-only' in sys.argv
def capture():
 result={}
 for o in bpy.data.objects:
  allowed=(o.name in ['SF_BASIN_WATER_SURFACE','SF_BASIN_OUTER_WALL','SF_FRONT_LAND','SF_COAST_FOLDED_FACE']) if water_only else (o.name=='SF_CLOUD_RIGHT') if right_only else (o.name.startswith('SF_CHINA_') or o.name in ['SF_CLOUD_LEFT','SF_CLOUD_RIGHT'])
  if allowed:continue
  row={'parent':o.parent.name if o.parent else None,'matrix':list(map(list,o.matrix_basis)),'hide':o.hide_render}
  if o.type=='MESH':row['vertices']=[list(v.co)for v in o.data.vertices]
  result[o.name]=hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()
 actions={}
 for a in bpy.data.actions:
  actions[a.name]=[[fc.data_path,fc.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation]for k in fc.keyframe_points]]for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]
 return result,actions
candidate=bpy.data.filepath;bpy.context.scene.frame_set(156);after,aa=capture()
baseline='v007' if water_only else 'v006' if right_only else 'v004'
bpy.ops.wm.open_mainfile(filepath=str(R/f'review/layout-proposal-{baseline}.blend'));bpy.context.scene.frame_set(156);before,ba=capture()
result={'candidate':candidate,'unmodified_objects_checked':len(before),'object_differences':[k for k in before.keys()|after.keys() if before.get(k)!=after.get(k)],'all_actions_equal':aa==ba,'actions_checked':len(ba),'note':'Existing v004 camera continuity failure f104 is outside this title-only correction; not claimed fixed.'}
version=Path(candidate).stem.rsplit('-',1)[-1]
(R/f'review/title-scope-{version}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert not result['object_differences'] and result['all_actions_equal']
