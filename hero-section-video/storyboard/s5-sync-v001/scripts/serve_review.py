from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R),**kw)
 def do_POST(self):
  if self.path!='/playback':self.send_error(404);return
  length=int(self.headers.get('Content-Length','0'))
  if length>20000:self.send_error(413);return
  try:data=json.loads(self.rfile.read(length))
  except ValueError:self.send_error(400);return
  data['video_sha256']=hashlib.sha256((R/'preview/main.mp4').read_bytes()).hexdigest();data['recorded_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();data['observer']='assistant browser technical review, not user approval'
  (R/'review/playback.json').write_text(json.dumps(data,indent=2),encoding='utf8');self.send_response(200);self.end_headers();self.wfile.write(b'ok')
ThreadingHTTPServer(('127.0.0.1',8767),Handler).serve_forever()
