"""Build the boundary handoff from measured saved-state evidence; never changes Blender."""
import json,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];load=lambda p:json.loads((R/p).read_text(encoding='utf-8-sig'));cfg=load('config.json');d=load('review/after-validation.json');contacts=load('review/contacts.json');frames={row['frame']:row for row in d['rows']};baseline=load('review/baseline-boundary.json');acceptance=load('review/acceptance-result.json');framing=load('review/framing.json')
def velocity(frame,kind,space='world'):
 a=frames[frame-.25][kind][space+'_position'];b=frames[frame+.25][kind][space+'_position'];return [(y-x)*2 for x,y in zip(a,b)]
states={}
for frame in [cfg['boundary'],cfg['handoff']]:
 st=d['states'][str(frame)];ct=next(row for row in contacts if row['frame']==frame)
 for kind in ['camera','target','vehicle']:
  st[kind]['world_velocity_per_frame']=velocity(frame,kind);st[kind]['world_velocity_per_second']=[v*cfg['fps'] for v in velocity(frame,kind)];st[kind]['local_velocity_per_frame']=velocity(frame,kind,'local')
 st['camera']['lens_mm']=st['lens'];st['contacts']=ct;st['hoist_gap']=ct['hoist_bottom']-ct['container_top'];st['doors_closed']=all(abs(v)<1e-5 for angles in ct['doors'].values() for v in angles);st['ship_docked']=all(row['ship_matrix']==contacts[0]['ship_matrix'] for row in contacts);states[str(frame)]=st
departure_gap=max(abs(w['gap']) for row in d['rows'] if row['frame']>=648 for w in row['support']);whole_gap=d['metrics']['wheel_ground_abs_gap_max']
contract=dict(status='Review candidate; user framing choice pending; not approval for full S5 integration',source_sha256=cfg['source_sha256'],blend_sha256=d['sha256'],scene=cfg['scene'],fps=cfg['fps'],timeline=[0,1392],camera='CAM_MASTER',target='CAM_LOOK_TARGET',tractor='A03_TRACTOR',trailer='A03_TRAILER',container='A01_CONTAINER',payload='W01_NEW_PALLET',boundary=cfg['boundary'],next_stage_handoff=cfg['handoff'],edit_windows={'camera':[608,780],'support_and_payload':[608,744],'height_correction':[608,720],'hoist_and_cables':[608,666]},camera_return_complete=780,source_original_restored_from=780,coordinate_system={'local_frame':'US_FRAME','matrix_to_world':baseline['matrix_US'],'forward':'+X','left':'+Y','up':'+Z','container_rear':'-X','quaternion_order':'w,x,y,z','distance_units':'Blender master units; symbolic metres'},states=states,limits={'wheel_support_abs_gap_m':.08,'actual_departure_max_abs_gap_m':departure_gap,'warning':'Polygon tyre and abrupt quay/road step approximation, not exact rigid-body contact or continuous collision certification.'},exclusions=['Original route, timing, steering, doors, dock reverse, S6 and S7 retained. No dock-test asset/animation transplant.','Before edit_start, inherited quay penetration remains in protected source frames.','Single master-derived review candidate; not a user framing selection.'])
(R/'boundary-contract.json').write_text(json.dumps(contract,indent=2),encoding='utf8')
summary=dict(file_sha256=d['sha256'],source_sha256=cfg['source_sha256'],acceptance=acceptance,metrics=d['metrics'],departure_support_max=departure_gap,pre_edit_inherited_support_max=whole_gap,framing=framing,contacts_max_abs_plane_gap=max(abs(v) for row in contacts for v in row['seat_plane_corner_gaps']),visibility=d['visibility'],method=d['sampling'])
(R/'review/validation-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps({k:summary[k] for k in ['acceptance','departure_support_max','contacts_max_abs_plane_gap','framing']},indent=2))
