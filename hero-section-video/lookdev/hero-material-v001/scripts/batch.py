import subprocess,time,json,sys,hashlib
from pathlib import Path
import ctypes
from ctypes import wintypes
class PMC(ctypes.Structure):
 _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
def memory(pid):
 k=ctypes.windll.kernel32;k.OpenProcess.restype=wintypes.HANDLE;h=k.OpenProcess(0x0410,False,pid)
 info=PMC();info.cb=ctypes.sizeof(info);ctypes.windll.psapi.GetProcessMemoryInfo(wintypes.HANDLE(h),ctypes.byref(info),info.cb);k.CloseHandle(wintypes.HANDLE(h));return info.PeakWorkingSetSize
R=Path(__file__).resolve().parents[1];BL='C:/Program Files/Blender Foundation/Blender 5.1/blender.exe';src=json.loads((R/'review/survey.json').read_text())['file'];dst=str(R/'pnpline-hero-material-v001.blend')
stage=sys.argv[1]
jobs={'styles':[(dst,'after','45,110,200,315,390,530,720,820',1920,128),(src,'before','45,110,200,315,390,530,720,820',1920,128)],'clips':[(dst,'water-glass','105:135',1920,128),(dst,'us-port','330:360',1920,128),(dst,'warehouse','710:740',1920,128)]}[stage]
records=[]
for file,label,frames,width,samples in jobs:
 oldmetrics=R/'review'/label/'render-metrics.json'
 expected=list(range(*map(int,frames.split(':')))) if ':' in frames else list(map(int,frames.split(',')))
 if oldmetrics.exists():
  metrics=json.loads(oldmetrics.read_text());sha=hashlib.sha256(Path(file).read_bytes()).hexdigest()
  if [m['frame'] for m in metrics]==expected and all(m['source_sha256']==sha and m['samples']==samples and m['width']==width and Path(m['file']).exists() for m in metrics):
   oldbench=R/'review'/f'{stage}-benchmarks.json'
   records.extend(r for r in json.loads(oldbench.read_text()) if r['label']==label) if oldbench.exists() else None
   print('REUSE_VERIFIED',label,flush=True);continue
 cmd=[BL,'--background','--factory-startup',file,'-t','6','--python-exit-code','1','--python',str(R/'scripts/render.py'),'--','--frames',frames,'--width',str(width),'--samples',str(samples),'--label',label]
 start=time.time();rss=0;vram=[]
 with open(R/f'{label}.log','w') as log:
  proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
  while proc.poll() is None:
   try:rss=max(rss,memory(proc.pid))
   except Exception:pass
   try:vram.append(int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip()))
   except Exception:pass
   time.sleep(2)
 rec=dict(label=label,command=cmd,exit_code=proc.returncode,wall_seconds=time.time()-start,peak_process_rss_gib=rss/2**30,system_gpu_memory_mib_min=min(vram) if vram else None,system_gpu_memory_mib_peak=max(vram) if vram else None,gpu_note='Whole GPU usage including other applications, not isolated Blender VRAM')
 records.append(rec);(R/'review'/f'{stage}-benchmarks.json').write_text(json.dumps(records,indent=2));print(json.dumps(rec),flush=True)
 if proc.returncode:sys.exit(proc.returncode)
