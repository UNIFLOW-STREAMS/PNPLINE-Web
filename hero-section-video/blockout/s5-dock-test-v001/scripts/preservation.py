"""Semantic signatures for the original Scene, including every evaluated frame."""
import bpy,json,hashlib,sys,argparse
from pathlib import Path
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def props(block):
 out={}
 for p in block.bl_rna.properties:
  if p.identifier in ['rna_type','name','name_full','users','session_uid','is_updated','is_updated_data','is_evaluated','original','id_data']:continue
  if p.type in ['BOOLEAN','INT','FLOAT','STRING','ENUM']:
   try:
    v=getattr(block,p.identifier);out[p.identifier]=list(v) if p.is_array or isinstance(v,set) else v
   except (AttributeError,TypeError):pass
 return out
def action(ad):
 if not ad or not ad.action:return None
 return [[fc.data_path,fc.array_index,[[list(k.co),k.interpolation,list(k.handle_left),list(k.handle_right)] for k in fc.keyframe_points]] for l in ad.action.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]
def capture(scene):
 bpy.context.window.scene=scene;old=scene.frame_current;scene.frame_set(scene.frame_start);objects=sorted(scene.objects,key=lambda o:o.name);static={};materials={}
 for o in objects:
  d=dict(props=props(o),parent=o.parent.name if o.parent else None,parent_inverse=[list(r) for r in o.matrix_parent_inverse],metadata=dict(o.items()),action=action(o.animation_data),data_name=o.data.name if o.data else None,hide=o.hide_get(),collections=sorted(c.name for c in o.users_collection))
  if o.data:
   d['data_props']=props(o.data);d['data_action']=action(getattr(o.data,'animation_data',None))
   if o.type=='MESH':d['mesh']=[[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]]
   if o.type in ['CURVE','FONT']:d['splines']=[[[*p.co] for p in sp.points] for sp in o.data.splines]
   for mat in getattr(o.data,'materials',[]):
    if mat:materials[mat.name]=sha(dict(props=props(mat),nodes=[(n.name,props(n),[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in mat.node_tree.nodes] if mat.node_tree else None))
  static[o.name]=sha(d)
 rows=[]
 for f in range(scene.frame_start,scene.frame_end+1):
  scene.frame_set(f);rows.append(dict(frame=f,hash=sha([[o.name,[list(r) for r in o.matrix_world],o.hide_render,props(o.data) if o.type=='CAMERA' else None] for o in objects])))
 scene.frame_set(old)
 return dict(scene=scene.name,objects=static,materials=materials,frames=rows,render=props(scene.render),display=props(scene.display.shading),world=props(scene.world),markers=[(m.name,m.frame) for m in scene.timeline_markers],range=[scene.frame_start,scene.frame_end],metadata=dict(scene.items()),camera=scene.camera.name)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);result=capture(bpy.data.scenes[a.scene]);Path(a.output).write_text(json.dumps(result),encoding='utf8');print('SIGNATURE',sha(result),len(result['objects']),len(result['frames']))
