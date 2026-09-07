# #TILT! — Prototype V0.1

Cette branche contient une version test indépendante de l'application #TILT!.

## Objectif
Tester une expérience très simple autour de trois usages :

1. noter rapidement son état du jour ;
2. relire son journal ;
3. accéder à quelques outils courts issus de la pair-aidance et de la réduction des risques.

## Lancer le prototype

```bash
python -m pip install streamlit
python -m streamlit run tilt_app.py
```

## Ce qui est inclus

- humeur sur 5 niveaux ;
- anxiété sur 10 ;
- tension / impulsivité sur 10 ;
- consommation du jour et type ;
- note courte ;
- journal des entrées de la session ;
- résumé simple sur 7 jours ;
- outils rapides ;
- numéros d'aide immédiate.

## Ce qui est volontairement exclu

- compte utilisateur ;
- stockage permanent ;
- synchronisation cloud ;
- communauté ;
- messagerie ;
- mentor pair-aidant ;
- espace professionnel ;
- diagnostic ou décision médicale automatisée.

## Données

Cette version garde les saisies uniquement en mémoire pendant la session Streamlit. Fermer ou réinitialiser la session efface les données.

Ne pas utiliser cette branche comme dossier médical ni y enregistrer de données sensibles réelles.

## Statut

Prototype d'usage, pas dispositif médical.
