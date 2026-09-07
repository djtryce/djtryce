from __future__ import annotations

from typing import Any, Dict, Iterable, List


STATUS_LABELS = {
    "POTENTIEL": "Potentiel à vérifier",
    "POTENTIEL_AVEC_PARTICIPATION": "Potentiel avec participation",
    "A_SIMULER": "À simuler",
    "A_EXPLORER": "À explorer",
    "EVALUATION_HUMAINE_NECESSAIRE": "Évaluation humaine nécessaire",
    "INFORMATION_INSUFFISANTE": "Informations à compléter",
    "CONDITIONS_DECLAREES_INCOMPATIBLES": "Conditions déclarées non compatibles",
}

STATUS_ACTIONS = {
    "POTENTIEL": "Vérifier les conditions restantes puis consulter la source officielle pour engager la démarche.",
    "POTENTIEL_AVEC_PARTICIPATION": "Vérifier les conditions restantes et le montant de participation auprès de l'organisme compétent.",
    "A_SIMULER": "Utiliser le simulateur ou le service officiel indiqué par les sources avant toute conclusion.",
    "A_EXPLORER": "Consulter la source officielle et réunir les informations ou justificatifs demandés.",
    "EVALUATION_HUMAINE_NECESSAIRE": "Faire examiner la situation par l'organisme ou le professionnel compétent.",
    "INFORMATION_INSUFFISANTE": "Compléter les informations manquantes avant de poursuivre l'évaluation.",
    "CONDITIONS_DECLAREES_INCOMPATIBLES": "Ne pas conclure définitivement : revérifier les informations si la situation a changé ou si une exception peut s'appliquer.",
}


def _lines(items: Iterable[str], prefix: str = "  - ") -> List[str]:
    return [f"{prefix}{item}" for item in items]


def render_result(result: Dict[str, Any]) -> str:
    status = result.get("status", "INFORMATION_INSUFFISANTE")
    label = STATUS_LABELS.get(status, status)
    lines = [
        f"{result.get('name', result.get('right_id', 'Droit'))}",
        f"Statut : {label}",
        f"Pourquoi : {result.get('reason', 'Aucune explication disponible.')}",
    ]

    missing = result.get("missing_information") or []
    if missing:
        lines.append("Informations à compléter :")
        lines.extend(_lines(missing))

    lines.append(f"Prochaine étape : {STATUS_ACTIONS.get(status, 'Consulter la source officielle.')}")

    if result.get("human_evaluation_required"):
        lines.append("Attention : une appréciation humaine ou administrative est nécessaire.")

    sources = result.get("sources") or []
    if sources:
        lines.append("Sources officielles :")
        lines.extend(_lines(sources))

    return "\n".join(lines)


def render_report(evaluation: Dict[str, Any]) -> str:
    results = evaluation.get("results") or []
    header = [
        "ORIENTATION VERS LES DROITS",
        "============================",
        "Ce résultat est une orientation. Il ne remplace pas une décision de la Caf, CPAM, MDPH, caisse de retraite, département ou autre organisme compétent.",
        "",
        f"Version du moteur : {evaluation.get('engine_version', 'inconnue')}",
        f"Version du référentiel : {evaluation.get('rules_version', 'inconnue')}",
        f"Référentiel vérifié le : {evaluation.get('rules_verified_at', 'date inconnue')}",
        "",
    ]

    if not results:
        return "\n".join(header + ["Aucune piste n'a été produite avec les informations disponibles."])

    blocks = [render_result(result) for result in results]
    return "\n\n".join(["\n".join(header).rstrip(), *blocks])
