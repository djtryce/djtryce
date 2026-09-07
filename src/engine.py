from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES = ROOT / "data" / "droits_mvp_v1-audited.yaml"


class RightsEngine:
    """Prototype déterministe du moteur d'orientation.

    Important : ce moteur ne rend jamais de décision administrative. Il ne
    produit que des statuts d'orientation à partir de règles explicitement
    présentes dans le référentiel audité.
    """

    def __init__(self, rules_path: Path = DEFAULT_RULES) -> None:
        with rules_path.open("r", encoding="utf-8") as f:
            self.dataset = yaml.safe_load(f)
        self.rights = self.dataset.get("rights", {})

    def evaluate(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []

        for evaluator in (
            self._evaluate_css,
            self._evaluate_housing,
            self._evaluate_pch,
            self._evaluate_rqth,
            self._evaluate_cmi,
            self._evaluate_aah,
            self._evaluate_aeeh,
            self._evaluate_apa,
            self._evaluate_invalidity,
            self._evaluate_legal_aid,
            self._evaluate_ajpa,
            self._evaluate_fsl,
        ):
            result = evaluator(profile)
            if result:
                results.append(result)

        return {
            "engine_version": "0.2.0",
            "rules_version": self.dataset.get("version"),
            "rules_verified_at": self.dataset.get("verified_at"),
            "profile_id": profile.get("profile_id"),
            "results": results,
        }

    def _result(
        self,
        right_id: str,
        status: str,
        reason: str,
        missing: List[str] | None = None,
    ) -> Dict[str, Any]:
        right = self.rights[right_id]
        return {
            "right_id": right_id,
            "name": right.get("name"),
            "status": status,
            "reason": reason,
            "missing_information": missing or [],
            "sources": right.get("sources", []),
            "human_evaluation_required": bool(right.get("human_evaluation_required", False)),
        }

    def _evaluate_css(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        right = self.rights.get("css")
        if not right:
            return None
        household_size = p["household"].get("household_size")
        annual = p["income"].get("annual_household_resources")
        area = p["residence"].get("metropolitan_or_overseas")
        if household_size != 1 or area != "metropolitan_france":
            return self._result("css", "INFORMATION_INSUFFISANTE", "Le référentiel actuel du prototype ne contient qu'un barème sécurisé pour une personne seule en métropole.")
        if annual is None:
            return self._result("css", "INFORMATION_INSUFFISANTE", "Les ressources annuelles nécessaires à l'évaluation ne sont pas connues.", ["income.annual_household_resources"])
        thresholds = right["rules"]["metropolitan_thresholds_one_person"]
        if annual <= thresholds["free_annual"]:
            return self._result("css", "POTENTIEL", "Les ressources déclarées sont sous le plafond gratuit enregistré dans le référentiel audité. La caisse reste seule compétente pour attribuer le droit.")
        if annual <= thresholds["contribution_annual"]:
            return self._result("css", "POTENTIEL_AVEC_PARTICIPATION", "Les ressources déclarées se situent entre les deux plafonds enregistrés dans le référentiel audité.")
        return self._result("css", "CONDITIONS_DECLAREES_INCOMPATIBLES", "Les ressources déclarées dépassent le plafond actuellement enregistré pour une personne seule en métropole.")

    def _evaluate_housing(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "apl_alf_als" not in self.rights:
            return None
        status = p["housing"].get("status")
        if status in {"tenant", "social_residence"}:
            return self._result("apl_alf_als", "A_SIMULER", "La situation de logement déclarée justifie une simulation officielle. Le montant n'est pas calculé par ce prototype.")
        if status is None or status == "unknown":
            return self._result("apl_alf_als", "INFORMATION_INSUFFISANTE", "Le statut d'occupation du logement est inconnu.", ["housing.status"])
        return None

    def _evaluate_pch(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "pch" not in self.rights:
            return None
        if p["health_disability"].get("health_or_disability_difficulty"):
            return self._result("pch", "A_EXPLORER", "Des difficultés liées au handicap ou à la santé sont déclarées. L'ouverture de la PCH nécessite une évaluation MDPH/CDAPH.")
        return None

    def _evaluate_rqth(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "rqth" not in self.rights:
            return None
        if p["employment"].get("work_limitation_due_to_health_or_disability"):
            return self._result("rqth", "EVALUATION_HUMAINE_NECESSAIRE", "Une limitation de travail liée à la santé ou au handicap est déclarée. La décision relève de la MDPH/CDAPH.")
        return None

    def _evaluate_cmi(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "cmi" not in self.rights:
            return None
        if p["health_disability"].get("mobility_difficulty"):
            return self._result("cmi", "EVALUATION_HUMAINE_NECESSAIRE", "Une difficulté de mobilité est déclarée. La mention de CMI applicable ne peut pas être déterminée automatiquement.")
        return None

    def _evaluate_aah(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "aah" not in self.rights:
            return None
        age = p["person"].get("age")
        difficulty = p["health_disability"].get("health_or_disability_difficulty")
        if age is None:
            return self._result("aah", "INFORMATION_INSUFFISANTE", "L'âge est nécessaire pour l'orientation AAH.", ["person.age"])
        if age < 16:
            return self._result("aah", "CONDITIONS_DECLAREES_INCOMPATIBLES", "L'âge déclaré est inférieur au seuil minimal prévu pour une demande d'AAH.")
        if difficulty:
            return self._result("aah", "EVALUATION_HUMAINE_NECESSAIRE", "Une situation de handicap est déclarée. Le taux d'incapacité et, selon le cas, la restriction d'accès à l'emploi doivent être évalués par la MDPH/CDAPH, puis les conditions administratives et de ressources vérifiées.")
        return None

    def _evaluate_aeeh(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "aeeh" not in self.rights:
            return None
        children = p.get("family", {}).get("children", []) or []
        for child in children:
            age = child.get("age")
            difficulty = child.get("disability_or_health_difficulty")
            if difficulty and age is not None and age < 20:
                return self._result("aeeh", "EVALUATION_HUMAINE_NECESSAIRE", "Un enfant de moins de 20 ans avec une difficulté de santé ou un handicap est déclaré. L'ouverture de l'AEEH nécessite une évaluation du handicap et une décision administrative.")
        return None

    def _evaluate_apa(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "apa" not in self.rights:
            return None
        age = p["person"].get("age")
        gir = p["health_disability"].get("gir_level")
        if age is None:
            return self._result("apa", "INFORMATION_INSUFFISANTE", "L'âge est inconnu.", ["person.age"])
        if age < 60:
            return self._result("apa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "L'âge déclaré est inférieur au seuil d'âge enregistré pour l'APA.")
        if gir is None:
            return self._result("apa", "EVALUATION_HUMAINE_NECESSAIRE", "L'âge est compatible mais le niveau GIR doit être évalué ou renseigné.", ["health_disability.gir_level"])
        if gir <= 4:
            return self._result("apa", "EVALUATION_HUMAINE_NECESSAIRE", "L'âge et le GIR déclarés sont compatibles avec les critères généraux enregistrés, mais l'attribution reste une décision administrative.")
        return self._result("apa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "Le GIR déclaré est hors des niveaux 1 à 4 enregistrés pour l'ouverture de l'APA.")

    def _evaluate_invalidity(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "pension_invalidite" not in self.rights:
            return None
        h = p["health_disability"]
        if not h.get("health_or_disability_difficulty"):
            return None
        assessed = h.get("medical_capacity_loss_two_thirds_assessed")
        if assessed is not True:
            return self._result("pension_invalidite", "EVALUATION_HUMAINE_NECESSAIRE", "Une difficulté de santé est déclarée, mais la réduction de capacité doit être appréciée par le médecin-conseil.", ["health_disability.medical_capacity_loss_two_thirds_assessed"])
        return self._result("pension_invalidite", "A_EXPLORER", "Une réduction de capacité des deux tiers est déclarée comme déjà évaluée. Les autres conditions administratives doivent encore être vérifiées.")

    def _evaluate_legal_aid(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "aide_juridictionnelle" not in self.rights:
            return None
        if not p["legal_admin"].get("legal_proceeding"):
            return None
        if p["household"].get("household_size") != 1:
            return self._result("aide_juridictionnelle", "A_SIMULER", "Une procédure est déclarée, mais le prototype ne contient pas encore les plafonds sécurisés de toutes les compositions de foyer.")
        rfr = p["income"].get("reference_tax_income")
        if rfr is None:
            return self._result("aide_juridictionnelle", "INFORMATION_INSUFFISANTE", "Le revenu fiscal de référence est manquant.", ["income.reference_tax_income"])
        return self._result("aide_juridictionnelle", "A_SIMULER", "Une procédure est déclarée. Le revenu et le patrimoine doivent être examinés ensemble avant toute conclusion.")

    def _evaluate_ajpa(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "ajpa" not in self.rights:
            return None
        if p["family"].get("caregiver_for_relative"):
            return self._result("ajpa", "A_EXPLORER", "La personne déclare aider un proche. Les conditions d'ouverture doivent être vérifiées avant toute conclusion.")
        return None

    def _evaluate_fsl(self, p: Dict[str, Any]) -> Dict[str, Any] | None:
        if "fsl" not in self.rights:
            return None
        housing = p.get("housing", {})
        if housing.get("rent_arrears") or housing.get("energy_debt"):
            return self._result("fsl", "A_EXPLORER", "Une dette de loyer ou d'énergie est déclarée. Le FSL doit être exploré, mais ses conditions et montants dépendent du règlement départemental.")
        return None


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Prototype de moteur d'orientation vers les droits")
    parser.add_argument("profile", type=Path, help="Chemin vers un profil JSON")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    args = parser.parse_args()
    with args.profile.open("r", encoding="utf-8") as f:
        profile = json.load(f)
    result = RightsEngine(args.rules).evaluate(profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
