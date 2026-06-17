from enum import StrEnum


class InvoiceEvents(StrEnum):

    # ── 1. Invoice Completeness Check ──────────────────────────
    COMPLETENESS_PASSED     = "COMPLETENESS_PASSED"
    COMPLETENESS_FAILED     = "COMPLETENESS_FAILED"

    # ── 2. OCR Confidence Validation ───────────────────────────
    OCR_HIGH_CONFIDENCE     = "OCR_HIGH_CONFIDENCE"
    OCR_LOW_CONFIDENCE      = "OCR_LOW_CONFIDENCE"

    # ── 3. Vendor Validation ────────────────────────────────────
    VENDOR_VALIDATED        = "VENDOR_VALIDATED"
    VENDOR_NOT_FOUND        = "VENDOR_NOT_FOUND"
    VENDOR_BLACKLISTED      = "VENDOR_BLACKLISTED"

    # ── 4. PO Matching ──────────────────────────────────────────
    PO_MATCHED              = "PO_MATCHED"
    PO_MISMATCH             = "PO_MISMATCH"
    PO_NOT_FOUND            = "PO_NOT_FOUND"

    # ── 5. GRN Matching ─────────────────────────────────────────
    GRN_MATCHED             = "GRN_MATCHED"
    GRN_PARTIAL_MATCH       = "GRN_PARTIAL_MATCH"
    GRN_NOT_FOUND           = "GRN_NOT_FOUND"

    # ── 6. Tax Validation ───────────────────────────────────────
    TAX_VALID               = "TAX_VALID"
    TAX_MISMATCH            = "TAX_MISMATCH"
    TAX_EXEMPTION_APPLIED   = "TAX_EXEMPTION_APPLIED"

    # ── 7. Duplicate Detection ──────────────────────────────────
    DUPLICATE_NOT_FOUND     = "DUPLICATE_NOT_FOUND"
    DUPLICATE_DETECTED      = "DUPLICATE_DETECTED"

