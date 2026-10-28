import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
names=['A01_CONTAINER','W01_NEW_PALLET','CAM_MASTER','CAM_LOOK_TARGET']
def snap():
 s=bpy.context.scene
 out={}
 for name in names:
  o=s.objects[name];ad=o.animation_data
  for l in ad.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     if bag.slot_handle!=ad.action_slot.handle:continue
     for fc in bag.fcurves:
      out[(name,fc.data_path,fc.array_index)]=[fc.evaluate(t/8) for t in range(72*8,s.frame_end*8+1)]
 return out
candidate=Path(bpy.data.filepath);a=snap()
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));b=snap()
errors={str(k):max(abs(x-y)for x,y in zip(a[k],b[k])) for k in a}
report={'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((R/'inputs/base.blend').read_bytes()).hexdigest(),'range':[72,bpy.context.scene.frame_end],'step':0.125,'curve_count':len(errors),'max_curve_error':max(errors.values()),'nonzero_errors':{k:v for k,v in errors.items()if v},'pass':max(errors.values())<0.0001}
(R/'review/reviewer-fractional.json').write_text(json.dumps(report,indent=2));print('REVIEWER_FRACTIONAL',report,flush=True)
assert report['pass']
