from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# ── Singleton Metaclass ────────────────────────────────────────
class SingletonMeta(type):
    _instances: Dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# ── Event envelope ─────────────────────────────────────────────
class Event:
    def __init__(self, event_type: Any, payload: Dict[str, Any],
                 severity: str = "INFO"):
        self.id        = f"evt_{uuid.uuid4().hex[:8]}"
        self.type      = self._normalize_type(event_type)
        self.severity  = severity.upper()   # INFO | WARNING | ERROR | CRITICAL
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.payload   = payload

    @staticmethod
    def _normalize_type(event_type: Any) -> str:
        if isinstance(event_type, Enum):
            return str(event_type.value)
        return str(event_type)

    def to_dict(self) -> Dict:
        return {
            "id":        self.id,
            "type":      self.type,
            "severity":  self.severity,
            "timestamp": self.timestamp,
            "payload":   self.payload,
        }

    def __repr__(self):
        return f"Event(type={self.type!r}, severity={self.severity!r}, id={self.id!r})"


# ── EventBus Singleton ─────────────────────────────────────────
class EventBus(metaclass=SingletonMeta):
    """
    Partha's shared publish/subscribe channel.

    Partha knows NOTHING about invoice validation, vendors,
    OCR, PO matching, etc. He only provides:
        bus.publish(event_type, payload, severity)
        bus.subscribe(event_type, handler)  -> unsub callable
        bus.subscribe_all(handler)          -> catches every event
        bus.get_history()                   -> full audit trail
        bus.clear_history()
        bus.get_listener_count(event_type)

    Any domain (Tanisha's, or anyone else's) can plug in
    their own event types and consumers without Partha
    ever touching this file.
    """

    def __init__(self):
        self._listeners:          Dict[str, List[Callable]] = {}
        self._severity_listeners: Dict[str, List[Callable]] = {}
        self._history:            List[Event]               = []

    # ── Subscribe ──────────────────────────────────────────────

    @staticmethod
    def _event_key(event_type: Any) -> str:
        if isinstance(event_type, Enum):
            return str(event_type.value)
        return str(event_type)

    def subscribe(self, event_type: Any, handler: Callable[[Event], None]) -> Callable:
        if not callable(handler):
            raise TypeError(f"handler for '{event_type}' must be callable")
        key = self._event_key(event_type)
        self._listeners.setdefault(key, []).append(handler)
        return lambda: self.unsubscribe(key, handler)

    def unsubscribe(self, event_type: Any, handler: Callable) -> None:
        key = self._event_key(event_type)
        if key in self._listeners:
            self._listeners[key] = [
                h for h in self._listeners[key] if h is not handler
            ]

    def subscribe_all(self, handler: Callable[[Event], None]) -> Callable:
        """Wildcard — fires for every event regardless of type."""
        return self.subscribe("*", handler)

    def subscribe_severity(self, severity: str, handler: Callable[[Event], None]) -> Callable:
        """
        Subscribe to all events at one severity.

        Consumers can react to WARNING, ERROR, or CRITICAL without knowing
        Tanisha's stage names or event names.
        """
        if not callable(handler):
            raise TypeError(f"handler for severity '{severity}' must be callable")
        key = severity.upper()
        self._severity_listeners.setdefault(key, []).append(handler)
        return lambda: self.unsubscribe_severity(key, handler)

    def unsubscribe_severity(self, severity: str, handler: Callable) -> None:
        key = severity.upper()
        if key in self._severity_listeners:
            self._severity_listeners[key] = [
                h for h in self._severity_listeners[key] if h is not handler
            ]

    # ── Publish ────────────────────────────────────────────────

    def publish(self, event_type: Any,
                payload: Optional[Dict[str, Any]] = None,
                severity: str = "INFO") -> Event:
        event = Event(event_type, payload or {}, severity)
        self._history.append(event)

        handlers = (
            self._listeners.get(event.type, []) +
            self._listeners.get("*", []) +
            self._severity_listeners.get(event.severity, [])
        )

        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:
                print(f"[EventBus] Handler error for '{event_type}': {exc}")

        return event

    # ── Diagnostics ────────────────────────────────────────────

    def get_history(self) -> List[Event]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()

    def get_listener_count(self, event_type: Any) -> int:
        return len(self._listeners.get(self._event_key(event_type), []))

    def get_counts_by_severity(self) -> Dict[str, int]:
        counts = {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
        for e in self._history:
            if e.severity in counts:
                counts[e.severity] += 1
        return counts
