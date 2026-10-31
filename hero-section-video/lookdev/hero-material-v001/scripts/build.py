import bpy,json,math,hashlib,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
source=Path(bpy.data.filepath);survey=json.loads((R/'review/survey.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==survey['sha256']
S.frame_set(0)
def category(name):
 n=name.lower()
 if n=='port ivory':return 'paint'
 if any(w in n for w in ['ocean','water','sf_wave']):return 'water'
 if any(w in n for w in ['glass','glazing','windows']):return 'glass'
 if any(w in n for w in ['rubber']):return 'rubber'
 if any(w in n for w in ['leaf','leaves','foliage','trees','green','pine']):return 'foliage'
 if any(w in n for w in ['grass','lawn']):return 'grass'
 if any(w in n for w in ['wood','bark','timber']):return 'wood'
 if any(w in n for w in ['cardboard','cargo','paper']):return 'paper'
 if 'light'==n.split('_')[-1]:return 'light'
 if any(w in n for w in ['gold','lattice','silver','steel','metal','rail','mullion']):return 'metal'
 if any(w in n for w in ['tile','ceramic','glazed','roof']):return 'ceramic'
 if any(w in n for w in ['asphalt','road']):return 'asphalt'
 if any(w in n for w in ['brick']):return 'brick'
 if any(w in n for w in ['concrete','paving','floor','land','base','edge']):return 'concrete'
 if any(w in n for w in ['stone','ivory','marble','plaster','cream','rock']):return 'stone'
 return 'paint'
# Noise is object-local (not world coordinates); no time or per-frame random input.
# One shared surface group gives coherent broad tint/roughness and subtle micro-normal.
g=bpy.data.node_groups.new('LD_Stable_Surface_v1','ShaderNodeTree')
for name,typ,io in [('Color','NodeSocketColor','INPUT'),('Roughness','NodeSocketFloat','INPUT'),('Scale','NodeSocketFloat','INPUT'),('Relief','NodeSocketFloat','INPUT'),('Color','NodeSocketColor','OUTPUT'),('Roughness','NodeSocketFloat','OUTPUT'),('Normal','NodeSocketVector','OUTPUT')]:g.interface.new_socket(name=name,in_out=io,socket_type=typ)
n=g.nodes;l=g.links;i=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.55
l.new(tc.outputs['Object'],noise.inputs['Vector']);l.new(i.outputs['Scale'],noise.inputs['Scale'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.90,.90,.90,1);ramp.color_ramp.elements[1].color=(1,1,1,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;l.new(i.outputs['Color'],mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Color'])
remap=n.new('ShaderNodeMapRange');remap.inputs['To Min'].default_value=-.025;remap.inputs['To Max'].default_value=.025;l.new(noise.outputs['Fac'],remap.inputs[0]);add=n.new('ShaderNodeMath');add.operation='ADD';l.new(i.outputs['Roughness'],add.inputs[0]);l.new(remap.outputs[0],add.inputs[1]);l.new(add.outputs[0],out.inputs['Roughness'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(i.outputs['Relief'],bump.inputs['Distance']);l.new(bump.outputs[0],out.inputs['Normal'])
settings={'glass':(.24,0,1.5,0),'rubber':(.82,0,8,.004),'foliage':(.66,0,3,.014),'grass':(.88,0,5,.008),'wood':(.65,0,5,.005),'paper':(.78,0,12,.001),'metal':(.29,.9,3,.0004),'ceramic':(.38,0,6,.002),'asphalt':(.87,0,8,.004),'brick':(.77,0,5,.003),'concrete':(.72,0,4,.003),'stone':(.6,0,5,.002),'paint':(.34,0,3,.0007),'light':(.4,0,2,0),'water':(.28,0,1.8,.07)}
report=[]
for m in list(bpy.data.materials):
 old=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.node_tree else None
 color=list(old.inputs['Base Color'].default_value) if old else list(m.diffuse_color)
 if all(abs(v-.8)<.0001 for v in color[:3]) and list(m.diffuse_color)!=color:color=list(m.diffuse_color)
 cat=category(m.name);rough,metal,scale,relief=settings[cat]
 if m.name=='SF_roof':cat='ceramic';rough,metal,scale,relief=settings[cat]
 if m.name in ['UC_NAVY','SF_navy']:color=[.009,.035,.065,1] if m.name=='UC_NAVY' else color
 if cat=='water':color=[.016,.080,.115,1] if 'OCEAN'in m.name else [.012,.052,.066,1]
 if cat=='foliage':color=[v*.76 for v in color[:3]]+[1]
 if cat=='glass':color=[v*.7 for v in color[:3]]+[1]
 m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();p=nt.nodes.new('ShaderNodeBsdfPrincipled');o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(p.outputs['BSDF'],o.inputs['Surface'])
 surf=nt.nodes.new('ShaderNodeGroup');surf.node_tree=g;surf.inputs['Color'].default_value=color;surf.inputs['Roughness'].default_value=rough;surf.inputs['Scale'].default_value=scale;surf.inputs['Relief'].default_value=relief
 for a,b in [('Color','Base Color'),('Roughness','Roughness'),('Normal','Normal')]:nt.links.new(surf.outputs[a],p.inputs[b])
 p.inputs['Metallic'].default_value=metal;p.inputs['IOR'].default_value=1.5
 if cat=='glass':
  p.inputs['IOR'].default_value=1.48;p.inputs['Coat Weight'].default_value=.38;p.inputs['Coat Roughness'].default_value=.21
  # Opaque backed architectural glazing avoids black interiors in solid massing.
  p.inputs['Transmission Weight'].default_value=0
 if cat=='water':p.inputs['IOR'].default_value=1.333;p.inputs['Coat Weight'].default_value=.5;p.inputs['Coat Roughness'].default_value=.25
 if cat=='paint':p.inputs['Coat Weight'].default_value=.22;p.inputs['Coat Roughness'].default_value=.28
 if cat=='foliage':p.inputs['Subsurface Weight'].default_value=.035;p.inputs['Subsurface Radius'].default_value=(.08,.12,.04)
 if cat=='light':p.inputs['Emission Color'].default_value=color;p.inputs['Emission Strength'].default_value=2
 if m.name=='WH_tape':p.inputs['Coat Weight'].default_value=.15
 m.diffuse_color=color;m.roughness=rough;m.metallic=metal
 m['lookdev_family']=cat;m['coordinate_policy']='Self Object coordinates; deterministic 3D Noise; no animated seed';m['asset_origin']='Procedural Blender nodes authored for PNPLINE; no external texture assets'
 report.append(dict(name=m.name,family=cat,color=color,roughness=rough,metallic=metal,noise_scale=scale,bump_distance=relief))
# Split proven shared material usages without touching meshes or face assignments.
assignments=[]
for o in S.objects:
 for slot in o.material_slots:
  m=slot.material
  if not m:continue
  target=None
  if m.name=='SF_roof' and 'window' in o.name.lower():target=bpy.data.materials['SF_glass']
  if m.name=='WH_tape' and 'PALLET' in o.name:target=bpy.data.materials['USD_wood']
  if target:
   slot.link='OBJECT';slot.material=target;assignments.append([o.name,m.name,target.name])
# Corrugated steel normal only on blockout cargo boxes; preserve all logo geometry.
rib_materials={}
for ob in S.objects:
 if not (ob.name.startswith(('P03_DECK_','P03_UPPER_','CN_YARD_STACK_')) or ob.name in ['A01_SIDE_L','A01_SIDE_R','A01_FRONT','A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF']):continue
 for slot in ob.material_slots:
  base=slot.material
  if not base:continue
  if base.name not in rib_materials:
   m=base.copy();m.name='LD_CORRUGATED_'+base.name;nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');surf=next(n for n in nt.nodes if n.type=='GROUP')
   tc=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tc.outputs['Generated'],sep.inputs[0]);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=150;nt.links.new(sep.outputs['X'],mul.inputs[0]);wave=nt.nodes.new('ShaderNodeMath');wave.operation='SINE';nt.links.new(mul.outputs[0],wave.inputs[0]);b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.25;b.inputs['Distance'].default_value=.018;nt.links.new(wave.outputs[0],b.inputs['Height']);nt.links.new(surf.outputs['Normal'],b.inputs['Normal']);nt.links.new(b.outputs[0],p.inputs['Normal']);rib_materials[base.name]=m
  slot.link='OBJECT';slot.material=rib_materials[base.name];assignments.append([ob.name,base.name,slot.material.name])
# Consistent fixed light field, broad warm key and neutral-cool reflection fill.
S.world=bpy.data.worlds.new('LD_Studio_Environment');S.world.use_nodes=True
bg=S.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.70,.79,.88,1);bg.inputs['Strength'].default_value=.45
wn=S.world.node_tree.nodes;wl=S.world.node_tree.links;cam_bg=wn.new('ShaderNodeBackground');cam_bg.inputs['Color'].default_value=(.88,.91,.94,1);cam_bg.inputs['Strength'].default_value=1
lp=wn.new('ShaderNodeLightPath');mix=wn.new('ShaderNodeMixShader');wl.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);wl.new(bg.outputs[0],mix.inputs[1]);wl.new(cam_bg.outputs[0],mix.inputs[2]);wl.new(mix.outputs[0],wn.get('World Output').inputs['Surface'])
S.objects['SF_COMPARISON_KEY'].data.energy=0
for o in S.objects:
 if o.type=='LIGHT' and o.name.startswith('WH_INTERIOR_'):o.data.energy=420;o.data.color=(1,.94,.84)
col=bpy.data.collections.new('LD_LIGHTING');S.collection.children.link(col)
def area(name,location,target,power,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
 ob=bpy.data.objects.new(name,d);col.objects.link(ob);ob.location=location;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
area('LD_CN_KEY',(-225,-55,145),(-120,0,65),170000,95,(1,.91,.79))
area('LD_CN_FILL',(-140,90,155),(-120,0,65),70000,115,(.76,.87,1))
area('LD_US_KEY',(60,-85,250),(80,28,125),200000,105,(1,.92,.82))
area('LD_US_RIM',(180,100,215),(80,28,125),110000,95,(.78,.88,1))
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=128;S.cycles.use_adaptive_sampling=True;S.cycles.adaptive_threshold=.015;S.cycles.adaptive_min_samples=32
S.cycles.use_denoising=True;S.cycles.denoiser='OPENIMAGEDENOISE';S.cycles.seed=29;S.cycles.use_animated_seed=False
S.cycles.max_bounces=6;S.cycles.diffuse_bounces=3;S.cycles.glossy_bounces=4;S.cycles.transmission_bounces=4;S.cycles.transparent_max_bounces=8
S.cycles.sample_clamp_indirect=3;S.cycles.blur_glossy=.7
S.render.resolution_x=1920;S.render.resolution_y=1080;S.render.resolution_percentage=100;S.render.use_file_extension=True;S.render.use_border=False
S.render.film_transparent=False;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='16';S.render.image_settings.compression=20
S.render.use_persistent_data=True;S.render.filter_size=1.5
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.3;S.view_settings.gamma=1
S.render.filepath='//frames/hero_';S['lookdev_version']='hero-material-v001';S['lookdev_source_sha256']=survey['sha256']
S.frame_set(315)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'pnpline-hero-material-v001.blend'))
shutil.copyfile(source.parent/'time-map.json',R/'time-map.json')
(R/'review/material-manifest.json').write_text(json.dumps(dict(materials=report,slot_overrides=assignments,external_assets=[],notes=['Architectural glazing is opaque reflective backed glass for existing solid building massing.','Ocean is opaque layered Fresnel water; no geometry displacement or new water animation.','Procedural color values are scene-linear; scalar roughness and normal are non-color data.']),indent=2))
print('BUILD_COMPLETE',len(report),len(assignments),flush=True)
