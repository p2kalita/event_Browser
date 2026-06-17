"""
============================================================
  main.py — ties everything together
  Run:  python main.py
  Outputs: frontend/events_data.js  (consumed by the HTML dashboard)
============================================================
"""

import json
import os

from tanisha.invoice_pipeline import run_invoice, export_history_as_json

# ── Sample Invoices ───────────────────────────────────────────

INVOICES = [
    # 1. Happy path
    {
        "invoice_number": "INV-2024-101",
        "vendor_id":      "V001",
        "line_items":     [{"desc": "Laptop", "qty": 10, "unit": 1500}],
        "total_amount":   15000.0,
        "tax_amount":     2700.0,
        "due_date":       "2024-12-31",
        "po_number":      "PO-2024-55",
        "grn_number":     "GRN-2024-88",
        "ocr_scores":     {"vendor_id": 0.99, "total_amount": 0.97, "due_date": 0.95},
    },
    # 2. Soft failures → AI flags
    {
        "invoice_number": "INV-2024-202",
        "vendor_id":      "V002",
        "line_items":     [{"desc": "Chairs", "qty": 5, "unit": 200}],
        "total_amount":   15000.0,
        "tax_amount":     100.0,       # wrong tax
        "due_date":       "2024-12-31",
        "po_number":      "PO-2024-55",
        "grn_number":     "GRN-2024-88",
        "ocr_scores":     {"vendor_id": 0.99, "total_amount": 0.61}, # low OCR
    },
    # 3. Critical abort — blacklisted vendor
    {
        "invoice_number": "INV-2024-303",
        "vendor_id":      "V999",
        "line_items":     [{"desc": "Services", "qty": 1, "unit": 5000}],
        "total_amount":   5000.0,
        "tax_amount":     900.0,
        "due_date":       "2024-12-31",
        "po_number":      "PO-2024-55",
        "grn_number":     "GRN-2024-88",
        "ocr_scores":     {"vendor_id": 0.98, "total_amount": 0.96},
    },
    # 4. Missing fields
    {
        "invoice_number": "INV-2024-404",
        "vendor_id":      "V003",
        "line_items":     [],
        "total_amount":   None,        # missing
        "tax_amount":     0,
        "due_date":       None,        # missing
        "po_number":      "PO-2024-55",
        "grn_number":     "GRN-2024-88",
        "ocr_scores":     {},
    },
    # 5. Duplicate invoice detected before approval
    {
        "invoice_number": "INV-2024-999",
        "vendor_id":      "V001",
        "line_items":     [{"desc": "Monitor", "qty": 10, "unit": 1500}],
        "total_amount":   15000.0,
        "tax_amount":     2700.0,
        "due_date":       "2024-12-31",
        "po_number":      "PO-2024-55",
        "grn_number":     "GRN-2024-88",
        "ocr_scores":     {"vendor_id": 0.98, "total_amount": 0.96, "due_date": 0.95},
    },
]

print("\n══════════════════════════════════════════════════")
print("  Running Invoice Validation Pipeline")
print("══════════════════════════════════════════════════\n")

for inv in INVOICES:
    result = run_invoice(inv)
    status = "PASSED" if result["passed"] else (
        f"ABORTED at {result['aborted_at']}" if result["aborted_at"]
        else f"REVIEW ({len(result['soft_failures'])} soft failures)"
    )
    print(f"  {inv['invoice_number']} → {status}")

# ── Export event history to JS file for the frontend ─────────
events = export_history_as_json()

os.makedirs("frontend", exist_ok=True)
js_content = f"window.EVENTS_DATA = {json.dumps(events, indent=2)};\n"

with open("frontend/events_data.js", "w") as f:
    f.write(js_content)

print(f"\n  {len(events)} events exported → frontend/events_data.js")
print("  Open frontend/index.html in your browser.\n")
