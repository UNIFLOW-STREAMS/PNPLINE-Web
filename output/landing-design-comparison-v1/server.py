from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args):pass
    def do_GET(self):
        path=Path(self.translate_path(self.path))
        match=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers.get('Range',''))
        if path.suffix=='.mp4' and path.is_file() and match:
            size=path.stat().st_size;start=int(match[1]);end=min(int(match[2]) if match[2] else size-1,size-1)
            if start>=size or end<start:self.send_error(416);return
            self.send_response(206);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Content-Length',str(end-start+1));self.end_headers()
            try:
                with path.open('rb') as f:
                    f.seek(start);left=end-start+1
                    while left:
                        chunk=f.read(min(left,65536));self.wfile.write(chunk);left-=len(chunk)
            except (ConnectionResetError,ConnectionAbortedError,BrokenPipeError):pass
        else:super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
print(f'PNPLINE design comparison: http://127.0.0.1:{server.server_port}/index.html',flush=True)
server.serve_forever()
