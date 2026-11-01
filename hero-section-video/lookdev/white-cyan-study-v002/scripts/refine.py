import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;old=R.parent/'white-cyan-study-v001'
record=json.loads((old/'study.json').read_text())
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(bpy.data.filepath)==record['output_sha256']
def signature():
 return hashlib.sha256(repr([(o.name,o.parent.name if o.parent else None,tuple(tuple(row) for row in o.matrix_basis),o.data.name if o.data else None,o.hide_render) for o in S.objects]).encode()).hexdigest()
sig=signature()
def adjust(m,color,rough,metal):
 p=m.node_tree.nodes.get('Principled BSDF');before=dict(color=list(p.inputs['Base Color'].default_value),roughness=p.inputs['Roughness'].default_value,metallic=p.inputs['Metallic'].default_value)
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;m.diffuse_color=(*color,1)
 return before
glass=bpy.data.materials['STUDY | glass'];before=adjust(glass,(.16,.235,.29),.24,.19)
glass.node_tree.nodes.get('Principled BSDF').inputs['Coat Roughness'].default_value=.24
roof=bpy.data.materials['STUDY | roof'].copy();roof.name='STUDY | architectural slate';adjust(roof,(.32,.37,.40),.53,.08)
light=roof.copy();light.name='STUDY | light industrial roof';adjust(light,(.51,.555,.58),.45,.16)
changes=[]
for name,index,source,role in record['assignments']:
 o=S.objects.get(name)
 if not o:continue
 n=source.lower();on=name.lower()
 # Only actual architectural roof surfaces. Existing rails, grills and frame
 # materials sharing the old roof family retain their original light treatment.
 architectural=(any(k in n for k in ['roof','tile']) or ('roof' in on and ('asphalt' in n or on.endswith('_roof'))) or 'mansard' in on) and not any(k in on for k in ['wheel','tire','tyre'])
 industrial='whe | 01 | insulated standing seam roof' in on
 if architectural or industrial:
  o.material_slots[index].link='OBJECT';o.material_slots[index].material=light if industrial else roof
  changes.append((name,index,source,'light industrial roof' if industrial else 'architectural slate'))
assert signature()==sig
out=R/'pnpline-white-cyan-study-v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
report=dict(source=record['output'],source_sha256=record['output_sha256'],output=str(out),output_sha256=sha(out),glass_before=before,glass_after=dict(color=[.16,.235,.29],roughness=.24,metallic=.19),roof_color=[.32,.37,.40],industrial_roof_color=[.51,.555,.58],roof_slots_changed=changes,geometry_transform_signature=sig,scope='Glass surface shading and architectural roof slots only. Water, transparent warehouse observation glass, camera, animation, light and world are unchanged.')
(R/'study.json').write_text(json.dumps(report,indent=2))
print('SAVED',out,'roof slots',len(changes))
