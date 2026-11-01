import bpy,json,hashlib,math,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
ptr=R.parent/'latest-lookdev.json';prev=json.loads(ptr.read_text())
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(bpy.data.filepath)==prev['sha256']
(R/'source-record.json').write_text(json.dumps(prev,indent=2))
def scene_signature():
 return hashlib.sha256(repr([(o.name,o.parent.name if o.parent else None,tuple(tuple(row) for row in o.matrix_basis),o.data.name if o.data else None,o.hide_render) for o in S.objects]).encode()).hexdigest()
sig=scene_signature()
water_names={'Pacific | painted swells and aerated wake','SF_water','SF_wave','CNX_water'}
def nodesig(m):
 t=m.node_tree
 return repr(([(n.name,n.bl_idname,[(i.name,str(i.default_value[:]) if hasattr(i.default_value,'__len__') else str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in t.nodes],[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in t.links]))
waters={m.name:nodesig(m) for m in bpy.data.materials if m.name in water_names}
palette={
 'porcelain':((.79,.81,.82),.48,.0), 'limestone':((.69,.715,.73),.67,0),
 'foliage':((.84,.86,.85),.82,0), 'roof':((.60,.64,.665),.44,.12),
 'glass':((.41,.49,.535),.26,.23), 'metal':((.63,.68,.71),.30,.48),
 'road':((.48,.515,.54),.80,0), 'joint':((.22,.265,.29),.62,.05),
 'rubber':((.055,.07,.08),.85,0), 'wood':((.24,.26,.265),.78,0),
 'paper':((.63,.605,.555),.78,0), 'cyan':((0,.40724,.75294),.32,.08),
 'ink':((.035,.052,.065),.44,.08), 'light':((.87,.89,.90),.34,0),
}
mats={}
for role,(col,rough,metal) in palette.items():
 m=bpy.data.materials.new('STUDY | '+role);m.use_nodes=True;m.diffuse_color=(*col,1)
 t=m.node_tree;t.nodes.clear();p=t.nodes.new('ShaderNodeBsdfPrincipled');o=t.nodes.new('ShaderNodeOutputMaterial');t.links.new(p.outputs['BSDF'],o.inputs['Surface'])
 p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Coat Weight'].default_value=.14 if role in {'porcelain','cyan','glass'} else 0
 if role=='light':p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=1.3
 if role in {'limestone','road','paper'}:
  tex=t.nodes.new('ShaderNodeTexCoord');n=t.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=11;n.inputs['Detail'].default_value=1.5;t.links.new(tex.outputs['Object'],n.inputs['Vector'])
  b=t.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.10;b.inputs['Distance'].default_value=.001;t.links.new(n.outputs['Fac'],b.inputs['Height']);t.links.new(b.outputs['Normal'],p.inputs['Normal'])
 m['study']='White/cyan architectural miniature. Object-local procedural microtexture; no external resources.'
 mats[role]=m

def role_for(m,o):
 n=m.name.lower();on=o.name.lower()
 # Exact logo split remains modeled; dark LINE reads on the new white hull/container.
 if 'logo cyan' in n or ('fleet' in n and 'signal cyan' in n):return 'cyan'
 if n=='pnpline | white enamel':return 'ink'
 if any(x in on for x in ['logo','brand','letter']):
  if 'cyan' in n or 'blue'==n:return 'cyan'
  if o.type=='FONT' or 'brand' in on:return 'ink'
 if n.startswith('crew'):
  if any(w in n for w in ['ocean','piping','screen']):return 'cyan'
  if any(w in n for w in ['boot','rubber','hair','ink']):return 'joint'
  return 'porcelain'
 # Teal/cyan cargo only; primary crane steel and blue ship hull become white.
 ancestry=on;p=o.parent
 while p:ancestry+=' '+p.name.lower();p=p.parent
 cargo=any(k in ancestry for k in ['container','freight','cargo','traveling box','pt_stack'])
 if cargo and any(w in n for w in ['azure','cobalt','teal','cyan','port blue','pt_blue','sf_blue','atlantic',' blue']):return 'cyan'
 if n=='wh_cyan' and 'conveyor' in on:return 'cyan'
 if any(w in n for w in ['rubber','tire','tyre','outsole','weather seal']):return 'rubber'
 if any(w in n for w in ['glass','glazing','window','screen','glint']):return 'glass'
 if any(w in n for w in ['leaf','leaves','foliage','canopy','pine','spruce','juniper','willow','sea olive','heather']):return 'foliage'
 if any(w in n for w in ['wood','bark','timber','walnut']):return 'wood'
 if any(w in n for w in ['grass','green','lawn','meadow','soil']):return 'limestone'
 if any(w in n for w in ['paper','cardboard','cargo','tape','newcargo']):return 'paper'
 if any(w in n for w in ['asphalt','road']):return 'road'
 if 'light' in n or 'headlamp' in n:return 'light'
 if any(w in n for w in ['roof','tile','joint','mullion','recess','grate','iron','rail']):return 'joint' if 'recess' in n else 'roof'
 if any(w in n for w in ['silver','steel','metal','aluminium','alloy','lattice','brass','gold','trim','frame']):return 'metal'
 if any(w in n for w in ['stone','concrete','paving','brick','sand','granite','slate','rock','base','edge']):return 'limestone'
 return 'porcelain'

changes=[];unassigned=[]
for o in S.objects:
 if o.type not in {'MESH','CURVE','FONT','SURFACE','META'}:continue
 for i,sl in enumerate(o.material_slots):
  m=sl.material
  if m is None:continue
  if m.name in water_names:continue
  if m.name=='WHE | Low iron observation glass':continue
  if m.name.startswith('STUDY | '):continue
  role=role_for(m,o)
  # OBJECT link prevents shared meshes with different roles affecting each other.
  sl.link='OBJECT';sl.material=mats[role];changes.append((o.name,i,m.name,role))
 if len(o.material_slots)==0 and o.type in {'MESH','CURVE'}:
  unassigned.append(o.name)
  # No material slot creation, to preserve shared geometry data in this study.
assert scene_signature()==sig
assert all(nodesig(bpy.data.materials[n])==v for n,v in waters.items())
out=R/'pnpline-white-cyan-study-v001.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
report=dict(output=str(out),source=prev['versioned_copy'],source_sha256=prev['sha256'],output_sha256=sha(out),geometry_transform_signature=sig,water_materials_unchanged=list(waters),slots_replaced=len(changes),unassigned_objects=unassigned,palette=palette,assignments=changes,master_unmodified=sha(prev['file'])==prev['sha256'])
(R/'study.json').write_text(json.dumps(report,indent=2))
print('STUDY SAVED',len(changes),'slots',len(unassigned),'unassigned')
