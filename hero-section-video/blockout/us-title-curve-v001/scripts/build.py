"""Balanced, continuous curved USA letters embedded in the existing radial city."""
import bpy,bmesh,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
sys.path.append(str(R.parent/'curvature-rework-v001/scripts'))
from mapping import surface,normal
SOURCE=R.parent/'us-city-density-v001/pnpline-us-city-density-v001.blend'
OUT=R/'pnpline-us-title-curve-v001.blend'
SHA='90cf22b0693b0d3702236f88a3871da371491090c7b9a2d1d70d58047f22da9a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def design(x,y):return (.8480480909*x+.5299192667*y-19.6070099,-.5299192667*x+.8480480909*y+6.6222191)
assert sha(SOURCE)==SHA
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;original_frame=s.frame_current;s.frame_set(349)
U=s.objects['US_FRAME'];col=bpy.data.collections.new('UST_CURVED_CITY_TITLE');s.collection.children.link(col)
allowed={};hidden=[]
for letter in 'USA':
 for name in [f'UC_LETTER_{letter}',f'UC_AR_LETTER_PLINTH_{letter}',f'CV_FOUNDATION_LETTER_{letter}']:
  ob=s.objects[name];ob.hide_render=True;ob.hide_viewport=True;hidden.append(name);allowed[name]=['hide_render','hide_viewport']
height=23.5;stretch=1.6;radius=80.;center_x=-9.5;backline=57.;gap=1.2;depth=2.5
spec=[]
for letter in 'USA':
 ob=s.objects['UC_LETTER_'+letter];lo=[min(v.co[i]for v in ob.data.vertices)for i in range(3)];hi=[max(v.co[i]for v in ob.data.vertices)for i in range(3)]
 sy=height/(hi[1]-lo[1]);sx=sy*stretch;w=(hi[0]-lo[0])*sx
 spec.append({'letter':letter,'lo':lo,'hi':hi,'width':w,'height':height,'scale':[sx,sy,depth/(hi[2]-lo[2])]})
total=sum(r['width']for r in spec)+2*gap;cursor=-total/2
for row in spec:
 letter=row['letter'];src=s.objects['UC_LETTER_'+letter];me=src.data.copy();me.name='UST_LETTER_'+letter+'_MESH'
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 sx,sy,sz=row['scale'];lo=row['lo'];hi=row['hi']
 for v in bm.verts:v.co=Vector(((v.co.x-lo[0])*sx,(v.co.y-lo[1])*sy,(v.co.z-(lo[2]+hi[2])/2)*sz))
 # Split long horizontal/depth edges, including broad flat A faces, before bending.
 for iteration in range(8):
  edges=[e for e in bm.edges if math.hypot(e.verts[0].co.x-e.verts[1].co.x,e.verts[0].co.y-e.verts[1].co.y)>1.05]
  if not edges:break
  bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
  bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3])
 start=cursor;row['arc_start']=start;row['arc_end']=start+row['width'];row['sagitta']=radius*(1-math.cos((start+row['width']/2)/radius))
 for v in bm.verts:
  along=start+v.co.x;theta=along/radius;z=v.co.y;extrusion=v.co.z
  x=center_x+(radius-extrusion)*math.sin(theta)
  y=backline-radius+(radius-extrusion)*math.cos(theta)
  ax,ay=design(x,y);v.co=surface(ax,ay,.665+z)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new('UST_LETTER_'+letter,me);col.objects.link(ob);ob.parent=U
 ob['ust_role']='city_integrated_curved_title';ob['ust_glyph']=letter;ob['ust_unwrapped_width']=row['width'];ob['ust_unwrapped_height']=height
 row['object']=ob.name;row['vertices']=len(me.vertices);row['triangles']=len(me.polygons)
 cursor+=row['width']+gap
 print('LETTER',letter,row['width'],row['vertices'],flush=True)

# Optional exact, assembly-level relocations are declared in a separate reviewed layout.
relocations=[];replacement_supports=[];hidden_supports=[]
config=R/'scripts/relocations.json'
if config.exists():
 I=U.matrix_world.inverted()
 for entry in json.loads(config.read_text()):
  if entry['root']=='CE_REAR_SPACE_NEEDLE_ROOT':entry=dict(entry,design_xy=json.loads((R/'scripts/needle-location.json').read_text())['design_xy']if(R/'scripts/needle-location.json').exists()else[-17,47],extras=[])
  root=s.objects[entry['root']];x,y=design(*entry['design_xy']);oldanchor=next(list(root[k])for k in ('cv_anchor','ce_anchor','usd_anchor')if k in root)
  ox,oy,oz=oldanchor[:3]
  def F(a,b,c):return Matrix.Translation(surface(a,b,c))@Vector((0,0,1)).rotation_difference(normal(a,b)).to_matrix().to_4x4()
  delta=F(x,y,oz)@F(ox,oy,oz).inverted()
  root.matrix_world=U.matrix_world@delta@I@root.matrix_world
  anchor_key=next(k for k in ('cv_anchor','ce_anchor','usd_anchor')if k in root)
  root[anchor_key]=[x,y,oz]
  allowed[root.name]=['matrix_basis','matrix_world','properties']
  for child in root.children_recursive:allowed[child.name]=['matrix_world']
  for extra in entry.get('extras',[]):
   o=s.objects[extra];o.matrix_world=U.matrix_world@delta@I@o.matrix_world;allowed[o.name]=['matrix_basis','matrix_world']
  relocations.append(dict(entry,old_anchor=oldanchor,new_anchor=[x,y,oz]))
  bpy.context.view_layer.update()
  if root.name=='CE_REAR_SPACE_NEEDLE_ROOT':
   for n in ['CE_REAR_SPACE_NEEDLE_FOUNDATION','CE_REAR_SPACE_NEEDLE_PLAZA']:
    ob=s.objects[n];ob.hide_render=True;ob.hide_viewport=True;allowed[n]=['hide_render','hide_viewport'];hidden_supports.append(n)
   basis=F(x,y,oz)@Matrix.Rotation(math.radians(-32),4,'Z')
   corners=[Vector((a*1.95,b*1.95,-.008))for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]];top=[]
   for a,b in zip(corners,corners[1:]+corners[:1]):top.extend(basis@a.lerp(b,k/12)for k in range(12))
   center=Vector((0,0,-140));bottom=[center+(p-center).normalized()*140.65 for p in top];n=len(top)
   me=bpy.data.meshes.new('UST_NEEDLE_CITY_PAD_MESH');me.from_pydata(top+bottom,[],[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,n+i,n+(i+1)%n,(i+1)%n)for i in range(n)])
   me.materials.append(bpy.data.materials['UC_LIMESTONE']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
   ob=bpy.data.objects.new('UST_NEEDLE_CITY_PAD',me);col.objects.link(ob);ob.parent=U;replacement_supports.append(ob.name)
s.frame_set(original_frame);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
assert sha(SOURCE)==SHA
delivery={'source':str(SOURCE),'source_sha256':SHA,'file':str(OUT),'sha256':sha(OUT),'allowed_original_changes':allowed,
 'hidden_original_objects':hidden,'hidden_original_supports':hidden_supports,'replacement_supports':replacement_supports,'letters':spec,'relocations':relocations,'design':{'height':height,'horizontal_to_vertical_scale_ratio':stretch,'depth':depth,'arc_length':total,'radius':radius,'arc_degrees':math.degrees(total/radius),'center_design_x':center_x,'center_design_y':backline,'baseline_radius':140.665,'ground_radius':140.68,'plinths':False,'gap':gap},
 'preservation':'Original meshes retained as hidden alternatives; no actions, cameras, materials or scene settings authored.'}
(R/'delivery.json').write_text(json.dumps(delivery,indent=2),encoding='utf-8')
print('SAVED',OUT,delivery['sha256'],flush=True)

