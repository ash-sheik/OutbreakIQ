"""Run traceable ingestion for uploaded CSV data."""

import csv
import hashlib
import io
from pathlib import Path

from mysql.connector import IntegrityError

from app.ingestion.csv_reader import normalize_outbreak_csv_records
from app.ingestion.outbreak_parser import parse_outbreaks_with_errors
from app.repositories.data_quality_repository import save_data_quality_issues
from app.repositories.ingestion_audit_repository import (
    complete_ingestion_run,
    create_ingestion_run,
    get_or_create_source_document,
    save_rejected_records,
    save_outbreaks_with_lineage,
    update_source_document_status,
)


def ingest_csv_bytes(
    content: bytes,
    filename: str,
    source_url: str | None = None,
    reporting_period: str | None = None,
) -> dict:
    """Validate and save CSV data while recording its source and run history."""
    source_filename = Path(filename).name
    source_id = get_or_create_source_document(
        filename=source_filename,
        content_sha256=hashlib.sha256(content).hexdigest(),
        source_url=source_url,
        reporting_period=reporting_period,
    )
    run_id = create_ingestion_run(source_id)

    try:
        decoded_content = content.decode("utf-8-sig")
        records = normalize_outbreak_csv_records(
            list(csv.DictReader(io.StringIO(decoded_content)))
        )
        if not records:
            raise ValueError("CSV file is empty or contains no data records")

        valid_outbreaks, rejected_records = parse_outbreaks_with_errors(records)
        save_rejected_records(run_id, rejected_records)
        quality_issues = [
            {
                "source_unique_id": outbreak.unique_id,
                "issue_type": "reporting_date_before_outbreak_start",
                "severity": "warning",
                "message": outbreak.data_quality_note,
                "original_value": {
                    "outbreak_start_date": outbreak.outbreak_start_date,
                    "reporting_date": outbreak.reporting_date,
                },
            }
            for outbreak in valid_outbreaks
            if outbreak.data_quality_note
        ]
        save_data_quality_issues(run_id, quality_issues)

        import_errors = []
        accepted = duplicates = failed = 0
        outcomes = save_outbreaks_with_lineage(
            valid_outbreaks,
            source_id=source_id,
            ingestion_run_id=run_id,
        )
        for outbreak, error in outcomes:
            if error is None:
                accepted += 1
            elif isinstance(error, IntegrityError) and error.errno == 1062:
                duplicates += 1
            else:
                failed += 1
                import_errors.append({
                    "unique_id": outbreak.unique_id,
                    "error": str(error),
                })

        status = "completed" if failed == 0 else "completed_with_errors"
        complete_ingestion_run(
            run_id=run_id,
            status=status,
            processed=len(records),
            accepted=accepted,
            rejected=len(rejected_records),
            duplicates=duplicates,
            failed=failed,
            errors=import_errors,
        )
        update_source_document_status(source_id, status)
        return {
            "run_id": run_id,
            "source_id": source_id,
            "status": status,
            "total_records": len(records),
            "imported": accepted,
            "duplicates": duplicates,
            "invalid": len(rejected_records),
            "failed": failed,
            "validation_errors": rejected_records,
            "import_errors": import_errors,
        }
    except Exception as error:
        error_details = [{"error": str(error)}]
        complete_ingestion_run(
            run_id=run_id,
            status="failed",
            processed=0,
            accepted=0,
            rejected=0,
            duplicates=0,
            failed=1,
            errors=error_details,
        )
        update_source_document_status(source_id, "failed")
        raise
