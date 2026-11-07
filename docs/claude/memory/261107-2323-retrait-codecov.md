# Issue #126 — Retrait de l'upload Codecov (template et projet généré)

## Résumé

L'étape « 📊 Upload coverage to Codecov » de `test-template.yml` échouait en silence : `uv run pytest tests/ -v` ne produisait pas de `coverage.xml`, le dépôt n'avait aucun secret (`gh secret list` vide, donc pas de `CODECOV_TOKEN`), et `fail_ci_if_error: false` laissait l'étape au vert. Dans `ci.yml`, la condition `matrix.python-version == '3.11'` était écrite en dur : un projet généré avec `python_version=3.12` n'envoyait jamais rien.

Décision de l'utilisateur : retirer Codecov du template **et** des projets générés.

Spécification : [commentaire de l'issue #126](https://github.com/castorfou/PyFoundry/issues/126#issuecomment-6713786999).

## Changements

| Fichier | Changement |
|---------|------------|
| `.github/workflows/test-template.yml` | étape Codecov supprimée du job `test-template` |
| `{{ cookiecutter.project_slug }}/.github/workflows/ci.yml` | étape Codecov supprimée ; `pytest` garde `--cov=src --cov-report=term-missing` et perd `--cov-report=xml` |
| `tests/test_ci_strict.py` | `test_no_codecov_upload` (ni `codecov` ni `CODECOV_TOKEN` dans les deux workflows), `test_no_silenced_step_errors` (aucun `fail_ci_if_error: false`), `test_generated_ci_coverage_in_log_only` |
| `tests/test_github_actions.py` | `codecov/codecov-action` retiré de `MIN_MAJOR` : une action absente de `MIN_MAJOR` est refusée, donc réintroduire Codecov oblige à revoir ce choix |
| `docs/dev/contributing.md` | ligne « Upload de couverture vers Codecov » retirée |

## Points saillants

- La couverture du template mesurerait surtout des fichiers rendus et des scripts shell : peu de valeur pour un compte Codecov à maintenir.
- Dans les projets générés, la couverture reste lisible dans le log du job (`term-missing`). `cruft update` retire l'étape ; un projet qui veut garder Codecov la remet après la mise à jour.
- Un `fail_ci_if_error: false` cache un échec comme un `|| echo` (#111) : le test le refuse désormais dans les deux workflows.
