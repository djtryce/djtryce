from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from src.engine import RightsEngine
from src.questionnaire import QuestionnaireSession, validate_profile
from src.result_presenter import STATUS_ACTIONS, STATUS_LABELS


st.set_page_config(
    page_title="Mes droits à explorer",
    page_icon="📋",
    layout="centered",
)


MARITAL = {
    "Seul(e)": "single",
    "En couple": "couple",
    "Séparé(e)": "separated",
    "Veuf / veuve": "widowed",
    "Je ne sais pas": "unknown",
}

NATIONALITY = {
    "Française": "french",
    "UE / EEE / Suisse": "eu_eea_swiss",
    "Hors UE": "non_eu",
    "Réfugié(e) / apatride": "stateless_or_refugee",
    "Je ne sais pas": "unknown",
}

HOUSING = {
    "Locataire": "tenant",
    "Propriétaire": "owner",
    "Hébergé(e) gratuitement": "hosted_free",
    "Résidence sociale / foyer": "social_residence",
    "Sans logement": "homeless",
    "Hébergement d'urgence": "emergency_accommodation",
    "Autre": "other",
    "Je ne sais pas": "unknown",
}

EMPLOYMENT = {
    "Salarié(e)": "employee",
    "Indépendant(e)": "self_employed",
    "Sans emploi": "unemployed",
    "Sans activité": "inactive",
    "Retraité(e)": "retired",
    "Étudiant(e)": "student",
    "Arrêt maladie": "sick_leave",
    "Autre": "other",
    "Je ne sais pas": "unknown",
}

TRI = {
    "Je ne sais pas": None,
    "Oui": True,
    "Non": False,
}


def parse_number(value: str) -> float | None:
    value = (value or "").strip().replace(" ", "").replace(",", ".")
    if not value:
        return None
    return float(value)


def parse_ages(value: str) -> List[int]:
    value = (value or "").strip()
    if not value:
        return []
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def reverse_label(mapping: Dict[str, Any], value: Any, fallback: str) -> str:
    for label, stored in mapping.items():
        if stored == value:
            return label
    return fallback


def tri_label(value: Any) -> str:
    return reverse_label(TRI, value, "Je ne sais pas")


def put(key: str, value: Any) -> None:
    st.session_state.answers[key] = value


def build_profile(answers: Dict[str, Any]) -> Dict[str, Any]:
    session = QuestionnaireSession()
    supported = {
        "age", "marital_status", "child_ages", "school_child_ages",
        "disabled_child_ages", "single_parent", "pregnancy",
        "stable_residence", "department_code", "nationality_status",
        "valid_residence_permit", "housing_status", "monthly_rent",
        "rent_arrears", "energy_debt", "resources_known",
        "annual_resources", "monthly_resources", "rfr",
        "employment_status", "working", "monthly_earned_income",
        "monthly_gross_earned_income", "hours_worked_last_3_years",
        "health_difficulty", "mobility_difficulty",
        "daily_living_difficulty", "work_limitation", "gir_level",
        "is_retired", "all_pensions_liquidated", "retirement_inaptitude",
        "caregiver", "unpaid_child_support", "legal_proceeding",
        "existing_rights",
    }

    for key, value in answers.items():
        if key in supported:
            session.answer(key, value)

    profile = session.build_test_profile()
    profile["metadata"] = {
        "source": "questionnaire",
        "contains_real_personal_data": True,
        "storage_policy": "ephemeral_only",
        "notes": "Profil construit en mémoire par l'interface web locale. Aucune sauvegarde par l'application.",
    }
    validate_profile(profile)
    return profile


def go_to(step: int) -> None:
    st.session_state.step = step
    st.rerun()


def reset() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}

answers = st.session_state.answers
step = st.session_state.step

st.title("Mes droits à explorer")
st.caption("Prototype d'orientation vers des aides et démarches en France")

if step == 0:
    st.info(
        "Cette démonstration ne rend aucune décision administrative. "
        "Elle repère des droits à vérifier à partir des informations que vous saisissez."
    )
    st.warning(
        "Confidentialité : les réponses restent dans la session de cette page et ne sont pas enregistrées par l'application. "
        "Ne saisissez ni nom, ni adresse complète, ni numéro de sécurité sociale, ni numéro CAF."
    )
    st.markdown(
        "Le questionnaire utilise des questions de vie courante. Vous n'avez pas besoin de connaître les noms des prestations."
    )
    if st.button("Commencer", type="primary", use_container_width=True):
        go_to(1)
    st.stop()

st.progress(step / 4)
st.caption(f"Étape {step} sur 4")

if step == 1:
    st.header("1. Votre foyer et votre résidence")
    with st.form("step_1"):
        age = st.number_input(
            "Quel âge avez-vous ?",
            min_value=0,
            max_value=130,
            value=int(answers.get("age", 30)),
            step=1,
        )
        marital_label = st.selectbox(
            "Quelle est votre situation de couple ?",
            list(MARITAL.keys()),
            index=list(MARITAL.keys()).index(reverse_label(MARITAL, answers.get("marital_status"), "Seul(e)")),
        )
        child_ages_text = st.text_input(
            "Âge des enfants à votre charge, séparés par des virgules",
            value=", ".join(map(str, answers.get("child_ages", []))),
            placeholder="Exemple : 6, 14. Laissez vide si vous n'en avez pas.",
        )
        school_ages_text = st.text_input(
            "Parmi eux, âges des enfants scolarisés",
            value=", ".join(map(str, answers.get("school_child_ages", []))),
            placeholder="Exemple : 6, 14",
        )
        disabled_ages_text = st.text_input(
            "Parmi eux, âges des enfants ayant une difficulté importante de santé ou un handicap",
            value=", ".join(map(str, answers.get("disabled_child_ages", []))),
            placeholder="Laissez vide si aucun",
        )
        single_parent_label = st.selectbox(
            "Si vous avez des enfants, les élevez-vous seul(e) ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("single_parent"))),
        )
        pregnancy_label = st.selectbox(
            "Y a-t-il une grossesse à prendre en compte dans votre foyer ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("pregnancy"))),
        )
        stable_label = st.selectbox(
            "Vivez-vous habituellement et de façon stable en France ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("stable_residence"))),
        )
        department = st.text_input(
            "Votre département",
            value=str(answers.get("department_code") or ""),
            placeholder="Exemple : 31",
        )
        nationality_label = st.selectbox(
            "Quelle est votre situation de nationalité ou de séjour ?",
            list(NATIONALITY.keys()),
            index=list(NATIONALITY.keys()).index(reverse_label(NATIONALITY, answers.get("nationality_status"), "Je ne sais pas")),
        )
        permit_label = st.selectbox(
            "Si vous êtes hors UE, avez-vous un titre de séjour en cours de validité ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("valid_residence_permit"))),
        )

        submitted = st.form_submit_button("Suivant", type="primary", use_container_width=True)
        if submitted:
            try:
                put("age", int(age))
                put("marital_status", MARITAL[marital_label])
                put("child_ages", parse_ages(child_ages_text))
                put("school_child_ages", parse_ages(school_ages_text))
                put("disabled_child_ages", parse_ages(disabled_ages_text))
                put("single_parent", TRI[single_parent_label])
                put("pregnancy", TRI[pregnancy_label])
                put("stable_residence", TRI[stable_label])
                put("department_code", department.strip() or None)
                put("nationality_status", NATIONALITY[nationality_label])
                put("valid_residence_permit", TRI[permit_label])
                go_to(2)
            except ValueError:
                st.error("Vérifiez les âges des enfants : utilisez uniquement des nombres séparés par des virgules.")

elif step == 2:
    st.header("2. Logement et ressources")
    with st.form("step_2"):
        housing_label = st.selectbox(
            "Quelle est votre situation de logement ?",
            list(HOUSING.keys()),
            index=list(HOUSING.keys()).index(reverse_label(HOUSING, answers.get("housing_status"), "Je ne sais pas")),
        )
        rent_text = st.text_input(
            "Loyer ou redevance mensuelle approximative",
            value="" if answers.get("monthly_rent") is None else str(answers.get("monthly_rent")),
            placeholder="Exemple : 650. Laissez vide si non concerné.",
        )
        rent_arrears_label = st.selectbox(
            "Avez-vous actuellement des loyers ou charges de logement impayés ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("rent_arrears"))),
        )
        energy_debt_label = st.selectbox(
            "Avez-vous actuellement une dette d'électricité, de gaz ou d'énergie ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("energy_debt"))),
        )
        resources_known_label = st.selectbox(
            "Connaissez-vous approximativement les ressources de votre foyer ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("resources_known"))),
        )
        annual_text = st.text_input(
            "Ressources annuelles approximatives du foyer",
            value="" if answers.get("annual_resources") is None else str(answers.get("annual_resources")),
            placeholder="Exemple : 12000",
        )
        monthly_text = st.text_input(
            "Ressources mensuelles actuelles du foyer",
            value="" if answers.get("monthly_resources") is None else str(answers.get("monthly_resources")),
            placeholder="Exemple : 1000",
        )
        rfr_text = st.text_input(
            "Revenu fiscal de référence, si vous le connaissez",
            value="" if answers.get("rfr") is None else str(answers.get("rfr")),
            placeholder="Laissez vide si vous ne savez pas",
        )

        c1, c2 = st.columns(2)
        back = c1.form_submit_button("Retour", use_container_width=True)
        next_ = c2.form_submit_button("Suivant", type="primary", use_container_width=True)

        if back:
            go_to(1)
        if next_:
            try:
                put("housing_status", HOUSING[housing_label])
                put("monthly_rent", parse_number(rent_text))
                put("rent_arrears", TRI[rent_arrears_label])
                put("energy_debt", TRI[energy_debt_label])
                put("resources_known", TRI[resources_known_label])
                put("annual_resources", parse_number(annual_text))
                put("monthly_resources", parse_number(monthly_text))
                put("rfr", parse_number(rfr_text))
                go_to(3)
            except ValueError:
                st.error("Vérifiez les montants : indiquez seulement des nombres, par exemple 650 ou 650,50.")

elif step == 3:
    st.header("3. Travail, santé et autres situations")
    with st.form("step_3"):
        employment_label = st.selectbox(
            "Quelle est votre situation professionnelle principale ?",
            list(EMPLOYMENT.keys()),
            index=list(EMPLOYMENT.keys()).index(reverse_label(EMPLOYMENT, answers.get("employment_status"), "Je ne sais pas")),
        )
        working_label = st.selectbox(
            "Travaillez-vous actuellement, même à temps partiel ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("working"))),
        )
        earned_text = st.text_input(
            "Revenu professionnel mensuel approximatif",
            value="" if answers.get("monthly_earned_income") is None else str(answers.get("monthly_earned_income")),
            placeholder="Laissez vide si non concerné",
        )
        gross_text = st.text_input(
            "Si vous êtes étudiant(e), revenu professionnel brut mensuel approximatif",
            value="" if answers.get("monthly_gross_earned_income") is None else str(answers.get("monthly_gross_earned_income")),
            placeholder="Laissez vide si non concerné",
        )
        hours_text = st.text_input(
            "Si vous avez moins de 25 ans, nombre approximatif d'heures travaillées sur les 3 dernières années",
            value="" if answers.get("hours_worked_last_3_years") is None else str(answers.get("hours_worked_last_3_years")),
            placeholder="Laissez vide si vous ne savez pas",
        )

        health_label = st.selectbox(
            "Avez-vous une maladie, un handicap ou des difficultés durables qui compliquent votre vie quotidienne ou votre autonomie ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("health_difficulty"))),
        )
        mobility_label = st.selectbox(
            "Avez-vous des difficultés importantes pour vous déplacer ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("mobility_difficulty"))),
        )
        daily_label = st.selectbox(
            "Avez-vous des difficultés importantes pour des actes de la vie quotidienne ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("daily_living_difficulty"))),
        )
        work_limit_label = st.selectbox(
            "Votre santé ou votre handicap limite-t-il votre capacité à travailler ou à conserver un emploi ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("work_limitation"))),
        )

        gir_choices = ["Je ne sais pas", "1", "2", "3", "4", "5", "6"]
        gir_default = "Je ne sais pas" if answers.get("gir_level") is None else str(answers.get("gir_level"))
        gir_label = st.selectbox("Si vous avez 60 ans ou plus, connaissez-vous votre GIR ?", gir_choices, index=gir_choices.index(gir_default))
        retired_label = st.selectbox(
            "Êtes-vous retraité(e) ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("is_retired"))),
        )
        all_pensions_label = st.selectbox(
            "Si vous êtes retraité(e), avez-vous liquidé toutes vos retraites possibles ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("all_pensions_liquidated"))),
        )
        inaptitude_label = st.selectbox(
            "Une inaptitude au travail pour la retraite vous a-t-elle été officiellement reconnue ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("retirement_inaptitude"))),
        )
        caregiver_label = st.selectbox(
            "Aidez-vous régulièrement un proche malade, handicapé ou en perte d'autonomie ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("caregiver"))),
        )
        unpaid_support_label = st.selectbox(
            "Une pension alimentaire destinée à un enfant est-elle impayée ou insuffisamment versée ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("unpaid_child_support"))),
        )
        legal_label = st.selectbox(
            "Avez-vous une procédure judiciaire en cours ou besoin d'en engager une ?",
            list(TRI.keys()),
            index=list(TRI.keys()).index(tri_label(answers.get("legal_proceeding"))),
        )

        c1, c2 = st.columns(2)
        back = c1.form_submit_button("Retour", use_container_width=True)
        analyse = c2.form_submit_button("Voir mes pistes", type="primary", use_container_width=True)

        if back:
            go_to(2)
        if analyse:
            try:
                put("employment_status", EMPLOYMENT[employment_label])
                put("working", TRI[working_label])
                put("monthly_earned_income", parse_number(earned_text))
                put("monthly_gross_earned_income", parse_number(gross_text))
                put("hours_worked_last_3_years", parse_number(hours_text))
                put("health_difficulty", TRI[health_label])
                put("mobility_difficulty", TRI[mobility_label])
                put("daily_living_difficulty", TRI[daily_label])
                put("work_limitation", TRI[work_limit_label])
                put("gir_level", None if gir_label == "Je ne sais pas" else int(gir_label))
                put("is_retired", TRI[retired_label])
                put("all_pensions_liquidated", TRI[all_pensions_label])
                put("retirement_inaptitude", TRI[inaptitude_label])
                put("caregiver", TRI[caregiver_label])
                put("unpaid_child_support", TRI[unpaid_support_label])
                put("legal_proceeding", TRI[legal_label])
                go_to(4)
            except ValueError:
                st.error("Vérifiez les montants et le nombre d'heures saisis.")

elif step == 4:
    st.header("4. Vos droits et démarches à explorer")
    try:
        profile = build_profile(answers)
        evaluation = RightsEngine().evaluate(profile)
    except Exception as exc:
        st.error("Le profil n'a pas pu être analysé. Revenez à l'étape précédente et vérifiez les réponses.")
        st.code(str(exc))
        if st.button("Retour au questionnaire"):
            go_to(3)
        st.stop()

    results = evaluation.get("results", [])
    active = [r for r in results if r.get("status") != "CONDITIONS_DECLAREES_INCOMPATIBLES"]
    incompatible = [r for r in results if r.get("status") == "CONDITIONS_DECLAREES_INCOMPATIBLES"]

    st.info(
        "Ce sont des pistes d'orientation, pas des décisions d'attribution. "
        "Les organismes compétents restent seuls habilités à décider."
    )

    if not active:
        st.write("Aucune piste n'a été produite avec les informations actuellement disponibles.")

    for result in active:
        status = result.get("status", "INFORMATION_INSUFFISANTE")
        label = STATUS_LABELS.get(status, status)
        with st.container(border=True):
            st.subheader(result.get("name", result.get("right_id", "Droit")))
            st.markdown(f"**Statut : {label}**")
            st.write(result.get("reason", "Aucune explication disponible."))

            missing = result.get("missing_information") or []
            if missing:
                st.markdown("**Informations à compléter :**")
                for item in missing:
                    st.write(f"- {item}")

            st.markdown("**Prochaine étape**")
            st.write(STATUS_ACTIONS.get(status, "Consulter la source officielle."))

            if result.get("human_evaluation_required"):
                st.warning("Une appréciation humaine ou administrative est nécessaire pour cette piste.")

            sources = result.get("sources") or []
            if sources:
                with st.expander("Voir les sources officielles"):
                    for i, source in enumerate(sources, start=1):
                        st.markdown(f"[Source officielle {i}]({source})")

    if incompatible:
        with st.expander("Pistes non compatibles avec les informations saisies"):
            for result in incompatible:
                st.markdown(f"**{result.get('name', result.get('right_id'))}**")
                st.write(result.get("reason", ""))

    st.caption(
        f"Moteur {evaluation.get('engine_version', '?')} · Référentiel {evaluation.get('rules_version', '?')} · "
        f"Vérifié le {evaluation.get('rules_verified_at', '?')}"
    )

    c1, c2 = st.columns(2)
    if c1.button("Modifier mes réponses", use_container_width=True):
        go_to(1)
    if c2.button("Recommencer", use_container_width=True):
        reset()
