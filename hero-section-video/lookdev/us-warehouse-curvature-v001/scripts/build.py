import bpy,bmesh,sys,json,re
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout'
sys.path[:0]=[str(R/'scripts'),str(B/'curvature-rework-v001/scripts')]
from surface_site import *

s=bpy.context.scene
opened_frame=s.frame_current
u=s.objects['US_FRAME']
s.frame_set(0);ui=u.matrix_world.inverted()
old={o.name:o.matrix_world.copy() for o in s.objects}
report=dict(removed=[],warehouse=[],terrain=[],rear=[],street_roots=[],motion=[])
tracks=np.load(R/'review/motion-fit.npz')
def under(o,names):
    while o:
        if o.name in names:return True
        o=o.parent
    return False

def discard(o):
    report['removed'].append(o.name)
    bpy.data.objects.remove(o,do_unlink=True)

def coordinates(mesh):
    a=np.empty(3*len(mesh.vertices),dtype=np.float32)
    mesh.vertices.foreach_get('co',a)
    return a.reshape(-1,3).astype(float)

def deform(o,fn,refine=False):
    """Keep UVs, materials, procedural coordinates and original object hierarchy."""
    d=o.data.copy();o.data=d
    m=np.asarray(ui@old[o.name]);v=coordinates(d)
    if refine and len(v):
        p=transform(WI,transform(m,v))
        if max(np.ptp(p[:,:2],axis=0))>1.4:
            # Split only edges spanning ground distance; vertical columns stay straight.
            bm=bmesh.new();bm.from_mesh(d)
            to_flat=Matrix((WI@m).tolist())
            bm.transform(to_flat)
            bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
            for level in range(7):
                edges=[e for e in bm.edges if (e.verts[0].co.xy-e.verts[1].co.xy).length>1.35]
                if not edges:break
                bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
            bm.transform(to_flat.inverted());bm.to_mesh(d);bm.free()
            v=coordinates(d)
    out=transform(np.linalg.inv(m),fn(transform(m,v)))
    assert np.isfinite(out).all(),o.name
    d.vertices.foreach_set('co',out.astype(np.float32).ravel());d.update()

def displace_root(o,delta):
    parent_old=old[o.parent.name] if o.parent else Matrix.Identity(4)
    par=ui@parent_old
    o.matrix_parent_inverse=par.inverted()@Matrix(delta.tolist())@par@o.matrix_parent_inverse

roots=set(tracks.files)
for group in ('CV_WH_US_FRAME','CV_WH_WORLD','DSP_WAREHOUSE_DETAIL_ROOT','DSP_APRON_ROOT'):
    for o in list(s.objects[group].children_recursive):
        if under(o,roots):continue
        if o.type=='MESH':
            deform(o,warehouse,True)
        elif o.type=='FONT':
            # Preserve editable text and original font data; use its center for tangent.
            co=(ui@old[o.name])@(sum((Vector(p) for p in o.bound_box),Vector())/8)
            displace_root(o,wh_rigid(np.asarray(co)))
        elif o.type=='LIGHT':
            displace_root(o,wh_rigid(np.array((ui@old[o.name]).translation)))
        elif o.type=='EMPTY':continue
        else:raise ValueError((o.name,o.type))
        report['warehouse'].append(o.name)
print('WAREHOUSE',len(report['warehouse']),flush=True)

for o in [o for o in s.objects if o.get('ce_role')=='building_root']:
    name=o.name
    if not name.startswith('CE_') or o.get('ce_role')!='building_root':continue
    x,y,_=o['ce_anchor']
    if not (name.startswith('CE_REAR_') or 26<=x<=86 and 39<=y<=62):continue
    fd=s.objects.get(name[:-5]+'_FOUNDATION')
    if not fd:continue
    # Seat the bottom corners into the radial grade as well as the center.
    m=np.asarray(ui@old[fd.name]);pts=transform(m,coordinates(fd.data))
    rad=np.linalg.norm(pts-C,axis=1);spread=max(np.linalg.norm(v-pts[:4].mean(0)) for v in pts[:4])
    seat=.68-(spread**2)/(2*140)-.007
    oldpos=np.array((ui@old[name]).translation);q=arc(oldpos);q[2]=seat
    displace_root(o,correction(np.eye(3),oldpos,sphere(q)))
    o['ce_anchor']=[x,y,seat];discard(fd);report['rear'].append(name)

for name in ['CV_FOUNDATION_WAREHOUSE','CV_SUPPORT_MANEUVER','CV_SUPPORT_E09_MANEUVER_YARD',
             'CV_SUPPORT_E11_ROUTE_1','CV_SUPPORT_E11_ROUTE_-1','CV_SUPPORT_A05_WAIT_MERGE',
             *['CV_FOUNDATION_E12_DESTINATION_'+str(i) for i in range(4)]]:
    if name in s.objects:discard(s.objects[name])

def grade_mesh(v):return new_grade(recover(v))
for o in list(u.children):
    n=o.name
    if n.startswith(('E07_','E11_ROUTE','E09_MANEUVER','A05_WAIT_MERGE')) or n=='US_YARD_ROAD':
        if o.type=='MESH':
            deform(o,grade_mesh);report['terrain'].append(n)
        elif o.type=='CURVE':
            d=o.data.copy();o.data=d
            for sp in d.splines:
                for pt in sp.points:pt.co=(*grade_mesh(np.array(pt.co[:3])),pt.co.w)
            report['terrain'].append(n)
    if n.startswith('DSP_') and n not in ('DSP_WAREHOUSE_DETAIL_ROOT','DSP_APRON_ROOT'):
        if n.endswith('_FOUNDATION'):
            discard(o);continue
        if o.type=='EMPTY':
            loc=np.array((ui@old[n]).translation)
            displace_root(o,grade_rigid(loc,-.064 if re.fullmatch('DSP_B[0-9]+_ROOT',n) else 0.))
            report['street_roots'].append(n)
        elif o.type=='MESH':
            if n=='DSP_GROUND_EDGE':
                def edge(v):
                    v=v.copy();p=recover(v[::2]);p[:,2]=.703
                    v[::2]=new_grade(p);return v
                deform(o,edge)
            elif n=='DSP_CONTINUOUS_GROUND':
                def ground(v):
                    p=recover(v);p[:,2]=.703;return new_grade(p)
                deform(o,ground)
            else:deform(o,grade_mesh)
            report['terrain'].append(n)

# The engineered port approach still joins a flat berth outside the requested
# district. Retain the apron lip there and end its edge flush with city grade.
for name in ('CV_SUPPORT_E07_INBOUND_ROAD','CV_SUPPORT_US_YARD_ROAD'):
    o=s.objects.get(name)
    if not o:continue
    def embankment(v):
        out=v.copy();mid=len(v)//2
        out[:mid]=grade_mesh(v[:mid]);return out
    deform(o,embankment);report['terrain'].append(name)

collection=bpy.data.collections.new('Warehouse • spherical motion corrections')
s.collection.children.link(collection)
for name in tracks.files:
    o=s.objects[name];wrapper=bpy.data.objects.new('SURF_'+name,None)
    collection.objects.link(wrapper);wrapper.parent=o.parent;wrapper.empty_display_size=.15
    inv=o.matrix_parent_inverse.copy();bas=o.matrix_basis.copy()
    o.parent=wrapper;o.matrix_parent_inverse=inv;o.matrix_basis=bas
    seq=tracks[name]
    wrapper.rotation_mode='QUATERNION'
    # Static sections share two end keys. Retain every varying native-frame sample.
    changed=np.max(abs(np.diff(seq,axis=0)),axis=(1,2))>1.e-8
    times=np.unique(np.r_[0,np.where(changed)[0],np.where(changed)[0]+1,len(seq)-1])
    if not changed.any():times=np.array([0])
    last=None
    for i in times:
        m=Matrix(seq[i].tolist());q=m.to_quaternion()
        if last is not None:q.make_compatible(last)
        wrapper.location=m.translation;wrapper.rotation_quaternion=q;last=q.copy()
        if len(times)>1:
            wrapper.keyframe_insert('location',frame=int(i),group='Surface compensation')
            wrapper.keyframe_insert('rotation_quaternion',frame=int(i),group='Surface compensation')
    if wrapper.animation_data:
        for layer in wrapper.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:k.interpolation='LINEAR'
    report['motion'].append(name)
s.frame_set(opened_frame)
report['original_saved_frame']=opened_frame
s['us_warehouse_surface_revision']='us-warehouse-curvature-v001'
bpy.context.preferences.filepaths.save_version=0
out=R/'pnpline-us-warehouse-curvature-v001.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'review/build.json').write_text(json.dumps(report,indent=2))
print('SAVED',str(out),{k:len(v) for k,v in report.items() if isinstance(v,list)},flush=True)
