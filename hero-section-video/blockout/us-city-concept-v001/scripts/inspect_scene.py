"""Read-only scene survey; writes only task review JSON, never a blend."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene
s.frame_set(510)
u=s.objects.get('US_FRAME')
inv=u.matrix_world.inverted() if u else None
rows={}
for o in s.objects:
    p=o.parent
    ancestry=[]
    while p:
        ancestry.append(p.name);p=p.parent
    pts=[inv@o.matrix_world@Vector(p) for p in o.bound_box] if inv and o.type in {'MESH','CURVE','FONT'} else []
    rows[o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,'ancestors':ancestry,'data':o.data.name if o.data else None,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'constraints':[{'type':c.type,'name':c.name,'target':getattr(getattr(c,'target',None),'name',None)} for c in o.constraints],'local_to_US':list(inv@o.matrix_world.translation) if inv else None,'bounds_US':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]] if pts else None,'hidden':[o.hide_render,o.hide_viewport,o.hide_get()],'collections':[c.name for c in o.users_collection]}
out={'file':bpy.data.filepath,'blender':bpy.app.version_string,'scene':s.name,'scenes':list(bpy.data.scenes.keys()),'camera':s.camera.name if s.camera else None,'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base],'markers':[(m.name,m.frame) for m in s.timeline_markers],'render':[s.render.engine,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'objects':rows}
label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'base'
(R/'review'/f'{label}-survey.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='objects'}))
print('OBJECTS',len(rows))
