from datetime import date

from pydantic import BaseModel, Field


class TrendFilters(BaseModel):
    disease: str | None = None
    state: str | None = None
    district: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    lookback_periods: int = Field(default=8, ge=1, le=52)
    minimum_baseline_periods: int = Field(default=4, ge=1, le=52)


class BaselineEvidence(BaseModel):
    reporting_week: str
    cases: int
    deaths: int


class TrendPoint(BaseModel):
    disease: str
    state: str
    district: str
    reporting_week: str
    reporting_week_start: date
    observed_cases: int
    observed_deaths: int
    baseline_cases: float | None = None
    baseline_deaths: float | None = None
    case_change: float | None = None
    case_percentage_change: float | None = None
    baseline_available: bool
    baseline_evidence: list[BaselineEvidence]
    limitations: list[str]
