import bpy,sys,json,uuid,datetime,argparse
from pathlib import Path
CODE=Path(__file__).resolve().parent
sys.path.insert(0,str(CODE))
from lineage import digest,require,validate_expression
parser=argparse.ArgumentParser()
for name in ['input','scene','camera','selection','raw-record','output']:parser.add_argument('--'+name,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
B=Path(args.output).resolve();rp_raw=Path(args.raw_record).resolve();sp=Path(args.selection).resolve()
require(Path(args.input).resolve()==Path(bpy.data.filepath).resolve(),'loaded input differs from requested input')
require(B!=Path(args.input).resolve(),'input/output same path')
r=json.loads(rp_raw.read_text(encoding='utf-8'));sel=json.loads(sp.read_text(encoding='utf-8'))
require(args.scene==r['scene'] and args.camera==r['camera'],'requested Scene/Camera mismatch')
require(all(p['status']=='selected' for p in sel['panels']),'frame selection not recorded')
source=Path(bpy.data.filepath);require(digest(source)==r['source']['sha256']==sel['source_sha256'],'wrong source')
s=bpy.data.scenes[r['scene']];bpy.context.window.scene=s;require(s.camera.name==r['camera'],'wrong camera')
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=r['render']['resolution'][0];s.render.resolution_y=r['render']['resolution'][1];s.render.resolution_percentage=100
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1
m=bpy.data.materials.new('TEMP_STYLE_WHITE');m.use_nodes=True;nodes=m.node_tree.nodes;nodes.clear();emit=nodes.new('ShaderNodeEmission');emit.inputs['Color'].default_value=(1,1,1,1);outnode=nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(emit.outputs[0],outnode.inputs['Surface']);s.view_layers[0].material_override=m
s.render.use_freestyle=True;s.render.line_thickness=1
fs=s.view_layers[0].freestyle_settings;ls=fs.linesets[0] if len(fs.linesets) else fs.linesets.new('Visible contours')
ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True;ls.select_external_contour=True;ls.select_material_boundary=True
ls.linestyle.color=(.025,.025,.025);ls.linestyle.thickness=1.1
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
run=uuid.uuid4().hex[:12];folder=B/'line-art'/run;folder.mkdir(exist_ok=False)
record={'status':'rendering','run_id':run,'arguments':vars(args),'source_path':str(source),'source_sha256':digest(source),'scene':s.name,'camera':s.camera.name,'resolution':r['render']['resolution'],'pixel_aspect':r['render']['pixel_aspect'],'selection_sha256':digest(sp),'render_script_sha256':digest(__file__),'lineage_script_sha256':digest(CODE/'lineage.py'),'original_render_record':str(rp_raw),'original_render_record_sha256':digest(rp_raw),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Blender EEVEE white emission override + Freestyle visible silhouette/border/crease/material edges','settings':{'line_thickness':1,'linestyle_thickness':1.1,'color':[.025,.025,.025],'view_transform':'Standard','look':'None','exposure':0,'gamma':1,'border':False,'crop':False},'images':[]}
rp=folder/'record.json'
def save():rp.write_text(json.dumps(record,indent=2),encoding='utf-8')
save()
for p in sel['panels']:
 raw=next(i for i in r['images'] if i['frame']==p['frame']);s.frame_set(p['frame'])
 c={'world_matrix':list(map(list,s.camera.matrix_world)),'lens_mm':s.camera.data.lens,'shift':[s.camera.data.shift_x,s.camera.data.shift_y],'sensor':[s.camera.data.sensor_width,s.camera.data.sensor_height],'type':s.camera.data.type,'clip':[s.camera.data.clip_start,s.camera.data.clip_end]}
 require(c==raw['camera_state'],'camera changed')
 path=folder/f"{p['id']}-f{p['frame']}.png";s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 record['images'].append({'id':p['id'],'frame':p['frame'],'raw_sha256':raw['sha256'],'raw_path':raw['path'],'camera_state':c,'path':str(path),'sha256':digest(path)});save()
require(digest(source)==record['source_sha256'],'original modified')
record['status']='complete';save();validate_expression(record,r,sp)
(B/'line-art-record.json').write_text(rp.read_text(encoding='utf-8'),encoding='utf-8')
print('LINE_ART_COMPLETE',folder,flush=True)
