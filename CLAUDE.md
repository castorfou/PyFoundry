# Project: PyFoundry Template
## Description
Un template Cookiecutter de qualité industrielle pour démarrer des projets de Data Science en Python. Il vise à garantir la reproductibilité, la qualité du code et un démarrage rapide grâce à une configuration complète et automatisée.

## La Stack
- **Templating**: Cookiecutter / Cruft
- **Environnement**: Devcontainer (VS Code)
- **Dépendances**: uv & pyproject.toml
- **Qualité de Code**: pre-commit & ruff
- **Tests du Template**: pytest & pytest-cookies
- **Documentation**: MkDocs & mkdocs-material
- **CI/CD**: GitHub Actions

## Architecture Cible
### Structure du Template (Dépôt PyFoundry)

.
├── .github/workflows/          # CI/CD pour le template et la doc
├── docs/                       # Fichiers source MkDocs
├── tests/                      # Tests du template avec pytest-cookies
├── {{ cookiecutter.project_slug }}/   # <-- Contenu du projet généré
├── cookiecutter.json
├── mkdocs.yml
└── pyproject.toml              # Dépendances pour tester/documenter le template

### Structure du Projet Généré

.
├── .devcontainer/              # Environnement de dev reproductible
├── .github/workflows/          # CI pour le code du projet
├── data/
├── notebooks/
├── src/
├── .gitignore
├── .pre-commit-config.yaml
└── pyproject.toml              # Dépendances du projet


## Conventions & Style de Code
- **Source de vérité unique**: `pyproject.toml` pour toutes les configurations (dépendances, outils).
- **Formatage & Linting**: `ruff` est l'outil par défaut, configuré dans `pyproject.toml`.
- **Commits**: Messages de commit suivant la convention `type(scope): message` (ex: `feat`, `fix`, `docs`, `test`, `chore`).
- **Templating**: Utiliser la syntaxe `{{ cookiecutter.variable }}` pour rendre les fichiers dynamiques.

## Stratégie de Test
- Les tests du template se trouvent dans le dossier `/tests` à la racine.
- Utilisation de `pytest-cookies` pour générer un projet dans un environnement temporaire.
- Les tests doivent valider la génération du projet ET exécuter des commandes de validation (`uv pip sync`, `ruff check`) à l'intérieur du projet généré.
- Test de configuration devcontainer : validation de l'héritage de timezone du host (TZ env var + montages /etc/timezone et /etc/localtime).

## Commandes Utiles (à la racine du template)
- `uv run pytest tests/`: Lance la suite de tests du template.
- `cruft create . --no-input`: Génère un projet de test localement avec les valeurs par défaut.
- `mkdocs serve`: Lance le serveur local pour la documentation.
