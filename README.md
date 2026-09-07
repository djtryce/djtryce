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

Une première interface web locale est maintenant disponible dans `app.py`.

Le périmètre couvre environ 20 dispositifs prioritaires. Certaines règles restent volontairement en orientation, simulation externe ou évaluation humaine.

## Classification des règles

- **A** : règle vérifiée, déterministe et automatisable
- **B** : règle vérifiée mais nécessitant un calcul ou simulateur externe
- **H** : règle vérifiée mais nécessitant une appréciation humaine ou administrative
- **C** : information insuffisamment sécurisée

## Lancer l'interface web

Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

Puis lancer :

```bash
python -m streamlit run app.py
```

Une page web s'ouvre avec 4 étapes :

1. foyer et résidence ;
2. logement et ressources ;
3. travail, santé et autres situations ;
4. droits et démarches à explorer.

Les réponses du questionnaire web sont utilisées uniquement en mémoire par l'application. Elles ne sont pas enregistrées dans le dépôt GitHub.

## Lancer la démonstration fictive dans le terminal

```bash
python -m src.demo --answers examples/demo_answers.yaml
```

## Lancer l'ancien questionnaire interactif dans le terminal

```bash
python -m src.demo
```

## Tests

```bash
python -m pytest -q
```

GitHub Actions vérifie également automatiquement la syntaxe de `app.py` et lance les tests à chaque modification.

## Données personnelles

Ce dépôt est public. Ne jamais y ajouter de profil réel, nom, adresse, numéro de sécurité sociale, numéro allocataire, document médical, avis d’imposition ou autre donnée personnelle.

Les fichiers présents dans `examples/` et `tests/` doivent rester entièrement fictifs.

L'interface web marque les profils saisis comme éphémères : ils restent en mémoire pour produire le résultat et ne sont pas écrits dans GitHub.

## Prochaine étape

Tester l'interface avec des profils fictifs, corriger l'expérience utilisateur, puis préparer un environnement privé et sécurisé avant tout essai avec de vraies situations personnelles.
