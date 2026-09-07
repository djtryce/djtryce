# Méthodologie de vérification du référentiel

Date de référence : 7 septembre 2026.

## Principe

Le projet ne cherche pas à décider à la place d'une administration. Il détecte des droits potentiels, explique les raisons de la détection et oriente vers la démarche, la simulation ou l'évaluation humaine appropriée.

## Niveaux par règle

- **A** : règle vérifiée sur une source officielle primaire, déterministe et automatisable.
- **B** : règle vérifiée, mais calcul ou simulation externe nécessaire.
- **H** : règle vérifiée, mais appréciation humaine, médicale, sociale ou administrative nécessaire.
- **C** : information insuffisamment sécurisée. La règle reste hors moteur.

La notation porte sur chaque règle, pas sur le dispositif entier.

## Séparation obligatoire

Pour chaque droit, distinguer :

1. conditions d'ouverture ;
2. calcul du montant ;
3. décision administrative ;
4. date d'effet ;
5. versement ;
6. renouvellement ;
7. recours ;
8. rétroactivité, rappel, régularisation et révision.

## Provenance

Toute règle utilisée par le moteur doit conserver :

- source officielle ;
- champ justifié par la source ;
- date de vérification ;
- version de la règle ;
- niveau A/B/H/C ;
- commentaire d'audit si nécessaire.

## Sorties autorisées du moteur

Le moteur peut produire :

- `CONDITIONS_COMPATIBLES`
- `POTENTIEL`
- `A_SIMULER`
- `A_EXPLORER`
- `EVALUATION_HUMAINE_NECESSAIRE`
- `CONDITIONS_DECLAREES_INCOMPATIBLES`
- `INFORMATION_INSUFFISANTE`

Il ne doit pas produire `ELIGIBLE` pour une prestation nécessitant une décision ou une appréciation administrative.

## Règles documentaires

Les numéros Cerfa et liens de formulaires sont des données versionnées. Le système doit privilégier une page officielle permettant de récupérer la version courante plutôt que dépendre indéfiniment d'un numéro figé.

## Mise à jour

Une modification réglementaire crée une nouvelle version de la règle. L'ancienne version est conservée afin de pouvoir expliquer une décision ou une simulation effectuée à une date antérieure.

## Non-recours

Le moteur doit rechercher les droits auxquels la situation décrite justifie de s'intéresser, même si l'utilisateur ne connaît pas le nom du dispositif. Il ne doit jamais transformer cette détection en promesse d'attribution.
