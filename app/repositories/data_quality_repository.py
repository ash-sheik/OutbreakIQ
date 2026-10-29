"""Persistence for non-destructive data-quality findings."""

import json
from datetime import datetime, timezone

from app.database import get_db_connection


def save_data_quality_issues(run_id: int, issues: list[dict]) -> None:
    """Store accepted-record quality findings linked to an ingestion run."""
    if not issues:
        return

    values = [
        (
            issue.get("record_id"),
            run_id,
            issue.get("source_unique_id"),
            issue["issue_type"],
            issue["severity"],
            issue["message"],
            json.dumps(issue.get("original_value"), default=str),
            datetime.now(timezone.utc).replace(tzinfo=None),
        )
        for issue in issues
    ]
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.executemany(
            """
            INSERT INTO data_quality_issues (
                record_id, run_id, source_unique_id, issue_type,
                severity, message, original_value, detected_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
