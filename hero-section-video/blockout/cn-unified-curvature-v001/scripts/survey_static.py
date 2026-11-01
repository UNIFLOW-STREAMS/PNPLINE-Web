"""Read-only grouping inventory for rigid radial relocation in SF_CN_LAYOUT space."""
import bpy,json,hashlib,sys,math,re
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT.parent/'cn-city-expansion-v001/pnpline-cn-city-expansion-v001.blend'
SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
EXPECTED=json.loads((SOURCE.parent/'delivery.json').read_text(encoding='utf-8'))['sha256']
assert SHA==EXPECTED,(SHA,EXPECTED)
if Path(bpy.data.filepath)!=SOURCE:bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene;s.frame_set(0);s.view_layers[0].update()
D=s.objects['SF_CN_LAYOUT'];I=D.matrix_world.inverted()
def vec(v):return [round(float(x),6)for x in v]
def mat(m):return [[round(float(v),9)for v in r]for r in m]
def lineage(o):
 out=[]
 while o:out.append(o.name);o=o.parent
 return out
def bounds(o):
 if o.type not in {'MESH','CURVE','FONT','SURFACE','META'}:return None
 T=I@o.matrix_world
 pts=[T@Vector(v)for v in o.bound_box]
 return {'min':vec([min(p[a]for p in pts)for a in range(3)]),'max':vec([max(p[a]for p in pts)for a in range(3)])}
def anim(o):
 ad=o.animation_data
 return {'action':ad.action.name if ad and ad.action else None,'drivers':len(ad.drivers)if ad else 0,
         'constraints':[{'name':c.name,'type':c.type,'target':getattr(getattr(c,'target',None),'name',None)}for c in o.constraints]}

nodes={};allroots=Counter();parentcounts=Counter()
for o in s.objects:
 chain=lineage(o);allroots[chain[-1]]+=1
 cn=('CN_FRAME'in chain or 'SF_CN_LAYOUT'in chain or 'PORT_MODEL_ROOT'in chain or o.name.startswith('CNX_'))
 if not cn:continue
 row={'type':o.type,'parent':o.parent.name if o.parent else None,'lineage':chain,
      'origin':vec((I@o.matrix_world).translation),'matrix':mat(I@o.matrix_world),'bounds':bounds(o),
      'hidden_render':o.hide_render,'hidden_viewport':o.hide_viewport,'collections':[c.name for c in o.users_collection],
      'properties':{k:o[k] for k in o.keys()if k.startswith(('cnx_','port_')) and isinstance(o[k],(str,int,float))},
      'animation':anim(o),'vertices':len(o.data.vertices)if o.type=='MESH'else None}
 nodes[o.name]=row;parentcounts[row['parent']]+=1

def merged(names):
 bs=[nodes[n]['bounds']for n in names if nodes[n]['bounds']]
 return {'min':[min(b['min'][a]for b in bs)for a in range(3)],'max':[max(b['max'][a]for b in bs)for a in range(3)]}if bs else None
def descend(root):return [n for n,r in nodes.items()if root in r['lineage']]
def visible(names):return [n for n in names if nodes[n]['bounds']and not nodes[n]['hidden_render']]
def feet(names):
 bb=merged(visible(names));z=bb['min'][2]
 points=[]
 for n in visible(names):
  o=s.objects[n];T=I@o.matrix_world
  if o.type=='MESH':points.extend(p for v in o.data.vertices if (p:=T@v.co).z<=z+.045)
 if not points:return [(bb['min'][0]+bb['max'][0])/2,(bb['min'][1]+bb['max'][1])/2,z]
 return [(min(p[a]for p in points)+max(p[a]for p in points))/2 for a in range(2)]+[z]
clusters=[];covered=set();surfaces=[];components=[];special=[]
def cluster(key,names,roots=None,anchor=None,rule='foot_support_bbox',category='static_structure'):
 names=sorted(set(names));vis=visible(names)
 if not vis:return
 bb=merged(vis);anchor=anchor or feet(vis)
 row={'id':key,'category':category,'roots':roots or [],'objects':names,'visible_geometry':vis,
      'anchor':vec(anchor),'anchor_rule':rule,'bounds':bb,'mesh_deformation_allowed':False,
      'animation_objects':[n for n in names if nodes[n]['animation']['action']or nodes[n]['animation']['drivers']or nodes[n]['animation']['constraints']]}
 if len(roots or [])==1:
  root=roots[0];row['original_root_matrix']=nodes[root]['matrix'];row['original_up']=vec((I@s.objects[root].matrix_world).to_3x3()@Vector((0,0,1)))
 clusters.append(row);covered.update(names)

excluded={'SF_WHITE_COAST','SF_INTERNAL_WATER','PORT_MODEL_ROOT','PORT_CRANE_PLACEMENT'}
for n,r in nodes.items():
 if r['type']!='EMPTY'or r['parent']!='SF_CN_LAYOUT'or n in excluded:continue
 names=descend(n)
 if not visible(names):continue
 if n.startswith('CNX_'):
  anchor=r['origin'];rule='existing_cnx_root_ground_frame';cat='cnx_landmark'if r['properties'].get('cnx_role')=='landmark'else 'cnx_building'
 elif n.startswith('SF_CHINA_'):
  anchor=r['origin'];rule='letter_baseline_origin';cat='title_letter'
 elif n.startswith('SF_CLOUD_'):
  anchor=[r['origin'][0],r['origin'][1],1.249988];rule='ground_below_floating_cloud_preserve_vertical_offset';cat='floating_cloud'
 else:
  anchor=feet(names);rule='foot_support_bbox';cat='original_building_or_structure'
 cluster(n,names,[n],anchor,rule,cat)

stacks=defaultdict(list)
for n,r in nodes.items():
 if r['parent']!='PORT_MODEL_ROOT'or r['type']!='EMPTY':continue
 if n.startswith('PORT_CONTAINER_'):stacks[(round(r['origin'][0],3),round(r['origin'][1],3))].append(n);continue
 names=descend(n);anchor=feet(names)
 if n=='PORT_COMPANION_CRANE_0':anchor=[-19,-10.425,1.254985]
 if n=='PORT_COMPANION_CRANE_1':anchor=[-3,-10.425,1.254985]
 cluster(n,names,[n],anchor,category='port_crane'if'CRANE'in n else'port_vehicle')
for index,((x,y),roots)in enumerate(sorted(stacks.items())):
 names=[n for root in roots for n in descend(root)]
 z=merged(visible(names))['min'][2]
 cluster('PORT_CONTAINER_STACK_%03d'%index,names,roots,[x,y,z],'shared_bottom_anchor_for_vertical_stack','container_stack')

def remaining(prefix):return [n for n,r in nodes.items()if n.startswith(prefix)and n not in covered and r['bounds']and not r['hidden_render']]
def center(n):
 b=nodes[n]['bounds'];return [(a+z)/2 for a,z in zip(b['min'],b['max'])]
def nearest_groups(base_prefix,part_prefixes,label):
 bases=remaining(base_prefix);assigned={n:[n]for n in bases}
 for prefix in part_prefixes:
  for n in remaining(prefix):
   p=center(n);base=min(bases,key=lambda b:sum((center(b)[a]-p[a])**2 for a in (0,1)))
   assigned[base].append(n)
 for n,names in assigned.items():cluster(label+'_'+n,names,category=label)
nearest_groups('SF_TREE_TRUNK',['SF_TREE_CROWN'],'tree')
def suffix_index(name):return int(name.rsplit('.',1)[1])if '.'in name else 0
# Original refine_c_district.py creates one trunk then exactly five crowns;
# one neighboring crown overlaps in XY, so use the verified construction order.
trunks=sorted(remaining('DT_TREE_TRUNK'),key=suffix_index)
crowns=sorted(remaining('DT_TREE_CROWN'),key=suffix_index)
assert len(crowns)==5*len(trunks)
for j,n in enumerate(trunks):
 parts=[n]+crowns[j*5:(j+1)*5]
 assert max(math.dist(center(n)[:2],center(p)[:2])for p in parts)<.4
 cluster('tree_'+n,parts,rule='five_crowns_per_trunk_verified_from_source_generation_order',category='tree')
for base,parts,label in [('DT_STREET_LAMP',['DT_STREET_LAMP_GLASS'],'street_lamp'),('NA_STREET_LAMP',['NA_LAMP_GLOBE'],'street_lamp'),
 ('PORT_LIGHT_POLE',['PORT_LIGHT'],'port_lamp'),('PORT_BOLLARD_CAP',[],'unused')]:
 if label=='unused':continue
 # Prefix overlap must not make lamp glass/head objects into additional bases.
 bases=[n for n in remaining(base)if n.split('.')[0]==base]
 assigned={n:[n]for n in bases}
 for prefix in parts:
  for n in remaining(prefix):
   if n in bases or n.split('.')[0]!=prefix:continue
   p=center(n);b=min(bases,key=lambda b:sum((center(b)[a]-p[a])**2 for a in (0,1)))
   assigned[b].append(n)
 for n,names in assigned.items():cluster(label+'_'+n,names,category=label)
for base,parts,label in [('PORT_BOLLARD',['PORT_BOLLARD_CAP'],'bollard'),('PORT_SERVICE_SHED',['PORT_SHED_DOOR','PORT_SHED_ROOF','PORT_SHED_WINDOW'],'port_shed'),('PORT_SERVICE_OFFICE',['PORT_OFFICE_DOOR','PORT_OFFICE_ROOF','PORT_OFFICE_WINDOW'],'port_office')]:
 bases=[n for n in remaining(base)if n.split('.')[0]==base];assigned={n:[n]for n in bases}
 for prefix in parts:
  for n in remaining(prefix):
   p=center(n);b=min(bases,key=lambda b:sum((center(b)[a]-p[a])**2 for a in (0,1)))
   assigned[b].append(n)
 for n,names in assigned.items():cluster(label+'_'+n,names,category=label)
for prefix,cat in [('DT_SHRUB','shrub'),('DT_GARDEN_ROCK','rock'),('NA_QUAY_BOLLARD','bollard'),('PORT_FENDER','fender')]:
 for n in remaining(prefix):
  anchor=feet([n]);rule='foot_support_bbox'
  if cat=='fender':anchor[2]=1.249988;rule='quay_top_anchor_preserve_fender_below_edge'
  cluster(n,[n],anchor=anchor,rule=rule,category=cat)

def mesh_components(name):
 o=s.objects[name];me=o.data;parents=list(range(len(me.vertices)))
 def find(x):
  while parents[x]!=x:parents[x]=parents[parents[x]];x=parents[x]
  return x
 for e in me.edges:
  a,b=map(find,e.vertices);parents[a]=b
 parts=defaultdict(list)
 for v in me.vertices:parts[find(v.index)].append(v.index)
 T=I@o.matrix_world;result=[]
 for ids in sorted(parts.values(),key=lambda ids:ids[0]):
  ps=[T@me.vertices[i].co for i in ids];lo=[min(p[a]for p in ps)for a in range(3)];hi=[max(p[a]for p in ps)for a in range(3)]
  row={'object':name,'vertex_range':[min(ids),max(ids)+1],'vertex_count':len(ids),'bounds':{'min':vec(lo),'max':vec(hi)}}
  if max(ids)-min(ids)+1!=len(ids):row['vertex_indices']=ids
  result.append(row)
 return result
for stem,base_mat,head_mat,height,cat in [('CNX_STREET_TREES','wood','green',.78,'batched_tree'),('CNX_STREET_FURNITURE','dark','white',1.65,'batched_lamp')]:
 base_name=stem+'_'+base_mat;head_name=stem+'_'+head_mat
 base=mesh_components(base_name);head=mesh_components(head_name);assert len(base)==len(head)
 o=s.objects[base_name];T=I@o.matrix_world
 for j,(a,b)in enumerate(zip(base,head)):
  ids=list(range(*a['vertex_range']));half=len(ids)//2
  p=sum((T@o.data.vertices[i].co for i in ids[:half]),Vector())/half
  tip=sum((T@o.data.vertices[i].co for i in ids[half:]),Vector())/half
  assert abs((tip-p).length-height)<1e-3
  components.append({'id':stem+'_%03d'%j,'category':cat,'anchor':vec(p),'original_up':vec((tip-p).normalized()),
                     'parts':[a,b],'mesh_deformation_allowed':False,'rule':'apply_one_rigid_transform_to_corresponding_base_and_head_vertex_ranges'})
 covered.update([base_name,head_name])

for n,r in nodes.items():
 if n in covered or not r['bounds']or r['hidden_render']:continue
 if 'PORT_CRANE_PLACEMENT'in r['lineage']:continue
 if n.startswith('SF_OCEAN_WAVE'):
  special.append({'object':n,'rule':'ocean_decoration_keep_or_radially_project_to_ocean_separately','bounds':r['bounds']});covered.add(n);continue
 if n.startswith('CNX_')and any(t in n for t in ['TERRACE','FOUNDATION']):
  surfaces.append({'object':n,'category':'foundation_skirt','rule':'rebuild_skirt_after_its_building_root_moves','old_ground_reference':'CNX_CURVED_DISTRICT_LAND top BVH','bounds':r['bounds']});covered.add(n);continue
 if n.startswith('CNX_'):
  cat='district_terrain'if n=='CNX_CURVED_DISTRICT_LAND'else'district_surface_ribbon'
  surfaces.append({'object':n,'category':cat,'rule':'replace_unified_terrain'if cat=='district_terrain'else'wrap_each_vertex_preserving_offset_from_old_ground',
                   'old_ground_reference':'CNX_CURVED_DISTRICT_LAND top BVH','bounds':r['bounds']});covered.add(n);continue
 if n=='CN_QUAY'or any(n.startswith(p)for p in ['SF_FRONT_LAND','SF_COAST_FOLDED_FACE','SF_BASIN_','SF_ISLAND_','DT_GARDEN_PATH','DT_PATH_JOINT','DT_GARDEN_LAWN','DT_GARDEN_STONE_BORDER','DT_WATERFRONT_WALK','PORT_ACCESS_ROAD','PORT_APRON','PORT_BAY_LINE','PORT_CRANE_RAIL','PORT_EDGE_FRONT','PORT_ROAD_DASH','PORT_YARD_CROSS_LANE']):
  surfaces.append({'object':n,'category':'original_ground_or_water_surface','rule':'tessellate_then_radially_wrap_preserving_ground_relative_height','old_ground_reference':1.249988,'bounds':r['bounds']});covered.add(n)

animated_names=descend('PORT_CRANE_PLACEMENT')
covered.update(animated_names)
special.append({'group':'PORT_CRANE_PLACEMENT','objects':animated_names,'rule':'coordinated_animation_placement_only','ground_anchor':[15.65,-10.8,1.249985],
                'related_external_roots':['PORT_HOIST_PLACEMENT','PORT_SHIP_WATERLINE_CORRECTION','A01_CONTAINER','A02_SHIP']})
unassigned=[n for n,r in nodes.items()if r['bounds']and not r['hidden_render']and n not in covered]
cluster_report={'source':str(SOURCE),'sha256':SHA,'space':'SF_CN_LAYOUT','frame':0,'source_saved':False,
 'spherical_ground':{'center':[0,-4.6,-140],'top_radius':141.25},'rigid_clusters':clusters,'batched_component_clusters':components,
 'surfaces':surfaces,'special_groups':special,'unassigned_visible_geometry':unassigned,
 'notes':['Do not bend individual rigid building meshes. Transform an existing root or all members by one common rigid matrix.',
 'CNX roots already have nonvertical up axes; replace old terrain alignment with new radial alignment, preserving yaw.',
 'Container tiers share a stack anchor. Transform the whole stack, not each tier onto the ground.',
 'CNX street tree/lamp meshes contain many disconnected components. Transform paired vertex ranges as rigid units.',
 'Bounds are conservative transformed local bounding boxes; foot anchors use actual mesh vertices.',
 'Foundation skirts are separate siblings of CNX building roots and must be rebuilt after each building moves.',
 'Great Wall root includes wall architecture, hills, and forest as one authored assembly. Its broad hill skirt needs terrain treatment if breaking assembly into radial subsegments.']}
(OUT/'static-clusters.json').write_text(json.dumps(cluster_report,indent=2),encoding='utf-8')
original={k:v for k,v in cluster_report.items()if k not in ['rigid_clusters','batched_component_clusters','surfaces','notes']}
original['rigid_clusters']=[r for r in clusters if not r['category'].startswith('cnx_')]
hide=['CN_QUAY','SF_FRONT_LAND','SF_COAST_FOLDED_FACE','SF_ISLAND_TOP','SF_ISLAND_WALL','SF_BASIN_OUTER_WALL']
original['replace_ground_objects']=[{'object':n,'old_ground_z':1.249988,'bounds':nodes[n]['bounds']}for n in hide]
original['wrap_surfaces']=[r for r in surfaces if not r['object'].startswith('CNX_')and r['object']not in hide]
original['notes']=['Source ground top z=1.249988. Replace source ground solids/skirts with unified spherical ground.',
 'SF_BASIN_WATER_SURFACE is z=0.919988, 0.33 below old ground. Unified ground must retain a channel cutout/depression or intentionally raise the inlay above its new support surface to avoid burial.',
 'Source SF_ISLAND_EDGE is a separate curve: preserve/wrap as island/river edging if desired.',
 'Original-only list omits all CNX, which root rebuilds.',
 'Trees, lamps, sheds, and office are grouped by actual geometry centers because numerous part origins are baked at the layout origin.',
 'All common rigid matrices must be applied only once per top root/member. Do not transform descendants again.',
 'PORT_CRANE_PLACEMENT and all related animated assemblies excluded from static groups.']
counts=Counter(len(r['objects'])for r in original['rigid_clusters']if r['category']=='tree')
assert counts=={2:104,6:16},counts
assert all(len(r['objects'])==2 for r in original['rigid_clusters']if r['category']in ['street_lamp','port_lamp','bollard']and r['id'].startswith(('street_lamp','port_lamp','bollard_PORT')))
assert all(len(r['objects'])==6 for r in original['rigid_clusters']if r['category']=='port_shed')
assert len({n for r in original['rigid_clusters']for n in r['objects']})==sum(len(r['objects'])for r in original['rigid_clusters'])
(OUT/'static-original-clusters.json').write_text(json.dumps(original,indent=2),encoding='utf-8')
report={'source':str(SOURCE),'sha256':SHA,'source_saved':False,'frame':0,'space':'SF_CN_LAYOUT',
        'layout_matrix_world':mat(D.matrix_world),'scene_object_count':len(s.objects),
        'cn_object_count':len(nodes),'all_root_counts':dict(allroots.most_common()),
        'parent_counts':dict(parentcounts.most_common()),'objects':nodes}
(OUT/'static-survey.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SURVEY_COUNTS',json.dumps({'scene_objects':len(s.objects),'cn_objects':len(nodes),'rigid_clusters':len(clusters),'component_clusters':len(components),
 'surfaces':len(surfaces),'categories':dict(Counter(r['category']for r in clusters)),'unassigned':unassigned}),flush=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
