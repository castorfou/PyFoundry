# Issue #68 — `pre-commit run --all-files` échoue sur un projet généré

## Résumé

Deux problèmes corrigés sur la branche `68-fixtemplate-pre-commit-run-all-files-échoue-sur-un-projet-généré` :

1. **Squelette non conforme aux hooks** : sur un projet tout juste généré, `check-json`, `end-of-file-fixer` et `trailing-whitespace` échouaient. Tous les hooks passent maintenant, dans les 3 variantes (défaut, `use_node=y`, `docker_in_docker=y`).
2. **Rebuild qui commite le travail en cours** : `setup_pre-commit` dans `postCreateCommand.sh` faisait `git add .` puis `git commit` à chaque rebuild dès que l'arbre de travail était modifié. Seul `.pre-commit-config.yaml` est désormais commité, et seulement s'il a changé.

Spécifications : commentaires de l'[issue #68](https://github.com/castorfou/PyFoundry/issues/68).

---

## Travaux de la branche

Au moment de cette mémoire, la branche contenait un commit `126681f` « chore: update pre-commit hooks and fix formatting » non poussé. **Il a été créé par le bug n°2 lui-même** : un rebuild du devcontainer PyFoundry a commité le travail de la première boucle (squelette + tests) avec ce message trompeur. Il est refait en commits atomiques avant le push.

### Boucle 1 — squelette conforme aux hooks

- `{{ cookiecutter.project_slug }}/.vscode/settings.json` : virgule finale supprimée (JSON invalide).
- Retour à la ligne final ajouté : `.devcontainer/devcontainer.json`, `.github/workflows/ci.yml`, `mkdocs.yml`, `pyproject.toml`, `docs/index.md`, `docs/user/.nav.yml`, `docs/user/README.md`, `docs/dev/README.md`, `docs/cheatsheets/github.md`, `docs/cheatsheets/vscode.md` (tous sous `{{ cookiecutter.project_slug }}/`).
- `{{ cookiecutter.project_slug }}/.gitignore` : bloc Node réécrit avec `{%- if ... %}` / `{%- endif %}` (voir apprentissages).
- Espaces en fin de ligne supprimés : `pyproject.toml`, `docs/cheatsheets/github.md`, `docs/cheatsheets/vscode.md`. Dans `vscode.md:10`, les deux espaces servaient de saut de ligne Markdown, remplacés par une ligne vide.
- `{{ cookiecutter.project_slug }}/.pre-commit-config.yaml` : copie du `.pre-commit-config.yaml` racine (déjà propre, R1.5).
- Tests dans `tests/test_configurations.py`, paramétrés sur les 3 contextes :
  - `test_generated_files_end_with_single_newline`
  - `test_generated_files_have_no_trailing_whitespace`
  - `test_generated_json_files_are_valid`
  - helpers `_precommit_exclude_patterns` (lit les exclusions dans le `.pre-commit-config.yaml` généré) et `_text_files` (liste les fichiers via `git init` + `git ls-files --others --exclude-standard`, comme pre-commit).

### Boucle 2 — `setup_pre-commit` ne commite plus le travail en cours

- `.devcontainer/postCreateCommand.sh` et `{{ cookiecutter.project_slug }}/.devcontainer/postCreateCommand.sh` : `autoupdate` conservé à chaque rebuild (choix de l'utilisateur), mais :
  - test limité à la config : `git diff --quiet -- .pre-commit-config.yaml` ;
  - commit ciblé : `git commit -m "..." -- .pre-commit-config.yaml` ;
  - repli `git add .` supprimé ; en cas d'échec, avertissement et config laissée non commitée.
- `tests/test_post_create_command.py` : extrait `setup_pre-commit` du script (dépôt et projet généré), l'exécute dans un dépôt temporaire avec un faux `pre-commit` (`FAKE_AUTOUPDATE=change|none`) et du travail en cours (fichier modifié, fichier dans l'index, fichier non suivi).
  - `test_no_hook_update_commits_nothing`
  - `test_hook_update_commits_only_precommit_config`

---

## Apprentissages clés

### Pourquoi les défauts du squelette passaient inaperçus

Le `.pre-commit-config.yaml` de PyFoundry exclut `{{ cookiecutter.project_slug }}/` de **tous** les hooks (exclusion globale, nécessaire à cause de la syntaxe Jinja). Les fichiers du squelette ne sont donc jamais nettoyés. Décision : garder l'exclusion, et laisser les tests de `test_configurations.py` servir de garde-fou en CI.

### `end-of-file-fixer` refuse aussi les lignes vides en trop

Il exige **exactement** un `\n` final. Un fichier qui finit par un bloc Jinja vide (`{% if %}...{% endif %}` faux) rend souvent `\n\n`. Pour `.gitignore` :

```
.vscode/settings.local.json
{%- if cookiecutter.use_node == "y" %}

# Node.js
...
.cache/
{%- endif %}
```

suivi d'un retour à la ligne final : les deux branches finissent par un seul `\n`.

À l'inverse, `docs/cheatsheets/devcontainer.md` finit par `{% endraw %}` **sans** retour à la ligne, et c'est correct : la ligne précédente apporte déjà le `\n`. En ajouter un donnait `\n\n` (le test l'a détecté).

### Tester sur le rendu, pas sur les sources

Les tests rendent le template (`cookies.bake`) au lieu de lire les sources : seul le rendu montre l'effet des blocs Jinja. Lister les fichiers via `git ls-files --others --exclude-standard` applique le `.gitignore` généré. Sans ce filtre, un `.env` local non suivi dans le squelette (absent de git, donc de `cruft`) faisait échouer le test à tort.

### `git commit -- fichier`

Commite uniquement ce fichier (mode `--only`) : l'index existant et le reste de l'arbre de travail ne sont pas touchés. C'est la bonne forme pour un commit automatique dans un script qui tourne sur le dépôt de l'utilisateur.

---

## Vérification

- `pytest tests` : 100 passed, 1 skipped (le skip existait déjà).
- `ruff check tests/ docs/` propre ; `mypy` propre sur les fichiers ajoutés (l'erreur `types-PyYAML` de `tests/test_configurations.py` existait déjà sur `main`).
- De bout en bout avec le vrai pre-commit : `pre-commit run --all-files` passe sur les 3 variantes générées ; `setup_pre-commit` avec un hook rétrogradé ne commite que `.pre-commit-config.yaml` et laisse `git status` intact.
