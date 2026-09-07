# Roadmap MVP — Assistant d'accès aux droits

## Objectif
Construire un premier prototype capable de lire un profil utilisateur, d'appliquer uniquement des règles auditées et d'expliquer les droits à explorer sans jamais prétendre rendre une décision administrative.

## Étapes

- [ ] 1. Finir l'audit des 20 dispositifs du MVP
- [ ] 2. Compléter les sources officielles manquantes
- [ ] 3. Séparer clairement ouverture du droit / calcul / décision / recours / rétroactivité
- [ ] 4. Compléter `data/droits_mvp_v1-audited.yaml`
- [ ] 5. Compléter `tests/cas_mvp.yaml` avec au moins 20 profils fictifs
- [ ] 6. Définir le format standard d'un profil utilisateur
- [ ] 7. Créer le premier moteur de règles
- [ ] 8. Faire tourner automatiquement les cas de test
- [ ] 9. Produire une sortie lisible : potentiel / à simuler / à explorer / évaluation humaine nécessaire
- [ ] 10. Ajouter les explications et les sources à chaque résultat
- [ ] 11. Construire un questionnaire adaptatif simple
- [ ] 12. Tester le prototype avec des cas fictifs avant toute donnée réelle

## Règles non négociables

- Aucune règle déterminante sans source officielle primaire.
- Pas de statut `ELIGIBLE` lorsque l'administration ou un professionnel doit apprécier la situation.
- Les règles de niveau C restent hors moteur.
- Chaque résultat doit être explicable et sourcé.
- Aucun stockage de données personnelles réelles pendant les premiers tests.

## Définition du premier succès

Entrée : un profil fictif simple.

Sortie : une liste de droits ou démarches à explorer, avec :
- statut ;
- raison ;
- information manquante éventuelle ;
- source officielle ;
- prochaine action conseillée.

Exemple :

> PCH — À EXPLORER
> Vous décrivez des difficultés importantes dans plusieurs activités quotidiennes. Une évaluation MDPH est nécessaire. L'outil ne peut pas déterminer lui-même l'ouverture du droit.
