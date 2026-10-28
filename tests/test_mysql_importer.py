
from unittest.mock import patch
from mysql.connector import IntegrityError

from app.ingestion.mysql_importer import import_outbreaks_from_csv


def test_mysql_importer_handles_duplicates():
    with patch(
        "app.ingestion.mysql_importer.save_outbreaks"
    ) as mock_save:

        duplicate_error = IntegrityError(
            msg="Duplicate entry",
            errno=1062
        )

        mock_save.side_effect = lambda outbreaks: [
            (outbreaks[0], None),
            (outbreaks[1], duplicate_error),
            (outbreaks[2], None)
        ]

        results = import_outbreaks_from_csv(
            "data/sample_outbreaks.csv"
        )

    assert results["imported"] == 2
    assert results["duplicates"] == 1
    assert results["invalid"] == 1
    assert results["failed"] == 0

    assert mock_save.call_count == 1

def test_mysql_importer_handles_database_errors():
    from mysql.connector import Error

    with patch(
        "app.ingestion.mysql_importer.save_outbreaks"
    ) as mock_save:

        database_error = Error(msg="Database connection lost")

        mock_save.side_effect = lambda outbreaks: [
            (outbreaks[0], None),
            (outbreaks[1], database_error),
            (outbreaks[2], None)
        ]

        results = import_outbreaks_from_csv(
            "data/sample_outbreaks.csv"
        )

    assert results["imported"] == 2
    assert results["duplicates"] == 0
    assert results["invalid"] == 1
    assert results["failed"] == 1

    assert mock_save.call_count == 1
    assert results["errors"][-1]["unique_id"] == "KA/BLR/2024/102"
    assert "Database connection lost" in results["errors"][-1]["error"]

def test_import_validated_outbreaks_success():
    from unittest.mock import patch
    from app.models.outbreak import Outbreak
    from app.ingestion.mysql_importer import import_validated_outbreaks

    outbreak = Outbreak(
        unique_id="KL/KSD/2024/200",
        state="Kerala",
        district="Kasaragod",
        disease="Dengue",
        cases=25,
        deaths=0,
        outbreak_start_date="2024-08-01",
        reporting_date="2024-08-03",
        status="Under Control",
        comments="Test outbreak"
    )

    with patch(
        "app.ingestion.mysql_importer.save_outbreaks"
    ) as mock_save:

        mock_save.return_value = [(outbreak, None)]

        results = import_validated_outbreaks([outbreak])

    mock_save.assert_called_once_with([outbreak])

    assert results["imported"] == 1
    assert results["duplicates"] == 0
    assert results["failed"] == 0
    assert results["errors"] == []
