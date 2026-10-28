# OutbreakIQ design

## Architecture

```text
NCDC/IDSP cleaned CSV
        |
        v
CSV reader and source-header mapping
        |
        v
Pydantic outbreak validation
        |
        v
MySQL importer and outbreak repository
        |
        v
MySQL outbreaks table
        |
        v
FastAPI endpoints
```

## Application modules

| Module | Responsibility |
| --- | --- |
| `app/database.py` | Loads environment settings and opens MySQL connections. |
| `app/models/outbreak.py` | Defines the validated `Outbreak` model. |
| `app/ingestion/csv_reader.py` | Reads CSV files and maps NCDC/IDSP headers to application fields. |
| `app/ingestion/outbreak_parser.py` | Separates validated and invalid records. |
| `app/ingestion/mysql_importer.py` | Imports validated records and reports imported, duplicate, invalid, and failed records. |
| `app/repositories/outbreak_repository.py` | Inserts and retrieves database records, including shared-connection batch saves. |
| `app/main.py` | Exposes FastAPI endpoints. |

## Source-field mapping

| NCDC/IDSP CSV field | Application field | Database column |
| --- | --- | --- |
| `Unique_ID` | `unique_id` | `unique_id` |
| `State` | `state` | `state` |
| `District` | `district` | `district` |
| `Disease` | `disease` | `disease` |
| `Cases` | `cases` | `cases` |
| `Deaths` | `deaths` | `deaths` |
| `Outbreak_Start_Date` | `outbreak_start_date` | `outbreak_start_date` |
| `Reporting_Date` | `reporting_date` | `reporting_date` |
| `Status` | `status` | `status` |
| `PDF_File` | `source_pdf_file` | `source_pdf_file` |
| `Week` | `source_week` | `source_week` |
| `Page` | `source_page` | `source_page` |
| `Table_Number` | `source_table_number` | `source_table_number` |

## Database design

The `outbreaks` table uses `record_id` as its generated primary key. `unique_id` is retained from the source and may repeat because one outbreak can appear in several weekly reports.

The index below prevents the same source row from being imported twice:

```text
uq_outbreaks_source_location
(unique_id, source_pdf_file, source_page, source_table_number)
```

`reporting_date` accepts `NULL` to preserve blank source dates. `district` is `TEXT` so multi-district source records are stored without truncation.

## Data-quality policy

| Situation | Current handling |
| --- | --- |
| Blank reporting date | Store as `NULL`. |
| Repeated original outbreak ID across reports | Store each source-report row separately. |
| Exact repeat of a source-report row | Blocked by the unique source-location index. |
| Reporting date before outbreak start date | Store both source dates unchanged and add an explicit `data_quality_note`. |

## Upload behavior

The CSV preview and upload-and-import endpoints normalize incoming rows before checking required fields. They accept both lowercase application headers and NCDC/IDSP headers, including source-report metadata.

## Import reports

Every CSV import through the API appends one JSON object to `data/processed/import_reports.jsonl`. Each line records the source filename, UTC import time, total record count, imported, duplicate, invalid, and failed counts, plus categorized validation and database error details. Preview-only uploads do not create a report.

## Verification

The automated suite passed after the import, upload, model, and repository changes: 24 tests passed. The suite still reports one non-fatal Starlette deprecation warning from the installed test-client dependency.
- Seven date-conflict records are stored with quality notes and should be reviewed before analytical use.
