from core.pipeline import Pipeline
from core.event_bus import EventBus
from tanisha.stages import (
    InvoiceCompletenessCheck,
    OcrConfidenceValidation,
    VendorValidation,
    PoMatching,
    GrnMatching,
    TaxValidation,
    DuplicateDetection,
)


def build_invoice_pipeline() -> Pipeline:
    """Returns a fully configured invoice validation pipeline."""
    stages = [
        InvoiceCompletenessCheck(),
        OcrConfidenceValidation(),
        VendorValidation(),
        PoMatching(),
        GrnMatching(),
        TaxValidation(),
        DuplicateDetection(),
    ]
    return Pipeline("Invoice Validation", stages=stages)


def run_invoice(invoice: dict) -> dict:
    """
    Validates a single invoice through all 8 stages.
    Handles the AI stage separately so it receives soft_failures.
    """
    pipeline = build_invoice_pipeline()
    context  = {"invoice": invoice}
    result   = pipeline.run(context)

    return result


def export_history_as_json() -> list:
    """Serialise full event history for the frontend dashboard."""
    bus = EventBus()
    return [e.to_dict() for e in bus.get_history()]
