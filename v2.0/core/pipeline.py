from typing import List
from core.base_stage import BaseStage
from core.event_bus import EventBus


class Pipeline:
    """
    Runs a list of BaseStage objects in sequence.

    Partha provides this generic runner.
    Tanisha plugs in her own stages.

    Usage:
        pipeline = Pipeline("Invoice Validation", stages=[...])
        pipeline.run(context={"invoice": invoice_obj})
    """

    PIPELINE_STARTED   = "PIPELINE_STARTED"
    PIPELINE_COMPLETED = "PIPELINE_COMPLETED"
    PIPELINE_ABORTED   = "PIPELINE_ABORTED"

    def __init__(self, name: str, stages: List[BaseStage]):
        self.name   = name
        self.stages = stages
        self._bus   = EventBus()

    def run(self, context: dict) -> dict:
        """
        Execute all stages sequentially.

        Returns a result dict:
            {
                "passed":        bool,
                "stages_passed": int,
                "soft_failures": [stage_name, ...],
                "aborted_at":    stage_name | None,
            }
        """
        soft_failures = []
        aborted_at    = None
        invoice_id     = self._context_invoice_id(context)

        self._bus.publish(self.PIPELINE_STARTED, {
            "pipeline": self.name,
            "invoice_id": invoice_id,
            "context_keys": list(context.keys()),
        }, severity="INFO")

        for stage in self.stages:
            passed = stage.execute(context)

            if not passed:
                if stage.critical:
                    aborted_at = stage.name
                    self._bus.publish(self.PIPELINE_ABORTED, {
                        "pipeline":   self.name,
                        "invoice_id": invoice_id,
                        "aborted_at": stage.name,
                    }, severity="CRITICAL")
                    break
                else:
                    soft_failures.append(stage.name)

        overall_passed = aborted_at is None and not soft_failures

        if aborted_at is None:
            self._bus.publish(self.PIPELINE_COMPLETED, {
                "pipeline":      self.name,
                "invoice_id":    invoice_id,
                "stages_passed": len(self.stages) - len(soft_failures),
                "soft_failures": soft_failures,
            }, severity="INFO")

        return {
            "passed":        overall_passed,
            "stages_passed": len(self.stages) - len(soft_failures),
            "soft_failures": soft_failures,
            "aborted_at":    aborted_at,
        }

    @staticmethod
    def _context_invoice_id(context: dict) -> str | None:
        invoice = context.get("invoice")
        if isinstance(invoice, dict):
            return invoice.get("invoice_number") or invoice.get("invoice_id")
        return None
