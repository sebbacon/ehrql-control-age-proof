from datetime import date

from dataset_definition import dataset


test_data = {
    # In population: a matching control ID and index date produce age 40.
    1: {
        "patients": {
            "date_of_birth": date(1980, 3, 1),
            "sex": "female",
        },
        "expected_in_population": True,
        "expected_columns": {
            "index_date": date(2020, 3, 31),
            "age": 40,
            "sex": "female",
        },
    },
    # In population: age is calculated from this patient's own later index date.
    2: {
        "patients": {
            "date_of_birth": date(2000, 7, 1),
            "sex": "male",
        },
        "expected_in_population": True,
        "expected_columns": {
            "index_date": date(2021, 6, 15),
            "age": 20,
            "sex": "male",
        },
    },
    # Debugging case: the control exists but has no matching patients-table row.
    3: {
        "patients": [],
        "expected_in_population": True,
        "expected_columns": {
            "index_date": date(2022, 1, 1),
            "age": None,
            "sex": "female",
        },
    },
    # Debugging case: the patient matches, but a missing index date gives a missing age.
    4: {
        "patients": {
            "date_of_birth": date(1990, 1, 1),
            "sex": "unknown",
        },
        "expected_in_population": True,
        "expected_columns": {
            "index_date": None,
            "age": None,
            "sex": "unknown",
        },
    },
}
