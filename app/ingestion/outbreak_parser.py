
from app.models.outbreak import Outbreak

from pydantic import ValidationError


def parse_outbreak(record: dict) -> Outbreak:
    """
    Convert an outbreak dictionary into
    a validated Outbreak object.
    """
    outbreak = Outbreak.model_validate(record)

    return outbreak

def parse_multiple_outbreaks(records: list[dict]) -> list[Outbreak]:
    """
    Validate multiple outbreak records
    and return a list of Outbreak objects.
    """
    validated_outbreaks = []

    for record in records:
        outbreak = parse_outbreak(record)
        validated_outbreaks.append(outbreak)

    return validated_outbreaks

def parse_outbreaks_with_errors(records: list[dict]):
    """
    Validate outbreak records and separate
    valid records from invalid records.
    """
    valid_outbreaks = []
    invalid_records = []

    for index, record in enumerate(records):
        try:
            outbreak = parse_outbreak(record)
            valid_outbreaks.append(outbreak)

        except ValidationError as error:
            invalid_records.append({
                "record_index": index,
                "unique_id": record.get("unique_id"),
                "original_record": record.copy(),
                "errors": error.errors(include_context=False)
            })

    return valid_outbreaks, invalid_records
