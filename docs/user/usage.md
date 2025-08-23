# Guide d'utilisation

## Commandes principales

### Gestion des dépendances

#### Avec uv (recommandé)
```bash
# Activer l'environnement (si pas déjà fait)
source .venv/bin/activate

# Installer les dépendances du projet
uv pip install -e .

# Installer les outils de développement
uv pip install -e ".[dev]"

# Ajouter une nouvelle dépendance
uv add pandas numpy scikit-learn

# Ajouter une dépendance de développement
uv add --dev pytest black
```

#### Avec pip standard
```bash
# Activer l'environnement
source .venv/bin/activate

# Installer les dépendances
pip install -e .
pip install -e ".[dev]"

# Ajouter des dépendances (modifier pyproject.toml puis)
pip install -e .
```

### Jupyter et notebooks

```bash
# Démarrer Jupyter Lab
jupyter lab

# Démarrer Jupyter Notebook classique
jupyter notebook

# Convertir un notebook en script Python
jupyter nbconvert --to script notebook.ipynb
```

### Environnement de développement

```bash
# Installer les hooks pre-commit (quand disponible)
pre-commit install

# Vérifier la qualité du code
ruff check .
ruff format .
```

## Workflow recommandé

### 1. Exploration des données
- Placez vos données brutes dans `data/raw/`
- Créez des notebooks d'exploration dans `notebooks/`
- Documentez vos découvertes dans les notebooks

### 2. Développement de code
- Développez vos fonctions dans `src/`
- Créez des modules réutilisables
- Ajoutez des tests si nécessaire

### 3. Traitement des données
- Sauvegardez les données traitées dans `data/processed/`
- Documentez les transformations effectuées
- Versionnez vos scripts de traitement

## Bonnes pratiques

### Structure des notebooks
```python
# Cell 1: Imports et configuration
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuration
plt.style.use('default')
pd.set_option('display.max_columns', None)

# Cell 2: Chargement des données
data = pd.read_csv('data/raw/mon_dataset.csv')

# Cell 3+: Analyse...
```

### Gestion des secrets
```python
# Utilisez python-dotenv pour les configurations
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('API_KEY')
```

### Organisation des fichiers
```
├── data/
│   ├── raw/           # Données d'origine (ne pas modifier)
│   └── processed/     # Données transformées
├── notebooks/
│   ├── 01-exploration.ipynb
│   ├── 02-cleaning.ipynb
│   └── 03-modeling.ipynb
├── src/
│   ├── data/          # Scripts de collecte/nettoyage
│   ├── features/      # Feature engineering
│   └── models/        # Modèles ML
```

## Variables d'environnement

Créez un fichier `.env` à la racine pour vos configurations :

```env
# API Keys
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/db

# Configuration
DEBUG=True
LOG_LEVEL=INFO
```

## Résolution de problèmes

### Problèmes de dépendances
```bash
# Réinstaller toutes les dépendances
uv pip sync pyproject.toml

# Nettoyer le cache
uv cache clean
```

### Problèmes Jupyter
```bash
# Réinstaller le kernel Jupyter
python -m ipykernel install --user --name=mon-projet

# Vérifier les kernels disponibles
jupyter kernelspec list
```

### Problèmes devcontainer
1. Rebuild container : `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"
2. Vérifier Docker Desktop est lancé
3. Vérifier les logs du container dans VS Code