
from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_csv_upload_validation():
    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "data" / "sample_outbreaks.csv"

    with csv_path.open("rb") as file:
        response = client.post(
            "/outbreaks/upload-csv",
            files={
                "file": (
                    "sample_outbreaks.csv",
                    file,
                    "text/csv"
                )
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total_records"] == 4
    assert data["valid_records"] == 3
    assert data["invalid_records"] == 1

    assert (
        data["validation_errors"][0]["unique_id"]
        == "KL/KSD/2024/104"
    )

def test_reject_non_csv_upload():
    response = client.post(
        "/outbreaks/upload-csv",
        files={
            "file": (
                "notes.txt",
                b"This is not a CSV file",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only CSV files are allowed"
    )

def test_reject_empty_csv_upload():
    response = client.post(
        "/outbreaks/upload-csv",
        files={
            "file": (
                "empty.csv",
                b"",
                "text/csv"
            )
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "CSV file is empty or contains no data records"
    )

def test_reject_csv_with_missing_columns():
    csv_content = (
        "unique_id,state,district,cases\n"
        "KL/KSD/2024/105,Kerala,Kasaragod,25\n"
    )

    response = client.post(
        "/outbreaks/upload-csv",
        files={
            "file": (
                "missing_columns.csv",
                csv_content.encode("utf-8"),
                "text/csv"
            )
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["message"] == (
        "CSV is missing required columns"
    )

    assert "disease" in data["detail"]["missing_columns"]
    assert "deaths" in data["detail"]["missing_columns"]

def test_upload_and_import_csv_success():
    from unittest.mock import patch

    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "data" / "sample_outbreaks.csv"

    mock_results = {
        "imported": 3,
        "duplicates": 0,
        "failed": 0,
        "errors": []
    }

    with patch(
        "app.main.import_validated_outbreaks",
        return_value=mock_results
    ) as mock_import:

        with csv_path.open("rb") as file:
            response = client.post(
                "/outbreaks/upload-and-import",
                files={
                    "file": (
                        "sample_outbreaks.csv",
                        file,
                        "text/csv"
                    )
                }
            )

    assert response.status_code == 200

    data = response.json()

    assert data["total_records"] == 4
    assert data["valid_records"] == 3
    assert data["invalid_records"] == 1

    assert data["import_summary"]["imported"] == 3
    assert data["import_summary"]["duplicates"] == 0
    assert data["import_summary"]["failed"] == 0

    mock_import.assert_called_once()

    validated_records = mock_import.call_args.args[0]
    assert len(validated_records) == 3

def test_upload_and_import_handles_duplicates():
    from unittest.mock import patch

    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "data" / "sample_outbreaks.csv"

    mock_results = {
        "imported": 0,
        "duplicates": 3,
        "failed": 0,
        "errors": []
    }

    with patch(
        "app.main.import_validated_outbreaks",
        return_value=mock_results
    ) as mock_import:

        with csv_path.open("rb") as file:
            response = client.post(
                "/outbreaks/upload-and-import",
                files={
                    "file": (
                        "sample_outbreaks.csv",
                        file,
                        "text/csv"
                    )
                }
            )

    assert response.status_code == 200

    data = response.json()

    assert data["import_summary"]["imported"] == 0
    assert data["import_summary"]["duplicates"] == 3
    assert data["import_summary"]["failed"] == 0
    assert data["invalid_records"] == 1

    mock_import.assert_called_once()

def test_upload_and_import_handles_database_failures():
    from unittest.mock import patch

    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "data" / "sample_outbreaks.csv"

    mock_results = {
        "imported": 2,
        "duplicates": 0,
        "failed": 1,
        "errors": [
            {
                "unique_id": "KL/KNR/2024/103",
                "error": "Simulated database error"
            }
        ]
    }

    with patch(
        "app.main.import_validated_outbreaks",
        return_value=mock_results
    ) as mock_import:

        with csv_path.open("rb") as file:
            response = client.post(
                "/outbreaks/upload-and-import",
                files={
                    "file": (
                        "sample_outbreaks.csv",
                        file,
                        "text/csv"
                    )
                }
            )

    assert response.status_code == 200

    data = response.json()
    summary = data["import_summary"]

    assert summary["imported"] == 2
    assert summary["duplicates"] == 0
    assert summary["failed"] == 1
    assert len(summary["errors"]) == 1
    assert data["invalid_records"] == 1

    mock_import.assert_called_once()
