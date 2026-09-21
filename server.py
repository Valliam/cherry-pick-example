"""Serve the demo and read Git metadata from this repository; no dependencies."""

import argparse
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )


def git_state():
    status = git("status", "--porcelain")
    if status.returncode:
        raise RuntimeError("Cannot read repository status")
    branch = git("symbolic-ref", "--quiet", "--short", "HEAD").stdout.strip()
    head = git("rev-parse", "--verify", "--short", "HEAD").stdout.strip()
    subject = git("log", "-1", "--format=%s").stdout.strip() if head else ""
    return {
        "branch": branch or "detached HEAD",
        "head": head,
        "subject": subject,
        "dirty": bool(status.stdout.strip()),
    }


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/git":
            try:
                body = json.dumps(git_state(), ensure_ascii=False).encode("utf-8")
                self.respond(200, "application/json; charset=utf-8", body)
            except (OSError, RuntimeError):
                self.respond(500, "application/json", b'{"error":"Git unavailable"}')
        elif path in STATIC_FILES:
            filename, content_type = STATIC_FILES[path]
            self.respond(200, content_type, (ROOT / filename).read_bytes())
        else:
            self.respond(404, "text/plain; charset=utf-8", b"Not found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Open http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
