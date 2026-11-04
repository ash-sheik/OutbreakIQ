
"""Deterministic, explainable rules for disease trend anomaly detection."""

from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class AnomalyRule:
    """Configuration for a versioned percentage-change rule."""

    rule_id: str = "case_increase_v1"
    version: int = 1
    minimum_history_periods: int = 4
    percentage_change_threshold: float = 50.0


@dataclass(frozen=True)
class AnomalyResult:
    """Explainable result of evaluating one observation."""

    is_alert: bool
    rule_id: str
    rule_version: int
    observed_value: float
    baseline_value: Optional[float]
    absolute_change: Optional[float]
    percentage_change: Optional[float]
    score: Optional[float]
    threshold: float
    history_periods: int
    reason: str


def evaluate_anomaly(
    observed_value: float,
    historical_values: Sequence[float],
    rule: AnomalyRule = AnomalyRule(),
) -> AnomalyResult:
    """Evaluate an observation against the mean of historical values.

    Only increases meeting the configured percentage threshold trigger alerts.
    A zero baseline and insufficient history do not trigger alerts.
    """

    if observed_value < 0:
        raise ValueError("observed_value cannot be negative")

    if any(value < 0 for value in historical_values):
        raise ValueError("historical values cannot be negative")

    if rule.minimum_history_periods < 1:
        raise ValueError("minimum_history_periods must be at least 1")

    if rule.percentage_change_threshold < 0:
        raise ValueError("percentage_change_threshold cannot be negative")

    history_count = len(historical_values)

    if history_count < rule.minimum_history_periods:
        return AnomalyResult(
            is_alert=False,
            rule_id=rule.rule_id,
            rule_version=rule.version,
            observed_value=observed_value,
            baseline_value=None,
            absolute_change=None,
            percentage_change=None,
            score=None,
            threshold=rule.percentage_change_threshold,
            history_periods=history_count,
            reason="Insufficient historical periods",
        )

    baseline = sum(historical_values) / history_count
    absolute_change = observed_value - baseline

    if baseline == 0:
        return AnomalyResult(
            is_alert=False,
            rule_id=rule.rule_id,
            rule_version=rule.version,
            observed_value=observed_value,
            baseline_value=baseline,
            absolute_change=absolute_change,
            percentage_change=None,
            score=None,
            threshold=rule.percentage_change_threshold,
            history_periods=history_count,
            reason="Zero baseline; percentage change is undefined",
        )

    percentage_change = (absolute_change / baseline) * 100
    is_alert = percentage_change >= rule.percentage_change_threshold and absolute_change > 0

    return AnomalyResult(
        is_alert=is_alert,
        rule_id=rule.rule_id,
        rule_version=rule.version,
        observed_value=observed_value,
        baseline_value=baseline,
        absolute_change=absolute_change,
        percentage_change=percentage_change,
        score=percentage_change,
        threshold=rule.percentage_change_threshold,
        history_periods=history_count,
        reason=(
            "Increase meets configured threshold; verification required"
            if is_alert
            else "Increase does not meet configured threshold"
            if absolute_change > 0
            else "No increase above historical baseline"
        ),
    )
