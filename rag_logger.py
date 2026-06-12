"""
rag_logger.py
-------------
Central logger for the RAG pipeline event monitor.
Captures structured events at every pipeline stage and writes them to:
  - A JSON-lines log file  (machine-readable, consumed by the browser)
  - Console (optional, coloured via colorama if available)

Usage
-----
    from rag_logger import get_logger

    log = get_logger("chunking")
    log.info("Chunking complete", extra={"chunks": 3840, "docs": 320})
    log.warning("Chunk size exceeded", extra={"doc_id": "9871", "size": 4200})
    log.error("Write failure", extra={"node": "rag-vec-02", "disk_pct": 97})
    log.critical("Endpoint timeout", extra={"request_id": "#4482"})
"""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# ── optional colour support ──────────────────────────────────────────────────
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    _HAS_COLOR = True
except ImportError:
    _HAS_COLOR = False

# ── pipeline stage constants ─────────────────────────────────────────────────
class Stage:
    DATA_INGESTION    = "data_ingestion"
    CHUNKING          = "chunking"
    EMBEDDING         = "embedding"
    VECTOR_INDEXING   = "vector_indexing"
    RETRIEVAL         = "retrieval"
    CONTEXT_ASSEMBLY  = "context_assembly"
    LLM_GENERATION    = "llm_generation"
    OUTPUT_VALIDATION = "output_validation"
    DEPLOYMENT        = "deployment"
    MONITORING        = "monitoring"

    ALL = [
        DATA_INGESTION, CHUNKING, EMBEDDING, VECTOR_INDEXING,
        RETRIEVAL, CONTEXT_ASSEMBLY, LLM_GENERATION,
        OUTPUT_VALIDATION, DEPLOYMENT, MONITORING,
    ]

# ── severity colours ─────────────────────────────────────────────────────────
_LEVEL_COLOR = {
    "CRITICAL": "\033[91m",   # bright red
    "ERROR":    "\033[93m",   # yellow
    "WARNING":  "\033[92m",   # green
    "INFO":     "\033[94m",   # blue
    "DEBUG":    "\033[90m",   # grey
    "RESET":    "\033[0m",
}


# ── JSON-lines handler ───────────────────────────────────────────────────────
class JsonLinesHandler(logging.Handler):
    """Appends one JSON object per log record to a .jsonl file."""

    _lock = threading.Lock()

    def __init__(self, log_path: Path):
        super().__init__()
        self.log_path = log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            payload = self._build_payload(record)
            line = json.dumps(payload, default=str, ensure_ascii=False)
            with self._lock:
                with self.log_path.open("a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
        except Exception:
            self.handleError(record)

    @staticmethod
    def _build_payload(record: logging.LogRecord) -> Dict[str, Any]:
        extra = getattr(record, "pipeline_extra", {})
        payload: Dict[str, Any] = {
            "event_id":  getattr(record, "event_id", f"EVT-{uuid.uuid4().hex[:6].upper()}"),
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "stage":     getattr(record, "stage", record.name),
            "severity":  record.levelname,
            "message":   record.getMessage(),
            "logger":    record.name,
            "resolved":  False,
        }
        if extra:
            payload["extra"] = extra
        if record.exc_info:
            payload["traceback"] = traceback.format_exception(*record.exc_info)
        return payload


# ── coloured console handler ─────────────────────────────────────────────────
class ColouredConsoleHandler(logging.StreamHandler):
    """Pretty-prints records to stderr with ANSI colours per severity."""

    _ICONS = {
        "CRITICAL": "✖",
        "ERROR":    "✘",
        "WARNING":  "⚠",
        "INFO":     "ℹ",
        "DEBUG":    "·",
    }

    def emit(self, record: logging.LogRecord) -> None:
        try:
            col   = _LEVEL_COLOR.get(record.levelname, "")
            reset = _LEVEL_COLOR["RESET"]
            icon  = self._ICONS.get(record.levelname, " ")
            stage = getattr(record, "stage", record.name)
            ts    = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
            extra = getattr(record, "pipeline_extra", {})
            extra_str = ("  " + "  ".join(f"{k}={v}" for k, v in extra.items())) if extra else ""

            line = (
                f"{col}{icon} [{ts}] [{record.levelname:<8}] "
                f"[{stage}]{reset}  {record.getMessage()}"
                f"{col}{extra_str}{reset}"
            )
            self.stream.write(line + "\n")
            self.stream.flush()
        except Exception:
            self.handleError(record)


# ── LogAdapter — attaches stage + extra to every record ─────────────────────
class PipelineLogger(logging.LoggerAdapter):
    """
    Wraps a stdlib Logger and stamps every record with:
      - stage       : the RAG pipeline stage name
      - event_id    : auto-generated EVT-XXXXXX identifier
      - pipeline_extra : arbitrary key-value metadata
    """

    def __init__(self, logger: logging.Logger, stage: str):
        super().__init__(logger, extra={})
        self.stage = stage

    # ── public helpers ────────────────────────────────────────────────────────
    def debug(self, msg, *args, extra: Optional[Dict] = None, **kwargs):
        self._emit(logging.DEBUG, msg, *args, extra=extra, **kwargs)

    def info(self, msg, *args, extra: Optional[Dict] = None, **kwargs):
        self._emit(logging.INFO, msg, *args, extra=extra, **kwargs)

    def warning(self, msg, *args, extra: Optional[Dict] = None, **kwargs):
        self._emit(logging.WARNING, msg, *args, extra=extra, **kwargs)

    def error(self, msg, *args, extra: Optional[Dict] = None, **kwargs):
        self._emit(logging.ERROR, msg, *args, extra=extra, **kwargs)

    def critical(self, msg, *args, extra: Optional[Dict] = None, **kwargs):
        self._emit(logging.CRITICAL, msg, *args, extra=extra, **kwargs)

    def exception(self, msg, *args, extra: Optional[Dict] = None, **kwargs):
        kwargs["exc_info"] = True
        self._emit(logging.ERROR, msg, *args, extra=extra, **kwargs)

    # ── internal ──────────────────────────────────────────────────────────────
    def _emit(self, level: int, msg, *args, extra: Optional[Dict] = None, **kwargs):
        merged = {
            "stage":          self.stage,
            "event_id":       f"EVT-{uuid.uuid4().hex[:6].upper()}",
            "pipeline_extra": extra or {},
        }
        kwargs["extra"] = merged
        self.logger.log(level, msg, *args, **kwargs)


# ── factory ──────────────────────────────────────────────────────────────────
_loggers: Dict[str, PipelineLogger] = {}
_root_configured = False
_config: Dict[str, Any] = {}


def configure(
    log_dir: str = "logs",
    log_file: str = "rag_events.jsonl",
    level: str = "INFO",
    console: bool = True,
) -> None:
    """
    Call once at application start-up (before get_logger).

    Parameters
    ----------
    log_dir   : directory where the .jsonl file is written
    log_file  : filename for the JSON-lines event log
    level     : minimum level – "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL"
    console   : whether to also print coloured output to stderr
    """
    global _root_configured, _config

    _config = {
        "log_path": Path(log_dir) / log_file,
        "level":    getattr(logging, level.upper(), logging.INFO),
        "console":  console,
    }

    root = logging.getLogger("rag_pipeline")
    root.setLevel(_config["level"])
    root.handlers.clear()
    root.propagate = False

    root.addHandler(JsonLinesHandler(_config["log_path"]))
    if console:
        root.addHandler(ColouredConsoleHandler(sys.stderr))

    _root_configured = True


def get_logger(stage: str) -> PipelineLogger:
    """
    Return a PipelineLogger for *stage*.  Calls configure() with defaults
    if it has not yet been called.

    Parameters
    ----------
    stage : one of the Stage.* constants, or any custom string
    """
    global _root_configured
    if not _root_configured:
        configure()

    if stage not in _loggers:
        inner = logging.getLogger(f"rag_pipeline.{stage}")
        _loggers[stage] = PipelineLogger(inner, stage)

    return _loggers[stage]


def get_log_path() -> Optional[Path]:
    """Return the path of the active .jsonl log file."""
    return _config.get("log_path")
