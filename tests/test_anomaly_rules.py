
import pytest

from app.analytics.anomaly_rules import AnomalyRule, evaluate_anomaly


def test_increase_meeting_threshold_triggers_alert():
    result = evaluate_anomaly(18, [10, 10, 10, 10])

    assert result.is_alert is True
    assert result.baseline_value == 10
    assert result.absolute_change == 8
    assert result.percentage_change == 80
    assert result.rule_version == 1


def test_increase_below_threshold_does_not_trigger_alert():
    result = evaluate_anomaly(12, [10, 10, 10, 10])

    assert result.is_alert is False
    assert result.percentage_change == 20


def test_insufficient_history_does_not_trigger_alert():
    result = evaluate_anomaly(20, [10, 10, 10])

    assert result.is_alert is False
    assert result.baseline_value is None
    assert result.reason == "Insufficient historical periods"


def test_zero_baseline_has_no_finite_percentage_change():
    result = evaluate_anomaly(10, [0, 0, 0, 0])

    assert result.is_alert is False
    assert result.baseline_value == 0
    assert result.percentage_change is None


def test_rule_threshold_can_be_configured():
    rule = AnomalyRule(percentage_change_threshold=100)

    result = evaluate_anomaly(15, [10, 10, 10, 10], rule)

    assert result.is_alert is False
    assert result.threshold == 100


def test_negative_observation_is_rejected():
    with pytest.raises(ValueError, match="cannot be negative"):
        evaluate_anomaly(-1, [10, 10, 10, 10])
