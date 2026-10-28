"""Persist audit reports for CSV import attempts."""

import json
from datetime import datetime, timezone
from pathlib import Path


IMPORT_REPORT_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "import_reports.jsonl"
)


def save_import_report(
    source_filename: str,
    total_records: int,
    import_summary: dict,
    validation_errors: list[dict],
) -> dict:
    """Append one JSON report for a CSV import attempt."""
    import_errors = import_summary.get("errors", [])
    error_details = [
        {"category": "validation", **error}
        for error in validation_errors
    ] + [
        {"category": "import", **error}
        for error in import_errors
    ]

    report = {
        "source_filename": Path(source_filename).name,
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "total_records": total_records,
        "imported": import_summary["imported"],
        "duplicates": import_summary["duplicates"],
        "invalid": len(validation_errors),
        "failed": import_summary["failed"],
        "error_details": error_details,
    }

    IMPORT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with IMPORT_REPORT_PATH.open("a", encoding="utf-8") as report_file:
        report_file.write(json.dumps(report, default=str) + "\n")

    return report
