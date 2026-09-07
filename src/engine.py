from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES = ROOT / "data" / "droits_mvp_v1-audited.yaml"


class RightsEngine:
    """Moteur déterministe d'orientation, jamais moteur de décision administrative."""

    def __init__(self, rules_path: Path = DEFAULT_RULES) -> None:
        with rules_path.open("r", encoding="utf-8") as f:
            self.dataset = yaml.safe_load(f)
        self.rights = self.dataset.get("rights", {})

    def evaluate(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        evaluators = (
            self._evaluate_css,
            self._evaluate_rsa,
            self._evaluate_prime_activite,
            self._evaluate_housing,
            self._evaluate_pch,
            self._evaluate_rqth,
            self._evaluate_cmi,
            self._evaluate_aah,
            self._evaluate_aeeh,
            self._evaluate_ars,
            self._evaluate_asf,
            self._evaluate_apa,
            self._evaluate_aspa,
            self._evaluate_invalidity,
            self._evaluate_legal_aid,
            self._evaluate_ajpa,
            self._evaluate_cheque_energie,
            self._evaluate_fsl,
        )
        results = [r for fn in evaluators if (r := fn(profile))]
        return {
            "engine_version": "0.4.0",
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
        human_required: bool | None = None,
    ) -> Dict[str, Any]:
        right = self.rights[right_id]
        if human_required is None:
            human_required = bool(right.get("human_evaluation_required", False))
        return {
            "right_id": right_id,
            "name": right.get("name"),
            "status": status,
            "reason": reason,
            "missing_information": missing or [],
            "sources": right.get("sources", []),
            "human_evaluation_required": human_required,
        }

    def _evaluate_css(self, p):
        if "css" not in self.rights:
            return None
        size = p["household"].get("household_size")
        annual = p["income"].get("annual_household_resources")
        area = p["residence"].get("metropolitan_or_overseas")
        if size != 1 or area != "metropolitan_france":
            return self._result("css", "INFORMATION_INSUFFISANTE", "Le prototype ne contient pour l'instant qu'un barème automatisé sécurisé pour une personne seule en métropole.")
        if annual is None:
            return self._result("css", "INFORMATION_INSUFFISANTE", "Les ressources annuelles nécessaires ne sont pas connues.", ["income.annual_household_resources"])
        t = self.rights["css"]["rules"]["metropolitan_thresholds_one_person"]
        if annual <= t["free_annual"]:
            return self._result("css", "POTENTIEL", "Les ressources déclarées sont sous le plafond gratuit enregistré. La caisse reste seule compétente pour attribuer le droit.")
        if annual <= t["contribution_annual"]:
            return self._result("css", "POTENTIEL_AVEC_PARTICIPATION", "Les ressources déclarées se situent entre les deux plafonds enregistrés.")
        return self._result("css", "CONDITIONS_DECLAREES_INCOMPATIBLES", "Les ressources déclarées dépassent le plafond enregistré pour ce cas de figure.")

    def _evaluate_rsa(self, p):
        if "rsa" not in self.rights:
            return None
        age = p["person"].get("age")
        stable = p["residence"].get("stable_residence")
        if age is None:
            return self._result("rsa", "INFORMATION_INSUFFISANTE", "L'âge est nécessaire avant d'orienter vers le RSA.", ["person.age"])
        if age < 18:
            return self._result("rsa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "L'âge déclaré est inférieur à 18 ans.")
        if stable is False:
            return self._result("rsa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "La résidence stable en France n'est pas déclarée.")
        if stable is None:
            return self._result("rsa", "INFORMATION_INSUFFISANTE", "La résidence stable en France doit être précisée.", ["residence.stable_residence"])
        if age < 25:
            parent = bool(p["household"].get("dependent_children_count", 0)) or bool(p["household"].get("pregnancy"))
            hours = p["employment"].get("hours_worked_last_3_years")
            if parent:
                return self._result("rsa", "A_SIMULER", "Une exception liée à la parentalité ou à la grossesse peut s'appliquer. Une simulation officielle est nécessaire.")
            if hours is not None and hours >= self.rights["rsa"]["rules"]["young_active_hours_last_3_years"]:
                return self._result("rsa", "A_SIMULER", "Le volume de travail déclaré atteint le seuil jeune actif enregistré. Les autres conditions restent à vérifier.")
            return self._result("rsa", "A_SIMULER", "Entre 18 et 24 ans, des conditions particulières s'appliquent. Une simulation officielle reste nécessaire.", [] if hours is not None else ["employment.hours_worked_last_3_years"])
        return self._result("rsa", "A_SIMULER", "L'âge et la résidence permettent d'orienter vers une simulation RSA. Le montant dépend du foyer et des ressources.")

    def _evaluate_prime_activite(self, p):
        if "prime_activite" not in self.rights:
            return None
        e, person = p["employment"], p["person"]
        active = e.get("working") is True or e.get("partial_or_technical_unemployment") is True or e.get("status") in {"employee", "self_employed"} or person.get("is_student") is True
        if not active:
            return None
        age, stable = person.get("age"), p["residence"].get("stable_residence")
        if age is None:
            return self._result("prime_activite", "INFORMATION_INSUFFISANTE", "L'âge est nécessaire.", ["person.age"])
        if age < 18:
            return self._result("prime_activite", "CONDITIONS_DECLAREES_INCOMPATIBLES", "La prime d'activité est ouverte à partir de 18 ans.")
        if stable is False:
            return self._result("prime_activite", "CONDITIONS_DECLAREES_INCOMPATIBLES", "La résidence stable en France n'est pas déclarée.")
        if stable is None:
            return self._result("prime_activite", "INFORMATION_INSUFFISANTE", "La résidence stable en France doit être précisée.", ["residence.stable_residence"])
        if person.get("is_student") is True or e.get("status") == "student":
            gross = e.get("monthly_gross_earned_income")
            return self._result("prime_activite", "A_SIMULER", "Une activité étudiante est déclarée. Une règle de revenu spécifique s'applique et la simulation CAF doit vérifier la situation.", [] if gross is not None else ["employment.monthly_gross_earned_income"])
        return self._result("prime_activite", "A_SIMULER", "Une activité professionnelle est déclarée. Une simulation CAF est nécessaire pour le calcul.")

    def _evaluate_housing(self, p):
        if "apl_alf_als" not in self.rights:
            return None
        status = p["housing"].get("status")
        if status in {"tenant", "social_residence"}:
            return self._result("apl_alf_als", "A_SIMULER", "La situation de logement justifie une simulation officielle. Le montant n'est pas calculé par ce moteur.")
        if status is None or status == "unknown":
            return self._result("apl_alf_als", "INFORMATION_INSUFFISANTE", "Le statut d'occupation du logement est inconnu.", ["housing.status"])
        return None

    def _evaluate_pch(self, p):
        if "pch" in self.rights and p["health_disability"].get("health_or_disability_difficulty"):
            return self._result("pch", "A_EXPLORER", "Des difficultés liées au handicap ou à la santé sont déclarées. Une évaluation MDPH/CDAPH est nécessaire.")
        return None

    def _evaluate_rqth(self, p):
        if "rqth" in self.rights and p["employment"].get("work_limitation_due_to_health_or_disability"):
            return self._result("rqth", "EVALUATION_HUMAINE_NECESSAIRE", "Une limitation de travail liée à la santé ou au handicap est déclarée. La décision relève de la MDPH/CDAPH.")
        return None

    def _evaluate_cmi(self, p):
        if "cmi" in self.rights and p["health_disability"].get("mobility_difficulty"):
            return self._result("cmi", "EVALUATION_HUMAINE_NECESSAIRE", "Une difficulté de mobilité est déclarée. La mention de CMI applicable ne peut pas être déterminée automatiquement.")
        return None

    def _evaluate_aah(self, p):
        if "aah" not in self.rights:
            return None
        age = p["person"].get("age")
        difficulty = p["health_disability"].get("health_or_disability_difficulty")
        if age is None:
            return self._result("aah", "INFORMATION_INSUFFISANTE", "L'âge est nécessaire pour l'orientation AAH.", ["person.age"])
        if age < 16:
            return self._result("aah", "CONDITIONS_DECLAREES_INCOMPATIBLES", "L'âge déclaré est inférieur au seuil minimal enregistré.")
        if difficulty:
            return self._result("aah", "EVALUATION_HUMAINE_NECESSAIRE", "Une situation de handicap est déclarée. L'évaluation du taux d'incapacité et, selon le cas, de la restriction d'accès à l'emploi relève de la MDPH/CDAPH.")
        return None

    def _evaluate_aeeh(self, p):
        if "aeeh" not in self.rights:
            return None
        for child in p.get("family", {}).get("children", []) or []:
            if child.get("disability_or_health_difficulty") and child.get("age") is not None and child["age"] < 20:
                return self._result("aeeh", "EVALUATION_HUMAINE_NECESSAIRE", "Un enfant de moins de 20 ans avec une difficulté de santé ou un handicap est déclaré. Une évaluation administrative est nécessaire.")
        return None

    def _evaluate_ars(self, p):
        if "ars" not in self.rights:
            return None
        for child in p.get("family", {}).get("children", []) or []:
            age, school = child.get("age"), child.get("in_school")
            if age is None:
                continue
            if 6 <= age <= 18 and school is not False:
                return self._result("ars", "A_SIMULER", "Un enfant d'âge compatible avec l'ARS est déclaré scolarisé ou sa scolarité n'est pas exclue. Les ressources de l'année de référence doivent être vérifiées.")
            if age < 6 and school is True:
                return self._result("ars", "A_EXPLORER", "Un enfant de moins de 6 ans est déclaré scolarisé. L'exception liée à une entrée anticipée en CP doit être vérifiée.")
        return None

    def _evaluate_asf(self, p):
        if "asf" not in self.rights:
            return None
        h, family = p["household"], p["family"]
        has_child = (h.get("dependent_children_count") or 0) > 0 or bool(family.get("children"))
        if h.get("single_parent") is True and (has_child or family.get("unpaid_child_support") is True):
            return self._result("asf", "A_EXPLORER", "Un parent seul avec enfant ou une pension alimentaire impayée est déclaré. L'ASF peut notamment concerner l'absence, le faible montant ou le non-paiement d'une pension, selon la situation.")
        return None

    def _evaluate_apa(self, p):
        if "apa" not in self.rights:
            return None
        age, gir = p["person"].get("age"), p["health_disability"].get("gir_level")
        if age is None:
            return self._result("apa", "INFORMATION_INSUFFISANTE", "L'âge est inconnu.", ["person.age"])
        if age < 60:
            return self._result("apa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "L'âge déclaré est inférieur au seuil enregistré pour l'APA.")
        if gir is None:
            return self._result("apa", "EVALUATION_HUMAINE_NECESSAIRE", "L'âge est compatible mais le GIR doit être évalué ou renseigné.", ["health_disability.gir_level"])
        if gir <= 4:
            return self._result("apa", "EVALUATION_HUMAINE_NECESSAIRE", "L'âge et le GIR déclarés sont compatibles avec les critères généraux, mais l'attribution reste administrative.")
        return self._result("apa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "Le GIR déclaré est hors des niveaux 1 à 4 enregistrés pour l'ouverture de l'APA.")

    def _evaluate_aspa(self, p):
        if "aspa" not in self.rights:
            return None
        person = p["person"]
        age, retired = person.get("age"), person.get("is_retired")
        if age is None:
            return self._result("aspa", "INFORMATION_INSUFFISANTE", "L'âge est nécessaire pour l'orientation ASPA.", ["person.age"]) if retired is True else None
        if age < 62:
            return self._result("aspa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "L'âge déclaré est inférieur au seuil minimal enregistré pour l'ASPA.") if retired is True else None
        if retired is False:
            return self._result("aspa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "Le profil indique que la personne n'est pas retraitée.")
        if retired is None:
            return self._result("aspa", "INFORMATION_INSUFFISANTE", "Il faut savoir si la personne est retraitée.", ["person.is_retired"])
        if age < 65:
            inaptitude = person.get("retirement_inaptitude_recognized")
            incapacity = person.get("permanent_incapacity_percent")
            if inaptitude is not True and (incapacity is None or incapacity < 50):
                if inaptitude is False and incapacity is not None:
                    return self._result("aspa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "Entre 62 et 64 ans, le profil ne remplit pas la condition anticipée enregistrée.")
                return self._result("aspa", "EVALUATION_HUMAINE_NECESSAIRE", "Entre 62 et 64 ans, l'ouverture anticipée dépend notamment d'une inaptitude reconnue ou d'une incapacité permanente d'au moins 50 %.", ["person.retirement_inaptitude_recognized", "person.permanent_incapacity_percent"], True)
        pensions = person.get("all_retirement_pensions_liquidated")
        if pensions is False:
            return self._result("aspa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "Toutes les retraites doivent avoir été demandées ou liquidées avant l'ASPA.")
        if pensions is None:
            return self._result("aspa", "INFORMATION_INSUFFISANTE", "Il faut vérifier que toutes les retraites ont été liquidées.", ["person.all_retirement_pensions_liquidated"])
        stable = p["residence"].get("stable_residence")
        if stable is False:
            return self._result("aspa", "CONDITIONS_DECLAREES_INCOMPATIBLES", "La résidence en France n'est pas déclarée comme stable.")
        if stable is None:
            return self._result("aspa", "INFORMATION_INSUFFISANTE", "La résidence en France doit être précisée.", ["residence.stable_residence"])
        return self._result("aspa", "A_SIMULER", "L'âge, la retraite et la résidence permettent d'explorer l'ASPA. Les ressources doivent être examinées selon les règles officielles.", human_required=False)

    def _evaluate_invalidity(self, p):
        if "pension_invalidite" not in self.rights or not p["health_disability"].get("health_or_disability_difficulty"):
            return None
        assessed = p["health_disability"].get("medical_capacity_loss_two_thirds_assessed")
        if assessed is not True:
            return self._result("pension_invalidite", "EVALUATION_HUMAINE_NECESSAIRE", "La réduction de capacité doit être appréciée par le médecin-conseil.", ["health_disability.medical_capacity_loss_two_thirds_assessed"])
        return self._result("pension_invalidite", "A_EXPLORER", "Une réduction de capacité des deux tiers est déclarée comme déjà évaluée. Les autres conditions administratives doivent encore être vérifiées.")

    def _evaluate_legal_aid(self, p):
        if "aide_juridictionnelle" not in self.rights or not p["legal_admin"].get("legal_proceeding"):
            return None
        if p["household"].get("household_size") != 1:
            return self._result("aide_juridictionnelle", "A_SIMULER", "Une procédure est déclarée, mais le prototype ne contient pas encore tous les plafonds par composition de foyer.")
        if p["income"].get("reference_tax_income") is None:
            return self._result("aide_juridictionnelle", "INFORMATION_INSUFFISANTE", "Le revenu fiscal de référence est manquant.", ["income.reference_tax_income"])
        return self._result("aide_juridictionnelle", "A_SIMULER", "Une procédure est déclarée. Revenu et patrimoine doivent être examinés ensemble.")

    def _evaluate_ajpa(self, p):
        if "ajpa" in self.rights and p["family"].get("caregiver_for_relative"):
            return self._result("ajpa", "A_EXPLORER", "La personne déclare aider un proche. Les conditions d'ouverture doivent être vérifiées.")
        return None

    def _evaluate_cheque_energie(self, p):
        if "cheque_energie" not in self.rights:
            return None
        rfr = p["income"].get("reference_tax_income")
        size = p["household"].get("household_size")
        if rfr is None or size is None or size < 1:
            return None
        uc = 1.0
        if size >= 2:
            uc += 0.5
        if size >= 3:
            uc += 0.3 * (size - 2)
        ratio = rfr / uc
        threshold = self.rights["cheque_energie"]["rules"]["rfr_per_uc_max_exclusive"]
        if ratio < threshold:
            return self._result("cheque_energie", "A_SIMULER", "Le RFR/UC estimé à partir du profil est sous le seuil enregistré. Le simulateur officiel reste prioritaire car le foyer fiscal et le logement doivent être correctement appariés.")
        return None

    def _evaluate_fsl(self, p):
        if "fsl" not in self.rights:
            return None
        housing = p.get("housing", {})
        if housing.get("rent_arrears") or housing.get("energy_debt"):
            return self._result("fsl", "A_EXPLORER", "Une dette de loyer ou d'énergie est déclarée. Le FSL doit être exploré selon le règlement départemental.")
        return None


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Prototype de moteur d'orientation vers les droits")
    parser.add_argument("profile", type=Path, help="Chemin vers un profil JSON")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    args = parser.parse_args()
    with args.profile.open("r", encoding="utf-8") as f:
        profile = json.load(f)
    print(json.dumps(RightsEngine(args.rules).evaluate(profile), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
