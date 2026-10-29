from datetime import datetime

from pydantic import BaseModel, Field


class IngestionRun(BaseModel):
    run_id: int
    source_id: int
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    records_processed: int = Field(ge=0)
    records_accepted: int = Field(ge=0)
    records_rejected: int = Field(ge=0)
    records_duplicate: int = Field(ge=0)
    records_failed: int = Field(ge=0)
    error_details: list[dict] = Field(default_factory=list)
