"""
event_server.py
---------------
Lightweight Flask server that:
  - Serves the event-browser UI at  GET  /
  - Exposes a REST API for the browser to read and update events
  - Watches rag_events.jsonl and streams new lines via Server-Sent Events

Endpoints
---------
  GET  /                     → serves event_browser.html
  GET  /api/events           → returns all events as JSON
  GET  /api/events/stream    → SSE stream of new events (live tail)
  PATCH /api/events/<id>     → update notes / action / resolved flag
  GET  /api/stats            → severity counts + stage summary

Start with:
    python event_server.py
    # or with auto-reload:
    FLASK_ENV=development flask --app event_server run --port 5050
"""

from __future__ import annotations

import json
import os
import queue
import threading
import time
from pathlib import Path
from typing import Any, Dict, Generator, List

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

from rag_logger import get_log_path

# ── config ───────────────────────────────────────────────────────────────────
LOG_PATH      = get_log_path() or Path("logs/rag_events.jsonl")
STATIC_DIR    = Path(__file__).parent
POLL_INTERVAL = 1.0          # seconds between tail polls

app = Flask(__name__, static_folder=str(STATIC_DIR))
CORS(app)

# ── in-memory event store ────────────────────────────────────────────────────
_events: Dict[str, Dict[str, Any]] = {}   # keyed by event_id
_lock   = threading.Lock()
_sse_queues: List[queue.Queue] = []


def _load_events_from_disk() -> None:
    """Read the entire .jsonl file and populate the in-memory store."""
    if not LOG_PATH.exists():
        return
    with open(LOG_PATH, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                eid = ev.get("event_id")
                if eid:
                    with _lock:
                        if eid not in _events:
                            _events[eid] = ev
            except json.JSONDecodeError:
                pass


def _tail_log_file() -> None:
    """Background thread: tail the log file and push new events to SSE queues."""
    last_size = 0
    while True:
        try:
            if LOG_PATH.exists():
                size = LOG_PATH.stat().st_size
                if size > last_size:
                    with open(LOG_PATH, encoding="utf-8") as fh:
                        fh.seek(last_size)
                        for line in fh:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                ev = json.loads(line)
                                eid = ev.get("event_id")
                                if eid:
                                    with _lock:
                                        if eid not in _events:
                                            _events[eid] = ev
                                    # fan-out to all SSE subscribers
                                    with _lock:
                                        for q in list(_sse_queues):
                                            try:
                                                q.put_nowait(ev)
                                            except queue.Full:
                                                pass
                            except json.JSONDecodeError:
                                pass
                    last_size = size
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)


# ── REST API ─────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "event_browser.html")


@app.route("/api/events", methods=["GET"])
def get_events():
    """
    Return all events, with optional filters:
      ?severity=critical,error
      ?stage=chunking,embedding
      ?resolved=false
    """
    severity_filter = request.args.get("severity", "")
    stage_filter    = request.args.get("stage", "")
    resolved_filter = request.args.get("resolved", "")

    with _lock:
        result = list(_events.values())

    if severity_filter:
        sev_set = {s.upper() for s in severity_filter.split(",")}
        result = [e for e in result if e.get("severity", "").upper() in sev_set]
    if stage_filter:
        st_set = {s.lower() for s in stage_filter.split(",")}
        result = [e for e in result if e.get("stage", "").lower() in st_set]
    if resolved_filter.lower() in ("true", "false"):
        want = resolved_filter.lower() == "true"
        result = [e for e in result if e.get("resolved", False) == want]

    result.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return jsonify(result)


@app.route("/api/events/<event_id>", methods=["PATCH"])
def patch_event(event_id: str):
    """
    Update mutable fields on an event.
    Accepts JSON body with any of:
      notes, action, resolved, message
    """
    with _lock:
        ev = _events.get(event_id)
    if ev is None:
        return jsonify({"error": "event not found"}), 404

    body = request.get_json(silent=True) or {}
    allowed = {"notes", "action", "resolved", "message"}
    updates = {k: v for k, v in body.items() if k in allowed}

    with _lock:
        _events[event_id].update(updates)

    return jsonify(_events[event_id])


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Return severity counts and per-stage breakdown."""
    with _lock:
        evs = list(_events.values())

    active = [e for e in evs if not e.get("resolved", False)]
    counts = {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
    by_stage: Dict[str, int] = {}

    for e in active:
        sev = e.get("severity", "").upper()
        if sev in counts:
            counts[sev] += 1
        stage = e.get("stage", "unknown")
        by_stage[stage] = by_stage.get(stage, 0) + 1

    return jsonify({"counts": counts, "by_stage": by_stage, "total_active": len(active)})


@app.route("/api/events/stream")
def sse_stream():
    """
    Server-Sent Events endpoint.
    The browser keeps this open and receives new events as they arrive.
    """
    q: queue.Queue = queue.Queue(maxsize=100)
    with _lock:
        _sse_queues.append(q)

    def generate() -> Generator[str, None, None]:
        try:
            while True:
                try:
                    ev = q.get(timeout=20)
                    yield f"data: {json.dumps(ev)}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        finally:
            with _lock:
                if q in _sse_queues:
                    _sse_queues.remove(q)

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ── startup ───────────────────────────────────────────────────────────────────
def _start_background_tailer():
    t = threading.Thread(target=_tail_log_file, daemon=True)
    t.start()


_load_events_from_disk()
_start_background_tailer()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    print(f"RAG Event Monitor → http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)