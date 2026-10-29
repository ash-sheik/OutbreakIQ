from datetime import datetime

from pydantic import BaseModel, Field


class DataQualityIssue(BaseModel):
    issue_id: int
    issue_type: str = Field(min_length=1)
    severity: str = Field(min_length=1)
    message: str = Field(min_length=1)
    status: str = Field(min_length=1)
    record_id: int | None = None
    run_id: int | None = None
    source_unique_id: str | None = None
    original_value: dict | None = None
    detected_at: datetime
