import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);ver=candidate.stem.rsplit('-',1)[-1]
s=bpy.context.scene;s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];di=D.matrix_world.inverted()
cfg=json.loads((R/f'review/title-arc-{ver}-config.json').read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def actions():
 return {a.name:digest([[fc.data_path,fc.array_index,fc.extrapolation,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type]for k in fc.keyframe_points]]for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves])for a in bpy.data.actions}
def objects():
 data={}
 for o in bpy.context.scene.objects:
  row={'type':o.type,'parent':o.parent.name if o.parent else None,'basis':list(map(list,o.matrix_basis)),'parent_inverse':list(map(list,o.matrix_parent_inverse)),'hide':o.hide_render,'materials':[m.name if m else None for m in o.data.materials]if hasattr(o.data,'materials')else []}
  if o.type=='MESH':row['v']=[list(v.co)for v in o.data.vertices];row['f']=[list(p.vertices)for p in o.data.polygons]
  if o.type=='CURVE':row['p']=[[[*p.co]for p in sp.points]for sp in o.data.splines];row['r']=o.data.bevel_depth
  if o.type=='CAMERA':row['lens']=o.data.lens;row['shift']=[o.data.shift_x,o.data.shift_y]
  data[o.name]=digest(row)
 return data
def protected_samples():
 s=bpy.context.scene;rows=[]
 for f in range(s.frame_start,s.frame_end+1):
  s.frame_set(f);rows.append([f,*[list(map(list,s.objects[n].matrix_world))for n in ['CAM_MASTER','CAM_LOOK_TARGET','A01_CONTAINER','A02_SHIP','P01_SPREADER','CR_SLEW_JIB']]])
 return digest(rows)
def inside(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if(a.y>p.y)!=(b.y>p.y)and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
def cross(a,b):return a.x*b.y-a.y*b.x
def crosses(poly):
 hits=[];n=len(poly)
 for i in range(n):
  a=poly[i];b=poly[(i+1)%n];e=b-a
  for j in range(i+2,n):
   if i==0 and j==n-1:continue
   c=poly[j];d=poly[(j+1)%n];g=d-c;den=cross(e,g)
   if abs(den)<1e-8:continue
   t=cross(c-a,g)/den;u=cross(c-a,e)/den
   if 1e-6<t<1-1e-6 and 1e-6<u<1-1e-6:hits.append([i,j])
 return hits
def points(name):
 o=s.objects[name];return [di@o.matrix_world@v.co for v in o.data.vertices]
water=points('SF_BASIN_WATER_SURFACE');n=len(water)//2;outer=water[:n];inner=water[n:];coast=points('SF_FRONT_LAND')[:n]
seams=[]
for ring,expected in [(points('SF_FRONT_LAND')[n:],outer),(points('SF_BASIN_OUTER_WALL')[:n],outer),(points('SF_BASIN_OUTER_WALL')[n:],outer),(points('SF_ISLAND_WALL')[:n],inner),(points('SF_ISLAND_TOP'),inner)]:
 seams.append(max(math.hypot(p.x-q.x,p.y-q.y)for p,q in zip(ring,expected)))
def dist(p,a,b):
 d=Vector((b.x-a.x,b.y-a.y));v=Vector((p.x-a.x,p.y-a.y));t=max(0,min(1,v.dot(d)/d.length_squared));return(v-t*d).length
front=[];uv=[]
for p in inner:
 q=world_to_camera_view(s,s.camera,D.matrix_world@Vector((p.x,p.y,1.25)));u=Vector((q.x*2048,(1-q.y)*1156));uv.append(u)
 if 650<u.x<1250 and u.y>548:front.append(p)
widths=[min(dist(p,outer[i],outer[(i+1)%n])for i in range(n))for p in front]
def front_y(x):
 hits=[]
 for a,b in zip(uv,uv[1:]+uv[:1]):
  if min(a.x,b.x)<=x<=max(a.x,b.x)and abs(a.x-b.x)>1e-8:hits.append(a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x))
 return max(hits)
ys={x:front_y(x)for x in [850,950,1050,1150,1230]};slopes=[(ys[b]-ys[a])/(b-a)for a,b in zip(list(ys)[:-1],list(ys)[1:])]
wet={};unsupported={}
for ch in 'CHINA':
 ps=points('SF_CHINA_GOLD_'+ch);z=min(p.z for p in ps);feet=[p for p in ps if p.z<z+.15]
 wet[ch]=sum(inside(p,outer)and not inside(p,inner)for p in feet)
 unsupported[ch]=sum(not inside(p,coast)for p in feet)
angle=math.radians(cfg['yaw_degrees']);center=Vector((cfg['midpoint'][0]+cfg['radius']*math.sin(angle),cfg['midpoint'][1]-cfg['radius']*math.cos(angle)))
roots={ch:s.objects['SF_CHINA_'+ch].location for ch in 'CHINA'}
ends=[math.atan2(roots[ch].x-center.x,roots[ch].y-center.y)for ch in 'CA'];turn=math.degrees(ends[1]-ends[0])
bands={ch:[min(math.hypot(p.x-center.x,p.y-center.y)for p in points('SF_CHINA_GOLD_'+ch)),max(math.hypot(p.x-center.x,p.y-center.y)for p in points('SF_CHINA_GOLD_'+ch))]for ch in 'CHINA'}
tree_out=[]
for j in range(45,105):
 name='SF_TREE_TRUNK.'+str(j).zfill(3);ps=points(name);p=sum(ps,Vector())/len(ps)
 if not inside(p,inner):tree_out.append(name)
tower_out=[]
for o in s.objects:
 if o.type=='EMPTY'and o.name.startswith(('SF_HIGHRISE_','SF_SPHERE_TOWER','SF_OPEN_TOWER','SF_STEP_TOWER','SF_TALLEST_TOWER')):
  feet=[p for child in o.children_recursive if child.type=='MESH'for p in points(child.name)if p.z<1.48]
  if not all(inside(p,inner)for p in feet):tower_out.append(o.name)
aa=actions();after=objects();samples_after=protected_samples()
bpy.ops.wm.open_mainfile(filepath=str(R/'review/layout-proposal-v021.blend'));s=bpy.context.scene;s.frame_set(156);before=objects();ba=actions();samples_before=protected_samples()
allowed={*['SF_CHINA_'+ch for ch in 'CHINA'],*['SF_CHINA_'+tone+'_'+ch for tone in ['RED','GOLD']for ch in 'CHINA'],'SF_CLOUD_LEFT','SF_CLOUD_RIGHT','SF_FRONT_LAND','SF_COAST_FOLDED_FACE','SF_BASIN_WATER_SURFACE','SF_BASIN_OUTER_WALL','SF_ISLAND_TOP','SF_ISLAND_WALL','SF_ISLAND_EDGE',*['SF_HIGHRISE_'+str(i)for i in range(8,14)],*['SF_TREE_'+kind+'.'+str(i).zfill(3)for kind in ['TRUNK','CROWN']for i in range(45,105)]}
changed=[k for k in before.keys()|after.keys()if before.get(k)!=after.get(k)];unexpected=[k for k in changed if k not in allowed]
checks={'all_actions_unchanged':aa==ba,'all_integer_frame_camera_cargo_crane_matrices_unchanged':samples_after==samples_before,'only_authorized_static_elements_changed':not unexpected,'title_end_tangent_enclosed_angle_80':abs(180-turn-80)<.01,'title_common_continuous_arc':all(lo>cfg['radius']-1.35 and hi<cfg['radius']+1.0 for lo,hi in bands.values()),'title_feet_on_dry_bank':not any(wet.values())and not any(unsupported.values()),'both_banks_no_self_intersections':not crosses(inner)and not crosses(outer),'island_inside_basin_and_basin_inside_land':all(inside(p,outer)for p in inner)and all(inside(p,coast)for p in outer),'bank_surface_seams_matched':max(seams)<.0001,'front_channel_width_above_1_5m':min(widths)>1.5,'visible_s_curve_inflection':min(slopes)<slopes[0]-.15 and slopes[-1]>min(slopes)+.15,'all_bank_tree_trunks_supported':not tree_out,'all_highrise_feet_supported':not tower_out}
report={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'action_count':len(aa),'object_count':len(after),'changed_static_objects':changed,'unexpected_changes':unexpected,'title_turn_degrees':turn,'title_enclosed_angle':180-turn,'letter_feet_over_water':wet,'letter_feet_outside_land':unsupported,'front_channel_min_width':min(widths),'max_seam_error':max(seams),'front_curve_y_at_2048px':ys,'front_curve_slopes':slopes,'unsupported_trees':tree_out,'unsupported_towers':tower_out,'sample_scope':'All actions and all integer-frame camera/cargo/ship/spreader/jib transforms against v021. Static bank containment and lower-vertex support checks; rendered appearance reviewed separately.'}
(R/f'review/title-water-verified-{ver}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert all(checks.values())
