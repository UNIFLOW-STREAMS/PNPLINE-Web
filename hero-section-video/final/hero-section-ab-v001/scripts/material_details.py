import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from state import tree,clean
bpy.context.scene.frame_set(0)
names=['Liberty | printed verdigris','DSP_stone','Liberty | pine patina','DSP_brick','Liberty | oxidised jade','DSP_paving','Liberty | ochre enamel','DSP_roof','Liberty | celadon']
out={n:[clean(bpy.data.materials[n].diffuse_color),tree(bpy.data.materials[n].node_tree)] for n in names}
(Path(__file__).resolve().parents[1]/'audit'/(sys.argv[-1]+'-material-details.json')).write_text(json.dumps(out,indent=2))
