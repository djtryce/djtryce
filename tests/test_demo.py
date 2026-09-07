from pathlib import Path

from src.demo import DEFAULT_DEMO_ANSWERS, run_from_answers
from src.result_presenter import render_report


def test_demo_answers_file_exists():
    assert Path(DEFAULT_DEMO_ANSWERS).exists()


def test_end_to_end_demo_produces_readable_report():
    report = run_from_answers(DEFAULT_DEMO_ANSWERS)
    assert "ORIENTATION VERS LES DROITS" in report
    assert "Version du moteur" in report
    assert "Sources officielles" in report
    assert "Complémentaire santé solidaire" in report
    assert "APL / ALF / ALS" in report
    assert "Prime d'activité" in report
    assert "Fonds de solidarité pour le logement" in report


def test_presenter_keeps_administrative_disclaimer():
    report = render_report(
        {
            "engine_version": "test",
            "rules_version": "test",
            "rules_verified_at": "2026-09-07",
            "results": [],
        }
    )
    assert "ne remplace pas une décision" in report
