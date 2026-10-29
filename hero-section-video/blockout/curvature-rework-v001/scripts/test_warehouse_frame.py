"""Run unchanged warehouse assertions in the new rigid work-floor frame."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for filename in ['test_warehouse.py','test_operations.py']:
 text=(R.parent/'warehouse-rework-v001/tests'/filename).read_text().replace("S.objects['US_FRAME']","S.objects['CV_WH_US_FRAME']")
 exec(compile(text,'warehouse-v008-'+filename,'exec'),{'__name__':'__main__'})
