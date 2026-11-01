"""Read-only exact surface-contact and radial support checks for this title revision."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'curvature-rework-v001/scripts'))
from mapping import surface,normal,CENTER
d=json.loads((R/'delivery.json').read_text());s=bpy.context.scene;s.frame_set(349);U=s.objects['US_FRAME'];I=U.matrix_world.inverted();deps=bpy.context.evaluated_depsgraph_get()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(bpy.data.filepath)==d['sha256']
def us(o):
 while o:
  if o.name=='US_FRAME':return True
  o=o.parent
 return False
def visible(o):return not o.hide_render and not all(c.hide_render for c in o.users_collection)
def mesh(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();T=I@ev.matrix_world;v=[T@p.co for p in me.vertices];f=[tuple(p.vertices)for p in me.polygons];ev.to_mesh_clear();return v,f
def bounds(v):return([min(p[i]for p in v)for i in range(3)],[max(p[i]for p in v)for i in range(3)])
def overlap(a,b):return all(a[0][i]<=b[1][i]and b[0][i]<=a[1][i]for i in range(3))
cache={}
def geo(n):
 if n not in cache:
  v,f=mesh(s.objects[n]);cache[n]=(v,f,BVHTree.FromPolygons(v,f))
 return cache[n]
groups=[]
for l in 'USA':groups.append(('UST_LETTER_'+l,{'UST_LETTER_'+l}))
for entry in d['relocations']:
 root=s.objects[entry['root']];members={o.name for o in [root]+list(root.children_recursive)if o.type in {'MESH','CURVE','FONT'}and visible(o)}|set(entry['extras'])
 if root.name=='CE_REAR_SPACE_NEEDLE_ROOT':members.update(d['replacement_supports'])
 groups.append((root.name,members))
obstacles=[]
grounds={'US_LAND_TERRACE','CE_NY_CURVED_LAND'}
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'}or not visible(o)or not us(o)or o.name in grounds:continue
 box=bounds([I@o.matrix_world@Vector(p)for p in o.bound_box]);obstacles.append((o.name,box))
contacts=[];tested=0
for group,members in groups:
 vv=[];ff=[]
 for n in members:
  v,f,t=geo(n);offset=len(vv);vv+=v;ff.extend(tuple(i+offset for i in p)for p in f)
 gb=bounds(vv);tree=BVHTree.FromPolygons(vv,ff)
 for n,b in obstacles:
  if n in members or not overlap(gb,b):continue
  v,f,t=geo(n);pairs=tree.overlap(t);tested+=1
  if pairs:contacts.append({'group':group,'object':n,'face_pairs':len(pairs)})
 print('CONTACT_CHECK',group,'contacts',len(contacts),flush=True)
groundtrees=[geo(n)[2]for n in grounds];support=[]
for row in d['letters']:
 o=s.objects[row['object']];v,f,t=geo(o.name);low=[p for p in v if (p-CENTER).length-140<.70];errors=[];missing=[]
 for p in low:
  n=(p-CENTER).normalized();origin=CENTER+n*210;hits=[g.ray_cast(origin,-n,90)[0]for g in groundtrees];hits=[h for h in hits if h is not None]
  if not hits:missing.append(list(p));continue
  top=max((h-CENTER).length for h in hits);errors.append((p-CENTER).length-top)
 support.append({'letter':row['letter'],'bottom_samples':len(low),'missing_ground':len(missing),'min_offset':min(errors)if errors else None,'max_offset':max(errors)if errors else None})
normals=[]
for entry in d['relocations']:
 o=s.objects[entry['root']];up=(I@o.matrix_world).to_3x3()@Vector((0,0,1));n=normal(*entry['new_anchor'][:2]);normals.append({'root':o.name,'normal_error_degrees':math.degrees(up.normalized().angle(n))})
checks={
 'three_visible_balanced_letters':all(s.objects['UST_LETTER_'+l].type=='MESH'and visible(s.objects['UST_LETTER_'+l])for l in 'USA'),
 'glyph_aspect_widened_60_percent':abs(d['design']['horizontal_to_vertical_scale_ratio']-1.6)<1e-8,
 'continuous_city_wrapping_curve':40<d['design']['arc_degrees']<50 and d['design']['radius']==80,
 'old_letters_plinths_foundations_hidden':len(d['hidden_original_objects'])==9 and all(not visible(s.objects[n])for n in d['hidden_original_objects']),
 'new_letters_have_no_pedestal':not d['design']['plinths']and all('PLINTH'not in o.name for o in s.objects if o.name.startswith('UST_')),
 'letter_feet_touch_actual_curved_ground':all(r['bottom_samples']>0 and not r['missing_ground']and r['min_offset']>-.04 and r['max_offset']<.04 for r in support),
 'no_title_or_relocated_building_intersections':not contacts,
 'relocated_assemblies_follow_earth_normal':all(r['normal_error_degrees']<.08 for r in normals),
 'relocated_geometry_count_preserved':len(d['relocations'])==6,
 'source_and_candidate_files_immutable':sha(d['source'])==d['source_sha256']and sha(bpy.data.filepath)==d['sha256']}
report={'file':bpy.data.filepath,'candidate_sha256':d['sha256'],'source_sha256':d['source_sha256'],'pass':all(checks.values()),'checks':checks,'contacts':contacts,'mesh_pairs_tested':tested,'letter_support':support,'relocation_normals':normals}
(R/'review/geometry-verification.json').write_text(json.dumps(report,indent=2));print('GEOMETRY_RESULT',json.dumps(report),flush=True)
assert report['pass'],'Geometry verification failed'
