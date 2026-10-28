import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);D=s.objects['SF_CN_LAYOUT']
data={}
for name in ['SF_BASIN_WATER_SURFACE','SF_ISLAND_TOP']:
 o=s.objects[name];data[name]=[]
 for i,v in enumerate(o.data.vertices):
  p=world_to_camera_view(s,s.camera,o.matrix_world@v.co)
  data[name].append({'i':i,'xyz':list(v.co),'uv':[p.x*2048,(1-p.y)*1156]})
data['roots']={n:list(s.objects[n].location)for n in ['SF_CHINA_'+x for x in 'CHINA']+['SF_CLOUD_LEFT','SF_CLOUD_RIGHT']}
(R/'review/arc-water-probe.json').write_text(json.dumps(data,indent=2))
print(json.dumps({'roots':data['roots'],'water':[data['SF_BASIN_WATER_SURFACE'][i]for i in range(0,192,8)]},indent=2))
