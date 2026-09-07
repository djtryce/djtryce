import copy
import json
from pathlib import Path

from src.engine import RightsEngine

ROOT = Path(__file__).resolve().parents[1]
BASE_PROFILE = ROOT / "examples" / "profile_test_01.json"


def profile():
    with BASE_PROFILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def statuses(p):
    result = RightsEngine().evaluate(p)
    return {item["right_id"]: item["status"] for item in result["results"]}


def test_ars_school_child_age_8_requires_simulation():
    p = profile()
    p["family"]["children"] = [{"age": 8, "in_school": True, "disability_or_health_difficulty": False}]
    assert statuses(p)["ars"] == "A_SIMULER"


def test_ars_school_child_age_17_requires_simulation():
    p = profile()
    p["family"]["children"] = [{"age": 17, "in_school": True, "disability_or_health_difficulty": False}]
    assert statuses(p)["ars"] == "A_SIMULER"


def test_ars_child_under_6_in_school_is_only_explored():
    p = profile()
    p["family"]["children"] = [{"age": 5, "in_school": True, "disability_or_health_difficulty": False}]
    assert statuses(p)["ars"] == "A_EXPLORER"


def test_asf_single_parent_with_unpaid_support_is_explored():
    p = profile()
    p["household"]["single_parent"] = True
    p["household"]["dependent_children_count"] = 1
    p["family"]["unpaid_child_support"] = True
    assert statuses(p)["asf"] == "A_EXPLORER"


def test_asf_couple_is_not_emitted():
    p = profile()
    p["household"]["single_parent"] = False
    p["household"]["dependent_children_count"] = 1
    p["family"]["unpaid_child_support"] = True
    assert "asf" not in statuses(p)


def test_energy_cheque_single_low_rfr_requires_official_simulation():
    p = profile()
    p["household"]["household_size"] = 1
    p["income"]["reference_tax_income"] = 9000
    assert statuses(p)["cheque_energie"] == "A_SIMULER"


def test_energy_cheque_two_person_household_low_ratio_requires_simulation():
    p = profile()
    p["household"]["household_size"] = 2
    p["income"]["reference_tax_income"] = 15000
    assert statuses(p)["cheque_energie"] == "A_SIMULER"


def test_energy_cheque_high_rfr_is_not_emitted_as_false_negative_label():
    p = profile()
    p["household"]["household_size"] = 1
    p["income"]["reference_tax_income"] = 30000
    assert "cheque_energie" not in statuses(p)


def test_mvp_dataset_covers_20_priority_schemes_counting_housing_three_times():
    engine = RightsEngine()
    ids = set(engine.rights)
    expected_entries = {
        "rsa", "prime_activite", "apl_alf_als", "aah", "pch", "rqth", "cmi",
        "css", "pension_invalidite", "aspa", "apa", "fsl", "cheque_energie",
        "aide_juridictionnelle", "asf", "ars", "aeeh", "ajpa"
    }
    assert expected_entries.issubset(ids)
    # APL / ALF / ALS sont trois dispositifs gérés par une entrée commune.
    assert len(expected_entries) + 2 == 20


def test_engine_reports_current_versions():
    result = RightsEngine().evaluate(profile())
    assert result["engine_version"] == "0.4.0"
    assert result["rules_version"] == "1.3-audited"
