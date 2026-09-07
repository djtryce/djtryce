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

Phase actuelle : audit et fiabilisation du référentiel MVP avant développement.

Le premier moteur doit couvrir environ 20 dispositifs prioritaires, avec un référentiel passif plus large à terme.

## Classification des règles

- **A** : règle vérifiée, déterministe et automatisable
- **B** : règle vérifiée mais nécessitant un calcul ou simulateur externe
- **H** : règle vérifiée mais nécessitant une appréciation humaine ou administrative
- **C** : information insuffisamment sécurisée

## Prochain jalon

Construire `droits_mvp_v1-audited` avec provenance de chaque règle, date de vérification, version, tests et séparation entre ouverture du droit, calcul, décision, versement, renouvellement et recours.
