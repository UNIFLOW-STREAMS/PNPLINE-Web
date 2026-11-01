"""Local review server with byte ranges so MP4 seeking and section loops work."""
import argparse,functools,os,re
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.remaining=None
        path=self.translate_path(self.path)
        request=self.headers.get('Range')
        if not request or not os.path.isfile(path): return super().send_head()
        size=os.path.getsize(path)
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',request.strip())
        if not match or not any(match.groups()):
            self.send_error(416);return None
        left,right=match.groups()
        start=int(left) if left else max(0,size-int(right))
        end=min(int(right),size-1) if left and right else size-1
        if start>=size or start>end:
            self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return None
        stream=open(path,'rb');stream.seek(start);self.remaining=end-start+1
        self.send_response(206)
        self.send_header('Content-Type',self.guess_type(path))
        self.send_header('Content-Length',str(self.remaining))
        self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.send_header('Last-Modified',self.date_time_string(os.path.getmtime(path)))
        self.end_headers();return stream

    def end_headers(self):
        self.send_header('Accept-Ranges','bytes')
        super().end_headers()

    def copyfile(self,source,outputfile):
        try:
            if self.remaining is None: return super().copyfile(source,outputfile)
            while self.remaining:
                block=source.read(min(1024*1024,self.remaining))
                if not block: break
                outputfile.write(block);self.remaining-=len(block)
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):
            pass # Browser cancelled a previous seek.

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=18789);a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    server=ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(RangeHandler,directory=str(root)))
    print(f'http://127.0.0.1:{a.port}/review.html',flush=True)
    server.serve_forever()
