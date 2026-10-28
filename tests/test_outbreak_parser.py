import pytest
from pydantic import ValidationError


from app.ingestion.outbreak_parser import (
    parse_outbreak,
    parse_multiple_outbreaks,
    parse_outbreaks_with_errors
)


def test_parse_valid_outbreak():
    record = {
        "unique_id": "TEST/PARSER/001",
        "state": "Kerala",
        "district": "Kasaragod",
        "disease": "Dengue",
        "cases": 25,
        "deaths": 0,
        "outbreak_start_date": "2024-08-01",
        "reporting_date": "2024-08-03",
        "status": "Under Control",
        "comments": "Sample outbreak record"
    }

    outbreak = parse_outbreak(record)

    assert outbreak.unique_id == "TEST/PARSER/001"
    assert outbreak.disease == "Dengue"
    assert outbreak.cases == 25
    assert outbreak.deaths == 0
    assert outbreak.state == "Kerala"

def test_parse_invalid_outbreak():
    record = {
        "unique_id": "TEST/PARSER/002",
        "state": "Kerala",
        "district": "Kasaragod",
        "disease": "Dengue",
        "cases": -25,
        "deaths": 0,
        "outbreak_start_date": "2024-08-01",
        "reporting_date": "2024-08-03",
        "status": "Under Control",
        "comments": "Invalid outbreak test"
    }

    with pytest.raises(ValidationError):
        parse_outbreak(record)

def test_parse_multiple_outbreaks():
    records = [
        {
            "unique_id": "TEST/MULTI/001",
            "state": "Kerala",
            "district": "Kasaragod",
            "disease": "Dengue",
            "cases": 25,
            "deaths": 0,
            "outbreak_start_date": "2024-08-01",
            "reporting_date": "2024-08-03",
            "status": "Under Control",
            "comments": "First test outbreak"
        },
        {
            "unique_id": "TEST/MULTI/002",
            "state": "Karnataka",
            "district": "Bengaluru",
            "disease": "Food Poisoning",
            "cases": 40,
            "deaths": 0,
            "outbreak_start_date": "2024-08-05",
            "reporting_date": "2024-08-06",
            "status": "Under Control",
            "comments": "Second test outbreak"
        }
    ]

    outbreaks = parse_multiple_outbreaks(records)

    assert len(outbreaks) == 2
    assert outbreaks[0].disease == "Dengue"
    assert outbreaks[1].disease == "Food Poisoning"
    assert outbreaks[0].cases == 25
    assert outbreaks[1].cases == 40

def test_parse_outbreaks_with_errors():
    valid_record = {
        "unique_id": "TEST/VALID/001",
        "state": "Kerala",
        "district": "Kasaragod",
        "disease": "Dengue",
        "cases": 25,
        "deaths": 0,
        "outbreak_start_date": "2024-08-01",
        "reporting_date": "2024-08-03",
        "status": "Under Control",
        "comments": "Valid test record"
    }

    invalid_record = {
        **valid_record,
        "unique_id": "TEST/INVALID/001",
        "cases": -10
    }

    records = [
        valid_record,
        invalid_record,
        {
            **valid_record,
            "unique_id": "TEST/VALID/002",
            "cases": 40
        }
    ]

    valid, invalid = parse_outbreaks_with_errors(records)

    assert len(valid) == 2
    assert len(invalid) == 1

    assert valid[0].unique_id == "TEST/VALID/001"
    assert valid[1].unique_id == "TEST/VALID/002"

    assert invalid[0]["record_index"] == 1
    assert invalid[0]["unique_id"] == "TEST/INVALID/001"
    assert len(invalid[0]["errors"]) > 0
