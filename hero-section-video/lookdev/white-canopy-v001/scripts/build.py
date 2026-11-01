import bpy,bmesh,math,random,re,json,sys
from pathlib import Path
from mathutils import Matrix,Vector
from collections import Counter
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R.parent/'container-ship-v001/scripts'))
from shipkit import Parts,finish
s=bpy.context.scene
w=s.objects
saved=s.frame_current
s.frame_set(0)
def material(name,hex,rough,metal=0):
    m=finish(name,hex,rough,metal)
    m.name=name
    return m
white=material('PNPLINE | white enamel','FFFFFF',.33,.06)
paint=material('A01 | pearl grey','B8BEC2',.37,.13)
for o in w['A01_CONTAINER'].children_recursive:
    if o.hide_render:continue
    for slot in o.material_slots:
        if slot.material and (slot.material.name in ('Fleet · Ocean blue roof','Fleet · Pacific lacquer') or o.name=='A01_FLOOR'):
            slot.link='OBJECT';slot.material=paint
logo_objects=[]
for o in w:
    for slot in o.material_slots:
        if slot.material and (slot.material.name=='VSL • logo silver' or o.name=='WH_LOGO_GRAY'):
            slot.link='OBJECT';slot.material=white;logo_objects.append(o.name)
    if o.type=='FONT' and o.data.body=='PNPLINE':
        if o.data.users>1:o.data=o.data.copy()
        i=len(o.data.materials);o.data.materials.append(white)
        for ch in list(o.data.body_format)[3:]:ch.material_index=i
        logo_objects.append(o.name)
assert len(logo_objects)>=36
col=bpy.data.collections.new('Street planting | porcelain crowns')
s.collection.children.link(col)
bark=material('Street tree | smoked walnut','4A4139',.81)
leaves=material('Street tree | warm porcelain','F5F4F1',.8)
models=[]
for kind in range(2):
    p=Parts('Broad crown' if kind==0 else 'Oval crown',None,col)
    p.rod((0,0,0),(0,0,.55),.016,bark,8,.009)
    for j in range(3):
        t=math.tau*j/3+.22
        dx,dy=math.cos(t),math.sin(t)
        p.rod((0,0,.225+.022*j),(.145*dx,.145*dy,.431),.010,bark,7,.0065)
        p.rod((.145*dx,.145*dy,.431),(.176*dx,.176*dy,.59),.007,bark,7,.004)
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
    bm.verts.ensure_lookup_table();bm.verts.index_update()
    rng=random.Random(486+kind)
    vs=[]
    for v in bm.verts:
        x,y,z=v.co
        jitter=rng.uniform(.92,1.075)
        k=.395 if kind==0 else .266
        vs.append(((x*jitter+.045*y+.055*z)*k,(y*jitter-.035*x)*k*(.91 if kind==0 else .98),.673+z*.327*jitter))
    zmin=min(v[2] for v in vs);zmax=max(v[2] for v in vs)
    vs=[(x,y,.351+(z-zmin)*.649/(zmax-zmin)) for x,y,z in vs]
    p.add(vs,[tuple(v.index for v in f.verts) for f in bm.faces],leaves);bm.free()
    ob=p.done();models.append(ob.data);bpy.data.objects.remove(ob,do_unlink=True)
rng=random.Random(17083);counts=Counter();groups=Counter()
def plant(label,parent,base,up,height,width=None):
    idx=rng.randrange(2);me=models[idx]
    o=bpy.data.objects.new('WC | '+label,me);col.objects.link(o);o.parent=parent
    size=min(height,width/.79) if width else height
    o.matrix_basis=Matrix.Translation(base)@Vector((0,0,1)).rotation_difference(up.normalized()).to_matrix().to_4x4()@Matrix.Rotation(rng.random()*math.tau,4,'Z')@Matrix.Diagonal(Vector((size,size,height,1)))
    counts[me.name]+=1;groups[label.split('_')[0]]+=1
def retire(objs):
    for o in objs:o.hide_render=True;o.hide_viewport=True
def avg(v):return sum(v,Vector())/len(v)
up=Vector((0,0,1))
for o in list(w):
    if not re.fullmatch(r'(DSP_TREE_\d+|(SHD|USD)_GAP_TREE_\d+_ROOT)',o.name):continue
    old=[x for x in o.children if x.type=='MESH' and not x.hide_render and 'TREEBED' not in x.name]
    if not old:continue
    corners=[o.matrix_world.inverted()@x.matrix_world@Vector(v) for x in old for v in x.bound_box]
    height=max(v.z for v in corners)
    width=max(v.x for v in corners)-min(v.x for v in corners)
    plant(o.name,o,Vector(),up,height,width*1.04);retire(old)
for prefix in ('SF','DT','NA','UC'):
    stems=[o for o in w if o.name.split('.')[0]==prefix+'_TREE_TRUNK' and not o.hide_render]
    crowns=[o for o in w if o.name.split('.')[0]==prefix+'_TREE_CROWN' and not o.hide_render]
    def center(o):return o.matrix_world@avg([Vector(p) for p in o.bound_box])
    sets={o:[] for o in stems}
    for c in crowns:sets[min(stems,key=lambda o:(center(o)-center(c)).length)].append(c)
    for stem,heads in sets.items():
        verts=[v.co.copy() for v in stem.data.vertices];k=len(verts)//2
        base=avg(verts[:k]);axis=(avg(verts[k:])-base).normalized()
        inv=stem.matrix_world.inverted()
        verts2=[inv@c.matrix_world@v.co for c in heads for v in c.data.vertices]
        h=max(((p-base).dot(axis) for p in verts2),default=(avg(verts[k:])-base).length*1.6)
        # Local vertices may be pre-transformed; parent to original space, not to retired geometry.
        T=stem.matrix_local
        normal=T.to_3x3()@axis
        plant(stem.name,stem.parent,T@base,normal,h*normal.length)
    retire(stems+crowns)
for name,k,ratio,foliage in [('CNX_STREET_TREES_wood',6,1.48/.78,['CNX_STREET_TREES_green']),('CE_STREET_FURNITURE_bark',4,2.7/1.2,['CE_STREET_FURNITURE_leaf','CE_STREET_FURNITURE_pine'])]:
    ob=w[name];verts=[ob.matrix_local@v.co for v in ob.data.vertices]
    assert len(verts)%(2*k)==0
    for j in range(0,len(verts),2*k):
        base=avg(verts[j:j+k]);axis=avg(verts[j+k:j+2*k])-base
        plant(name+'_'+str(j//(2*k)),ob.parent,base,axis,axis.length*ratio)
    retire([ob]+[w[n] for n in foliage])
s.frame_set(saved)
s['street_tree_revision']='white-canopy-v001'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'pnpline-white-canopy-v001.blend'),compress=True)
report={'types':dict(counts),'districts':dict(groups),'logo_objects':logo_objects,'total_trees':sum(counts.values())}
(R/'review/build.json').write_text(json.dumps(report,indent=2))
print(report)
