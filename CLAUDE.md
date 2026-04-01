# Project: PyFoundry Template

## Description

Un template Cookiecutter de qualité industrielle pour démarrer des projets de Data Science en Python. Il vise à garantir la reproductibilité, la qualité du code et un démarrage rapide grâce à une configuration complète et automatisée.

- **GitHub** : https://github.com/castorfou/PyFoundry
- **Documentation** : https://castorfou.github.io/PyFoundry
- **Version actuelle** : 0.4.0-dev

## La Stack

- **Templating** : Cookiecutter / Cruft
- **Environnement** : Devcontainer (VS Code)
- **Dépendances** : uv & pyproject.toml
- **Qualité de Code** : pre-commit & ruff & mypy
- **Tests du Template** : pytest & pytest-cookies
- **Documentation** : MkDocs & mkdocs-material
- **CI/CD** : GitHub Actions

## Architecture

### Structure du Template (Dépôt PyFoundry)

```
PyFoundry/
├── .devcontainer/                       # Environnement de dev pour travailler sur le template
├── .github/workflows/
│   ├── test-template.yml                # CI : lint + tests sur toutes les branches
│   ├── docs.yml                         # Déploiement documentation GitHub Pages
│   └── release.yml                      # Publication des releases
├── docs/                                # Fichiers source MkDocs
│   ├── cheatsheets/                     # Claude, GitHub, Docker, uv, VSCode, MkDocs...
│   ├── dev/                             # Docs développeur (architecture, tests, contribution)
│   └── user/                            # Docs utilisateur (getting started, conventions)
├── tests/
│   ├── conftest.py                      # Fixtures pytest (contextes de génération)
│   ├── test_template_generation.py      # Tests de génération (structure, fichiers)
│   ├── test_configurations.py           # Tests de validation (TOML, YAML, JSON)
│   └── test_mkdocs_integration.py       # Tests MkDocs (config, build)
├── {{ cookiecutter.project_slug }}/     # Contenu du projet généré
├── cookiecutter.json                    # Variables du template
├── mkdocs.yml
└── pyproject.toml                       # Dépendances et config outils (ruff, mypy, pytest)
```

### Variables Cookiecutter

```json
{
    "project_name": "Mon Projet Data Science",
    "project_slug": "<auto-généré depuis project_name>",
    "description": "Description courte",
    "python_version": "3.11",
    "github_username": "castorfou",
    "use_node": "n"
}
```

### Structure du Projet Généré

```
mon-projet-data-science/
├── .claude/
│   └── commands/                  # Commandes slash (fix-issue, stocke-memoire)
├── .devcontainer/                  # Environnement de dev reproductible
├── .github/workflows/              # CI/CD du projet généré
├── data/
│   ├── raw/
│   └── processed/
├── docs/                           # Documentation MkDocs du projet
│   ├── user/
│   ├── dev/
│   └── claude/memory/             # Mémoire Claude Code
├── notebooks/
├── src/
├── tests/
├── .gitignore
├── .pre-commit-config.yaml
├── CLAUDE.md
└── pyproject.toml
```

## Environnement de Développement

Pour travailler sur le template PyFoundry lui-même, deux options :

### Option 1 : Devcontainer (recommandé)

Le dépôt PyFoundry a son propre devcontainer. Ouvrir dans VS Code → "Reopen in Container".

### Option 2 : Environnement conda/mamba `pyfoundry`

```bash
# Créer l'environnement (une seule fois)
mamba create -y -n pyfoundry -c conda-forge python=3.11
mamba activate pyfoundry
mamba install nb_conda_kernels cruft mkdocs-material pytest pytest-cookies pytest-cov pre-commit ruff mypy --yes

# Activer l'environnement
source ~/miniforge3/etc/profile.d/conda.sh && conda activate pyfoundry
```

## Commandes Utiles

### Lancer les tests

```bash
# Via conda (règle R1.1)
eval "$(conda shell.bash hook)" && conda activate pyfoundry && pytest tests -v

# Via uv
uv sync --active --all-extras
uv run --active pytest tests/
```

### Linter / Formater

```bash
# Via conda (règle R1.2)
eval "$(conda shell.bash hook)" && conda activate pyfoundry && ruff check tests/ docs/ --fix

# Via uv
uv run --active ruff check . --fix
```

### Générer un projet de test localement

```bash
# cookiecutter lit le filesystem (voit les fichiers non commités) — pour test rapide
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input

# cruft utilise Git (ne voit que les fichiers commités) — pour test fidèle à la prod
cruft create . --no-input

# Avec paramètres personnalisés
cruft create . --no-input --extra-context '{"use_node": "y"}'
```

### Documentation

```bash
uv sync --active --extra doc
uv run --active mkdocs serve        # Prévisualiser sur http://localhost:8000
uv run --active mkdocs build --strict
```

## Règles Importantes pour Claude Code

### R1.1 — Lancer pytest

```bash
eval "$(conda shell.bash hook)" && conda activate pyfoundry && pytest tests -v
```

### R1.2 — Lancer ruff

```bash
eval "$(conda shell.bash hook)" && conda activate pyfoundry && ruff check tests/ docs/ --fix
```

### R1.3 — Tester localement le projet généré

```bash
mamba activate pyfoundry && \
cd /tmp && \
rm -rf /tmp/mon-projet-data-science && \
cruft create /workspaces/PyFoundry --no-input --extra-context '{"use_node": "y"}' && \
code mon-projet-data-science
```

Puis "Rebuild and Reopen in Container" depuis VS Code.

### R1.4 — cruft vs cookiecutter

- **`cruft create`** : utilise Git → ne voit que les fichiers **commités**
- **`cookiecutter`** : lit le filesystem → voit **tous** les fichiers

Pour tester des modifications non commitées, utiliser `cookiecutter` directement.

## Conventions & Style de Code

- **Source de vérité unique** : `pyproject.toml` pour toutes les configurations.
- **Formatage & Linting** : `ruff` configuré dans `pyproject.toml`.
- **Templating** : syntaxe `{{ cookiecutter.variable }}` pour les fichiers dynamiques.
- **Exclusion ruff** : le dossier `{{ cookiecutter.project_slug }}` est exclu via `extend-exclude = ["[{][{]*"]`.
- **Commits** : convention `type(scope): message` — `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.

## Stratégie de Test

### Fichiers de tests

| Fichier | Rôle |
|---------|------|
| `conftest.py` | Fixtures : `default_template_context`, `minimal_template_context` |
| `test_template_generation.py` | Structure générée, fichiers présents, variables injectées |
| `test_configurations.py` | Validité TOML/YAML/JSON, config ruff/mypy/devcontainer |
| `test_mkdocs_integration.py` | Config mkdocs.yml, build documentation |

### CI/CD GitHub Actions

| Workflow | Déclencheur | Rôle |
|----------|-------------|------|
| `test-template.yml` | Push toutes branches, PR main | Lint ruff + tests pytest |
| `docs.yml` | Push main (docs/ ou mkdocs.yml) | Déploiement GitHub Pages |
| `release.yml` | Tag `v*` | Release GitHub + tests |

## Ressources

- [Cookiecutter docs](https://cookiecutter.readthedocs.io/)
- [Cruft docs](https://cruft.github.io/cruft/)
- [uv docs](https://github.com/astral-sh/uv)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- [pytest-cookies](https://pytest-cookies.readthedocs.io/)
