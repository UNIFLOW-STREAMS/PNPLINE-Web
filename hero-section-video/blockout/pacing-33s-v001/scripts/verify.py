"""Independent reopened-file audit against v013 at corresponding source times."""
import hashlib, importlib.util, json, math, sys
from pathlib import Path
import bpy
import numpy as np

R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from timing import CONFIG,TimeMap
m=TimeMap();source=(R/CONFIG['source']).resolve();target=R/CONFIG['output']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)==CONFIG['source_sha256']
spec=importlib.util.spec_from_file_location('preservation',R.parent/'curvature-rework-v001/scripts/audit_preservation.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

def relevant_names(s):
    moving={o for o in s.objects if o.animation_data or o.constraints}
    pending=list(moving)
    while pending:
        for child in pending.pop().children:
            if child not in moving: moving.add(child);pending.append(child)
    return sorted(o.name for o in moving)

def snapshot(s,names,frames,source_clock):
    result=np.empty((len(frames),len(names),4,4),dtype=np.float32)
    lenses=[];visibility=[]
    # Cache object references. Collection name lookup scans the10k-object scene;
    # repeating it for every channel and every frame dominated the audit time.
    objects=[s.objects[n] for n in names]
    cam=s.camera.data
    for i,out in enumerate(frames):
        f=m.source(out) if source_clock else out
        s.frame_set(math.floor(f),subframe=f%1)
        result[i]=[list(map(list,o.matrix_world)) for o in objects]
        lenses.append([cam.lens,cam.shift_x,cam.shift_y,cam.clip_start,cam.clip_end])
        visibility.append([(o.hide_render,o.hide_viewport) for o in objects])
        if i%120==0:print('EVALUATED',source_clock,i,len(frames),flush=True)
    return result,np.array(lenses),np.array(visibility)

bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
before=audit.snap();names=relevant_names(s)
static_names=set(before['objects'])-set(names)
frames=sorted(set(list(range(990))+[a[1]*30 for a in CONFIG['anchors']]+[x+.5 for x in range(0,989,5)]))
expected,expected_lenses,expected_visibility=snapshot(s,names,frames,True)
bpy.ops.wm.open_mainfile(filepath=str(target));s=bpy.context.scene
assert (s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,s.frame_step)==(0,989,30,1,1)
assert len(s.objects)==10089
assert names==relevant_names(s)
after=audit.snap()
diff={k:before[k]!=after[k] for k in ['geometry','materials','world','view','camera']}
diff['static_objects']=[n for n in static_names if before['objects'][n]!=after['objects'].get(n)]
actual,actual_lenses,actual_visibility=snapshot(s,names,frames,False)
errors=np.max(np.abs(actual-expected),axis=(2,3))
peak=np.unravel_index(np.argmax(errors),errors.shape)
data={'source_sha256':sha(source),'output_sha256':sha(target),'objects':len(s.objects),
    'moving_objects_including_descendants':len(names),'static_objects':len(static_names),
    'sample_times':len(frames),'output_frames_checked':990,'differences':diff,
    'max_world_matrix_error':float(errors[peak]),'worst_object':names[peak[1]],'worst_output_frame':frames[peak[0]],
    'max_lens_and_shift_error':float(np.max(np.abs(actual_lenses-expected_lenses))),
    'visibility_mismatches':int(np.count_nonzero(actual_visibility!=expected_visibility))}
# Measure actual output camera continuity across the previously repaired joins.
cam_index=names.index(s.camera.name)
indices=[frames.index(f) for f in range(990)]
positions=actual[indices,cam_index,:3,3]
speeds=np.linalg.norm(np.diff(positions,axis=0),axis=1)
a,b=math.ceil(m.output(438)),math.floor(m.output(674))
data['approach_camera_min_units_per_frame']=float(speeds[a:b].min())
data['approach_camera_min_units_per_second']=float(speeds[a:b].min()*30)
data['time_map_min_speed']=min(m.speed(i/8) for i in range(7913))
data['time_map_max_speed']=max(m.speed(i/8) for i in range(7913))
(R/'review/verification.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2),flush=True)
assert not any(diff.values()),'Protected scene content changed'
assert data['max_world_matrix_error']<.002,'Time mapping broke evaluated transforms'
assert data['max_lens_and_shift_error']<.0002,'Projection drift'
assert data['visibility_mismatches']==0,'Visibility event drift'
assert data['approach_camera_min_units_per_frame']>.10,'Camera paused during approach'
print('PASS: reopened candidate preserves rigs, content, projection and all990 evaluated output poses')
