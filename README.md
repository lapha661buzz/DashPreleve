# 💰 Plateforme de Suivi des Pertes de Revenu

Application Streamlit dynamique pour explorer les revenus non prélevés
à partir du fichier `data/Resultat.xlsx`.

## Fonctionnalités

- **Vue d'ensemble** : KPIs globaux, répartition par type de revenu, top agences et top clients.
- **Par Client** : sélectionnez un client → montant total à prélever, détail de ses contrats.
- **Par Agence (DAO)** : sélectionnez une agence → liste complète de ses clients et montants.
- **Par Type de revenu** : sélectionnez un type (Intérêt / Pénalité) → tous les clients concernés.
- **Données complètes** : table brute filtrable et exportable en CSV.
- Filtres globaux dans la barre latérale : Pays, Agence, Type de revenu, Période.
- Export CSV disponible à chaque niveau (client, agence, type, global).

## Installation

```bash
cd plateforme_pertes_revenu
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur (par défaut
sur http://localhost:8501).

## Mise à jour des données

Remplacez simplement le fichier `data/Resultat.xlsx` par votre nouveau
fichier (même structure de colonnes : Pays, ID Contrat, Numero de compte,
ID Client, DAO, Type de revenu, Solde du compte, Montant non prélevé,
Date d'identification), puis relancez l'application. Aucune modification
de code n'est nécessaire.

## Structure du projet

```
plateforme_pertes_revenu/
├── app.py                # Application Streamlit
├── requirements.txt      # Dépendances Python
├── README.md
└── data/
    └── Resultat.xlsx     # Données sources (Vu détail + Vu consolidé)
```
