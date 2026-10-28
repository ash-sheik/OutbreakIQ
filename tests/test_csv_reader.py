
from pathlib import Path

from app.ingestion.csv_reader import load_and_validate_outbreaks


def test_csv_validation_pipeline():
    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "data" / "sample_outbreaks.csv"

    valid, invalid = load_and_validate_outbreaks(str(csv_path))

    assert len(valid) == 3
    assert len(invalid) == 1

    assert valid[0].disease == "Dengue"
    assert valid[1].disease == "Food Poisoning"
    assert valid[2].disease == "Leptospirosis"

    assert invalid[0]["unique_id"] == "KL/KSD/2024/104"
    assert invalid[0]["errors"][0]["loc"] == ("cases",)
