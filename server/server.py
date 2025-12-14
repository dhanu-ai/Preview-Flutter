import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

APP_ROOT = "/app"
FLUTTER_CMD_TEMPLATE = [
    "flutter", "run",
    "-d", "web-server",
    "--web-port=8080",
    "--web-hostname=0.0.0.0"
]

# Track Flutter processes per project
flutter_procs = {}


# ---------- PARSER ----------
def parse_payload(payload: dict) -> dict:
    if "project_id" not in payload:
        raise ValueError("project_id missing")

    files = {}
    for path, content in payload.items():
        if path == "project_id":
            continue
        if not isinstance(path, str):
            raise ValueError("Invalid file path")
        if path.startswith("/") or ".." in path:
            raise ValueError(f"Invalid path: {path}")
        if not isinstance(content, str):
            raise ValueError(f"File content must be string: {path}")
        files[path] = content

    if "pubspec.yaml" not in files:
        raise ValueError("pubspec.yaml missing")
    if "lib/main.dart" not in files:
        raise ValueError("lib/main.dart missing")

    return files


# ---------- FILE WRITER ----------
def write_files(project_id: str, files: dict):
    project_path = os.path.join(APP_ROOT, project_id)
    for path, content in files.items():
        full_path = os.path.join(project_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    return project_path


# ---------- FLUTTER RUNNER ----------
def restart_flutter(project_id: str, project_path: str):
    # Kill existing process if any
    if project_id in flutter_procs:
        flutter_procs[project_id].kill()

    print(f"🔹 Starting Flutter Web server for project: {project_id}")
    proc = subprocess.Popen(
        FLUTTER_CMD_TEMPLATE,
        cwd=project_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    flutter_procs[project_id] = proc


# ---------- HTTP HANDLER ----------
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers["Content-Length"])
            raw_body = self.rfile.read(length)
            print("RAW BODY (first 500 bytes):", raw_body[:500])

            payload = json.loads(raw_body)
            print("PARSED JSON KEYS:", payload.keys())

            project_id = payload["project_id"]
            files = parse_payload(payload)
            project_path = write_files(project_id, files)
            restart_flutter(project_id, project_path)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"Preview updated for project {project_id}".encode())

        except Exception as e:
            print("ERROR:", e)
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(e).encode())


# ---------- MAIN ----------
if __name__ == "__main__":
    print("🟢 Flutter Preview MVP started")
    HTTPServer(("0.0.0.0", 7000), Handler).serve_forever()
