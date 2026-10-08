from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R/'preview'),**kw)
 def do_POST(self):
  if self.path!='/playback-result':self.send_error(404);return
  j=json.loads(self.rfile.read(int(self.headers['Content-Length'])));j['candidate_sha256']=hashlib.sha256((R/'master-s5-integration-v001.blend').read_bytes()).hexdigest();j['video_hashes']={n:hashlib.sha256((R/'preview'/n).read_bytes()).hexdigest() for n in ['main.mp4','top.mp4']};(R/'review/playback.json').write_text(json.dumps(j,indent=2));self.send_response(200);self.end_headers();self.wfile.write(b'OK')
ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
