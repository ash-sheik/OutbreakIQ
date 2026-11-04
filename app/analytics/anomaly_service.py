
"""Orchestrate explainable anomaly detection and alert persistence."""

import hashlib
import json
from datetime import date

from app.analytics.anomaly_rules import AnomalyRule, evaluate_anomaly
from app.analytics.trends import calculate_trends
from app.models.trend import TrendFilters
from app.repositories.anomaly_alert_repository import save_alert


def build_analysis_run_key(
    rule: AnomalyRule,
    disease: str,
    state: str,
    district: str,
    period_start: date,
    period_end: date,
) -> str:
    """Build a stable key for a rule and observation period."""
    payload = {
        "rule_id": rule.rule_id,
        "rule_version": rule.version,
        "disease": disease,
        "state": state,
        "district": district,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_anomaly_analysis(
    filters: TrendFilters,
    rule: AnomalyRule | None = None,
) -> dict:
    """Evaluate trend points and persist qualifying case-increase alerts."""
    rule = rule or AnomalyRule(
        minimum_history_periods=filters.minimum_baseline_periods,
    )

    points = calculate_trends(filters)
    alerts_created_or_reused = []

    for point in points:
        if not point["baseline_available"]:
            continue

        evidence = point["baseline_evidence"]
        historical_cases = [item["cases"] for item in evidence]

        result = evaluate_anomaly(
            observed_value=point["observed_cases"],
            historical_values=historical_cases,
            rule=rule,
        )

        if not result.is_alert:
            continue

        period_start = point["reporting_week_start"]
        if isinstance(period_start, str):
            period_start = date.fromisoformat(period_start)

        # ISO reporting weeks start on Monday and end on Sunday.
        period_end = date.fromordinal(period_start.toordinal() + 6)

        run_key = build_analysis_run_key(
            rule=rule,
            disease=point["disease"],
            state=point["state"],
            district=point["district"],
            period_start=period_start,
            period_end=period_end,
        )

        alert = {
            "rule_id": result.rule_id,
            "rule_version": result.rule_version,
            "disease": point["disease"],
            "state": point["state"],
            "district": point["district"],
            "reporting_period_start": period_start,
            "reporting_period_end": period_end,
            "observed_value": result.observed_value,
            "baseline_value": result.baseline_value,
            "absolute_change": result.absolute_change,
            "percentage_change": result.percentage_change,
            "score": result.score,
            "threshold": result.threshold,
            "history_periods": result.history_periods,
            "analysis_run_key": run_key,
            "interpretation": (
                "Analytical finding requiring verification"
            ),
        }

        evidence_rows = [
            {
                "record_id": None,
                "evidence_type": "historical_week",
                "evidence_description": (
                    f"Baseline week {item['reporting_week']}: "
                    f"{item['cases']} cases"
                ),
            }
            for item in evidence
        ]

        for limitation in point["limitations"]:
            evidence_rows.append({
                "record_id": None,
                "evidence_type": "data_quality_limitation",
                "evidence_description": limitation,
            })

        alert_id = save_alert(alert, evidence_rows)

        alerts_created_or_reused.append({
            "alert_id": alert_id,
            "disease": point["disease"],
            "state": point["state"],
            "district": point["district"],
            "reporting_period_start": period_start.isoformat(),
            "reporting_period_end": period_end.isoformat(),
            "percentage_change": result.percentage_change,
            "interpretation": alert["interpretation"],
        })

    return {
        "rule_id": rule.rule_id,
        "rule_version": rule.version,
        "trend_points_evaluated": len(points),
        "alerts_found": len(alerts_created_or_reused),
        "alerts": alerts_created_or_reused,
        "message": (
            "Alerts are analytical findings requiring verification; "
            "they do not confirm an outbreak."
        ),
    }
