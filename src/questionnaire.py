from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "questionnaire_mvp.yaml"
PROFILE_SCHEMA = ROOT / "schemas" / "profile.schema.json"

RIGHT_IDS = [
    "rsa", "prime_activite", "apl", "alf", "als", "aah", "pch", "rqth",
    "cmi", "css", "pension_invalidite", "aspa", "apa", "fsl",
    "cheque_energie", "aide_juridictionnelle", "asf", "ars", "aeeh", "ajpa",
]


def blank_test_profile() -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "profile_id": None,
        "assessment_date": date.today().isoformat(),
        "person": {
            "age": None,
            "date_of_birth_known": False,
            "is_student": None,
            "is_retired": None,
            "all_retirement_pensions_liquidated": None,
            "retirement_inaptitude_recognized": None,
            "permanent_incapacity_percent": None,
        },
        "household": {
            "marital_status": "unknown",
            "household_size": 1,
            "dependent_children_count": 0,
            "single_parent": None,
            "pregnancy": None,
        },
        "residence": {
            "country": "France",
            "metropolitan_or_overseas": "unknown",
            "department_code": None,
            "postal_code": None,
            "stable_residence": None,
            "residence_duration_months": None,
            "nationality_status": "unknown",
            "valid_residence_permit": None,
        },
        "housing": {
            "status": "unknown",
            "monthly_rent_or_fee": None,
            "housing_aid_already_received": None,
            "rent_arrears": None,
            "energy_debt": None,
            "housing_convention_known": None,
        },
        "income": {
            "resources_known": None,
            "monthly_household_resources": None,
            "annual_household_resources": None,
            "reference_tax_income": None,
            "movable_assets": None,
            "real_estate_assets_excluding_main_home": None,
            "resource_period_start": None,
            "resource_period_end": None,
        },
        "employment": {
            "status": "unknown",
            "working": None,
            "partial_or_technical_unemployment": None,
            "monthly_earned_income": None,
            "monthly_gross_earned_income": None,
            "registered_france_travail": None,
            "work_limitation_due_to_health_or_disability": None,
            "insurance_affiliation_months": None,
            "hours_worked_last_12_months": None,
            "hours_worked_last_3_years": None,
        },
        "health_disability": {
            "health_or_disability_difficulty": None,
            "difficulty_expected_duration_months": None,
            "difficulty_absolute_count": None,
            "difficulty_severe_count": None,
            "mobility_difficulty": None,
            "daily_living_difficulty": None,
            "needs_human_assistance": None,
            "mdph_file_exists": None,
            "mdph_decision_exists": None,
            "disability_rate_percent": None,
            "gir_level": None,
            "medical_capacity_loss_two_thirds_assessed": None,
            "requires_third_person_assistance": None,
        },
        "family": {
            "children": [],
            "unpaid_child_support": None,
            "caregiver_for_relative": None,
            "number_of_aided_persons_over_career": None,
        },
        "legal_admin": {
            "legal_proceeding": None,
            "urgent_legal_situation": None,
            "recent_administrative_refusal": None,
            "decision_date": None,
            "appeal_deadline_known": None,
        },
        "existing_rights": {right_id: None for right_id in RIGHT_IDS},
        "metadata": {
            "source": "test_fixture",
            "contains_real_personal_data": False,
            "storage_policy": "test_fixture",
            "notes": "Profil fictif produit par le questionnaire de test du MVP.",
        },
    }


def set_path(obj: Dict[str, Any], dotted_path: str, value: Any) -> None:
    parts = dotted_path.split(".")
    cursor = obj
    for part in parts[:-1]:
        cursor = cursor[part]
    cursor[parts[-1]] = value


class QuestionnaireSession:
    def __init__(self, config_path: Path = DEFAULT_CONFIG) -> None:
        with config_path.open("r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.questions: List[Dict[str, Any]] = self.config.get("questions", [])
        self.answers: Dict[str, Any] = {}
        self._by_id = {q["id"]: q for q in self.questions}

    def is_active(self, question: Dict[str, Any]) -> bool:
        condition = question.get("when")
        if not condition:
            return True
        answer = self.answers.get(condition["question"])
        op = condition["op"]
        expected = condition.get("value")

        if op == "equals":
            return answer == expected
        if op == "in":
            return answer in (expected or [])
        if op == "nonempty":
            return bool(answer)
        if op == "lt":
            return answer is not None and answer < expected
        if op == "gte":
            return answer is not None and answer >= expected
        if op == "between":
            return answer is not None and expected[0] <= answer <= expected[1]
        raise ValueError(f"Opérateur inconnu: {op}")

    def next_question(self) -> Dict[str, Any] | None:
        for question in self.questions:
            if question["id"] not in self.answers and self.is_active(question):
                return question
        return None

    def answer(self, question_id: str, value: Any) -> None:
        question = self._by_id[question_id]
        self.answers[question_id] = self._coerce(question, value)

    def _coerce(self, question: Dict[str, Any], value: Any) -> Any:
        qtype = question.get("type", "string")
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return [] if qtype in {"integer_list", "string_list"} else None
            if value.lower() in {"?", "inconnu", "inconnue", "je ne sais pas", "jsp"}:
                return None

        if qtype == "boolean":
            if isinstance(value, bool):
                return value
            normalized = str(value).lower()
            if normalized in {"oui", "o", "yes", "y", "1", "true", "vrai"}:
                return True
            if normalized in {"non", "n", "no", "0", "false", "faux"}:
                return False
            raise ValueError("Réponse booléenne non comprise")
        if qtype == "integer":
            return int(value)
        if qtype == "number":
            return float(str(value).replace(" ", "").replace(",", "."))
        if qtype == "integer_list":
            if isinstance(value, list):
                return [int(x) for x in value]
            return [int(x.strip()) for x in str(value).split(",") if x.strip()]
        if qtype == "string_list":
            if isinstance(value, list):
                return [str(x).strip() for x in value if str(x).strip()]
            return [x.strip() for x in str(value).split(",") if x.strip()]
        if qtype == "choice":
            if value not in question.get("choices", []):
                raise ValueError("Choix non autorisé")
            return value
        return str(value)

    def build_test_profile(self) -> Dict[str, Any]:
        profile = blank_test_profile()

        for question in self.questions:
            qid = question["id"]
            if qid in self.answers and question.get("target"):
                set_path(profile, question["target"], self.answers[qid])

        child_ages = self.answers.get("child_ages") or []
        school_ages = self.answers.get("school_child_ages") or []
        disabled_ages = self.answers.get("disabled_child_ages") or []
        profile["family"]["children"] = [
            {
                "age": age,
                "in_school": age in school_ages if school_ages else None,
                "disability_or_health_difficulty": age in disabled_ages if disabled_ages else None,
            }
            for age in child_ages
        ]
        profile["household"]["dependent_children_count"] = len(child_ages)
        adults = 2 if profile["household"]["marital_status"] == "couple" else 1
        profile["household"]["household_size"] = adults + len(child_ages)

        status = profile["employment"]["status"]
        profile["person"]["is_student"] = status == "student"
        if "is_retired" not in self.answers:
            profile["person"]["is_retired"] = status == "retired"

        department = profile["residence"].get("department_code")
        if department:
            department = str(department).upper()
            profile["residence"]["metropolitan_or_overseas"] = (
                "overseas" if department.startswith(("97", "98")) else "metropolitan_france"
            )

        selected = self.answers.get("existing_rights")
        if selected is not None:
            selected_ids = set(selected)
            for right_id in RIGHT_IDS:
                profile["existing_rights"][right_id] = right_id in selected_ids

        return profile


def validate_profile(profile: Dict[str, Any]) -> None:
    import jsonschema

    with PROFILE_SCHEMA.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.Draft202012Validator(schema).validate(profile)
