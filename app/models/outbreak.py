
from datetime import date

from pydantic import BaseModel, Field, model_validator


class Outbreak(BaseModel):
    unique_id: str = Field(min_length=1)
    state: str = Field(min_length=1)
    district: str = Field(min_length=1)
    disease: str = Field(min_length=1)

    cases: int = Field(ge=0)
    deaths: int = Field(ge=0)

    outbreak_start_date: date
    reporting_date: date | None = None

    status: str = Field(min_length=1)
    comments: str | None = None
    data_quality_note: str | None = None
    allow_reporting_date_conflict: bool = Field(
        default=False,
        exclude=True,
    )
    source_pdf_file: str | None = None
    source_week: int | None = Field(default=None, ge=1)
    source_page: int | None = Field(default=None, ge=1)
    source_table_number: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_deaths(self):
        if self.deaths > self.cases:
            raise ValueError(
                "Number of deaths cannot exceed number of cases"
            )

        return self

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.reporting_date is not None
            and self.reporting_date < self.outbreak_start_date
            and not (
                self.allow_reporting_date_conflict
                and self.data_quality_note
            )
        ):
            raise ValueError(
                "Reporting date cannot be earlier than outbreak start date "
                "without an explicit data-quality note"
            )

        return self
