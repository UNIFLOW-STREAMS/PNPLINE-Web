"""Loopback-only static review server with video byte ranges; no upload API."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R),**kw)
 def send_head(self):
  path=Path(self.translate_path(self.path));self.byte_count=None
  if 'Range' not in self.headers or not path.is_file():return super().send_head()
  match=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers['Range'])
  if not match:self.send_error(416);return None
  size=path.stat().st_size;start=int(match[1]);end=min(int(match[2]) if match[2] else size-1,size-1)
  if start> end:self.send_error(416);return None
  f=path.open('rb');f.seek(start);self.byte_count=end-start+1
  self.send_response(206);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Content-Length',str(self.byte_count));self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Accept-Ranges','bytes');self.end_headers();return f
 def copyfile(self,source,outputfile):
  if self.byte_count is None:return super().copyfile(source,outputfile)
  left=self.byte_count
  while left:
   chunk=source.read(min(left,65536))
   if not chunk:break
   outputfile.write(chunk);left-=len(chunk)
ThreadingHTTPServer(('127.0.0.1',8773),Handler).serve_forever()
