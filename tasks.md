# OutbreakIQ task tracker

## Completed

- [x] Create the `outbreakiq_db` MySQL database and `outbreaks` table.
- [x] Create the MySQL connection and outbreak repository functions.
- [x] Add Pydantic outbreak validation.
- [x] Create FastAPI endpoints for creating, listing, and retrieving outbreaks.
- [x] Create CSV reading, validation, and MySQL import modules.
- [x] Create CSV preview and upload-and-import endpoints.
- [x] Verify the earlier automated test suite: 24 tests passed, with a non-fatal Starlette deprecation warning.
- [x] Copy `outbreak_records_2024_clean.csv` into `data/processed/`.
- [x] Inspect the source columns, blank reporting dates, duplicate IDs, and MySQL compatibility.
- [x] Add NCDC/IDSP header mapping in `app/ingestion/csv_reader.py`.
- [x] Allow `reporting_date` to be `NULL` in the model and MySQL table.
- [x] Replace the `unique_id` primary key with generated `record_id` values.
- [x] Add source PDF, week, page, and table-number columns.
- [x] Widen `district` to `TEXT` to preserve full multi-district source values.
- [x] Add the `uq_outbreaks_source_location` unique index.
- [x] Import 3,009 validated NCDC/IDSP records.
- [x] Create `data/processed/outbreak_records_2024_review.md` for unresolved source issues.

## Open tasks

- [x] Decide how to store the 7 records whose reporting date is earlier than their outbreak start date.
- [x] Implement that approved handling while retaining both original dates and a data-quality note.
- [x] Import the 7 date-conflict records with explicit data-quality notes.
- [x] Make the upload preview and upload-and-import endpoints use the NCDC/IDSP header mapping.
- [x] Improve the CSV importer to use one shared database connection and one final commit per import.
- [x] Re-run the automated test suite after the model and schema changes; 24 tests passed with one non-fatal Starlette deprecation warning.
- [x] Add JSON Lines import-summary logging for future CSV imports.

## Current checkpoint

The MySQL table contains 3,020 rows: 3,016 imported NCDC/IDSP rows and 4 rows that existed before this import. The source CSV remains unchanged. Seven rows retain their original conflicting dates and have explicit data-quality notes.

