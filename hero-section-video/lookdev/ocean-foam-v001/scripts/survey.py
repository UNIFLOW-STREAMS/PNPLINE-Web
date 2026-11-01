import bpy
from mathutils import Vector
s=bpy.context.scene;ship=s.objects['A02_SHIP']
for n in ['EARTH_CONTINUOUS_OCEAN','US_WATER','OCEAN_DISC','WAKE_RIBBON_0','SF_BASIN_WATER_SURFACE']:
 o=s.objects.get(n)
 if o:print(n,o.hide_render,o.data.users,[m.name for m in o.data.materials],list(o.matrix_world.translation),[(m.name,m.type) for m in o.modifiers])
for f in [0,75,110,125,135,145,155,170,195,225,250,295,315,340,365,390,415,445,490,989]:
 s.frame_set(f)
 print(f,tuple(round(a,2) for a in ship.matrix_world.translation),tuple(round(a,2) for a in ship.matrix_world@Vector((-7.8,-.17,0))),s.objects['WAKE_RIBBON_0'].hide_render)
print('frame',s.render.engine)

