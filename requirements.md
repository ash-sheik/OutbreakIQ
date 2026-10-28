# OutbreakIQ requirements

## Purpose

OutbreakIQ stores and serves disease-outbreak surveillance records from NCDC/IDSP reports through a FastAPI application backed by MySQL.

## Functional requirements

| ID | Requirement | Status |
| --- | --- | --- |
| FR-01 | Create, list, and retrieve outbreak records through FastAPI. | Complete |
| FR-02 | Validate core outbreak fields: identifiers, location, disease, cases, deaths, dates, and status. | Complete |
| FR-03 | Reject negative case or death counts and deaths greater than cases. | Complete |
| FR-04 | Reject ordinary API records whose reporting date is earlier than the outbreak start date. | Complete |
| FR-05 | Read and validate outbreak records from UTF-8 CSV files. | Complete |
| FR-06 | Map NCDC/IDSP source headers to the application field names. | Complete |
| FR-07 | Store NCDC/IDSP source metadata: PDF file, week, page, and table number. | Complete |
| FR-08 | Preserve missing reporting dates as `NULL`; do not invent dates. | Complete |
| FR-09 | Store weekly updates that share one original outbreak ID as separate database records. | Complete |
| FR-10 | Prevent a source row from being imported more than once. | Complete |
| FR-11 | Provide an import preview and upload workflow through the API, accepting application and NCDC/IDSP headers. | Complete |
| FR-12 | Handle source records whose reporting date precedes the outbreak start date with an explicit data-quality note. | Complete |

## Data-preservation rules

- Keep the copied NCDC/IDSP source CSV unchanged.
- Store blank source reporting dates as database `NULL` values.
- Do not silently discard source rows.
- Keep source-report metadata with each imported source row.
- Keep all weekly updates when one `unique_id` appears in multiple reports.
- Keep rejected rows in the review report until an explicit handling rule exists.

## Current source-data status

| Measure | Value |
| --- | ---: |
| Source CSV records | 3,016 |
| Imported NCDC/IDSP records | 3,016 |
| Imported records with `NULL` reporting date | 329 |
| Imported records with a date-conflict quality note | 7 |
| Weekly updates stored for `GJ/BKT/2024/29/1638` | 4 |

