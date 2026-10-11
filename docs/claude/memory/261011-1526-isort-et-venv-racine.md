# Issue #70 — retirer l'extension isort et empêcher un `.venv` à la racine

## Résumé

Point de départ : VS Code affichait souvent « isort client: couldn't create connection to server ». Deux corrections sur la branche `70-retirer-extension-isort` ([PR #71](https://github.com/castorfou/PyFoundry/pull/71)) :

1. **Extension `ms-python.isort` retirée** des devcontainers, dans le dépôt et dans le template. Ruff trie déjà les imports (règle `I`).
2. **`.venv` à la racine empêché et signalé** : `UV_PROJECT_ENVIRONMENT=/tmp/venv` dans `containerEnv`, et hook pre-commit local `no-venv-at-root`.

---

## Diagnostic

Log de l'extension (`~/.vscode-server/data/logs/*/exthost*/ms-python.isort/isort.log`) :

```
Interpreter from ms-python.python extension: /workspaces/PyFoundry/.venv/bin/python
Launching server ... failed. Error: spawn /workspaces/PyFoundry/.venv/bin/python ENOENT
```

- Un `.venv/` cassé (créé en avril par un `uv sync` sans `--active`) restait à la racine : `bin/` ne contenait que les scripts `activate*`, sans exécutable `python`.
- `ms-python.python` détecte un `.venv` dans le workspace et le préfère à `python.defaultInterpreterPath` (`/tmp/venv/bin/python`), qui n'est qu'une valeur par défaut.
- L'extension isort retente à chaque modification de `pyproject.toml` : la notification revenait souvent.

---

## Travaux de la branche

### Commit `38b698f` — retrait d'isort

- `.devcontainer/devcontainer.json` et `{{ cookiecutter.project_slug }}/.devcontainer/devcontainer.json` : ligne `"ms-python.isort"` supprimée.
- `tests/test_configurations.py` : `test_devcontainer_has_no_isort_extension`, paramétré `repo` / `generated`.

### Commit `6fb1a87` — `.venv` à la racine

- `containerEnv` des deux devcontainers : `"UV_PROJECT_ENVIRONMENT": "/tmp/venv"`. Un `uv sync` sans `--active` cible désormais `/tmp/venv`.
- `.pre-commit-config.yaml` et `{{ cookiecutter.project_slug }}/.pre-commit-config.yaml` (toujours identiques) : dépôt `local` avec le hook `no-venv-at-root` (`language: system`, `always_run: true`, `pass_filenames: false`), qui échoue avec le message « Supprime-le avec rm -rf .venv ».
- `tests/test_configurations.py` :
  - helper `_project_root(source, cookies, context)` : racine du dépôt (`REPO_ROOT`) ou d'un projet généré ;
  - `test_precommit_rejects_venv_at_root` : lit le hook dans le `.pre-commit-config.yaml`, exécute son `entry` (`shlex.split`) dans un `tmp_path` sans puis avec `.venv`.
- `tests/test_persistent_home.py` : `test_uv_project_environment_points_to_tmp_venv` (fixture `devcontainer_dir` : dépôt, défaut, `docker_in_docker`).
- `docs/user/usage.md` : hook ajouté au tableau des outils de qualité.

### Commit de documentation

- `CLAUDE.md` (tableau des tests) et `docs/dev/testing.md` : nouveaux tests mentionnés.

---

## Apprentissages clés

### Retirer `.venv/` du `.gitignore` ne le rend pas visible

L'utilisateur voulait retirer `.venv/` des `.gitignore` pour voir un `.venv` créé par erreur. Inutile : `uv venv` écrit `*` dans `.venv/.gitignore`, le dossier s'ignore lui-même. Vérifié dans un dépôt vide sans `.gitignore` racine : `git status` reste vide. Python 3.13+ fait de même avec `python -m venv`. D'où le hook pre-commit, qui teste l'existence du dossier, pas son statut git.

### Retirer une extension de `devcontainer.json` ne la désinstalle pas

Avec le HOME persistant (#59), `~/.vscode-server/extensions` survit aux rebuilds. Une extension retirée de la liste reste installée : il faut la désinstaller à la main.

### Le hook ruff de pre-commit est plus strict que `ruff check tests/`

`ruff check tests/ docs/` passait, mais le hook ruff a bloqué le commit sur `PLW1510` (`subprocess.run` sans `check=`). Ajouter `check=False` explicitement quand on teste un code retour.

### `language: system` sur pre-commit 4.5.1

Fonctionne sans avertissement pour un hook local `bash -c '...'`.

---

## Vérification

- `pytest tests` : 107 passed, 1 skipped (le skip existait déjà).
- `ruff check tests/ docs/` propre, `mkdocs build --strict` OK.
- Vrai pre-commit : `pre-commit run no-venv-at-root --all-files` passe sans `.venv`, échoue avec.
- CI de la PR #71 verte (tests 3.11 / 3.12, lint, pre-commit, build docs).
