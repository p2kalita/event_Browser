window.EVENTS_DATA = [
  {
    "id": "evt_7249a5ac",
    "type": "PIPELINE_STARTED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-101",
      "context_keys": [
        "invoice"
      ]
    }
  },
  {
    "id": "evt_f4e86571",
    "type": "COMPLETENESS_PASSED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Invoice Completeness",
      "invoice_id": "INV-2024-101"
    }
  },
  {
    "id": "evt_7dc8ae59",
    "type": "OCR_HIGH_CONFIDENCE",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "OCR Confidence",
      "invoice_id": "INV-2024-101"
    }
  },
  {
    "id": "evt_09fa5ffd",
    "type": "VENDOR_VALIDATED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Vendor Validation",
      "invoice_id": "INV-2024-101",
      "vendor_id": "V001"
    }
  },
  {
    "id": "evt_cba200f4",
    "type": "PO_MATCHED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "PO Matching",
      "invoice_id": "INV-2024-101",
      "po_number": "PO-2024-55"
    }
  },
  {
    "id": "evt_9329ad2d",
    "type": "GRN_MATCHED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "GRN Matching",
      "invoice_id": "INV-2024-101",
      "items_received": 10
    }
  },
  {
    "id": "evt_b4276f88",
    "type": "TAX_VALID",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Tax Validation",
      "invoice_id": "INV-2024-101",
      "tax_amount": 2700.0
    }
  },
  {
    "id": "evt_a84b67a5",
    "type": "DUPLICATE_NOT_FOUND",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Duplicate Detection",
      "invoice_id": "INV-2024-101"
    }
  },
  {
    "id": "evt_a9f28b05",
    "type": "PIPELINE_COMPLETED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-101",
      "stages_passed": 7,
      "soft_failures": []
    }
  },
  {
    "id": "evt_8bb1688a",
    "type": "AI_AUTO_APPROVED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "AI Clarification",
      "invoice_id": "INV-2024-101",
      "message": "All checks passed. Auto-approved."
    }
  },
  {
    "id": "evt_ef9379e9",
    "type": "PIPELINE_STARTED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-202",
      "context_keys": [
        "invoice"
      ]
    }
  },
  {
    "id": "evt_728fb9cf",
    "type": "COMPLETENESS_PASSED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Invoice Completeness",
      "invoice_id": "INV-2024-202"
    }
  },
  {
    "id": "evt_f2c2b0e0",
    "type": "OCR_LOW_CONFIDENCE",
    "severity": "WARNING",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "OCR Confidence",
      "invoice_id": "INV-2024-202",
      "low_confidence_fields": [
        {
          "field": "total_amount",
          "score": 0.61
        }
      ],
      "threshold": 0.85
    }
  },
  {
    "id": "evt_728320d9",
    "type": "VENDOR_VALIDATED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Vendor Validation",
      "invoice_id": "INV-2024-202",
      "vendor_id": "V002"
    }
  },
  {
    "id": "evt_c8b00604",
    "type": "PO_MATCHED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "PO Matching",
      "invoice_id": "INV-2024-202",
      "po_number": "PO-2024-55"
    }
  },
  {
    "id": "evt_d4b3606f",
    "type": "GRN_MATCHED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "GRN Matching",
      "invoice_id": "INV-2024-202",
      "items_received": 10
    }
  },
  {
    "id": "evt_004ec7ac",
    "type": "TAX_MISMATCH",
    "severity": "WARNING",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Tax Validation",
      "invoice_id": "INV-2024-202",
      "stated": 100.0,
      "calculated": 2700.0,
      "difference": 2600.0
    }
  },
  {
    "id": "evt_c34a0d11",
    "type": "DUPLICATE_NOT_FOUND",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Duplicate Detection",
      "invoice_id": "INV-2024-202"
    }
  },
  {
    "id": "evt_e63627a1",
    "type": "PIPELINE_COMPLETED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-202",
      "stages_passed": 5,
      "soft_failures": [
        "OCR Confidence",
        "Tax Validation"
      ]
    }
  },
  {
    "id": "evt_4babbeac",
    "type": "AI_CLARIFICATION_NEEDED",
    "severity": "WARNING",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "AI Clarification",
      "invoice_id": "INV-2024-202",
      "failed_stages": [
        "OCR Confidence",
        "Tax Validation"
      ],
      "recommendation": "Review needed for: OCR Confidence, Tax Validation"
    }
  },
  {
    "id": "evt_7f6c0c57",
    "type": "PIPELINE_STARTED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-303",
      "context_keys": [
        "invoice"
      ]
    }
  },
  {
    "id": "evt_a20ebe4c",
    "type": "COMPLETENESS_PASSED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Invoice Completeness",
      "invoice_id": "INV-2024-303"
    }
  },
  {
    "id": "evt_a509ea2a",
    "type": "OCR_HIGH_CONFIDENCE",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "OCR Confidence",
      "invoice_id": "INV-2024-303"
    }
  },
  {
    "id": "evt_f40fae7a",
    "type": "VENDOR_BLACKLISTED",
    "severity": "CRITICAL",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Vendor Validation",
      "invoice_id": "INV-2024-303",
      "vendor_id": "V999"
    }
  },
  {
    "id": "evt_63cfdc5b",
    "type": "PIPELINE_ABORTED",
    "severity": "CRITICAL",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-303",
      "aborted_at": "Vendor Validation"
    }
  },
  {
    "id": "evt_74d8a6ec",
    "type": "PIPELINE_STARTED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-404",
      "context_keys": [
        "invoice"
      ]
    }
  },
  {
    "id": "evt_7c42e7b2",
    "type": "COMPLETENESS_FAILED",
    "severity": "ERROR",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Invoice Completeness",
      "invoice_id": "INV-2024-404",
      "missing_fields": [
        "line_items",
        "total_amount",
        "due_date"
      ]
    }
  },
  {
    "id": "evt_e7c19e4b",
    "type": "PIPELINE_ABORTED",
    "severity": "CRITICAL",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-404",
      "aborted_at": "Invoice Completeness"
    }
  },
  {
    "id": "evt_92f71cdb",
    "type": "PIPELINE_STARTED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-999",
      "context_keys": [
        "invoice"
      ]
    }
  },
  {
    "id": "evt_402ceb45",
    "type": "COMPLETENESS_PASSED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Invoice Completeness",
      "invoice_id": "INV-2024-999"
    }
  },
  {
    "id": "evt_0bab4344",
    "type": "OCR_HIGH_CONFIDENCE",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "OCR Confidence",
      "invoice_id": "INV-2024-999"
    }
  },
  {
    "id": "evt_898692d8",
    "type": "VENDOR_VALIDATED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Vendor Validation",
      "invoice_id": "INV-2024-999",
      "vendor_id": "V001"
    }
  },
  {
    "id": "evt_ae836614",
    "type": "PO_MATCHED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "PO Matching",
      "invoice_id": "INV-2024-999",
      "po_number": "PO-2024-55"
    }
  },
  {
    "id": "evt_a3df5906",
    "type": "GRN_MATCHED",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "GRN Matching",
      "invoice_id": "INV-2024-999",
      "items_received": 10
    }
  },
  {
    "id": "evt_d5b5459d",
    "type": "TAX_VALID",
    "severity": "INFO",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Tax Validation",
      "invoice_id": "INV-2024-999",
      "tax_amount": 2700.0
    }
  },
  {
    "id": "evt_b5f2328d",
    "type": "DUPLICATE_DETECTED",
    "severity": "CRITICAL",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "stage": "Duplicate Detection",
      "invoice_id": "INV-2024-999"
    }
  },
  {
    "id": "evt_823732fe",
    "type": "PIPELINE_ABORTED",
    "severity": "CRITICAL",
    "timestamp": "2026-06-15T19:52:27.789956+00:00",
    "payload": {
      "pipeline": "Invoice Validation",
      "invoice_id": "INV-2024-999",
      "aborted_at": "Duplicate Detection"
    }
  }
];
