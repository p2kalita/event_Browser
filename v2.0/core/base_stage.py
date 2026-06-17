from abc import ABC, abstractmethod
from typing import Any

from core.event_bus import EventBus, Event


class BaseStage(ABC):
    """
    Any validation stage inherits from this.
    Partha defines the interface:
        - name       : display label
        - critical   : if True, failure aborts the pipeline
        - execute()  : subclass implements domain logic

    Partha does NOT dictate which events get published —
    that's entirely up to the subclass.
    """

    def __init__(self, name: str, critical: bool = False):
        self.name     = name
        self.critical = critical
        self._bus     = EventBus()   # always the singleton

    @abstractmethod
    def execute(self, context: dict) -> bool:
        """
        Run the stage against the given context dict.
        Returns True (passed) or False (failed).
        Subclass is responsible for publishing events.
        """
        ...

    def _publish(self, event_type: Any, payload: dict,
                 severity: str = "INFO") -> Event:
        """
        Publish a stage event with standard metadata.

        Domain stages can still choose any event name and payload shape.
        The core only adds the stage name so generic dashboards and audit
        consumers can display unknown future stages cleanly.
        """
        event_payload = {
            "stage": self.name,
            **payload,
        }
        return self._bus.publish(event_type, event_payload, severity)
