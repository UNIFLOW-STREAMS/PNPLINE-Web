"""Human-readable metadata and evidence inventory; no blend modification."""
import json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R.parents[2]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
manifest={'head':'b9353e1c99d046d78df4e7d1dc9db2bbad940515','branch':'main','remote_main_verified_via_github_connector':'b9353e1c99d046d78df4e7d1dc9db2bbad940515','original_path':str(R.parent/'previz-crane-height-v002/master-previz-crane-height-v002.blend'),'source_git_blob':'a291b3ff7fd3aad16ef74ee7f575dce4f4ddc1cd','source_save_commit':'f3e0aacbb1c08e60cb6644df57c02823605179a9','source_sha256':h(R/'inputs/base.blend'),'old_manifest_sha256':'61a08f1be06c6239ba40fcb40ee35628457fb2f4328432e945eb6316156225e6','hash_difference_explanation':'Saved again by f3e0aacb; current disk blob matches checked HEAD. No rollback.','files':{p.name:{'bytes':p.stat().st_size,'sha256':h(p)} for p in (R/'inputs').iterdir() if p.is_file() and p.name != 'manifest.json'},'blender':'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe','version':'5.1.0 adfe2921d5f3','startup':'--background --factory-startup','gui':'No Blender window/process at initial inventory; no GUI state touched','runtime_model':'unknown','reasoning_effort':'unknown','timeline':[0,1392,12],'camera':'CAM_MASTER','reference_priority':'User attachment; repo same-name image differs','set_dressing':'Survey 7262 objects and all surveyed object records match base; not merged or promoted','tracked_modifications_before':False,'untracked_before':'inputs/git-status-before.txt'}
write('inputs/manifest.json',manifest)
ref={
'D01':{'implementation':'UC_LETTER_U/S/A: actual mesh, silver expanded contour and navy inset, beveled thickness','difference':'Arial Black outline approximation. Reference U/S widths and curves are not exact. No external font dependency in saved display geometry.'},
'D02':{'implementation':'UC_STAR_L_1..5 and UC_STAR_R_1..5, individual relief meshes','difference':'World fixed; full pair recognition in main camera is unresolved.'},
'D03':{'implementation':'Folded patinated robe, raised arm, torch flame, seven crown rays, modeled face, tablet, pedestal, island','ratio':'148/344 image pixels = .43023 of central tower; reference body 7.74; chosen body 10.836 (1.4x). Initial assumption, not user-approved scale.','difference':'Procedural sculpt approximation; entire landmark clips in actual arrival camera.'},
 'D04':{'implementation':'Dense six-row grid with varied blocks, central stepped stone tower, tapered glass spire tower','difference':'Facade modules simplified; skyline proportions and density require artistic revision, not accepted solely by object count.'},
'D05':{'implementation':'Dome, ribs, lantern, wings, colonnade, stairs/lawn; red suspension bridge outside arrival corridor','difference':'Civic forecourt compressed to protect functional warehouse. Bridge aligned to existing shoreline, not reference image coordinates.'},
'D06':{'implementation':'Front masonry blocks with window/cornice meshes, yellow taxis, rail wagons, rear facade dressing of existing warehouse','difference':'Existing warehouse remains open cutaway; not replaced with closed concept warehouse. Only safe background rail/transport representation.'},
'D07':{'implementation':'Existing PNPLINE ship and working P02 untouched; two blue-white static gantries, container stacks','difference':'Working gantry retains baseline gold material and simplified rig; reference crane appearance is not fully matched. Decorative booms remain landward to avoid approach.'},
'D08':{'implementation':'All city objects parented within US_FRAME; existing continuous ocean and land terrace unchanged; new island and bridge foundations descend into spherical water','difference':'Existing steep terrace/coast retained. No separate sea plate, studio floor or cloud backdrop.'}}
write('reference-map.json',{'reference_sha256':h(R/'inputs/usa-miniature.png'),'mapping':ref,'status':'Implementation candidate; not artistic acceptance'})
obj=R/'candidate-us-city-concept-v004-object-map.json'
if obj.exists():(R/'object-map.json').write_bytes(obj.read_bytes())
hashes={str(p.relative_to(R)).replace('\\','/'):{'sha256':h(p),'bytes':p.stat().st_size} for p in R.rglob('*') if p.is_file() and p.name!='hashes.json' and '__pycache__' not in str(p)}
write('hashes.json',hashes)
print('MANIFEST_WRITTEN',len(hashes))

