# 💰 Plateforme de Suivi des Pertes de Revenu

Application Streamlit dynamique pour explorer les revenus non prélevés
à partir du fichier `data/Resultat.xlsx`.

## Fonctionnalités

- **Vue d'ensemble** : KPIs globaux, répartition par type de revenu, top agences et top clients.
- **Par Client** : sélectionnez un client → montant total à prélever, détail de ses contrats.
- **Par Agence** : sélectionnez une agence → liste complète de ses clients et montants.
- **Par Type de revenu** : sélectionnez un type (Intérêt / Pénalité) → tous les clients concernés.
- **Données complètes** : table brute filtrable et exportable en CSV.
- **Régularisation client** : dans l'onglet Client, le bouton « ✓ Marquer régularisé » retire le
  client de la liste après confirmation. La liste des clients régularisés est consultable et
  réversible depuis la barre latérale. ⚠️ Cet état est conservé uniquement le temps de la session
  (il est réinitialisé si l'application est redémarrée) — il n'écrit rien dans le fichier Excel.
- Filtres globaux dans la barre latérale (repliés par défaut) : Pays, Agence, Type de revenu, Période.
- Export CSV disponible à chaque niveau (client, agence, type, global).
- Logo et couleur de marque Baobab (rose `#E40473`) intégrés au design.

## Personnaliser le logo

Remplacez le fichier `logo-dark.png` à la racine du projet par votre propre logo (fond transparent
recommandé) pour qu'il s'affiche automatiquement dans l'en-tête et la barre latérale — aucune
modification de code n'est nécessaire.

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
