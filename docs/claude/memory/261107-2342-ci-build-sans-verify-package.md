# Issue #125 — Job `build` de la CI générée : étape « Verify package » retirée

## Résumé

Dans `{{ cookiecutter.project_slug }}/.github/workflows/ci.yml`, l'étape « ✅ Verify package » du job `build` lançait `uv run python -m pip show <pkg> || echo "Package not installed yet"`. Elle ne vérifiait rien : le wheel n'était jamais installé, le venv créé par uv n'a pas `pip`, et le `|| echo` masquait l'échec.

En construisant le wheel d'un projet généré, un second défaut est apparu : `[project.scripts]` déclarait `<package>_setup = "scripts.setup:main"` (hérité de la v0.2), alors qu'aucun module `scripts` n'existe. La commande installée plantait avec `ModuleNotFoundError`.

Décisions de l'utilisateur : supprimer l'étape (l'artefact `dist/` uploadé suffit), supprimer `[project.scripts]`, et vérifier le wheel dans les tests du template.

Spécification : [commentaire de l'issue #125](https://github.com/castorfou/PyFoundry/issues/125#issuecomment-6713977961).

## Changements

| Fichier | Changement |
|---------|------------|
| `{{ cookiecutter.project_slug }}/.github/workflows/ci.yml` | étape « ✅ Verify package » supprimée ; le job garde `uv build` et l'upload de `dist/` |
| `{{ cookiecutter.project_slug }}/pyproject.toml` | section `[project.scripts]` supprimée |
| `tests/test_ci_strict.py` | `test_generated_ci_never_swallows_failures` (aucun `\|\| echo`, `\|\| true` ou `\|\| :` dans les étapes de `ci.yml`, quelle que soit la commande), `test_generated_ci_has_no_verify_package_step`, `test_generated_entry_points_resolve` (chaque cible de `[project.scripts]` existe sous `src/`), `test_generated_wheel_imports` (`uv build --wheel` puis `uv run --isolated --no-project --with <wheel> python -c "import <package>"`) |

## Points saillants

- `test_checkers_failures_are_not_swallowed` (#111) ne visait que les lignes ruff, mypy ou pre-commit : c'est pourquoi l'étape `pip show … || echo` lui avait échappé. La règle couvre maintenant toutes les étapes de la CI générée.
- Pour essayer un wheel sans toucher au projet : `uv run --isolated --no-project --with dist/<wheel>.whl python -c "import <package>"`.
- `test_generated_wheel_imports` passait déjà avant la correction : c'est un garde-fou, pas un test RED. Les trois autres étaient RED.
- Pas de migration : `cruft update` retire l'étape et la section. Un projet qui avait modifié ces lignes reçoit un rejet classique.
