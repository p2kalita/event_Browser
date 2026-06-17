from core.base_stage import BaseStage
from tanisha.invoice_events import InvoiceEvents


class InvoiceCompletenessCheck(BaseStage):
    def __init__(self):
        super().__init__(name="Invoice Completeness", critical=True)

    def execute(self, ctx: dict) -> bool:
        invoice  = ctx["invoice"]
        required = ["vendor_id", "invoice_number", "line_items", "total_amount", "due_date"]
        missing  = [f for f in required if not invoice.get(f)]

        if missing:
            self._publish(InvoiceEvents.COMPLETENESS_FAILED, {
                "invoice_id":     invoice["invoice_number"],
                "missing_fields": missing,
            }, severity="ERROR")
            return False

        self._publish(InvoiceEvents.COMPLETENESS_PASSED, {
            "invoice_id": invoice["invoice_number"],
        })
        return True


class OcrConfidenceValidation(BaseStage):
    THRESHOLD = 0.85

    def __init__(self):
        super().__init__(name="OCR Confidence", critical=False)

    def execute(self, ctx: dict) -> bool:
        invoice   = ctx["invoice"]
        low       = [
            {"field": f, "score": s}
            for f, s in invoice.get("ocr_scores", {}).items()
            if s < self.THRESHOLD
        ]
        if low:
            self._publish(InvoiceEvents.OCR_LOW_CONFIDENCE, {
                "invoice_id":            invoice["invoice_number"],
                "low_confidence_fields": low,
                "threshold":             self.THRESHOLD,
            }, severity="WARNING")
            return False

        self._publish(InvoiceEvents.OCR_HIGH_CONFIDENCE, {
            "invoice_id": invoice["invoice_number"],
        })
        return True


class VendorValidation(BaseStage):
    KNOWN       = {"V001", "V002", "V003"}
    BLACKLISTED = {"V999"}

    def __init__(self):
        super().__init__(name="Vendor Validation", critical=True)

    def execute(self, ctx: dict) -> bool:
        invoice = ctx["invoice"]
        vid     = invoice["vendor_id"]

        if vid in self.BLACKLISTED:
            self._publish(InvoiceEvents.VENDOR_BLACKLISTED, {
                "invoice_id": invoice["invoice_number"],
                "vendor_id":  vid,
            }, severity="CRITICAL")
            return False

        if vid not in self.KNOWN:
            self._publish(InvoiceEvents.VENDOR_NOT_FOUND, {
                "invoice_id": invoice["invoice_number"],
                "vendor_id":  vid,
            }, severity="ERROR")
            return False

        self._publish(InvoiceEvents.VENDOR_VALIDATED, {
            "invoice_id": invoice["invoice_number"],
            "vendor_id":  vid,
        })
        return True


class PoMatching(BaseStage):
    PO_DB = {"PO-2024-55": {"amount": 15000.0}}

    def __init__(self):
        super().__init__(name="PO Matching", critical=False)

    def execute(self, ctx: dict) -> bool:
        invoice = ctx["invoice"]
        po      = self.PO_DB.get(invoice.get("po_number"))

        if not po:
            self._publish(InvoiceEvents.PO_NOT_FOUND, {
                "invoice_id": invoice["invoice_number"],
                "po_number":  invoice.get("po_number"),
            }, severity="ERROR")
            return False

        if abs(po["amount"] - invoice["total_amount"]) > 0.01:
            self._publish(InvoiceEvents.PO_MISMATCH, {
                "invoice_id":     invoice["invoice_number"],
                "po_amount":      po["amount"],
                "invoice_amount": invoice["total_amount"],
            }, severity="WARNING")
            return False

        self._publish(InvoiceEvents.PO_MATCHED, {
            "invoice_id": invoice["invoice_number"],
            "po_number":  invoice.get("po_number"),
        })
        return True


class GrnMatching(BaseStage):
    GRN_DB = {"GRN-2024-88": {"received": 10}}

    def __init__(self):
        super().__init__(name="GRN Matching", critical=False)

    def execute(self, ctx: dict) -> bool:
        invoice = ctx["invoice"]
        grn     = self.GRN_DB.get(invoice.get("grn_number"))

        if not grn:
            self._publish(InvoiceEvents.GRN_NOT_FOUND, {
                "invoice_id": invoice["invoice_number"],
                "grn_number": invoice.get("grn_number"),
            }, severity="ERROR")
            return False

        self._publish(InvoiceEvents.GRN_MATCHED, {
            "invoice_id":    invoice["invoice_number"],
            "items_received": grn["received"],
        })
        return True


class TaxValidation(BaseStage):
    TAX_RATE = 0.18

    def __init__(self):
        super().__init__(name="Tax Validation", critical=False)

    def execute(self, ctx: dict) -> bool:
        invoice     = ctx["invoice"]
        expected    = round(invoice["total_amount"] * self.TAX_RATE, 2)
        diff        = abs(expected - invoice["tax_amount"])

        if diff > 0.5:
            self._publish(InvoiceEvents.TAX_MISMATCH, {
                "invoice_id": invoice["invoice_number"],
                "stated":     invoice["tax_amount"],
                "calculated": expected,
                "difference": round(diff, 2),
            }, severity="WARNING")
            return False

        self._publish(InvoiceEvents.TAX_VALID, {
            "invoice_id": invoice["invoice_number"],
            "tax_amount": invoice["tax_amount"],
        })
        return True


class DuplicateDetection(BaseStage):
    PROCESSED = {"INV-2024-000", "INV-2024-999"}

    def __init__(self):
        super().__init__(name="Duplicate Detection", critical=True)

    def execute(self, ctx: dict) -> bool:
        invoice = ctx["invoice"]

        if invoice["invoice_number"] in self.PROCESSED:
            self._publish(InvoiceEvents.DUPLICATE_DETECTED, {
                "invoice_id": invoice["invoice_number"],
            }, severity="CRITICAL")
            return False

        self._publish(InvoiceEvents.DUPLICATE_NOT_FOUND, {
            "invoice_id": invoice["invoice_number"],
        })
        return True


