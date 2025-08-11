# File: core/assertion_handler.py
import json
import os
import pytest
import allure

def load_json_file(json_path):
    if not os.path.exists(json_path):
        pytest.fail(f"Expected JSON file not found: {json_path}")
    with open(json_path) as f:
        return json.load(f)


def assert_from_bulk_json(actual_data: dict, json_config: dict):
    print("Asserting using json")
    print(f"******* Actual data ****************** {actual_data}")
    """
    Compare multiple keys in actual_data against a JSON file.

    Args:
        actual_data: Dict of the actual data returned from the model.
        json_config: Dict with 'file' key (and optionally 'type' for assertion strategy).

    Example:
        expectations:
          from_json:
            file: test_data/expected_output.json
    """
    file_path = json_config.get("file")
    assertion_type = json_config.get("type", "equals")

    expected_data = load_json_file(file_path)

    for key, expected_value in expected_data.items():
        print(f"***** expected key ***** {key}")
        print(f"***** expected_value ***** {expected_value}")
        actual_value = getattr(actual_data, key, None)

        with allure.step(f"Assert {key} matches expectations"):
            if assertion_type == "equals":
                assert actual_value == expected_value, (
                    f"[ASSERTION FAILED] Key: '{key}' | Expected: {expected_value} | Got: {actual_value}"
                )
            else:
                pytest.fail(f"Unsupported bulk assertion type: {assertion_type}")