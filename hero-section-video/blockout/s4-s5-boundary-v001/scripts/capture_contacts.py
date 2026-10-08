import bpy,sys,argparse,json,math
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=bpy.data.scenes[a.scene];bpy.context.window.scene=s;I=bpy.data.objects['US_FRAME'].matrix_world.inverted();rows=[]
def heights(name):
 o=bpy.data.objects[name];vs=[I@o.matrix_world@Vector(v) for v in o.bound_box];return min(v.z for v in vs),max(v.z for v in vs)
for f in [632,637,648,649,660,672,704,708,720,732,744,780]:
 s.frame_set(f);cargo=bpy.data.objects['A01_CONTAINER'];deck=bpy.data.objects['TRAILER_CHASSIS'];bottom=(I@cargo.matrix_world@Vector((0,0,-.75))).z;top=heights('TRAILER_CHASSIS')[1]
 normal=(deck.matrix_world.to_3x3()@Vector((0,0,1))).normalized();plane=deck.matrix_world@Vector((0,0,max(v[2] for v in deck.bound_box)));gaps=[(cargo.matrix_world@Vector((x,y,-.75))-plane).dot(normal) for x in [-1.6,1.6] for y in [-.75,.75]]
 rows.append(dict(frame=f,container_bottom=bottom,trailer_deck_top=top,seat_gap=bottom-top,seat_plane_corner_gaps=gaps,payload_relative=[list(r) for r in cargo.matrix_world.inverted()@bpy.data.objects['W01_NEW_PALLET'].matrix_world],doors={n:list(bpy.data.objects[n].rotation_euler) for n in ['A01_DOOR_L','A01_DOOR_R']},ship_matrix=[list(r) for r in bpy.data.objects['A02_SHIP'].matrix_world],hoist_bottom=heights('P02_SPREADER_FRAME')[0],container_top=(I@cargo.matrix_world@Vector((0,0,.75))).z))
Path(a.output).write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
