
"""Database persistence and retrieval for anomaly alerts."""

import hashlib
import json

from app.database import get_db_connection

def _build_evidence_key(item: dict) -> str:
    """Create a stable fingerprint for an evidence item."""
    canonical = json.dumps(
        {
            "record_id": item.get("record_id"),
            "evidence_type": item["evidence_type"],
            "evidence_description": item["evidence_description"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def save_alert(
    alert: dict,
    evidence: list[dict],
) -> int:
    """Save an alert and its evidence atomically."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        connection.start_transaction()

        cursor.execute(
            """
            INSERT INTO anomaly_alerts (
                rule_id,
                rule_version,
                disease,
                state,
                district,
                reporting_period_start,
                reporting_period_end,
                observed_value,
                baseline_value,
                absolute_change,
                percentage_change,
                score,
                threshold,
                history_periods,
                analysis_run_key,
                interpretation
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON DUPLICATE KEY UPDATE
                alert_id = LAST_INSERT_ID(alert_id)
            """,
            (
                alert["rule_id"],
                alert["rule_version"],
                alert["disease"],
                alert["state"],
                alert["district"],
                alert["reporting_period_start"],
                alert["reporting_period_end"],
                alert["observed_value"],
                alert["baseline_value"],
                alert["absolute_change"],
                alert.get("percentage_change"),
                alert.get("score"),
                alert["threshold"],
                alert["history_periods"],
                alert["analysis_run_key"],
                alert.get(
                    "interpretation",
                    "Analytical finding requiring verification",
                ),
            ),
        )

        # Retrieve the inserted ID, or the existing ID on duplicate.
        alert_id = cursor.lastrowid

        for item in evidence:
            evidence_key = _build_evidence_key(item)

            cursor.execute(
                """
                INSERT INTO anomaly_alert_evidence (
                    alert_id,
                    record_id,
                    evidence_type,
                    evidence_description,
                    evidence_key
                )
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    evidence_id = evidence_id
                """,
                (
                    alert_id,
                    item.get("record_id"),
                    item["evidence_type"],
                    item["evidence_description"],
                    evidence_key,
                ),
            )

        connection.commit()
        return alert_id

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()



def get_alert_by_id(alert_id: int) -> dict | None:
    """Retrieve one alert and its evidence."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM anomaly_alerts
            WHERE alert_id = %s
            """,
            (alert_id,),
        )
        alert = cursor.fetchone()

        if alert is None:
            return None

        cursor.execute(
            """
            SELECT
                evidence_id,
                record_id,
                evidence_type,
                evidence_description,
                created_at
            FROM anomaly_alert_evidence
            WHERE alert_id = %s
            ORDER BY evidence_id
            """,
            (alert_id,),
        )
        alert["evidence"] = cursor.fetchall()

        return alert

    finally:
        cursor.close()
        connection.close()


def list_alerts(
    disease: str | None = None,
    state: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """List alerts with optional disease/state filters."""
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")

    if offset < 0:
        raise ValueError("offset cannot be negative")

    filters = []
    values = []

    if disease is not None:
        filters.append("disease = %s")
        values.append(disease)

    if state is not None:
        filters.append("state = %s")
        values.append(state)

    where_clause = (
        f"WHERE {' AND '.join(filters)}" if filters else ""
    )

    query = f"""
        SELECT *
        FROM anomaly_alerts
        {where_clause}
        ORDER BY reporting_period_start DESC, alert_id DESC
        LIMIT %s OFFSET %s
    """
    values.extend([limit, offset])

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, tuple(values))
        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()
