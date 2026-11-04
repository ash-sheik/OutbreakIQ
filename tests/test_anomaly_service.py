
from datetime import date
from unittest.mock import patch

from app.analytics.anomaly_rules import AnomalyRule
from app.analytics.anomaly_service import (
    build_analysis_run_key,
    run_anomaly_analysis,
)
from app.models.trend import TrendFilters


def make_trend_point(
    observed_cases=18,
    baseline_available=True,
):
    return {
        "disease": "Example Disease",
        "state": "Example State",
        "district": "Example District",
        "reporting_week": "2026-W05",
        "reporting_week_start": date(2026, 1, 26),
        "observed_cases": observed_cases,
        "baseline_cases": 10,
        "case_change": observed_cases - 10,
        "case_percentage_change": (observed_cases - 10) / 10 * 100,
        "baseline_available": baseline_available,
        "baseline_evidence": [
            {"reporting_week": "2026-W01", "cases": 10, "deaths": 0},
            {"reporting_week": "2026-W02", "cases": 10, "deaths": 0},
            {"reporting_week": "2026-W03", "cases": 10, "deaths": 0},
            {"reporting_week": "2026-W04", "cases": 10, "deaths": 0},
        ],
        "limitations": ["Test limitation"],
    }


def test_qualifying_trend_persists_alert():
    point = make_trend_point()

    with (
        patch(
            "app.analytics.anomaly_service.calculate_trends",
            return_value=[point],
        ),
        patch(
            "app.analytics.anomaly_service.save_alert",
            return_value=42,
        ) as save_alert,
    ):
        result = run_anomaly_analysis(TrendFilters())

    assert result["trend_points_evaluated"] == 1
    assert result["alerts_found"] == 1
    assert result["alerts"][0]["alert_id"] == 42
    assert result["alerts"][0]["percentage_change"] == 80

    alert, evidence = save_alert.call_args.args
    assert alert["analysis_run_key"]
    assert len(alert["analysis_run_key"]) == 64
    assert alert["interpretation"] == (
        "Analytical finding requiring verification"
    )
    assert len(evidence) == 5


def test_below_threshold_does_not_persist_alert():
    point = make_trend_point(observed_cases=12)

    with (
        patch(
            "app.analytics.anomaly_service.calculate_trends",
            return_value=[point],
        ),
        patch(
            "app.analytics.anomaly_service.save_alert",
        ) as save_alert,
    ):
        result = run_anomaly_analysis(TrendFilters())

    assert result["alerts_found"] == 0
    save_alert.assert_not_called()


def test_insufficient_baseline_skips_alert():
    point = make_trend_point(baseline_available=False)

    with (
        patch(
            "app.analytics.anomaly_service.calculate_trends",
            return_value=[point],
        ),
        patch(
            "app.analytics.anomaly_service.save_alert",
        ) as save_alert,
    ):
        result = run_anomaly_analysis(TrendFilters())

    assert result["alerts_found"] == 0
    save_alert.assert_not_called()


def test_analysis_run_key_is_deterministic():
    rule = AnomalyRule()

    first = build_analysis_run_key(
        rule,
        "Disease",
        "State",
        "District",
        date(2026, 1, 5),
        date(2026, 1, 11),
    )
    second = build_analysis_run_key(
        rule,
        "Disease",
        "State",
        "District",
        date(2026, 1, 5),
        date(2026, 1, 11),
    )

    assert first == second
    assert len(first) == 64


def test_rule_version_changes_analysis_run_key():
    first = build_analysis_run_key(
        AnomalyRule(version=1),
        "Disease",
        "State",
        "District",
        date(2026, 1, 5),
        date(2026, 1, 11),
    )
    second = build_analysis_run_key(
        AnomalyRule(version=2),
        "Disease",
        "State",
        "District",
        date(2026, 1, 5),
        date(2026, 1, 11),
    )

    assert first != second
