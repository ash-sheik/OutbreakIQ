"""Explainable historical trend calculations."""

from collections import defaultdict
from statistics import mean

from app.models.trend import TrendFilters
from app.repositories.trend_repository import get_weekly_observations


MISSING_DATE_LIMITATION = (
    "Records with a missing reporting date are excluded from weekly trends."
)


def calculate_trends(filters: TrendFilters) -> list[dict]:
    """Calculate trailing historical baselines for comparable weekly groups."""
    observations = get_weekly_observations(
        disease=filters.disease,
        state=filters.state,
        district=filters.district,
        date_from=filters.date_from,
        date_to=filters.date_to,
    )
    observations_by_group = defaultdict(list)
    for observation in observations:
        group_key = (
            observation["disease"],
            observation["state"],
            observation["district"],
        )
        observations_by_group[group_key].append(observation)

    trend_points = []
    for group_observations in observations_by_group.values():
        for index, observation in enumerate(group_observations):
            baseline_evidence = group_observations[
                max(0, index - filters.lookback_periods):index
            ]
            limitations = [MISSING_DATE_LIMITATION]
            baseline_available = (
                len(baseline_evidence) >= filters.minimum_baseline_periods
            )
            if not baseline_available:
                limitations.append(
                    "Insufficient prior reporting weeks for the configured "
                    f"minimum of {filters.minimum_baseline_periods}."
                )
                baseline_cases = baseline_deaths = None
                case_change = case_percentage_change = None
            else:
                baseline_cases = mean(
                    item["observed_cases"] for item in baseline_evidence
                )
                baseline_deaths = mean(
                    item["observed_deaths"] for item in baseline_evidence
                )
                case_change = observation["observed_cases"] - baseline_cases
                case_percentage_change = (
                    None
                    if baseline_cases == 0
                    else (case_change / baseline_cases) * 100
                )
                if baseline_cases == 0:
                    limitations.append(
                        "Case percentage change is undefined because the "
                        "historical baseline is zero."
                    )

            trend_points.append({
                **observation,
                "baseline_cases": baseline_cases,
                "baseline_deaths": baseline_deaths,
                "case_change": case_change,
                "case_percentage_change": case_percentage_change,
                "baseline_available": baseline_available,
                "baseline_evidence": [
                    {
                        "reporting_week": item["reporting_week"],
                        "cases": item["observed_cases"],
                        "deaths": item["observed_deaths"],
                    }
                    for item in baseline_evidence
                ],
                "limitations": limitations,
            })
    return trend_points
