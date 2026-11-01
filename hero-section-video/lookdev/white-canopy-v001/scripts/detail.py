import bpy,re,collections
s=bpy.context.scene
for n in ('SF_TREE_TRUNK','DT_TREE_TRUNK','NA_TREE_TRUNK','UC_TREE_TRUNK','CNX_STREET_TREES_wood','CE_STREET_FURNITURE_bark','WH_LOGO_GRAY','A01_ROOF'):
 o=s.objects[n];print(n,o.parent.name if o.parent else None,o.hide_render,len(o.data.vertices),[tuple(round(k,2) for k in v.co) for v in list(o.data.vertices)[:3]],[(m.material.name) for m in o.material_slots],flush=True)
print('OTHER',collections.Counter(re.sub(r'\d+','#',o.name.split('.')[0]) for o in s.objects if o.type=='MESH' and not o.hide_render and any(re.search('leaf|bark|foliage|tree|green',m.material.name,re.I) for m in o.material_slots if m.material) and not re.search('TREE|FURNITURE|SHRUB|GARDEN',o.name,re.I)).most_common(120))
print([(o.name,o.parent.name if o.parent else None,[ch.name for ch in o.children][:9]) for o in s.objects if o.name in ('NA_TREE','UC_TREE_TRUNK','SF_TREE_CROWN','SHD_GAP_TREE_001_ROOT','DT_TREE_CROWN','CNX_STREET_TREES_green')])
