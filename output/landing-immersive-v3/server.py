"""Serve this preview only, with byte ranges for scroll-linked MP4 seeking."""

from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
PUBLIC_EXTENSIONS = {".html", ".css", ".js", ".jpg", ".jpeg", ".png", ".webp", ".mp4", ".ttf", ".woff", ".woff2", ".txt"}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def list_directory(self, path):
        self.send_error(404)
        return None

    def send_head(self):
        self.byte_range = None
        path = Path(self.translate_path(self.path)).resolve()
        if not path.is_relative_to(ROOT) or any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            self.send_error(404)
            return None
        if path.is_file() and path.suffix.lower() not in PUBLIC_EXTENSIONS:
            self.send_error(404)
            return None
        value = self.headers.get("Range")
        if path.suffix.lower() != ".mp4" or not path.is_file() or not value:
            return super().send_head()
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", value.strip())
        size = path.stat().st_size
        if not match or not any(match.groups()):
            self.send_error(416)
            return None
        if not match[1]:
            start, end = max(0, size - int(match[2])), size - 1
        else:
            start = int(match[1])
            end = min(int(match[2]) if match[2] else size - 1, size - 1)
        if start >= size or end < start:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        stream = path.open("rb")
        stream.seek(start)
        self.byte_range = end - start + 1
        self.send_response(206)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(self.byte_range))
        self.end_headers()
        return stream

    def copyfile(self, source, outputfile):
        try:
            if self.byte_range is None:
                super().copyfile(source, outputfile)
                return
            remaining = self.byte_range
            while remaining:
                chunk = source.read(min(remaining, 65536))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"PNPLINE immersive preview: http://127.0.0.1:{server.server_port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
