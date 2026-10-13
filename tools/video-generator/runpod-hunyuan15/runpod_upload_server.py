import http.server
import os
import urllib.parse

ROOT = "/workspace/urvashi-h3"
os.makedirs(ROOT, exist_ok=True)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/upload":
            self.send_error(404)
            return
        name = urllib.parse.parse_qs(parsed.query).get("name", [""])[0]
        if not name or os.path.basename(name) != name or not name.endswith((".png", ".py", ".json")):
            self.send_error(400)
            return
        length = int(self.headers.get("Content-Length", "0"))
        target = os.path.join(ROOT, name)
        remaining = length
        with open(target, "wb") as out:
            while remaining:
                chunk = self.rfile.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                out.write(chunk)
                remaining -= len(chunk)
        if remaining:
            self.send_error(400)
            return
        self.send_response(201)
        self.end_headers()
        self.wfile.write(b"uploaded\n")

    def log_message(self, fmt, *args):
        return


http.server.ThreadingHTTPServer(("0.0.0.0", 19123), Handler).serve_forever()
