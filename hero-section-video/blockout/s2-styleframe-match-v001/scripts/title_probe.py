import bpy,json
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;s.frame_set(156);di=s.objects["SF_CN_LAYOUT"].matrix_world.inverted();d={}
for ch in "CHINA":
 o=s.objects["SF_CHINA_GOLD_"+ch];pts=[di@o.matrix_world@Vector(c)for c in o.bound_box];d[ch]={"pos":list(o.location),"bounds":[[min(p[i]for p in pts),max(p[i]for p in pts)]for i in range(3)]}
print(json.dumps(d,indent=2))
Path(__file__).resolve().parents[1].joinpath("review/title-before-measurements.json").write_text(json.dumps(d,indent=2))
