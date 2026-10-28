"""Logged local Blender commands, no installation or source mutation."""
import sys, subprocess, json, time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
BLENDER=Path('C:/Program Files/Blender Foundation/Blender 5.1/blender.exe')
label,blend,script,*args=sys.argv[1:]
cmd=[str(BLENDER),'--background',str(R/blend),'--python-exit-code','1','--python',str(R/script),'--',*args]
start=time.time()
with (R/'review'/f'{label}.log').open('w',encoding='utf-8') as log:
 p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
record={'command':cmd,'exit_code':p.returncode,'seconds':time.time()-start}
(R/'review'/f'{label}-command.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record));sys.exit(p.returncode)
