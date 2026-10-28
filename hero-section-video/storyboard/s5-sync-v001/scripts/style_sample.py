import bpy,sys,json,math,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from contracts import digest,validate_run,require
r=json.loads((R/'render-record.json').read_text(encoding='utf8'));validate_run(r)
require(digest(bpy.data.filepath)==r['source']['sha256'],'wrong style source')
raw=next(i for i in r['images'] if i['frame']==766)
s=bpy.context.scene;s.frame_set(raw['frame']);require(list(map(list,s.camera.matrix_world))==raw['camera_state']['world_matrix'],'camera changed')
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=r['render']['resolution'][0];s.render.resolution_y=r['render']['resolution'][1];s.render.resolution_percentage=100
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1
m=bpy.data.materials.new('TEMP_STYLE_WHITE');m.use_nodes=True;nodes=m.node_tree.nodes;nodes.clear();emit=nodes.new('ShaderNodeEmission');emit.inputs['Color'].default_value=(1,1,1,1);out=nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(emit.outputs[0],out.inputs['Surface'])
s.view_layers[0].material_override=m
s.render.use_freestyle=True;s.render.line_thickness=1
fs=s.view_layers[0].freestyle_settings
ls=fs.linesets[0] if len(fs.linesets) else fs.linesets.new('Visible contours')
ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True;ls.select_external_contour=True;ls.select_material_boundary=True
ls.linestyle.color=(.025,.025,.025);ls.linestyle.thickness=1.1
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
run=uuid.uuid4().hex[:12];p=R/'line-art'/f'sample-f766-{run}.png';rec={'status':'rendering','purpose':'minimal style sample, not selected final artwork','frame':766,'source':r['source'],'raw_path':raw['path'],'raw_sha256':raw['sha256'],'camera_state':raw['camera_state'],'method':'Blender EEVEE white emission override + Freestyle visible silhouette/border/crease/material edges','style_script_sha256':digest(__file__),'path':str(p),'resolution':r['render']['resolution'],'run_id':run}
rp=R/'line-art'/f'sample-f766-{run}.json';rp.write_text(json.dumps(rec,indent=2),encoding='utf8')
s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
rec.update(status='complete',sha256=digest(p));rp.write_text(json.dumps(rec,indent=2),encoding='utf8');(R/'review/style-sample-record.json').write_text(json.dumps(rec,indent=2),encoding='utf8')
print('STYLE',p,flush=True)
