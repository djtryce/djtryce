import copy
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from src.engine import RightsEngine


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "tests" / "profiles_matrix.yaml"
SCHEMA_PATH = ROOT / "schemas" / "profile.schema.json"


def load_matrix():
    with MATRIX_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_base_profile(matrix):
    with (ROOT / matrix["base_profile"]).open("r", encoding="utf-8") as f:
        return json.load(f)


def set_path(obj, dotted_path, value):
    parts = dotted_path.split(".")
    current = obj
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = value


def status_map(result):
    return {item["right_id"]: item["status"] for item in result["results"]}


MATRIX = load_matrix()
CASES = MATRIX["cases"]


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_profile_matrix(case):
    profile = copy.deepcopy(load_base_profile(MATRIX))
    profile["profile_id"] = f"matrix-{case['id']}"

    for path, value in case.get("set", {}).items():
        set_path(profile, path, value)

    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    Draft202012Validator(schema).validate(profile)

    statuses = status_map(RightsEngine().evaluate(profile))

    for right_id, expected_status in case.get("expect", {}).items():
        assert statuses.get(right_id) == expected_status, (
            f"{case['id']}: attendu {right_id}={expected_status}, "
            f"obtenu {statuses.get(right_id)}"
        )

    for right_id in case.get("absent", []):
        assert right_id not in statuses, (
            f"{case['id']}: {right_id} ne devait pas être émis par le moteur"
        )


def test_matrix_contains_at_least_20_scenarios():
    assert len(CASES) >= 20


def test_all_matrix_ids_are_unique():
    ids = [case["id"] for case in CASES]
    assert len(ids) == len(set(ids))
