# Référentiel MVP — cadrage et audit

## Périmètre initial

Le moteur complet vise environ 20 dispositifs prioritaires : RSA, prime d’activité, APL, ALF, ALS, AAH, PCH, RQTH, CMI, Complémentaire santé solidaire, pension d’invalidité, ASPA, APA, FSL, chèque énergie, aide juridictionnelle, ASF, ARS, AEEH et AJPA.

## Règle de gouvernance

Aucune condition déterminante ne doit être utilisée par le moteur si elle repose uniquement sur une source secondaire ou une approximation.

Chaque règle doit porter :

- une source officielle ;
- une date de vérification ;
- un niveau A/B/H/C ;
- une distinction entre ouverture du droit, calcul, décision, versement, renouvellement et recours ;
- un historique de version.

## Points d’audit prioritaires

1. APL / ALF / ALS
2. Complémentaire santé solidaire
3. aide juridictionnelle
4. pension d’invalidité
5. APA
6. AJPA
7. RQTH
8. CMI
9. formulaires officiels
10. interactions entre droits
11. rétroactivité, rappel, régularisation, révision et prescription

## Classification des règles

- **A** : vérifiée, déterministe et automatisable
- **B** : vérifiée mais nécessite une simulation ou un calcul externe
- **H** : vérifiée mais nécessite une appréciation humaine ou administrative
- **C** : insuffisamment vérifiée

## Statuts possibles du moteur

- DROIT ACTIF
- POTENTIEL
- À SIMULER
- À EXPLORER
- ÉVALUATION HUMAINE NÉCESSAIRE
- PROBABLEMENT NON APPLICABLE
- INFORMATION INSUFFISANTE

Le moteur ne doit jamais présenter `POTENTIEL` comme synonyme d’`ÉLIGIBLE`.
