"""Wait for the full render, validate/encode, apply both apps, and build them."""
import datetime, json, subprocess, sys, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
client_tz=datetime.timezone(datetime.timedelta(hours=8))
report={'status':'rendering','started':datetime.datetime.now(client_tz).isoformat()}
last_progress=0
try:
    while True:
        log=(ROOT/'render.log').read_text(encoding='utf-8',errors='replace')
        if ('SOURCE_UNCHANGED 65299a8273754bade3a47cc7dbf4f21e92a8e28ac4d6b0e48747a6e5556c55bb' in log
                and all((ROOT/'frames'/f'f{f:04}.png').exists() for f in range(990))):break
        rows=(ROOT/'review/frame-times.jsonl').read_text().splitlines() if (ROOT/'review/frame-times.jsonl').exists() else []
        frames=[json.loads(row) for row in rows]
        if time.monotonic()-last_progress>=60:
            mean=sum(f['seconds'] for f in frames[-60:])/max(1,len(frames[-60:]))
            remaining=round((990-len(frames))*mean/60)
            report.update(frames=len(frames),last_frame=frames[-1]['frame'] if frames else None,remaining_minutes_recent_rate=remaining,updated=datetime.datetime.now(client_tz).isoformat())
            (ROOT/'audit/progress.json').write_text(json.dumps(report,indent=2))
            print(f"Cycles GPU: {len(frames)}/990 frames ({len(frames)/9.9:.1f}%), recent-rate ETA {remaining} min",flush=True)
            last_progress=time.monotonic()
            gpu=subprocess.run(['nvidia-smi','--query-gpu=timestamp,memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader'],capture_output=True,text=True)
            with (ROOT/'review/gpu-memory.csv').open('a') as stream:stream.write(gpu.stdout)
        if time.time()-(ROOT/'render.log').stat().st_mtime>1200:raise RuntimeError('Render log unchanged for 20 minutes; inspect renderer')
        time.sleep(5)
    report['status']='encoding';(ROOT/'audit/progress.json').write_text(json.dumps(report,indent=2))
    with (ROOT/'review/encode.log').open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'scripts/encode.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
    print('990 frames rendered; desktop/mobile encodes validated. Applying both sites.',flush=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/sites.py'),'--apply'],check=True)
    sites=json.loads((ROOT/'audit/site-application.json').read_text())
    for lang,info in sites.items():
        with (ROOT/'review'/f'build-{lang}-final.log').open('w') as log:
            subprocess.run(['npm.cmd','run','build'],cwd=info['site'],stdout=log,stderr=subprocess.STDOUT,check=True)
        print(lang.upper()+' production build passed',flush=True)
    report.update(status='ready_for_browser_review',completed=datetime.datetime.now(client_tz).isoformat())
except Exception as error:
    report.update(status='failed',error=str(error));traceback.print_exc()
finally:
    (ROOT/'audit/progress.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
if report['status']=='failed':sys.exit(1)
