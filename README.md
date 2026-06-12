# RAG Pipeline Event Monitor

A modular, drop-in event logging and browser system for full RAG pipelines.

---

## Architecture

```
rag_logger.py            ← PipelineLogger (per-stage)
      │  writes
      ▼
logs/rag_events.jsonl    ← structured event log (one JSON object per line)
      │  tailed by
      ▼
event_server.py          ← Flask REST + SSE server
      │  serves
      ▼
event_browser.html       ← live event table in the browser
```

---

## Files

| File | Purpose |
|---|---|
| `rag_logger.py` | Core logger — `get_logger(stage)` returns a `PipelineLogger` |
| `event_server.py` | Flask server — serves the browser + REST API + SSE live stream |
| `event_browser.html` | Standalone HTML event browser (also served by Flask) |
| `requirements.txt` | Python dependencies |

---

## Quick Start

```bash
# 1. install dependencies
pip install -r requirements.txt

# 2. start the event server
python event_server.py
# → http://localhost:5050

```

Open `http://localhost:5050` in your browser — events appear live.

---

## Using the logger in your own code

```python
from rag_logger import Stage, configure, get_logger

# call once at startup
configure(log_dir="logs", log_file="rag_events.jsonl", level="INFO", console=True)

# get a stage-scoped logger
log = get_logger(Stage.CHUNKING)

log.info("Chunking started", extra={"docs": 320})
log.warning("Chunk too large", extra={"doc_id": "abc", "tokens": 4200})
log.error("Write failed",    extra={"node": "vec-02", "disk_pct": 97})
log.critical("Quota hit",    extra={"model": "text-embedding-3-small"})

# exceptions with full traceback
try:
    ...
except Exception:
    log.exception("Unexpected error in chunking stage")
```

### Stage constants

```python
from rag_logger import Stage

Stage.DATA_INGESTION     # "data_ingestion"
Stage.CHUNKING           # "chunking"
Stage.EMBEDDING          # "embedding"
Stage.VECTOR_INDEXING    # "vector_indexing"
Stage.RETRIEVAL          # "retrieval"
Stage.CONTEXT_ASSEMBLY   # "context_assembly"
Stage.LLM_GENERATION     # "llm_generation"
Stage.OUTPUT_VALIDATION  # "output_validation"
Stage.DEPLOYMENT         # "deployment"
Stage.MONITORING         # "monitoring"
```

---

## REST API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/events` | All events; filter with `?severity=critical,error&stage=chunking&resolved=false` |
| `PATCH` | `/api/events/<id>` | Update `notes`, `action`, `resolved`, `message` |
| `GET` | `/api/stats` | Severity counts + per-stage breakdown |
| `GET` | `/api/events/stream` | Server-Sent Events — live tail |

---

## Event JSON schema

```json
{
  "event_id":  "EVT-3A1F2C",
  "timestamp": "2026-06-12T08:11:05+00:00",
  "stage":     "chunking",
  "severity":  "WARNING",
  "message":   "Chunk size exceeds token limit (4200 > 4096)",
  "logger":    "rag_pipeline.chunking",
  "resolved":  false,
  "extra": {
    "doc_id": "9871",
    "size":   4200
  }
}
```

---

## Browser features

- **Color-coded rows** — Critical (red), Error (amber), Warning (green), Info (blue)
- **Live updates** — SSE stream pushes new events without page refresh
- **Severity filter cards** — click any card to filter to that severity
- **Active / Resolved toggle** — hide resolved events or review them
- **Search** — filter by message text or stage name
- **Validate popup** — edit message, add root-cause notes, pick corrective action, mark resolved
- **One event per sequential step** — the rule is enforced by stage constants; multiple events in one stage show as separate rows

---

## Customising severity thresholds

All threshold values are keyword arguments on each stage function:

```python
chunking(docs, chunk_size=512, overlap=64, max_tokens=4096)
embedding(chunks, latency_warn_s=2.0)
vector_indexing(embedded, disk_warn_pct=90.0)
retrieval(query, index_meta, score_threshold=0.65)
context_assembly(query, retrieved, max_context_tokens=7000)
monitoring(embedding_kl_threshold=0.2)
```
