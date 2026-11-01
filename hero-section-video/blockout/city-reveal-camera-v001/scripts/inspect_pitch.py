"""Measure pitch and horizon roll in a fixed world frame, not changing Euler bases."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;R=Path(__file__).resolve().parents[1];file=Path(bpy.data.filepath);U=s.objects['US_FRAME'].matrix_world
def angles(q):
 forward=q@Vector((0,0,-1));up=q@Vector((0,1,0));right=q@Vector((1,0,0))
 pitch=math.degrees(math.asin(max(-1,min(1,forward.z))))
 level_right=forward.cross(Vector((0,0,1))).normalized();level_up=level_right.cross(forward).normalized()
 roll=math.degrees(math.atan2(right.dot(level_up),right.dot(level_right)))
 return [round(pitch,5),round(roll,5),round(math.degrees(math.atan2(forward.y,forward.x)),5)]
out={'source':str(file),'world_frame':[],'us_frame':[]}
for f in [408,430,439,440,445,450,455,460,465,470,479,490,509,521,540,552,576,600,624,648,672]:
 s.frame_set(f);q=s.camera.matrix_world.to_quaternion();out['world_frame'].append([f,*angles(q)]);out['us_frame'].append([f,*angles(U.to_quaternion().inverted()@q)])
(R/'review'/f'{file.stem}-pitch.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
