# Issue #111 — CI : ruff, mypy et pre-commit font échouer le build

## Résumé

Des `|| echo "⚠️ ..."` après ruff, mypy et pre-commit masquaient tous les échecs, dans la CI du template (`test-template.yml`) et dans la CI générée (`ci.yml`). Les logs du run 42410410111 sur `main` montraient trois échecs cachés :

1. étape « 🏗️ Test generated project validity » : `ruff check . --show-source` → `error: unexpected argument '--show-source'` (option retirée de ruff), donc ruff n'a jamais vérifié le projet généré ;
2. même étape : `pre-commit run` → `FatalError: git failed`, car `cruft create` ne crée pas de dépôt git ;
3. job `pre-commit` du dépôt : le hook `no-venv-at-root` échouait, car `uv sync` crée `.venv` à la racine en CI. Le job `pre-commit` de `ci.yml` avait le même défaut.

Spécification : [commentaire de l'issue #111](https://github.com/castorfou/PyFoundry/issues/111#issuecomment-6712554285).

## Changements

| Fichier | Changement |
|---------|------------|
| `.github/workflows/test-template.yml` | job `pre-commit` : `env: UV_PROJECT_ENVIRONMENT: /tmp/venv`, sans `\|\| echo` ; étape de validité : `UV_PROJECT_ENVIRONMENT: /tmp/venv-generated`, `uv run ruff check .`, `git init` + `git add -A` + `git -c user.name=pyfoundry-ci -c user.email=... commit` avant pre-commit, plus aucun `\|\| echo` |
| `{{ cookiecutter.project_slug }}/.github/workflows/ci.yml` | `uv run mypy` sans `\|\| echo` ; job `pre-commit` : `UV_PROJECT_ENVIRONMENT: /tmp/venv`, sans `\|\| echo` |
| `tests/test_ci_strict.py` | nouveau : aucun `\|\| echo`/`\|\| true` après ruff, mypy ou pre-commit, pas de `--show-source`, venv sous `/tmp/` pour chaque étape pre-commit, ordre `git init` → `git add` → commit → pre-commit, et l'étape de validité rejouée en local sur un projet généré |

Le `|| echo "Package not installed yet"` du job `build` de `ci.yml` reste : vérification informative, hors périmètre.

## Points saillants

### Le venv hors du dépôt, comme dans le devcontainer

Le hook `no-venv-at-root` refuse un `.venv` à la racine. En CI, `uv sync` en crée un par défaut. `UV_PROJECT_ENVIRONMENT` au niveau du job aligne la CI sur le devcontainer (`/tmp/venv`). Dans l'étape de validité, `/tmp/venv-generated` évite d'écraser le venv du template.

### L'identité git passée en `-c`

Le commit de l'étape de validité passe `user.name` et `user.email` en `-c` : rien n'est écrit dans la config git du runner, comme `git_commit_with_fallback` dans le projet généré.

### Le test d'intégration passait en RED

`test_validity_step_passes_on_generated_project` rejoue le script de l'étape (après le `cd`) sur un projet cookiecutter. Tant que les `|| echo` étaient là, il passait : il ne devient significatif qu'avec les tests de structure (pas de `|| echo`). Il saute si le réseau manque pour installer les hooks.

### `ci.yml` lu après rendu

Le squelette brut de `ci.yml` contient `if: {% raw %}...`, que YAML lit comme une mapping : les tests chargent le `ci.yml` d'un projet généré.
