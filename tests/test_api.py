
from fastapi.testclient import TestClient
from app.main import app

from unittest.mock import patch
from mysql.connector import IntegrityError

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "OutbreakIQ API"
    }

def test_negative_cases_rejected():
    outbreak_data = {
        "unique_id": "TEST/NEGATIVE/001",
        "state": "Kerala",
        "district": "Kasaragod",
        "disease": "Dengue",
        "cases": -10,
        "deaths": 0,
        "outbreak_start_date": "2024-08-01",
        "reporting_date": "2024-08-03",
        "status": "Under Control",
        "comments": "Automated validation test"
    }

    response = client.post("/outbreaks", json=outbreak_data)

    assert response.status_code == 422

def test_deaths_exceed_cases_rejected():
    outbreak_data = {
        "unique_id": "TEST/DEATHS/001",
        "state": "Kerala",
        "district": "Kasaragod",
        "disease": "Dengue",
        "cases": 10,
        "deaths": 15,
        "outbreak_start_date": "2024-08-01",
        "reporting_date": "2024-08-03",
        "status": "Under Control",
        "comments": "Automated validation test"
    }

    response = client.post("/outbreaks", json=outbreak_data)

    assert response.status_code == 422
    assert "Number of deaths cannot exceed number of cases" in response.text

def test_invalid_reporting_date_rejected():
    outbreak_data = {
        "unique_id": "TEST/DATE/001",
        "state": "Kerala",
        "district": "Kasaragod",
        "disease": "Dengue",
        "cases": 20,
        "deaths": 0,
        "outbreak_start_date": "2024-08-10",
        "reporting_date": "2024-08-05",
        "status": "Under Control",
        "comments": "Automated date validation test"
    }

    response = client.post("/outbreaks", json=outbreak_data)

    assert response.status_code == 422
    assert "Reporting date cannot be earlier than outbreak start date" in response.text

def test_duplicate_outbreak_rejected():
    outbreak_data = {
        "unique_id": "TEST/DUPLICATE/001",
        "state": "Kerala",
        "district": "Kasaragod",
        "disease": "Dengue",
        "cases": 20,
        "deaths": 0,
        "outbreak_start_date": "2024-08-01",
        "reporting_date": "2024-08-03",
        "status": "Under Control",
        "comments": "Automated duplicate ID test"
    }

    duplicate_error = IntegrityError(
        msg="Duplicate entry for primary key",
        errno=1062
    )

    with patch(
        "app.main.save_outbreak",
        side_effect=duplicate_error
    ):
        response = client.post(
            "/outbreaks",
            json=outbreak_data
        )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Outbreak ID already exists"
    }

def test_create_outbreak_success():
    outbreak_data = {
        "unique_id": "TEST/SUCCESS/001",
        "state": "Kerala",
        "district": "Kasaragod",
        "disease": "Dengue",
        "cases": 25,
        "deaths": 0,
        "outbreak_start_date": "2024-08-01",
        "reporting_date": "2024-08-03",
        "status": "Under Control",
        "comments": "Automated successful creation test"
    }

    with patch(
        "app.main.save_outbreak",
        return_value="TEST/SUCCESS/001"
    ) as mock_save:
        response = client.post(
            "/outbreaks",
            json=outbreak_data
        )

    assert response.status_code == 201
    assert response.json()["message"] == "Outbreak saved successfully"
    assert response.json()["unique_id"] == "TEST/SUCCESS/001"
    assert response.json()["outbreak"] == outbreak_data
    mock_save.assert_called_once()

def test_get_all_outbreaks_success():
    mock_outbreaks = [
        {
            "unique_id": "TEST/001",
            "state": "Kerala",
            "district": "Kasaragod",
            "disease": "Dengue",
            "cases": 25,
            "deaths": 0,
            "outbreak_start_date": "2024-08-01",
            "reporting_date": "2024-08-03",
            "status": "Under Control",
            "comments": "Test record"
        }
    ]

    with patch(
        "app.main.get_all_outbreaks",
        return_value=mock_outbreaks
    ) as mock_get:
        response = client.get("/outbreaks")

    assert response.status_code == 200
    assert response.json()["total_records"] == 1
    assert response.json()["outbreaks"] == mock_outbreaks
    mock_get.assert_called_once()

def test_get_outbreak_by_id_success():
    mock_outbreak = {
        "unique_id": "KL/KSD/2024/002",
        "state": "Kerala",
        "district": "Kasaragod",
        "disease": "Dengue",
        "cases": 35,
        "deaths": 0,
        "outbreak_start_date": "2024-08-01",
        "reporting_date": "2024-08-03",
        "status": "Under Control",
        "comments": "Automated retrieval test"
    }

    with patch(
        "app.main.get_outbreak_by_id",
        return_value=mock_outbreak
    ) as mock_get:
        response = client.get(
            "/outbreaks/KL/KSD/2024/002"
        )

    assert response.status_code == 200
    assert response.json() == mock_outbreak

    mock_get.assert_called_once_with(
        "KL/KSD/2024/002"
    )

def test_get_outbreak_by_id_not_found():
    with patch(
        "app.main.get_outbreak_by_id",
        return_value=None
    ) as mock_get:
        response = client.get(
            "/outbreaks/TEST/NOTFOUND/999"
        )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Outbreak not found"
    }

    mock_get.assert_called_once_with(
        "TEST/NOTFOUND/999"
    )
