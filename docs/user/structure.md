# Structure du projet

## Vue d'ensemble

Chaque projet généré par PyFoundry suit cette structure standardisée :

```
mon-projet-data-science/
├── .devcontainer/          # Configuration environnement VS Code
│   └── devcontainer.json
├── src/                    # Code source principal
├── data/                   # Données du projet
│   ├── raw/               # Données brutes (lecture seule)
│   └── processed/         # Données transformées
├── notebooks/             # Notebooks Jupyter d'analyse
├── pyproject.toml         # Configuration et dépendances
├── README.md              # Documentation du projet
└── .gitignore             # Fichiers ignorés par Git
```

## Détail des dossiers

### `.devcontainer/`
Configuration pour VS Code Dev Containers. Garantit un environnement de développement reproductible avec :
- Python {{ cookiecutter.python_version }}
- uv pour la gestion des dépendances
- Extensions VS Code pré-installées
- Port 8888 exposé pour Jupyter

### `.venv/` (généré)
Environnement virtuel Python créé automatiquement par le devcontainer :
- Contient toutes les dépendances du projet
- Isolé des autres projets
- Activé automatiquement dans VS Code et les terminaux
- Ignoré par Git

### `src/`
Code source principal du projet. Structure recommandée :

```
src/
├── __init__.py
├── data/                  # Scripts de collecte/nettoyage
│   ├── __init__.py
│   ├── download.py
│   └── preprocess.py
├── features/              # Feature engineering
│   ├── __init__.py
│   └── build_features.py
├── models/                # Modèles et prédictions
│   ├── __init__.py
│   ├── train.py
│   └── predict.py
└── utils/                 # Utilitaires communs
    ├── __init__.py
    └── helpers.py
```

### `data/`
Stockage des données avec séparation claire :

- **`raw/`** : Données d'origine, **ne jamais modifier**
  - Versionnées avec Git LFS si nécessaire
  - Formats : CSV, JSON, Parquet, etc.
  
- **`processed/`** : Données transformées et nettoyées
  - Générées par vos scripts de traitement
  - Ignorées par Git (sauf si petites et importantes)

!!! warning "Données sensibles"
    Ne commitez jamais de données personnelles ou sensibles. Utilisez `.gitignore` et des fichiers de configuration pour les chemins externes.

### `notebooks/`
Notebooks Jupyter pour l'exploration et l'analyse :

```
notebooks/
├── 01-exploration-donnees.ipynb
├── 02-nettoyage-donnees.ipynb
├── 03-feature-engineering.ipynb
├── 04-modelisation.ipynb
└── 05-evaluation-resultats.ipynb
```

**Convention de nommage** : `##-description-courte.ipynb`

### Fichiers de configuration

#### `pyproject.toml`
Configuration centralisée pour :
- Métadonnées du projet (nom, version, description)
- Dépendances Python (runtime et développement)
- Configuration des outils (ruff, pytest, etc.)

#### `README.md`
Documentation générée dynamiquement avec :
- Description du projet
- Instructions d'installation
- Structure du projet
- Guide de contribution

#### `.gitignore`
Ignore automatiquement :
- Fichiers Python temporaires (`__pycache__/`, `*.pyc`)
- Environnements virtuels
- Notebooks checkpoints
- Données dans `data/raw/` et `data/processed/`
- Modèles ML volumineux
- Fichiers système

## Dépendances incluses

### Runtime
- **ipykernel** : Support Jupyter dans VS Code
- **ipywidgets** : Widgets interactifs pour notebooks
- **python-dotenv** : Gestion des variables d'environnement
- **gitpython** : Intégration Git programmatique

### Développement
- **pre-commit** : Hooks de qualité de code (v0.3)

## Personnalisation

### Ajouter des dépendances
```bash
# Dépendances runtime
uv add pandas numpy scikit-learn matplotlib seaborn

# Dépendances développement
uv add --dev pytest black isort mypy
```

### Modifier la structure
La structure est flexible. Vous pouvez :
- Ajouter des dossiers dans `src/`
- Créer des sous-modules spécialisés
- Adapter selon votre domaine (NLP, CV, etc.)

### Configuration personnalisée
Modifiez `pyproject.toml` pour :
- Ajuster les versions Python supportées
- Configurer les outils de développement
- Définir des scripts personnalisés