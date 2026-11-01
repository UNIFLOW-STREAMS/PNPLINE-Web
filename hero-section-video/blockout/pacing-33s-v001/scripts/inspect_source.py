import bpy, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = bpy.context.scene
def curves(action):
    return [f for l in action.layers for st in l.strips for b in st.channelbags for f in b.fcurves]

ids = []
for prop in bpy.data.bl_rna.properties:
    if prop.type == 'COLLECTION':
        for block in getattr(bpy.data, prop.identifier):
            if hasattr(block, 'animation_data'):
                ids.append(block)
data = {'source': bpy.data.filepath, 'range': [s.frame_start,s.frame_end],
        'fps':s.render.fps/s.render.fps_base, 'objects':len(s.objects),
        'markers':[(m.name,m.frame) for m in s.timeline_markers],
        'handlers':{k:[str(x) for x in getattr(bpy.app.handlers,k)] for k in ['frame_change_pre','frame_change_post']},
        'animated_ids':[], 'actions':[], 'simulations':[]}
for block in ids:
    ad=block.animation_data
    if not ad: continue
    data['animated_ids'].append({'name':block.name, 'type':block.bl_rna.identifier,
        'action':ad.action.name if ad.action else None,
        'drivers':[(f.data_path,f.driver.expression) for f in ad.drivers],
        'nla':[t.name for t in ad.nla_tracks]})
for a in bpy.data.actions:
    fs=curves(a)
    data['actions'].append({'name':a.name,'users':a.users,'curves':len(fs),
        'paths':sorted(set(f.data_path for f in fs)),
        'range':list(a.frame_range),'modifiers':[(f.data_path,[m.type for m in f.modifiers]) for f in fs if f.modifiers],
        'keys':sorted(set(round(k.co.x,4) for f in fs for k in f.keyframe_points)) if len(fs)<25 else []})
for o in s.objects:
    if o.rigid_body or o.particle_systems or any(m.type in ['FLUID','CLOTH','SOFT_BODY'] for m in o.modifiers):
        data['simulations'].append(o.name)
(ROOT/'review/source-inventory.json').write_text(json.dumps(data,indent=2))
print(json.dumps({k:v for k,v in data.items() if k not in ['actions','animated_ids']},indent=2))
print('ANIMATED_IDS',len(data['animated_ids']),'ACTIONS',len(data['actions']))
print('DRIVERS',[(x['name'],x['drivers']) for x in data['animated_ids'] if x['drivers']])
print('NLA',[(x['name'],x['nla']) for x in data['animated_ids'] if x['nla']])
