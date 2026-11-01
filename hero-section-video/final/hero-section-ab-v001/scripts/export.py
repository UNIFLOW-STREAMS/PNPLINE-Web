import sys,json,bpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from state import snapshot,presentation,sha
label=sys.argv[-1];root=Path(__file__).resolve().parents[1];(root/'audit').mkdir(parents=True,exist_ok=True)
result=dict(file=bpy.data.filepath,sha256=sha(bpy.data.filepath),snapshot=snapshot(),presentation=presentation(),camera_data=bpy.context.scene.camera.data.name)
(root/'audit'/f'{label}.json').write_text(json.dumps(result))
print('EXPORTED',label,'objects',len(result['snapshot']['objects']),'materials',len(result['snapshot']['materials']),flush=True)
