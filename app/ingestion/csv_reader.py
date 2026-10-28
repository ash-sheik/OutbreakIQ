
import csv
from datetime import date
from pathlib import Path

from app.ingestion.outbreak_parser import parse_outbreaks_with_errors


CSV_HEADER_MAP = {
    "Unique_ID": "unique_id",
    "State": "state",
    "District": "district",
    "Disease": "disease",
    "Cases": "cases",
    "Deaths": "deaths",
    "Outbreak_Start_Date": "outbreak_start_date",
    "Reporting_Date": "reporting_date",
    "Status": "status",
    "PDF_File": "source_pdf_file",
    "Week": "source_week",
    "Page": "source_page",
    "Table_Number": "source_table_number",
}


def normalize_outbreak_csv_record(record: dict) -> dict:
    """Map NCDC/IDSP CSV headers to the application's field names."""
    normalized_record = {
        CSV_HEADER_MAP.get(column, column): value
        for column, value in record.items()
    }

    if normalized_record.get("reporting_date") in (None, ""):
        normalized_record["reporting_date"] = None

    reporting_date = normalized_record.get("reporting_date")
    outbreak_start_date = normalized_record.get("outbreak_start_date")

    if reporting_date and outbreak_start_date:
        try:
            reporting_date_value = date.fromisoformat(reporting_date)
            outbreak_start_date_value = date.fromisoformat(
                outbreak_start_date
            )
        except ValueError:
            pass
        else:
            if reporting_date_value < outbreak_start_date_value:
                normalized_record["allow_reporting_date_conflict"] = True
                normalized_record["data_quality_note"] = (
                    "Source reporting date precedes outbreak start date; "
                    "both source dates were retained unchanged."
                )

    return normalized_record


def normalize_outbreak_csv_records(records: list[dict]) -> list[dict]:
    """Normalize every record read from an outbreak CSV file."""
    return [normalize_outbreak_csv_record(record) for record in records]


def read_outbreak_csv(file_path: str) -> list[dict]:
    """
    Read outbreak records from a CSV file
    and return them as dictionaries.
    """
    path = Path(file_path)

    with path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)
        records = normalize_outbreak_csv_records(list(reader))

    return records

def load_and_validate_outbreaks(file_path: str):
    """
    Read outbreak records from a CSV file
    and separate valid and invalid records.
    """
    records = read_outbreak_csv(file_path)

    valid_outbreaks, invalid_records = (
        parse_outbreaks_with_errors(records)
    )

    return valid_outbreaks, invalid_records
