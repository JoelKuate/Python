# Formation Complète Beobank

Support de formation Python (NumPy/Pandas) et SQL, bâti sur un dataset bancaire fictif "Beobank" (5 tables relationnelles). Formation de 3 jours, du plus simple au plus complexe : Jour 1 fondamentaux Python, Jour 2 structures de données / NumPy / Pandas, Jour 3 SQL et Vertica — sur les mêmes questions métier pour comparaison directe.


## Structure du dépôt — 3 jours progressifs

```
data/                                              CSV source partagés (CTR, TIE, TIE_ADR, TIE_X_CTR, TXN_X_CTR)

Jour_1_Fondamentaux_Python/
  01_Presentation_Dataset_Beobank/                 Dataset_Beobank (les 5 tables, relations, conventions)
  02_Bases_Python/                                 Jour1_Formateur + Jour1_Participants (modules 1 à 13)
  03_SAS_vs_Python/                                Aide-mémoire comparatif SAS ↔ Python

Jour_2_Structures_NumPy_Pandas/
  01_Listes_Dictionnaires_Tuples/                  Cours_Listes_Dicts_Tuples + Jour2_Participants
  02_NumPy/                                        Cours_NumPy
  03_Pandas_Initiation_Simple/                     Pandas expliqué simplement, dates & merge, XOR
  04_Pandas_Cours_Complet/                         Cours_Pandas (théorie + exercices + corrections)
  05_Pandas_Pratique_Formateur/                    Jour2_Formateur (groupby, merge, export SQLite...)
  06_Pandas_Cas_Pratiques_Beobank/                 Pandas A à Z, cahier participants, corrigé, mises en situation

Jour_3_SQL_et_Vertica/
  01_SQL_Fondamentaux/                             Cours_SQL, cahier participants, corrigé, mises en situation
  02_SQL_Analytique_Visualisation/                 Jour3_Formateur + Jour3_Participants (CTE, fenêtres, dates, Matplotlib)
  03_SQL_Vertica_Natif/                            Cahier participants, corrigé, mises en situation Vertica
```

Ordre : suivre les jours puis les chapitres dans l'ordre numérique.

**Cahiers à trous par chapitre.** Chaque chapitre contient un cahier participant à compléter
(trous `______`, minimum 20) construit sur un scénario métier Beobank, et son corrigé formateur :
- `Scenario_Exercices_Participants.ipynb` / `Scenario_Corrige_Formateur.ipynb` dans les chapitres
  de cours ;
- `Cahier_Exercices_Participants*.ipynb` / `Cahier_Corrige_Formateur*.ipynb` dans
  `06_Pandas_Cas_Pratiques_Beobank`, `01_SQL_Fondamentaux` et `03_SQL_Vertica_Natif`.

Ne pas distribuer les corrigés aux participants avant la correction collective.

Les notebooks lisent les données via `../../data/`.

## Dataset Beobank

5 tables CSV dans `data/` :
- `CTR` — contrats
- `TIE` — tiers (clients)
- `TIE_ADR` — adresses des tiers
- `TIE_X_CTR` — lien tiers/contrats
- `TXN_X_CTR` — transactions par contrat

## Prérequis

- Python 3.x, Jupyter Notebook/Lab
- pandas, numpy

## Utilisation

Ouvrir les notebooks (`.ipynb`) dans l'ordre du déroulé pédagogique. Chaque module cours a son cahier d'exercices participants et son corrigé formateur associé.

## Contacter Joel
[LinkedIn — Joel Parfait Kuate](https://www.linkedin.com/in/joelparfaitkuate/) 


## Vérifier que tout fonctionne

```
pip install pytest nbclient nbformat ipykernel
python -m pytest tests -v
```

Les tests vérifient le chargement des 5 CSV, l'existence de tous les chemins cités dans les notebooks, et exécutent chaque notebook dans une copie temporaire (les originaux ne sont pas modifiés). Les notebooks Vertica sont ignorés si aucun serveur Vertica n'est joignable.
