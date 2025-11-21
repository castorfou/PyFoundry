# Project: {{ cookiecutter.project_name }}

## Description
{{ cookiecutter.description }}

## La Stack Technique
- **Langage**: Python {{ cookiecutter.python_version }}
- **Gestionnaire de dépendances**: uv & pyproject.toml
- **Environnement de développement**: VS Code Dev Container
- **Qualité de Code**: pre-commit hooks avec ruff
- **Tests**: pytest
{%- if cookiecutter.use_node == 'y' %}
- **Node.js**: Installé et configuré (version LTS)
{%- endif %}

## Structure du Projet

```
.
├── .devcontainer/          # Configuration du dev container
├── .github/workflows/      # CI/CD GitHub Actions
├── data/
│   ├── raw/               # Données brutes (non versionnées)
│   └── processed/         # Données traitées
├── notebooks/             # Notebooks Jupyter pour l'exploration
├── src/                   # Code source Python
├── .gitignore
├── .pre-commit-config.yaml
└── pyproject.toml         # Configuration du projet et dépendances
```

## Environnement de Développement

### Prérequis
- VS Code avec l'extension Dev Containers
- Docker

### Installation
1. Ouvrir le projet dans VS Code
2. Accepter la proposition d'ouvrir dans un Dev Container
3. Le container se construit automatiquement avec toutes les dépendances

### Gestion des Dépendances
Les dépendances sont gérées via `uv` et définies dans `pyproject.toml`:

```bash
# Installer/synchroniser les dépendances
uv pip sync

# Ajouter une nouvelle dépendance
uv add package-name

# Ajouter une dépendance de développement
uv add --dev package-name
```

## Qualité du Code

### Pre-commit Hooks
Des hooks pre-commit sont configurés pour maintenir la qualité du code:

```bash
# Installer les hooks
pre-commit install

# Lancer manuellement sur tous les fichiers
pre-commit run --all-files
```

### Linting et Formatage
Le projet utilise `ruff` pour le linting et le formatage:

```bash
# Vérifier le code
ruff check .

# Formater le code
ruff format .
```

## Tests

```bash
# Lancer tous les tests
pytest

# Lancer avec coverage
pytest --cov=src --cov-report=html
```

## Conventions de Code

### Commits
Suivre la convention Conventional Commits:
- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation
- `test:` Ajout/modification de tests
- `chore:` Tâches de maintenance
- `refactor:` Refactoring sans changement de fonctionnalité

Exemple: `feat(data): ajouter pipeline de preprocessing`

### Style Python
- Utiliser les type hints autant que possible
- Documenter les fonctions avec des docstrings
- Respecter PEP 8 (appliqué automatiquement par ruff)
- Maximum 88 caractères par ligne

## Commandes Claude Code

Ce projet inclut des commandes slash pré-configurées pour Claude Code :

### `/fix-issue {numéro}`
Workflow TDD complet pour résoudre une issue GitHub :
- Récupère les détails de l'issue
- Crée une branche depuis l'issue
- Implémente en TDD (tests RED puis code)
- Vérifie qualité (tests, lint, typecheck)
- Met à jour la documentation
- Commit, push et crée la PR

### `/stocke-memoire`
Sauvegarde les apprentissages et décisions importantes dans `docs/claude/memory/` avec horodatage.

## Commandes Shell Utiles

```bash
# Synchroniser les dépendances
uv pip sync

# Lancer les tests
pytest

# Vérifier la qualité du code
ruff check .

# Formater le code
ruff format .

# Lancer pre-commit hooks
pre-commit run --all-files

# Mettre à jour pre-commit hooks
pre-commit autoupdate
```

## Ressources
- Dépôt GitHub: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}
- Documentation Python: https://docs.python.org/{{ cookiecutter.python_version }}/
- Documentation uv: https://github.com/astral-sh/uv
- Documentation ruff: https://docs.astral.sh/ruff/
