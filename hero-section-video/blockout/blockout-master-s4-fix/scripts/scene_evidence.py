import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
S=bpy.context.scene
def sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()
def matrix(o):return [list(r) for r in o.matrix_world]
def bounds(name):
    root=bpy.data.objects[name]
    meshes=[o for o in [root,*root.children_recursive] if o.type=='MESH' and not o.hide_render and not o.name.startswith('WAKE')]
    p=[world_to_camera_view(S,S.camera,o.matrix_world@Vector(v)) for o in meshes for v in o.bound_box]
    return [min(v.x for v in p),min(v.y for v in p),max(v.x for v in p),max(v.y for v in p)]
def curves(action):
    if not action:return None
    return [[f.data_path,f.array_index,[[list(k.co),k.interpolation,list(k.handle_left),list(k.handle_right)] for k in f.keyframe_points]] for l in action.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves]
def capture():
    S.frame_set(S.frame_start)
    objects=sorted(S.objects,key=lambda o:o.name)
    noncam=[o for o in objects if o.name not in ['CAM_MASTER','CAM_LOOK_TARGET']]
    static={}
    for o in noncam:
        entry={'type':o.type,'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'animation':curves(o.animation_data.action) if o.animation_data else None,'data':o.data.name if o.data else None,'modifiers':[(m.name,m.type) for m in o.modifiers]}
        if o.type=='MESH':entry.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],materials=[m.name if m else None for m in o.data.materials])
        if o.type=='CURVE':entry['splines']=[[[*p.co] for p in sp.points] for sp in o.data.splines]
        static[o.name]=sha(entry)
    mats={m.name:sha({'color':list(m.diffuse_color),'nodes':[(n.name,n.type,[(i.name,list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes] if m.node_tree else None}) for m in bpy.data.materials}
    rows=[]
    for f in range(S.frame_start,S.frame_end+1):
        S.frame_set(f)
        rows.append({'frame':f,'camera':matrix(S.camera),'target':list(bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation),'lens':S.camera.data.lens,'noncamera':sha([[o.name,matrix(o)] for o in noncam]),'ship':matrix(bpy.data.objects['A02_SHIP'])})
    return {'scene':S.name,'metadata':dict(S.items()),'fps':[S.render.fps,S.render.fps_base],'range':[S.frame_start,S.frame_end],'markers':{m.name:m.frame for m in S.timeline_markers},'objects':static,'materials':mats,'camera_clip':[S.camera.data.clip_start,S.camera.data.clip_end],'frames':rows}
if __name__=='__main__':
    out=sys.argv[sys.argv.index('--')+1]
    data=capture();(ROOT/'review'/out).write_text(json.dumps(data,default=str),encoding='utf-8')
    print('CAPTURE',out,'objects',len(data['objects']),'frames',len(data['frames']),'engine',S.render.engine)
