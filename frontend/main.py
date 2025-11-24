#!/usr/bin/env python3
import subprocess, threading, asyncio, os, aiofiles, queue
from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import uvicorn
import time
app = FastAPI()
LOGS = queue.Queue()
FLUTTER = None
PROJECT_DIR = "/app/project"
RELOAD_SIGNAL = PROJECT_DIR + "/.reload_signal"
def stream_logs(stream):
    while True:
        line = stream.readline()
        if not line:
            break
        LOGS.put(line.decode("utf-8"))
async def ws_log_stream(ws: WebSocket):
    await ws.accept()
    while not LOGS.empty():
        await ws.send_text(LOGS.get_nowait())
    try:
        while True:
            loop = asyncio.get_event_loop()
            line = await loop.run_in_executor(None, LOGS.get)
            await ws.send_text(line)
    except:
        await ws.close()
@app.websocket("/ws/logs")
async def logs(ws: WebSocket):
    await ws_log_stream(ws)
@app.put("/files/{path:path}")
async def upload_file(path: str, file: UploadFile = File(...), project_dir: str = ""):
    if not project_dir:
        raise HTTPException(400, "project_dir required")
    dest = Path(project_dir) / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)
    LOGS.put(f"[runner] updated {dest}\n")
    return JSONResponse({"ok": True})
@app.get("/health")
async def health():
    ok = FLUTTER and FLUTTER.poll() is None
    return {"status": "ok", "flutter_running": ok}
def watch_and_run_flutter(project_dir: str, web_port: int):
    global FLUTTER
    while True:
        # Wait for reload signal
        signal_file = Path(RELOAD_SIGNAL)
        if signal_file.exists():
            if FLUTTER and FLUTTER.poll() is None:
                LOGS.put("[runner] killing Flutter process for reload\n")
                FLUTTER.terminate()
                FLUTTER.wait()
            LOGS.put("[runner] starting Flutter web-server...\n")
            cmd = f"flutter run -d web-server --web-hostname=0.0.0.0 --web-port={web_port}"
            FLUTTER = subprocess.Popen(
                cmd, cwd=project_dir, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            threading.Thread(target=stream_logs, args=(FLUTTER.stdout,), daemon=True).start()
            signal_file.unlink()  # reset signal
        time.sleep(0.5)
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--project-dir", default="/app/project")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--web-port", type=int, default=8080)
    args = p.parse_args()
    Path(args.project_dir).mkdir(parents=True, exist_ok=True)
    # auto-create flutter project if empty
    if not (Path(args.project_dir) / "pubspec.yaml").exists():
        (Path(args.project_dir) / "pubspec.yaml").write_text(
            """name: preview_project
environment:
  sdk: ">=2.18.0 <3.0.0"
dependencies:
  flutter:
    sdk: flutter
flutter:
  uses-material-design: true
"""
        )
    lib = Path(args.project_dir) / "lib"
    lib.mkdir(exist_ok=True)
    if not (lib / "main.dart").exists():
        (lib / "main.dart").write_text(
            """import 'package:flutter/material.dart';
void main() => runApp(const MyApp());
class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text("Preview")),
        body: Center(child: Text("Replace lib/main.dart via API")),
      ),
    );
  }
}
"""
        )
    threading.Thread(target=watch_and_run_flutter, args=(args.project_dir, args.web_port), daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=args.port)

