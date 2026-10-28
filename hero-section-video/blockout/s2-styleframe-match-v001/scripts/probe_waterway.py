import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];inv=D.matrix_world.inverted()
w=s.objects['SF_BASIN_WATER_SURFACE'];v=[inv@w.matrix_world@p.co for p in w.data.vertices]
data={'water_outer':[[i,list(v[i])] for i in range(0,96,4)],'water_inner':[[i,list(v[i])] for i in range(96,192,8)],'letters':{ch:list(s.objects['SF_CHINA_'+ch].location)for ch in 'NA'},'crane':{o.name:[list(inv@o.matrix_world@Vector(p))for p in o.bound_box]for o in s.objects if o.name.startswith('SF_CRANE') and ('LEG' in o.name or 'FOOT' in o.name)}}
(R/'review/waterway-probe.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
print('CITY_ROOTS',json.dumps({o.name:list(o.location)for o in s.objects if o.name.startswith(('SF_HIGHRISE_','SF_TREE')) and o.type=='EMPTY'}))
