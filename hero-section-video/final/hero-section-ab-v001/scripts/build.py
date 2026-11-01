"""Adopt the final presentation scene and restore each approved material variant."""
import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from state import sha,snapshot,presentation,hashed
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
records={n:json.loads((R/'audit'/f'{n}.json').read_text()) for n in ['source-A','source-B','presentation-source']}
P=records['presentation-source'];assert sha(bpy.data.filepath)==P['sha256']
for name in ['source-A','source-B']:
 for field in ['objects','geometry','non_dof_actions','camera_990','timing']:
  assert hashed(records[name]['snapshot'][field])==hashed(P['snapshot'][field]),(name,field)
assert records['source-A']['snapshot']['materials']==P['snapshot']['materials']
assert records['source-A']['snapshot']['slots']==P['snapshot']['slots']
bpy.context.preferences.filepaths.save_version=0
reports={}
def adopt(label):
 expected=records['source-'+label]['snapshot'];current=snapshot();present=presentation()
 checks={field:hashed(current[field])==hashed(expected[field]) for field in ['objects','geometry','non_dof_actions','slots','materials','camera_990','timing']}
 checks['dof_990_exact']=hashed(current['dof_990'])==hashed(P['snapshot']['dof_990'])
 checks['lighting_world_gradient_color_exact']=hashed(present)==hashed(P['presentation'])
 checks['packed_gradient']=all(x['packed'] for x in present['gradient']) and bool(present['gradient'])
 assert all(checks.values()),checks
 S['hero_section_variant']=label;S['hero_material_source']=records['source-'+label]['file'];S['hero_presentation_source']=P['file'];S['hero_adopted_date']='2026-11-02'
 S.frame_set(132);S.render.filepath=f'//renders/{label}/hero-'
 out=R/f'hero-section-{label}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
 reports[label]=dict(file=str(out),sha256=sha(out),checks=checks,material_source=records['source-'+label]['file'],material_source_sha256=records['source-'+label]['sha256'],presentation_source=P['file'],presentation_source_sha256=P['sha256'],camera_990_hash=hashed(current['camera_990']),dof_990_hash=hashed(current['dof_990']),presentation_hash=hashed(present),frame_start=S.frame_start,frame_end=S.frame_end,fps=S.render.fps,production_render=dict(engine=S.render.engine,width=S.render.resolution_x,height=S.render.resolution_y,percentage=S.render.resolution_percentage,samples=S.cycles.samples),packed_images=[i.name for i in bpy.data.images if i.packed_file],missing_images=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and i.filepath and not Path(bpy.path.abspath(i.filepath)).is_file()])
 (R/'build-verification.json').write_text(json.dumps(reports,indent=2));print('ADOPTED',label,'ALL CHECKS PASS',flush=True)
adopt('A')
B=records['source-B'];new_names=[name for name in B['snapshot']['materials'] if name not in bpy.data.materials]
with bpy.data.libraries.load(B['file'],link=False) as (available,loaded):
 assert set(new_names)<=set(available.materials)
 loaded.materials=new_names
for name,slots in B['snapshot']['slots'].items():
 o=S.objects[name];assert len(o.material_slots)==len(slots)
 for i,(link,mat) in enumerate(slots):
  sl=o.material_slots[i];sl.link=link;sl.material=bpy.data.materials[mat] if mat else None
adopt('B')
