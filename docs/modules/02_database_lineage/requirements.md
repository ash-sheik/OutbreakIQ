# Database lineage requirements

- Store source documents, ingestion runs, data-quality issues, anomaly alerts, and investigation briefs as separate entities.
- Connect accepted outbreak records to their source document and ingestion run.
- Enforce stable primary keys and foreign keys where relationships exist.
- Preserve original extracted values whenever a future normalization produces a canonical value.
- Support indexes for disease, state, district, reporting date, status, and source-aware deduplication.
