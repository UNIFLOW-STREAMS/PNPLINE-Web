"""Fit the PNPLINE cab-over fleet to the existing articulation and load interfaces."""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector,geometry
from math import sin,cos,pi

root=Path(__file__).resolve().parents[1]
shipkit=root.parent/'container-ship-v001/scripts'
sys.path.insert(0,str(shipkit))
from shipkit import Parts,finish
s=bpy.context.scene
saved_frame=s.frame_current
s.frame_set(0)
fleet=bpy.data.collections.new('PNPLINE · road fleet')
s.collection.children.link(fleet)
w=s.objects
out=root/'pnpline-fleet-trucks-v001.blend'
assert w.get('VSL_Shell · faired plating') and not w.get('FLT_Inbound cab lacquer')
def P(label,parent):return Parts('FLT_'+label,parent,fleet)
def paint(label,hexcolor,rough,metal=0,coat=0):
    m=finish('fleet '+label,hexcolor,rough,metal,coat)
    m.name='Fleet · '+label
    return m
ivory=paint('Arctic white','F3F4ED',.28,.15,.38)
pearl=paint('Pearl silver','C6D4D7',.31,.55,.23)
blue=paint('Pacific lacquer','12618D',.34,.23,.28)
blue2=paint('Atlantic lacquer','327B9F',.36,.2,.28)
roofpaint=paint('Ocean blue roof','238BB0',.36,.23,.23)
cyan=paint('Signal cyan','08A9D6',.29,.25,.3)
navy=paint('Enamel deep navy','18394C',.36,.24,.2)
glass=paint('Laminated blue glass','254758',.13,.34,.61)
shade=paint('Smoked quarter glass','1A3644',.18,.31,.44)
rubber=paint('Rubber sidewall','252B30',.74)
tread=paint('Tread grooves','172027',.81)
black=paint('Weather seals','202C34',.57,.05)
steel=paint('Graphite frame','41505A',.52,.45)
alloy=paint('Spun alloy','ADBAC0',.28,.73)
bright=paint('Bright edges','E7E6DC',.28,.57)
lamp=paint('Headlight lenses','E2F4F4',.17,.34,.4)
amber=paint('Turn indicators','F2A15D',.25,.16,.45)
red=paint('Brake lenses','B6322D',.24,.12,.45)
logo_c=w['VSL_Raised logo port 1-P'].data.materials[0]
logo_g=w['VSL_Raised logo port 4-L'].data.materials[0]

def solid(p,loop,back,mat):
    off=Vector(back);n=len(loop)
    v=[Vector(q) for q in loop];poly=geometry.tessellate_polygon([v])
    p.add(v+[q+off for q in v],[tuple(t) for t in poly]+[tuple(n+i for i in reversed(t)) for t in poly]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)],mat)
def shell(p,rings,mat):
    n=len(rings[0])
    p.add([v for ring in rings for v in ring],[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]+[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(rings)-1) for j in range(n)],mat)
def deckring(x0,x1,width,z,c):
    return [(x0+c,-width,z),(x1-c,-width,z),(x1,-width+c,z),(x1,width-c,z),(x1-c,width,z),(x0+c,width,z),(x0,width-c,z),(x0,-width+c,z)]
def seal(o):
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
def finishpart(p,bevel=.003):
    obj=p.done(bevel);seal(obj);return obj
def hide(o):
    o.hide_render=True;o.hide_viewport=True
def matset(o,m):
    if o.data.users>1:o.data=o.data.copy()
    o.data.materials.clear();o.data.materials.append(m)

# The two old city cranes have their own foundations and never drive the hook.
removed=[]
for i in range(2):
    base=w[f'CV_CRANE_{i}_US_FRAME']
    items=list(base.children_recursive)+[base,w[f'CV_FOUNDATION_CRANE_{i}']]
    assert len(items)==14 and all(not o.animation_data for o in items)
    removed.extend(o.name for o in items)
    bpy.data.batch_remove(ids=items)

exec(compile((root/'scripts/cab.py').read_text(encoding='utf-8'),'fleet_cab','exec'))
exec(compile((root/'scripts/chassis.py').read_text(encoding='utf-8'),'fleet_chassis','exec'))
exec(compile((root/'scripts/freight.py').read_text(encoding='utf-8'),'fleet_freight','exec'))
s.frame_set(saved_frame)
s['fleet_revision']='fleet-trucks-v001'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(root/'review/build.json').write_text(json.dumps(dict(removed_cranes=removed,objects=[o.name for o in fleet.objects],source_wordmark='resources/logo/PNP-LINE.webp',wheel_objects=wheel_names),indent=2))
