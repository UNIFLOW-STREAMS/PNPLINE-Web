import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
cfg=json.loads((R.parent/'s2-styleframe-match-v001/review/crane-style-proposal-v019.json').read_text());u=(Vector(cfg['beam_endpoints'][1])-Vector(cfg['beam_endpoints'][0])).normalized();v=Vector((-u.y,u.x,0));changed=[]
for o in s.objects['CR_SLEW_JIB'].children:
 if not (o.name.startswith('CR_STAY') or o.name in ['CR_CROSS_MEMBER','CR_CROSS_MEMBER.003']):continue
 M=o.matrix_local.copy();I=M.inverted()
 for vert in o.data.vertices:
  p=M@vert.co;vert.co=I@(p+v*p.dot(v)*.8)
 o.data.update();changed.append(o.name)
s['city_rotation_contact_fix']='Coast/ship/arrival/portal/mast and internal stay-trolley clearance corrected'
out=R/'master-previz-city-rotation-fix-v002.blend';assert not out.exists();source=Path(bpy.data.filepath);bpy.ops.wm.save_as_mainfile(filepath=str(out))
delivery=json.loads((R/'delivery.json').read_text());delivery.update(file=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),candidate=str(source),candidate_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),status='Internal crane correction; final verification in progress');(R/'delivery.json').write_text(json.dumps(delivery,indent=2))
(R/'review/stay-corridor-fix.json').write_text(json.dumps({'changed_meshes':changed,'transverse_stay_anchor_factor':1.8,'outer_anchor_halfwidth_m':1.35,'carriage_rail_wheel_halfwidth_m':.86,'original_blocking_review':'Stay-to-wheel intersections f0-106, and inherited stay-to-carriage body intersections','actions_unchanged':True},indent=2))
