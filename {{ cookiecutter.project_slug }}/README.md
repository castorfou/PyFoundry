# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Configuration Initiale

### Option 1 : Devcontainer VS Code (Recommandé)

Si vous utilisez VS Code avec Docker, le projet se configurera automatiquement dans un devcontainer.

**Prérequis** : Authentification à ghcr.io pour les features devcontainer :

```bash
# 1. Créez un Personal Access Token sur GitHub avec permission 'read:packages'
# https://github.com/settings/tokens/new

# 2. Connectez-vous à ghcr.io
docker login ghcr.io -u VOTRE_USERNAME
# Utilisez le token comme mot de passe

# 3. Ouvrez le projet dans VS Code
code .
# VS Code proposera d'ouvrir dans un devcontainer
```

### Option 2 : Installation locale

```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate  # Windows

# Installer uv si nécessaire
pip install uv

# Installer les dépendances
uv pip install -e .
uv pip install -e ".[dev]"  # Dépendances de développement
```

## Structure du projet

```
├── src/           # Code source du projet
├── data/          # Données du projet
│   ├── raw/       # Données brutes
│   └── processed/ # Données traitées
├── notebooks/     # Notebooks Jupyter
└── pyproject.toml # Configuration du projet
```

## Usage

Décrivez ici comment utiliser votre projet.

## Contribution

1. Installez les hooks pre-commit : `pre-commit install`
2. Créez une branche pour votre fonctionnalité
3. Commitez vos changements
4. Ouvrez une Pull Request