
import csv
import io

from fastapi import FastAPI

from app.models.outbreak import Outbreak

from app.ingestion.outbreak_parser import parse_outbreaks_with_errors
from app.ingestion.csv_reader import normalize_outbreak_csv_records

from app.repositories.outbreak_repository import (
    save_outbreak,
    get_all_outbreaks,
    get_outbreak_by_id
)


from mysql.connector import IntegrityError

# Initialize the OutbreakIQ application
app = FastAPI(
    title="OutbreakIQ",
    description="AI-Powered Disease Surveillance Engine",
    version="1.0.0"
)


from app.ingestion.mysql_importer import (
    import_outbreaks_from_csv,
    import_validated_outbreaks
)
from app.ingestion.import_report import save_import_report



@app.get("/")
def home():
    return {
        "application": "OutbreakIQ",
        "message": "Welcome to OutbreakIQ!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "OutbreakIQ API"
    }




@app.post("/outbreaks", status_code=201)
def create_outbreak(outbreak: Outbreak):
    try:
        saved_id = save_outbreak(outbreak)

    except IntegrityError as error:
        if error.errno == 1062:
            raise HTTPException(
                status_code=409,
                detail="Outbreak ID already exists"
            ) from error
        raise

    return {
        "message": "Outbreak saved successfully",
        "unique_id": saved_id,
        "outbreak": outbreak.model_dump(mode="json", exclude_none=True)
    }


@app.get("/outbreaks")
def list_outbreaks():
    outbreaks = get_all_outbreaks()

    return {
        "total_records": len(outbreaks),
        "outbreaks": outbreaks
    }


from fastapi import FastAPI, HTTPException, UploadFile, File


@app.get("/outbreaks/{unique_id:path}")
def get_single_outbreak(unique_id: str):
    outbreak = get_outbreak_by_id(unique_id)

    if outbreak is None:
        raise HTTPException(
            status_code=404,
            detail="Outbreak not found"
        )

    return outbreak

@app.post("/outbreaks/import-csv")
def import_csv_outbreaks():
    """
    Import outbreak records from the sample CSV file.
    """

    file_path = "data/sample_outbreaks.csv"

    results = import_outbreaks_from_csv(file_path)
    report = save_import_report(
        source_filename=file_path,
        total_records=(
            results["imported"]
            + results["duplicates"]
            + results["invalid"]
            + results["failed"]
        ),
        import_summary=results,
        validation_errors=[
            error for error in results["errors"]
            if "errors" in error
        ],
    )

    return {
        "message": "CSV import completed",
        "summary": results,
        "import_report": report,
    }

@app.post("/outbreaks/upload-csv")
async def upload_outbreak_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file and preview its records.
    No database changes are made.
    """

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    try:
        content = await file.read()
        decoded_content = content.decode("utf-8-sig")

  
        reader = csv.DictReader(io.StringIO(decoded_content))
        records = normalize_outbreak_csv_records(list(reader))

        # Step 1: Check for empty CSV
        if not records:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty or contains no data records"
            )

        # Step 2: Check required columns
        required_columns = {
            "unique_id",
            "state",
            "district",
            "disease",
            "cases",
            "deaths",
            "outbreak_start_date",
            "reporting_date",
            "status"
        }

        actual_columns = set(records[0])
        missing_columns = required_columns - actual_columns

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "CSV is missing required columns",
                    "missing_columns": sorted(missing_columns)
                }
            )

 
        if not records:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty or contains no data records"
            )

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV file must use UTF-8 encoding"
        )

    finally:
        await file.close()
    
    valid_outbreaks, invalid_records = parse_outbreaks_with_errors(records)

    
    return {
        "message": "CSV uploaded and validated successfully",
        "filename": file.filename,
        "total_records": len(records),
        "valid_records": len(valid_outbreaks),
        "invalid_records": len(invalid_records),
        "validation_errors": invalid_records,
        "preview": records[:3]
    }


@app.post("/outbreaks/upload-and-import")
async def upload_and_import_outbreaks(file: UploadFile = File(...)):
    """
    Upload a CSV file, validate records,
    and import valid outbreaks into MySQL.
    """

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    try:
        content = await file.read()
        decoded_content = content.decode("utf-8-sig")

        reader = csv.DictReader(io.StringIO(decoded_content))
        records = normalize_outbreak_csv_records(list(reader))

        if not records:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty or contains no data records"
            )

        required_columns = {
            "unique_id", "state", "district", "disease",
            "cases", "deaths", "outbreak_start_date",
            "reporting_date", "status"
        }

        missing_columns = required_columns - set(records[0])

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "CSV is missing required columns",
                    "missing_columns": sorted(missing_columns)
                }
            )

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV file must use UTF-8 encoding"
        )

    finally:
        await file.close()

    valid_outbreaks, invalid_records = parse_outbreaks_with_errors(records)

    import_results = import_validated_outbreaks(valid_outbreaks)
    report = save_import_report(
        source_filename=file.filename,
        total_records=len(records),
        import_summary=import_results,
        validation_errors=invalid_records,
    )

    return {
        "message": "CSV import completed",
        "filename": file.filename,
        "total_records": len(records),
        "valid_records": len(valid_outbreaks),
        "invalid_records": len(invalid_records),
        "import_summary": import_results,
        "validation_errors": invalid_records,
        "import_report": report,
    }
