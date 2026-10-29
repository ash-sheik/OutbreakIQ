# Ingestion audit tasks

- [x] Design an additive MySQL migration for source documents, ingestion runs, and rejected records.
- [x] Apply `sql/001_ingestion_audit.sql` using a MySQL account with `CREATE` and `ALTER` privileges.
- [x] Add repositories and Pydantic schemas for the operational records.
- [x] Add a PDF extractor that preserves page and table provenance.
- [x] Create a CSV ingestion pipeline with source and run tracking.
- [x] Add API endpoints to start and retrieve ingestion runs.
- [ ] Add focused tests for success, invalid rows, duplicates, and extraction failure.
