"""Local profile preview with cached data from the existing stats service."""
import json
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(ROOT.parent / 'scripts'))
from profile_data import refresh
CACHE = None
LOCK = Lock()




class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global CACHE
        if self.path != '/api/stats':
            return super().do_GET()
        with LOCK:
            stale = False
            try:
                if CACHE is None or time.time() - CACHE[0] > 1800:
                    CACHE = (time.time(), refresh())
                payload = dict(CACHE[1])
            except Exception:
                stale = True
                payload = dict(CACHE[1]) if CACHE else json.loads((ROOT / 'stats-snapshot.json').read_text())
            payload['stale'] = stale
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 4173), partial(Handler, directory=str(ROOT))).serve_forever()
