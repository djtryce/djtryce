from src.questionnaire import QuestionnaireSession, validate_profile


def test_child_questions_activate_only_when_children_are_declared():
    session = QuestionnaireSession()
    session.answer("age", 34)
    session.answer("marital_status", "single")
    session.answer("child_ages", [])
    active_ids = {q["id"] for q in session.questions if session.is_active(q)}
    assert "school_child_ages" not in active_ids
    assert "disabled_child_ages" not in active_ids
    assert "single_parent" not in active_ids
    assert "unpaid_child_support" not in active_ids


def test_children_build_household_and_family_structure():
    session = QuestionnaireSession()
    session.answer("age", 40)
    session.answer("marital_status", "single")
    session.answer("child_ages", [8, 15])
    session.answer("school_child_ages", [8, 15])
    session.answer("disabled_child_ages", [15])
    session.answer("single_parent", True)
    profile = session.build_test_profile()

    assert profile["household"]["dependent_children_count"] == 2
    assert profile["household"]["household_size"] == 3
    assert profile["family"]["children"][0] == {
        "age": 8,
        "in_school": True,
        "disability_or_health_difficulty": False,
    }
    assert profile["family"]["children"][1] == {
        "age": 15,
        "in_school": True,
        "disability_or_health_difficulty": True,
    }


def test_couple_household_size_includes_two_adults():
    session = QuestionnaireSession()
    session.answer("marital_status", "couple")
    session.answer("child_ages", [6])
    profile = session.build_test_profile()
    assert profile["household"]["household_size"] == 3


def test_student_status_is_derived_from_employment_status():
    session = QuestionnaireSession()
    session.answer("employment_status", "student")
    profile = session.build_test_profile()
    assert profile["person"]["is_student"] is True


def test_retired_status_is_derived_when_not_answered_separately():
    session = QuestionnaireSession()
    session.answer("employment_status", "retired")
    profile = session.build_test_profile()
    assert profile["person"]["is_retired"] is True


def test_department_31_is_metropolitan_france():
    session = QuestionnaireSession()
    session.answer("department_code", "31")
    profile = session.build_test_profile()
    assert profile["residence"]["metropolitan_or_overseas"] == "metropolitan_france"


def test_overseas_department_is_detected():
    session = QuestionnaireSession()
    session.answer("department_code", "974")
    profile = session.build_test_profile()
    assert profile["residence"]["metropolitan_or_overseas"] == "overseas"


def test_existing_rights_are_mapped_without_assuming_unknowns():
    session = QuestionnaireSession()
    session.answer("existing_rights", ["aah", "apl"])
    profile = session.build_test_profile()
    assert profile["existing_rights"]["aah"] is True
    assert profile["existing_rights"]["apl"] is True
    assert profile["existing_rights"]["rsa"] is False


def test_synthetic_questionnaire_profile_validates_against_schema():
    session = QuestionnaireSession()
    answers = {
        "age": 42,
        "marital_status": "single",
        "child_ages": [10],
        "school_child_ages": [10],
        "single_parent": True,
        "pregnancy": False,
        "stable_residence": True,
        "department_code": "31",
        "nationality_status": "french",
        "housing_status": "tenant",
        "monthly_rent": 650,
        "rent_arrears": False,
        "energy_debt": False,
        "resources_known": True,
        "annual_resources": 15000,
        "monthly_resources": 1250,
        "rfr": 14000,
        "employment_status": "employee",
        "working": True,
        "monthly_earned_income": 1250,
        "health_difficulty": False,
        "caregiver": False,
        "unpaid_child_support": False,
        "legal_proceeding": False,
        "existing_rights": [],
    }
    for question_id, value in answers.items():
        session.answer(question_id, value)
    profile = session.build_test_profile()
    validate_profile(profile)
