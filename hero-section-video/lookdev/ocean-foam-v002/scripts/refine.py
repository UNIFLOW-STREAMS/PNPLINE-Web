import bpy, sys, json, hashlib
from pathlib import Path
import numpy as np

r = Path(__file__).resolve().parents[1]
old = r.parent / 'ocean-foam-v001'
sys.path.insert(0, str(old / 'scripts'))
import resources
resources.D = r
s = bpy.context.scene
initial = s.frame_current
pointer = r.parent / 'latest-lookdev.json'
previous = json.loads(pointer.read_text())
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest() == previous['sha256']
(r / 'previous-latest-lookdev.json').write_bytes(pointer.read_bytes())

# Two understated longitudinal shoulders. No central bubble web or transverse crests.
height, width = 384, 768
aft, cross = np.meshgrid((np.arange(width)+.5)*12/width-1,
                        (np.arange(height)+.5)*8/height-4)
fade = resources.ease(-.35,.45,aft)*(1-resources.ease(1.8,9.0,aft))**1.7
shoulder = 1.18 + .025*np.maximum(aft,0)
spread = .22 + .018*np.maximum(aft,0)
edge = np.exp(-((np.abs(cross)-shoulder)/spread)**2)
# Broad gentle variations interrupt the foam without shifting its centreline.
patch = .64 + .19*np.sin(aft*.74+cross*4.7) + .12*np.cos(aft*1.31-cross*2.8)
foam = .32*edge*patch*fade
mist = .14*np.exp(-((np.abs(cross)-shoulder)/(.38+spread))**2)*fade
atlas = resources.data_image('Wake - restrained cargo shoulders',np.stack([mist,foam,foam*.08],axis=-1))

# Reuse the established spherical chart and baked stern trajectory.
tree = bpy.data.node_groups['Pacific | Stern wash']
tree.nodes.clear()
helpers = (old/'scripts/build.py').read_text()
exec(helpers[helpers.index('def node('):helpers.index("F='Float'")])
i=node('NodeGroupInput').outputs
lut=bpy.data.images['Voyage - stern track metres']
tr=sep(tex(lut,vec(mul(add(i['East'],230),1/355),.5)))
track_distance=sub(mul(tr[0],384),64)
track_north=sub(mul(tr[1],64),32)
dy=sub(i['North'],track_north)
sine=sub(mul(tr[2],2),1)
across=mul(dy,op('SQRT',sub(1,mul(sine,sine))))
aft_distance=sub(sub(i['Progress'],track_distance),mul(dy,sine))
# Fixed chart coordinates leave foam on the water and follow the actual route.
uv=vec(mul(add(aft_distance,1),1/12),mul(add(across,4),1/8))
cloud,foam,ridge=sep(tex(atlas,uv))
strength=mul(i['Power'],ramp(track_distance,-.6,1.5))
done({'Cloud':mul(cloud,strength),'Lace':mul(foam,strength),'Ridge':mul(ridge,strength)})

s.frame_set(initial)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(r/'pnpline-ocean-foam-v002.blend'),compress=True)
print('REFINED cargo wake saved',flush=True)
