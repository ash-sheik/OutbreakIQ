
from app.models.outbreak import Outbreak

# Sample outbreak data for testing
outbreak_data = {
    "unique_id": "KL/KSD/2024/001",
    "state": "Kerala",
    "district": "Kasaragod",
    "disease": "Dengue",
    "cases": 25,
    "deaths": 0,
    "outbreak_start_date": "2024-07-01",
    "reporting_date": "2024-07-03",
    "status": "Under Control",
    "comments": "Sample outbreak record for testing."
}

# Validate outbreak data using Pydantic
outbreak = Outbreak(**outbreak_data)

print("Outbreak validation successful!")
print(outbreak.model_dump_json(indent=2))


from pydantic import ValidationError

# Test invalid outbreak data
invalid_data = outbreak_data.copy()
invalid_data["cases"] = -25

try:
    Outbreak(**invalid_data)
    print("ERROR: Invalid data was accepted!")

except ValidationError as error:
    print("\nInvalid outbreak correctly rejected!")
    print(error)
