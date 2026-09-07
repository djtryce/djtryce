import json
from pathlib import Path

from jsonschema import Draft202012Validator

from src.engine import RightsEngine


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "profile.schema.json"
EXAMPLE_PROFILE = ROOT / "examples" / "profile_test_01.json"


def load_profile():
    with EXAMPLE_PROFILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def status_map(result):
    return {item["right_id"]: item["status"] for item in result["results"]}


def test_example_profile_matches_schema():
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    profile = load_profile()
    Draft202012Validator(schema).validate(profile)


def test_example_profile_expected_orientations():
    profile = load_profile()
    result = RightsEngine().evaluate(profile)
    statuses = status_map(result)

    assert statuses["css"] == "POTENTIEL_AVEC_PARTICIPATION"
    assert statuses["apl_alf_als"] == "A_SIMULER"
    assert statuses["pch"] == "A_EXPLORER"
    assert statuses["rqth"] == "EVALUATION_HUMAINE_NECESSAIRE"
    assert statuses["cmi"] == "EVALUATION_HUMAINE_NECESSAIRE"
    assert statuses["apa"] == "CONDITIONS_DECLAREES_INCOMPATIBLES"
    assert statuses["pension_invalidite"] == "EVALUATION_HUMAINE_NECESSAIRE"


def test_css_exact_free_threshold_is_potential():
    profile = load_profile()
    profile["income"]["annual_household_resources"] = 10421
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["css"] == "POTENTIEL"


def test_css_one_euro_above_free_threshold_requires_contribution():
    profile = load_profile()
    profile["income"]["annual_household_resources"] = 10422
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["css"] == "POTENTIEL_AVEC_PARTICIPATION"


def test_css_exact_contribution_threshold_is_still_potential():
    profile = load_profile()
    profile["income"]["annual_household_resources"] = 14069
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["css"] == "POTENTIEL_AVEC_PARTICIPATION"


def test_css_one_euro_above_contribution_threshold_is_incompatible():
    profile = load_profile()
    profile["income"]["annual_household_resources"] = 14070
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["css"] == "CONDITIONS_DECLAREES_INCOMPATIBLES"


def test_css_missing_resources_never_guesses():
    profile = load_profile()
    profile["income"]["annual_household_resources"] = None
    result = RightsEngine().evaluate(profile)
    statuses = status_map(result)
    assert statuses["css"] == "INFORMATION_INSUFFISANTE"


def test_apa_age_under_60_is_incompatible():
    profile = load_profile()
    profile["person"]["age"] = 59
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["apa"] == "CONDITIONS_DECLAREES_INCOMPATIBLES"


def test_apa_age_60_without_gir_requires_human_evaluation():
    profile = load_profile()
    profile["person"]["age"] = 60
    profile["health_disability"]["gir_level"] = None
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["apa"] == "EVALUATION_HUMAINE_NECESSAIRE"


def test_apa_gir_4_still_requires_administrative_decision():
    profile = load_profile()
    profile["person"]["age"] = 72
    profile["health_disability"]["gir_level"] = 4
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["apa"] == "EVALUATION_HUMAINE_NECESSAIRE"


def test_unknown_housing_status_returns_insufficient_information():
    profile = load_profile()
    profile["housing"]["status"] = "unknown"
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["apl_alf_als"] == "INFORMATION_INSUFFISANTE"


def test_no_health_difficulty_does_not_emit_pch_or_invalidity():
    profile = load_profile()
    profile["health_disability"]["health_or_disability_difficulty"] = False
    profile["health_disability"]["mobility_difficulty"] = False
    profile["employment"]["work_limitation_due_to_health_or_disability"] = False
    statuses = status_map(RightsEngine().evaluate(profile))
    assert "pch" not in statuses
    assert "pension_invalidite" not in statuses
    assert "rqth" not in statuses
    assert "cmi" not in statuses


def test_legal_aid_is_not_decided_automatically():
    profile = load_profile()
    profile["legal_admin"]["legal_proceeding"] = True
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["aide_juridictionnelle"] == "A_SIMULER"


def test_caregiver_triggers_ajpa_exploration_only():
    profile = load_profile()
    profile["family"]["caregiver_for_relative"] = True
    statuses = status_map(RightsEngine().evaluate(profile))
    assert statuses["ajpa"] == "A_EXPLORER"
