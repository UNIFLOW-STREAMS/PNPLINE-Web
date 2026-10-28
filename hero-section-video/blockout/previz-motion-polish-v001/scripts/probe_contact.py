import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from motion import TimeMap
cfg=json.loads((R/'config.json').read_text());rows=[]
for variant in ['A','B']:
 m=TimeMap(1392,cfg['easing'],cfg['compression_B'] if variant=='B' else [])
 for kind,path in [('source',R/'inputs/source.blend'),('candidate',R/f'master-motion-polish-{variant}.blend')]:
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted();wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name];ground=[]
  for n in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
   o=s.objects[n];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
  worst=[0,None,None,None];camera=[]
  for out in range(round(m.output_end)+1):
   src=m.inverse(out);f=src if kind=='source' else out;s.frame_set(int(f),subframe=f%1);camera.append(s.camera.matrix_world.translation.copy())
   for o in wheels:
    matrix=I@o.matrix_world;c=matrix.translation;hits=[tree.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for tree in ground];height=max(p.z for p in hits if p is not None);bottom=min((matrix@v.co).z for v in o.data.vertices);error=abs(bottom-height)
    if error>worst[0]:worst=[error,out,src,o.name]
  peaks=sorted([((c-2*b+a).length,i+1) for i,(a,b,c) in enumerate(zip(camera,camera[1:],camera[2:]))],reverse=True)[:8]
  row={'variant':variant,'kind':kind,'worst_wheel':worst,'camera_accel_peaks':peaks};rows.append(row);print(json.dumps(row),flush=True)
(R/'review/contact-diagnosis.json').write_text(json.dumps(rows,indent=2))
