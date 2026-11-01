import bpy, re, collections
s=bpy.context.scene
def group(objs):
 d=collections.Counter(re.sub(r"\d+","#",o.name).split(".")[0] for o in objs)
 return d
print("TREES",group([o for o in s.objects if re.search("tree|canopy|trunk|foliage",o.name,re.I)]))
print("LOGOS",group([o for o in s.objects if re.search("pnpline|pnp.line|brand|logo|signboard",o.name,re.I)]))
print("IMAGES",[(i.name,i.filepath) for i in bpy.data.images])
print("FONTS",collections.Counter(o.data.body for o in s.objects if o.type=="FONT"))
print("CARGO",[(o.name,[m.material.name if m.material else None for m in o.material_slots],o.hide_render) for o in s.objects['A01_CONTAINER'].children_recursive if o.type=="MESH" and not o.hide_render])
print("SAMPLE",[(o.name,o.type,o.parent.name if o.parent else "",list(o.location),tuple(o.scale)) for o in s.objects if o.name.startswith("DSP_TREE_000")])
