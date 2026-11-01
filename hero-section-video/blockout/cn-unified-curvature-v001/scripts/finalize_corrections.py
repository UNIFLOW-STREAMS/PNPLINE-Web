"""Apply reviewed camera continuity and two small geometry corrections."""
import bpy, hashlib, json, sys
from pathlib import Path
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import terrain
from animation_reflow import apply_validated_camera_refinement

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    report=json.loads((ROOT/'delivery.json').read_text())
    path=Path(report['file'])
    assert sha(path)==report['sha256']=='f91b199ea4d722f8e7a90655e4fa1f0196c2c03e3822fda4140b46f6c65ecc06'
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(0)
    layout=scene.objects['SF_CN_LAYOUT'];I=layout.matrix_world.inverted();sphere=terrain.globe_surface(scene,layout)
    row=next(row for row in report['static_clusters']if row['id']=='DT_GARDEN_ROCK.012')
    old_delta=Matrix(row['delta_matrix']);anchor=Vector(row['source_anchor'])
    normal=sphere.normal(-26,2.5);target=sphere.point(-26,2.5)+normal*(anchor.z-1.249988)
    new_delta=Matrix.Translation(target)@Vector((0,0,1)).rotation_difference(normal).to_matrix().to_4x4()@Matrix.Translation(-anchor)
    correction=layout.matrix_world@new_delta@old_delta.inverted()@I
    for name in row['roots']:
        obj=scene.objects[name];obj.matrix_world=correction@obj.matrix_world;obj['cnc_radial_anchor']=list(target)
    row.update({'target_anchor':list(target),'target_normal':list(normal),'delta_matrix':[list(r)for r in new_delta],
                'relocation_reason':'Move preexisting stray garden rock out of the shipping channel and onto the left garden.'})
    walk=scene.objects['CNX_OUTER_PROMENADE'];T=I@walk.matrix_world;Ti=T.inverted()
    for vertex in walk.data.vertices:
        p=T@vertex.co;x=p.x*.988;y=p.y+(25-p.y)*.012
        vertex.co=Ti@(sphere.point(x,y)+sphere.normal(x,y)*.06)
    walk.data.update();bpy.context.view_layer.update()
    report['camera_refinement']=apply_validated_camera_refinement(scene,layout)
    report['animation']=json.loads((ROOT/'review/animation-reflow.json').read_text())
    report['geometry_review_fixes']=['Relocated stray garden rock to supported ground','Inset outer promenade to avoid perimeter overhang']
    scene.frame_set(132)
    bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
    report['sha256']=sha(path);report['status']='Pending final saved-file verification'
    (ROOT/'delivery.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (ROOT/'review/build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    assert sha(Path(report['source']))==report['source_sha256']
    print('CORRECTIONS_SAVED',report['sha256'],flush=True)

if __name__=='__main__':main()
