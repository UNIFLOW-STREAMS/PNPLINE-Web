"""Write a staged candidate with only the two new camera-adapter actions revised.

Run in the provisional blend with -- --input-sha HASH --output STAGED.blend.
The input is never overwritten; the caller validates and promotes the output.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import animation_reflow


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


parser=argparse.ArgumentParser()
parser.add_argument('--input-sha',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath).resolve()
target=Path(args.output).resolve()
assert source!=target,'Use a separate staging output; do not overwrite the input'
assert target.parent==ROOT.resolve(),'Staged output must stay inside the current deliverable folder'
assert not target.exists(),'Refusing to overwrite an existing staged candidate'
assert sha(source)==args.input_sha,'Input hash differs from the reviewed provisional candidate'
scene=bpy.context.scene
allowed={scene.objects[n].animation_data.action.name for n in('CNC_CAMERA_REFLOW','CNC_CAMERA_TARGET_REFLOW')}
before=animation_reflow._action_hashes()
result=animation_reflow.refine_camera_reflow(scene)
after=animation_reflow._action_hashes()
changed=[n for n,h in before.items()if after.get(n)!=h]
assert set(changed)==allowed,(changed,allowed)
assert set(after)==set(before),'Patch unexpectedly created or removed an action'
assert sha(source)==args.input_sha,'Input file changed during the camera patch'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
result.update({'input_file':str(source),'input_sha256':args.input_sha,
               'staged_file':str(target),'staged_sha256':sha(target),
               'only_changed_actions':changed,'input_file_unchanged':sha(source)==args.input_sha})
(ROOT/'review/camera-patch-delivery.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('CAMERA_PATCH_STAGED',json.dumps(result),flush=True)
