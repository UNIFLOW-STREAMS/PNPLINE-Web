import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];label=sys.argv[sys.argv.index('--')+1];source=bpy.data.filepath
tests=['test_city_rotation.py','test_s1_camera_preserved.py'] if label.startswith('city') else ['test_route_direction.py','test_camera_join.py']
results=[]
for name in tests:
 p=R/'tests'/name;sys.argv=['blender','--',label+'-final'];ns={'__file__':str(p),'__name__':'__main__'}
 try:exec(compile(p.read_text(),str(p),'exec'),ns);results.append({'test':name,'pass':True})
 except Exception as e:results.append({'test':name,'pass':False,'error':repr(e)})
(R/'review'/f'{label}-final-tests.json').write_text(json.dumps({'file':source,'sha256':hashlib.sha256(Path(source).read_bytes()).hexdigest(),'results':results},indent=2))
assert all(r['pass']for r in results),results
