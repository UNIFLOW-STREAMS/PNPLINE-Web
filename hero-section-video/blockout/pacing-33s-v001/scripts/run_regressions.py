"""Run unchanged logistics assertions in their original source-frame coordinates."""
import importlib.util, math, sys, unittest
from pathlib import Path
import bpy
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from timing import TimeMap
m=TimeMap()

class SourceClockScene:
    def __init__(self,scene): self.scene=scene
    def frame_set(self,frame,subframe=0):
        f=m.output(frame+subframe)
        self.scene.frame_set(math.floor(f),subframe=f%1)
    def __getattr__(self,key): return getattr(self.scene,key)

suite=unittest.TestSuite()
paths=[
    'curvature-rework-v001/tests/test_curvature.py',
    'curvature-rework-v001/tests/test_logistics.py',
    'warehouse-rework-v001/tests/test_operations.py',
    'warehouse-rework-v001/tests/test_warehouse.py',
    'city-reveal-camera-v001/tests/test_continuous_motion.py',
]
for index,path in enumerate(paths):
    # The camera test gathers samples at module load, so supply the mapped scene
    # by replacing only its scene binding in memory; assertions stay unchanged.
    full=R.parent/path
    text=full.read_text(encoding='utf-8')
    # Match curvature-rework-v001/scripts/test_warehouse_frame.py: the
    # warehouse is rigid on its own spherical tangent frame, not US_FRAME.
    if path.startswith('warehouse-rework-v001/'):
        text=text.replace("S.objects['US_FRAME']","S.objects['CV_WH_US_FRAME']")
    text=text.replace('s=bpy.context.scene','s=_scene').replace('S=bpy.context.scene','S=_scene')
    env={'__file__':str(full),'__name__':f'retimed_regression_{index}','_scene':SourceClockScene(bpy.context.scene)}
    exec(compile(text,str(full),'exec'),env)
    for value in list(env.values()):
        if isinstance(value,type) and issubclass(value,unittest.TestCase) and value is not unittest.TestCase:
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(value))
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful(): raise AssertionError('Retimed logistics regression failed')
