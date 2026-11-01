import hashlib,json,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sha='61c980107793a30b12a8d6d61f341bd233c864346e247b5c5d90cfb72c19afff'
deadline=time.monotonic()+2100
while True:
    assert hashlib.sha256((root/'pnpline-city-expansion-v002.blend').read_bytes()).hexdigest()==sha
    complete=True
    for a,b in [(0,494),(495,989)]:
        p=root/f'review/render-{a}-{b}.json'
        if not p.exists():complete=False;continue
        d=json.loads(p.read_text())
        complete=complete and d['sha256']==sha and d['frames']==list(range(a,b+1))
    if complete:break
    if time.monotonic()>deadline:raise TimeoutError('Final render reports not complete')
    time.sleep(10)
subprocess.run([sys.executable,str(root/'scripts/package.py')],check=True)
