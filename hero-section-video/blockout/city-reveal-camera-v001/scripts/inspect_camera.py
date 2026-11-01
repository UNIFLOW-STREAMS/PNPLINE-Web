import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted();cam=s.objects['CAM_MASTER'];target=s.objects['CAM_LOOK_TARGET']
out={'source':bpy.data.filepath,'resolution':[s.render.resolution_x,s.render.resolution_y],'fps':s.render.fps,'markers':[(m.name,m.frame) for m in s.timeline_markers],'camera_parent':cam.parent.name,'constraints':[(c.type,c.target.name if hasattr(c,'target') and c.target else None) for c in cam.constraints],'samples':[]}
for f in [380,408,430,455,470,479,480,490,500,509,528,540,552,576,600,624,648,672]:
 s.frame_set(f);cp=I@cam.matrix_world.translation;tp=I@target.matrix_world.translation
 out['samples'].append({'f':f,'cam':list(cp),'target':list(tp),'lens':cam.data.lens,'container':list(I@s.objects['A01_CONTAINER'].matrix_world.translation)})
(R/'review/camera-source.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
