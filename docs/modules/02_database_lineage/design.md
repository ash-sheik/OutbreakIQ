# Database lineage design

Keep the existing `outbreaks` table as the canonical observation store. Add `source_documents`, `ingestion_runs`, and `data_quality_issues` first; later modules add `anomaly_alerts` and `investigation_briefs`.

Use nullable foreign keys only for the four historical records that predate source tracking. New ingestion writes source and run IDs. Store issue type, message, severity, original value, and record/run reference in `data_quality_issues`. An accepted date-conflict record produces a warning issue linked to its ingestion run while preserving both dates unchanged.
