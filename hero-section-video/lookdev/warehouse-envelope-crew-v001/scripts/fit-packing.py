import bpy,sys,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
B=R.parents[1]/'blockout'
sys.path[:0]=[str(R.parent/'us-warehouse-curvature-v001/scripts'),str(B/'curvature-rework-v001/scripts'),str(R.parent/'container-ship-v001/scripts')]
from surface_site import sphere,arc,basis
S=bpy.context.scene
U=S.objects['US_FRAME']
def flat(p):return arc(np.array(U.matrix_world.inverted()@Vector(p)))
def loc(o):return flat(o.matrix_world.translation).round(3).tolist()
o=S.objects['Figure Pack | surface anchor'];pt=np.array([55.36,31.52,1.86]);a=Matrix(basis(sphere,pt).tolist()).to_4x4();a.translation=Vector(sphere(pt))
o.matrix_parent_inverse=o.parent.matrix_world.inverted()@U.matrix_world@a@Matrix.Rotation(1.04,4,'Z')
bpy.context.view_layer.update()
exec(compile((R/'scripts/review.py').read_text(encoding='utf-8-sig').replace("'cam-'+shot+'.png'","'fit-'+shot+'.png'"),str(R/'scripts/review.py'),'exec'))

