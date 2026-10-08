import bpy,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from scene_evidence import bounds

def horizon():
    s=bpy.context.scene;c=s.camera;p=c.matrix_world.translation;r=float(s['radius'])
    # Ray/sphere tangency; independent of mesh tessellation and coastal occlusion.
    vf=c.data.view_frame(scene=s);left=min(v.x for v in vf);right=max(v.x for v in vf)
    bottom=min(v.y for v in vf);top=max(v.y for v in vf);z=vf[0].z
    def hits(x,y):
        d=c.matrix_world.to_3x3()@Vector((left+(right-left)*x,bottom+(top-bottom)*y,z));d.normalize()
        b=p.dot(d);return b<0 and b*b>=p.length_squared-r*r
    ys=[]
    for x in [.05,.5,.95]:
        if not hits(x,0) or hits(x,1):ys.append(None);continue
        lo=0.;hi=1.
        for _ in range(30):
            m=(lo+hi)/2
            if hits(x,m):lo=m
            else:hi=m
        ys.append((lo+hi)/2)
    return {'y':ys,'rise':ys[1]-(ys[0]+ys[2])/2 if all(v is not None for v in ys) else None}

def sample(f):
    s=bpy.context.scene;s.frame_set(int(f),subframe=f-int(f));c=s.camera;ship=bpy.data.objects['A02_SHIP'].matrix_world.copy()
    p=ship.inverted()@c.matrix_world.translation;t=bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation
    up=ship.to_3x3()@Vector((0,0,1));forward=c.matrix_world.to_3x3()@Vector((0,0,-1));right=c.matrix_world.to_3x3()@Vector((1,0,0))
    b=bounds('A02_SHIP')
    return {'frame':f,'s3_seconds':(f-216)/12,'ship_local_camera':list(p),'distance':p.length,'height':p.z,'bearing_deg':math.degrees(math.atan2(p.y,p.x)),'target_local':list(ship.inverted()@t),'target_world':list(t),'ship_bounds':b,'ship_center':[(b[0]+b[2])/2,(b[1]+b[3])/2],'ship_width':b[2]-b[0],'elevation_deg':math.degrees(math.asin(max(-1,min(1,-forward.dot(up.normalized()))))),'right_up_dot':right.dot(up.normalized()),'horizon':horizon(),'lens':c.data.lens}
