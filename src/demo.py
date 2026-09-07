from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

import yaml

from src.engine import RightsEngine
from src.questionnaire import QuestionnaireSession, validate_profile
from src.result_presenter import render_report


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEMO_ANSWERS = ROOT / "examples" / "demo_answers.yaml"


def _show_question(question: Dict[str, Any]) -> None:
    print()
    print(question["text"])
    choices = question.get("choices") or []
    if choices:
        print("Choix possibles : " + ", ".join(str(choice) for choice in choices))
    if not question.get("required", False):
        print("Vous pouvez laisser vide ou répondre 'je ne sais pas'.")


def run_interactive() -> str:
    print("Assistant d'accès aux droits - démonstration locale")
    print("Ce prototype ne sauvegarde pas vos réponses.")
    print("Il fournit une orientation et jamais une décision administrative.")

    session = QuestionnaireSession()
    while True:
        question = session.next_question()
        if question is None:
            break
        _show_question(question)
        while True:
            raw = input("> ")
            try:
                session.answer(question["id"], raw)
                break
            except (TypeError, ValueError) as exc:
                print(f"Réponse non comprise : {exc}")

    profile = session.build_test_profile()
    profile["metadata"]["source"] = "questionnaire"
    profile["metadata"]["storage_policy"] = "memory_only"
    profile["metadata"]["notes"] = "Profil créé en mémoire par la démo locale, non enregistré par le programme."
    validate_profile(profile)

    evaluation = RightsEngine().evaluate(profile)
    return render_report(evaluation)


def run_from_answers(path: Path = DEFAULT_DEMO_ANSWERS) -> str:
    with path.open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f) or {}

    answers = payload.get("answers", payload)
    if not isinstance(answers, dict):
        raise ValueError("Le fichier de démonstration doit contenir une table 'answers'.")

    session = QuestionnaireSession()
    for question_id, value in answers.items():
        if question_id not in session._by_id:
            raise ValueError(f"Question inconnue dans la démo : {question_id}")
        session.answer(question_id, value)

    profile = session.build_test_profile()
    validate_profile(profile)
    evaluation = RightsEngine().evaluate(profile)
    return render_report(evaluation)


def main() -> None:
    parser = argparse.ArgumentParser(description="Démonstration de bout en bout du moteur d'accès aux droits")
    parser.add_argument(
        "--answers",
        type=Path,
        help="Fichier YAML de réponses fictives. Sans cette option, le questionnaire est interactif.",
    )
    args = parser.parse_args()

    if args.answers:
        report = run_from_answers(args.answers)
    else:
        report = run_interactive()

    print()
    print(report)


if __name__ == "__main__":
    main()
