
from unittest.mock import MagicMock, patch

import pytest

from app.repositories.anomaly_alert_repository import (
    _build_evidence_key,
    get_alert_by_id,
    list_alerts,
    save_alert,
)


@pytest.fixture
def mock_db():
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    cursor.lastrowid = 42

    with patch(
        "app.repositories.anomaly_alert_repository.get_db_connection",
        return_value=connection,
    ):
        yield connection, cursor


@pytest.fixture
def sample_alert():
    return {
        "rule_id": "case_increase_v1",
        "rule_version": 1,
        "disease": "Example Disease",
        "state": "Example State",
        "district": "Example District",
        "reporting_period_start": "2026-01-05",
        "reporting_period_end": "2026-01-11",
        "observed_value": 18,
        "baseline_value": 10,
        "absolute_change": 8,
        "percentage_change": 80,
        "score": 80,
        "threshold": 50,
        "history_periods": 4,
        "analysis_run_key": "a" * 64,
    }


def test_save_alert_commits_and_returns_id(mock_db, sample_alert):
    connection, cursor = mock_db

    alert_id = save_alert(
        sample_alert,
        [
            {
                "record_id": 123,
                "evidence_type": "outbreak_record",
                "evidence_description": "Supporting source record",
            }
        ],
    )

    assert alert_id == 42
    connection.start_transaction.assert_called_once()
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    assert cursor.execute.call_count == 2


def test_save_alert_rolls_back_on_database_error(
    mock_db, sample_alert
):
    connection, cursor = mock_db
    cursor.execute.side_effect = RuntimeError("Database failure")

    with pytest.raises(RuntimeError, match="Database failure"):
        save_alert(sample_alert, [])

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_get_alert_by_id_returns_alert_with_evidence(mock_db):
    connection, cursor = mock_db
    cursor.fetchone.return_value = {
        "alert_id": 42,
        "disease": "Example Disease",
    }
    cursor.fetchall.return_value = [
        {
            "evidence_id": 1,
            "record_id": 123,
            "evidence_type": "outbreak_record",
        }
    ]

    result = get_alert_by_id(42)

    assert result["alert_id"] == 42
    assert len(result["evidence"]) == 1
    assert result["evidence"][0]["record_id"] == 123
    assert cursor.execute.call_count == 2


def test_get_alert_by_id_returns_none_when_missing(mock_db):
    connection, cursor = mock_db
    cursor.fetchone.return_value = None

    result = get_alert_by_id(999)

    assert result is None
    assert cursor.execute.call_count == 1
    connection.close.assert_called_once()


def test_list_alerts_uses_filters_and_pagination(mock_db):
    connection, cursor = mock_db
    cursor.fetchall.return_value = [{"alert_id": 42}]

    result = list_alerts(
        disease="Example Disease",
        state="Example State",
        limit=20,
        offset=10,
    )

    assert result == [{"alert_id": 42}]

    query, parameters = cursor.execute.call_args.args
    assert "disease = %s" in query
    assert "state = %s" in query
    assert parameters == ("Example Disease", "Example State", 20, 10)


@pytest.mark.parametrize("limit", [0, -1, 501])
def test_list_alerts_rejects_invalid_limit(limit):
    with pytest.raises(ValueError, match="limit"):
        list_alerts(limit=limit)


def test_list_alerts_rejects_negative_offset():
    with pytest.raises(ValueError, match="offset"):
        list_alerts(offset=-1)


def test_evidence_fingerprint_is_deterministic_with_null_record_id():
    first_evidence = {
        "record_id": None,
        "evidence_type": "historical_week",
        "evidence_description": "Baseline week 2026-W01: 10 cases",
    }
    repeated_evidence = {
        "record_id": None,
        "evidence_type": "historical_week",
        "evidence_description": "Baseline week 2026-W01: 10 cases",
    }

    first_key = _build_evidence_key(first_evidence)
    repeated_key = _build_evidence_key(repeated_evidence)

    assert first_key == repeated_key
    assert len(first_key) == 64
