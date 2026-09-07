# Assistant universel d’accès aux droits

Projet de référentiel et moteur d’orientation pour aider les personnes en France à repérer des droits, aides et démarches qu’elles pourraient ignorer.

## Principes

- partir de la situation de vie, pas du nom des prestations ;
- ne jamais présenter une orientation comme une décision administrative ;
- privilégier les sources officielles primaires ;
- distinguer règles automatisables, simulations externes, appréciations humaines et informations insuffisamment vérifiées ;
- conserver la traçabilité et la date de vérification de chaque règle ;
- orienter vers un professionnel pour les cas complexes, urgents ou nécessitant une appréciation administrative.

## État du projet

Le MVP de démonstration fonctionne de bout en bout :

`questionnaire -> profile.json -> moteur de règles -> résultats expliqués et sourcés`

Le périmètre couvre environ 20 dispositifs prioritaires. Certaines règles restent volontairement en orientation, simulation externe ou évaluation humaine.

## Classification des règles

- **A** : règle vérifiée, déterministe et automatisable
- **B** : règle vérifiée mais nécessitant un calcul ou simulateur externe
- **H** : règle vérifiée mais nécessitant une appréciation humaine ou administrative
- **C** : information insuffisamment sécurisée

## Lancer la démonstration fictive

Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

Puis lancer le scénario fictif fourni dans le dépôt :

```bash
python -m src.demo --answers examples/demo_answers.yaml
```

Le programme affiche une orientation lisible avec le statut, la raison, les informations éventuellement manquantes, la prochaine étape et les sources officielles.

## Lancer le questionnaire interactif local

```bash
python -m src.demo
```

Le prototype interactif garde les réponses uniquement en mémoire pendant l’exécution. Il ne les enregistre pas dans le dépôt.

## Tests

```bash
python -m pytest -q
```

GitHub Actions exécute également les tests automatiquement à chaque modification.

## Données personnelles

Ce dépôt est public. Ne jamais y ajouter de profil réel, nom, adresse, numéro de sécurité sociale, numéro allocataire, document médical, avis d’imposition ou autre donnée personnelle.

Les fichiers présents dans `examples/` et `tests/` doivent rester entièrement fictifs.

## Prochaine étape

Construire une première interface web locale qui réutilise exactement le même questionnaire, le même schéma de profil, le même moteur et le même rendu de résultats, sans dupliquer les règles administratives dans l’interface.
