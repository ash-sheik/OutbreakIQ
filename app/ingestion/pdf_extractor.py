"""Extract tabular PDF rows while retaining page and table provenance."""

from pathlib import Path

import pdfplumber


def extract_pdf_tables(file_path: str) -> list[dict]:
    """Return extracted PDF table rows with their source page and table."""
    source_path = Path(file_path)
    extracted_tables = []

    with pdfplumber.open(source_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            for table_number, table in enumerate(
                page.extract_tables(),
                start=1,
            ):
                if not table or len(table) < 2:
                    continue

                headers = table[0]
                rows = []
                for row in table[1:]:
                    if len(row) != len(headers):
                        continue
                    rows.append({
                        str(header).strip(): value
                        for header, value in zip(headers, row)
                        if header
                    })

                extracted_tables.append({
                    "source_pdf_file": source_path.name,
                    "source_page": page_number,
                    "source_table_number": table_number,
                    "rows": rows,
                })

    return extracted_tables
