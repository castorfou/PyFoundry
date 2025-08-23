# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Installation

Ce projet utilise **uv** pour la gestion des dépendances et des environnements Python.

### Avec VS Code + Devcontainer (Recommandé)

Si vous avez Docker et VS Code :

```bash
# 1. Authentifiez-vous à ghcr.io (si nécessaire)
# Créez un Personal Access Token : https://github.com/settings/tokens/new
# Permissions : read:packages
docker login ghcr.io -u VOTRE_USERNAME

# 2. Ouvrez dans VS Code
code .
# VS Code proposera "Reopen in Container"
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