
import csv
import io
from datetime import date

from fastapi import FastAPI, HTTPException, UploadFile, File, Query

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
from app.ingestion.pipeline import ingest_csv_bytes
from app.analytics.trends import calculate_trends

from app.analytics.anomaly_rules import AnomalyRule
from app.analytics.anomaly_service import run_anomaly_analysis
from app.repositories.anomaly_alert_repository import (
    list_alerts,
    get_alert_by_id,
)
from app.models.trend import TrendFilters
from app.repositories.ingestion_audit_repository import get_ingestion_run



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


@app.get("/analytics/trends")
def get_trends(
    disease: str | None = None,
    state: str | None = None,
    district: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    lookback_periods: int = Query(default=8, ge=1, le=52),
    minimum_baseline_periods: int = Query(default=4, ge=1, le=52),
):
    """Return weekly observations with an explainable trailing baseline."""
    filters = TrendFilters(
        disease=disease,
        state=state,
        district=district,
        date_from=date_from,
        date_to=date_to,
        lookback_periods=lookback_periods,
        minimum_baseline_periods=minimum_baseline_periods,
    )
    trend_points = calculate_trends(filters)
    return {
        "filters": filters.model_dump(mode="json"),
        "total_points": len(trend_points),
        "points": trend_points,
    }


@app.post("/ingestion-runs/csv", status_code=201)
async def start_csv_ingestion_run(
    file: UploadFile = File(...),
    source_url: str | None = None,
    reporting_period: str | None = None,
):
    """Upload CSV data and retain source and run audit history."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed",
        )

    try:
        result = ingest_csv_bytes(
            content=await file.read(),
            filename=file.filename,
            source_url=source_url,
            reporting_period=reporting_period,
        )
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="CSV file must use UTF-8 encoding",
        ) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        await file.close()

    return result


@app.get("/ingestion-runs/{run_id}")
def get_csv_ingestion_run(run_id: int):
    """Retrieve one completed or failed ingestion run."""
    ingestion_run = get_ingestion_run(run_id)
    if ingestion_run is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return ingestion_run




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


@app.post("/analysis/run")
def run_analysis(
    filters: TrendFilters,
    percentage_change_threshold: float = Query(
        default=50.0,
        ge=0,
    ),
):
    """Run explainable anomaly detection for the selected filters."""
    rule = AnomalyRule(
        minimum_history_periods=filters.minimum_baseline_periods,
        percentage_change_threshold=percentage_change_threshold,
    )

    try:
        return run_anomaly_analysis(filters=filters, rule=rule)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@app.get("/alerts")
def get_alerts(
    disease: str | None = None,
    state: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List alerts with optional filters and pagination."""
    return {
        "alerts": list_alerts(
            disease=disease,
            state=state,
            limit=limit,
            offset=offset,
        ),
        "limit": limit,
        "offset": offset,
    }


@app.get("/alerts/{alert_id}")
def get_alert(alert_id: int):
    """Retrieve one alert with its supporting evidence."""
    if alert_id < 1:
        raise HTTPException(
            status_code=422,
            detail="alert_id must be a positive integer",
        )

    alert = get_alert_by_id(alert_id)

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    return alert
