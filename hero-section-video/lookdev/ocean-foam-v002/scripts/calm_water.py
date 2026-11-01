import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[1]
tree=bpy.data.node_groups['Pacific | Wind and shallow water']
tree.nodes.clear()
source=(r.parent/'ocean-foam-v001/scripts/build.py').read_text()
exec(source[source.index('def node('):source.index("F='Float'")])
i=node('NodeGroupInput').outputs
e=i['East'];n=i['North'];t=i['Seconds']
# Wide, slowly evolving ripples with isotropic soft highlights.
position=vec(add(e,mul(t,.025)),add(n,mul(t,-.018)),mul(t,.008))
broad=noise(position,.10,1.0)
soft=noise(position,.46,1.1)
shelf=tex(bpy.data.images['Shelf - coastal falloff'],i['Atlas'])
water=mix(add(.24,mul(broad,.44)),'1F586E','307788','Low contrast ocean colour')
water=mix(shelf,water,'67A99C','Island shallows')
glint=mul(ramp(soft,.64,.90),.075)
water=mix(glint,water,'79AAA9','Soft scattered reflections')
done({'Sea colour':water,'Height':add(mul(broad,.26),mul(soft,.16)),
      'Roughness':add(.44,mul(broad,.055)),'Breakup':soft})
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(r/'pnpline-ocean-foam-v002.blend'),compress=True)
