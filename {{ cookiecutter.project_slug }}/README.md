# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

[![CI](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/branch/main/graph/badge.svg)](https://codecov.io/gh/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }})
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

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

## Documentation

📚 La documentation complète est disponible sur [{{ cookiecutter.github_username }}.github.io/{{ cookiecutter.project_slug }}](https://{{ cookiecutter.github_username }}.github.io/{{ cookiecutter.project_slug }})

### Activer GitHub Pages (première fois)

Pour déployer la documentation, activez GitHub Pages :

```bash
# Via gh CLI (recommandé)
gh api repos/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/pages \
  -X POST \
  -f build_type=workflow

# Ou manuellement :
# 1. Allez dans Settings > Pages
# 2. Source : sélectionnez "GitHub Actions"
```

### Générer localement

```bash
# Installer les dépendances de documentation
uv sync --extra docs

# Prévisualiser localement
uv run mkdocs serve

# La documentation sera accessible à l'URL affichée dans les logs
# Example: http://127.0.0.1:8000/{{ cookiecutter.project_slug }}/
```

!!! note "URL locale"
    Comme `site_url` est configuré pour GitHub Pages avec un chemin de base,
    MkDocs servira la documentation avec ce même chemin en local.
    Accédez à l'URL complète affichée dans les logs (avec le chemin `/{{ cookiecutter.project_slug }}/`).

    Si vous souhaitez servir sans chemin de base pour le développement local,
    commentez temporairement la ligne `site_url` dans `mkdocs.yml`.

## Usage

Décrivez ici comment utiliser votre projet.

## Contribution

1. Installez les hooks pre-commit : `pre-commit install`
2. Créez une branche pour votre fonctionnalité
3. Commitez vos changements
4. Ouvrez une Pull Request