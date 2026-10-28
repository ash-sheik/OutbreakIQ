
from mysql.connector import IntegrityError, Error

from app.ingestion.csv_reader import load_and_validate_outbreaks
from app.repositories.outbreak_repository import save_outbreaks

def import_outbreaks_from_csv(file_path: str):
    """
    Import validated outbreak records into MySQL.
    Track successful, duplicate, and failed records.
    """

    valid_outbreaks, invalid_records = (
        load_and_validate_outbreaks(file_path)
    )

    results = {
        "imported": 0,
        "duplicates": 0,
        "invalid": len(invalid_records),
        "failed": 0,
        "errors": invalid_records.copy()
    }

    return _import_outbreaks(valid_outbreaks, results)


def _import_outbreaks(valid_outbreaks, results):
    try:
        outcomes = save_outbreaks(valid_outbreaks)
    except Error as error:
        for outbreak in valid_outbreaks:
            results["failed"] += 1
            results["errors"].append({
                "unique_id": outbreak.unique_id,
                "error": str(error)
            })
        return results

    for outbreak, error in outcomes:
        if error is None:
            results["imported"] += 1
        elif isinstance(error, IntegrityError) and error.errno == 1062:
            results["duplicates"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({
                "unique_id": outbreak.unique_id,
                "error": str(error)
            })

    return results


def import_validated_outbreaks(valid_outbreaks):
    """
    Save already-validated outbreak records to MySQL.
    """

    results = {
        "imported": 0,
        "duplicates": 0,
        "failed": 0,
        "errors": []
    }

    return _import_outbreaks(valid_outbreaks, results)
