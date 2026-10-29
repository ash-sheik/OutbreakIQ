"""Persistence for source documents and ingestion-run audit history."""

import json
from datetime import datetime, timezone

from app.database import get_db_connection
from app.models.outbreak import Outbreak
from app.repositories.outbreak_repository import outbreak_values


INSERT_OUTBREAK_WITH_LINEAGE_QUERY = """
    INSERT INTO outbreaks (
        unique_id, state, district, disease, cases, deaths,
        outbreak_start_date, reporting_date, status, comments,
        data_quality_note, source_pdf_file, source_week, source_page,
        source_table_number, source_id, ingestion_run_id
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_or_create_source_document(
    filename: str,
    content_sha256: str,
    source_url: str | None = None,
    reporting_period: str | None = None,
) -> int:
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT source_id
            FROM source_documents
            WHERE filename = %s AND content_sha256 = %s
            """,
            (filename, content_sha256),
        )
        row = cursor.fetchone()
        if row:
            return row[0]

        cursor.execute(
            """
            INSERT INTO source_documents (
                filename, source_url, reporting_period, content_sha256,
                ingested_at, status
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                filename,
                source_url,
                reporting_period,
                content_sha256,
                _utc_now(),
                "registered",
            ),
        )
        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def create_ingestion_run(source_id: int) -> int:
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO ingestion_runs (source_id, started_at, status)
            VALUES (%s, %s, %s)
            """,
            (source_id, _utc_now(), "running"),
        )
        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def update_source_document_status(source_id: int, status: str) -> None:
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE source_documents SET status = %s WHERE source_id = %s",
            (status, source_id),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def save_rejected_records(run_id: int, rejected_records: list[dict]) -> None:
    if not rejected_records:
        return

    values = [
        (
            run_id,
            record["record_index"],
            record.get("unique_id"),
            json.dumps(record["original_record"], default=str),
            json.dumps(record["errors"], default=str),
            _utc_now(),
        )
        for record in rejected_records
    ]
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.executemany(
            """
            INSERT INTO rejected_records (
                run_id, record_index, source_unique_id, original_record,
                validation_errors, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            values,
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def complete_ingestion_run(
    run_id: int,
    status: str,
    processed: int,
    accepted: int,
    rejected: int,
    duplicates: int,
    failed: int,
    errors: list[dict],
) -> None:
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE ingestion_runs
            SET completed_at = %s,
                status = %s,
                records_processed = %s,
                records_accepted = %s,
                records_rejected = %s,
                records_duplicate = %s,
                records_failed = %s,
                error_details = %s
            WHERE run_id = %s
            """,
            (
                _utc_now(), status, processed, accepted, rejected,
                duplicates, failed, json.dumps(errors, default=str), run_id,
            ),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def get_ingestion_run(run_id: int) -> dict | None:
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT run_id, source_id, status, started_at, completed_at,
                   records_processed, records_accepted, records_rejected,
                   records_duplicate, records_failed, error_details
            FROM ingestion_runs
            WHERE run_id = %s
            """,
            (run_id,),
        )
        run = cursor.fetchone()
        if run and isinstance(run["error_details"], str):
            run["error_details"] = json.loads(run["error_details"])
        return run
    finally:
        cursor.close()
        connection.close()


def save_outbreaks_with_lineage(
    outbreaks: list[Outbreak],
    source_id: int,
    ingestion_run_id: int,
) -> list[tuple[Outbreak, Exception | None]]:
    """Save validated records linked to an audited source and run."""
    connection = get_db_connection()
    cursor = connection.cursor()
    outcomes = []
    try:
        for outbreak in outbreaks:
            try:
                cursor.execute(
                    INSERT_OUTBREAK_WITH_LINEAGE_QUERY,
                    outbreak_values(outbreak) + (source_id, ingestion_run_id),
                )
                outcomes.append((outbreak, None))
            except Exception as error:
                outcomes.append((outbreak, error))
        connection.commit()
        return outcomes
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
