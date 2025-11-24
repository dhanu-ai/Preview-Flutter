# Flutter Preview Docker Setup

This project provides a live preview environment for a Flutter Web project using **Docker**. It includes:

* **Flutter Web container** (`flutter`) — serves the Flutter app on `localhost:8080`.
* **Runner container** (`runner`) — FastAPI backend that manages Flutter hot reload via API (`/files/{path}`) and streams logs via WebSocket (`/ws/logs`).
* **Frontend container** (`frontend`) — Streamlit app on `localhost:8501` for interacting with the runner.

## Features

* Live Flutter Web preview inside Docker.
* Hot reload triggered by file changes via `.reload_signal` or API.
* WebSocket logs from Flutter process streamed to frontend.
* Fully isolated environment — host OS doesn’t need Flutter installed.

## Prerequisites

* Docker & Docker Compose installed.
* Optional: `inotify-tools` (used inside Flutter container for file watching).

## Folder Structure

```
project-root/
├─ flutter-project/       # Flutter source code (lib/, web/, pubspec.yaml)
├─ frontend/              # Streamlit UI (main.py, requirements.txt)
├─ runner/                # FastAPI runner (runner.py, requirements.txt)
├─ Dockerfile.flutter     # Flutter container build
├─ Dockerfile.runner      # Runner container build
├─ watch_flutter.sh       # Flutter watcher script
└─ docker-compose.yaml    # Docker Compose configuration
```

## Usage

1. **Build and start all containers**:

```bash
docker-compose up --build
```

2. **Access services**:

* Flutter Web: [http://localhost:8080](http://localhost:8080)
* FastAPI Runner API: [http://localhost:8000](http://localhost:8000)
* Streamlit Frontend: [http://localhost:8501](http://localhost:8501)

3. **Hot Reload Flutter**:

* Edit any file in `flutter-project/lib/`.
* Runner watches `.reload_signal` or API file upload triggers Flutter restart automatically.
* Logs stream live to Streamlit frontend via WebSocket.

## API

### Upload a file to project

```
PUT /files/{path}
```

**Parameters:**

* `path` (string) — relative path in Flutter project.
* `project_dir` (string) — root project path inside container.

**Body:** `multipart/form-data` with `file`.

**Response:**

```json
{"ok": true}
```

### Health check

```
GET /health
```

Returns JSON:

```json
{
  "status": "ok",
  "flutter_running": true
}
```

### Logs WebSocket

```
ws://localhost:8000/ws/logs
```

Streams stdout from Flutter process in real time.

## Notes

* The Flutter container uses a **snapshot of `main.dart`** initially. Host changes only reflect if mounted volume (`./flutter-project:/app/project`) is active.
* Streamlit runs independently; changing its port does not affect Flutter reload.
* To fully isolate, you can let Flutter container manage all code inside `/app/project` without mounting.

## Troubleshooting

* **Flutter not reflecting changes:** Ensure the `flutter-project` volume is mounted and `.reload_signal` is being updated.
* **Port conflicts:** Change ports in `docker-compose.yaml` if 8080, 8000, or 8501 are taken.
* **Windows users:** Docker volume mounts may not propagate instantly; consider using Linux container or WSL2 for faster reloads.
