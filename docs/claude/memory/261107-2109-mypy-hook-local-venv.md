# Issue #112 — mypy : hook local dans le venv, même périmètre partout

## Résumé

Le hook `mirrors-mypy` tournait dans un environnement isolé (`additional_dependencies` recopiées à la main) et ne vérifiait que `src/`. `uv run mypy` vérifiait `tests/` (`files = ["tests"]`), la CI `src/`. Sur google-to-synology-photos, ajouter `keyring` et `platformdirs` faisait échouer le hook alors que `uv run mypy` passait.

Spécification : [commentaire de l'issue #112](https://github.com/castorfou/PyFoundry/issues/112#issuecomment-6712383933).

## Changements

| Fichier | Changement |
|---------|------------|
| `.pre-commit-config.yaml` (dépôt et squelette) | hook `repo: local`, `entry: uv run --active mypy`, `language: system`, `types: [python]`, `pass_filenames: false`, identique des deux côtés |
| `{{ cookiecutter.project_slug }}/pyproject.toml` | `[tool.mypy] files = ["src", "tests"]` ; `pandas-stubs`, `types-python-dateutil`, `types-requests` dans les extras `dev` |
| `{{ cookiecutter.project_slug }}/src/<package>/__init__.py`, `tests/test_<package>.py` | remplacent `src/.gitkeep` ; nom `{{ cookiecutter.project_slug\|replace('-', '_') }}` |
| `{{ cookiecutter.project_slug }}/.github/workflows/ci.yml` | `uv run mypy` sans chemin (le `if [ -d src/ ]` disparaît) |
| `.github/workflows/test-template.yml` | `uv run mypy --show-error-codes` sans `src/` sur le projet généré |
| `pyproject.toml` (racine) | `mypy` et `types-PyYAML` dans l'extra `test` ; override `ignore_missing_imports` pour `cookiecutter.*` ; `files = ["tests"]` gardé (pas de `src/` à la racine) |
| `tests/test_configurations.py` | annotation `cookies: Any` de `_project_root`, `expected_repos` attend `local` |
| `tests/test_mypy.py` | nouveau : hook, périmètre, stubs, package du squelette, vrai mypy sur le dépôt et sur un projet généré, commandes de la CI |

Les `|| echo` de la CI restent : ils relèvent de #111.

## Points saillants

### Un `src/` vide fait échouer mypy

Avec `files = ["src", "tests"]`, un projet neuf (`src/.gitkeep`, pas de `tests/`) donne `There are no .py[i] files in directory 'src'`, code 2. Le hook aurait cassé le premier commit Python, même un `cruft update` qui touche `.claude/skills/cruft-update/scripts/template_update.py` (`types: [python]` déclenche le hook, `pass_filenames: false` lui fait vérifier tout le périmètre). D'où le package et le test minimaux du squelette.

### Pas de double détection de module

Le commentaire retiré (« exclure src/ car déjà dans sys.path via editable install ») venait de la section « found twice » de `docs/user/troubleshooting.md`. Avec la mise en page `src/` et l'installation editable, mypy prend `src/` comme base du package : aucune erreur, vérifié sur un projet rendu.

### Pourquoi `mypy` est dans l'extra `test` de la racine

Le job `test-template` de la CI installe `--extra test` seulement, et `tests/test_mypy.py` lance `sys.executable -m mypy`. Sans mypy ni `types-PyYAML` dans `test`, ce job échouerait.

### `uv run --active` en CI

Pas de venv actif en CI : `uv run pre-commit` exporte `VIRTUAL_ENV` vers le venv du projet, et le `uv run --active mypy` du hook le réutilise. Dans le devcontainer, `/tmp/venv` est actif.

## Pour un projet existant

Un projet qui avait ajouté ses propres `additional_dependencies` au hook doit les reporter dans ses extras `dev`, puis lancer `uv lock` (note de migration du CHANGELOG).
