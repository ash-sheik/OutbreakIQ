# Ingestion audit requirements

- Extract structured rows from selected public PDF reports with `pdfplumber`.
- Register each input file with filename, source URL when known, reporting period, timestamp, and processing status.
- Create one ingestion run for every CSV or PDF attempt and persist processed, accepted, rejected, duplicate, and failed counts.
- Quarantine invalid records with their original values and validation reasons.
- Reuse the existing source-aware duplicate rule and never alter source dates or discard a source row silently.
