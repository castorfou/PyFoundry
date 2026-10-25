# Issue #87 — `uv sync` ne réécrit plus `uv.lock` au démarrage ni au rebuild

## Résumé

`ensure_venv.sh` (#86), appelé par `postCreateCommand.sh` (`--sync`) et par `postStartCommand`, lançait `uv sync --active --all-extras` sans `--frozen`. `uv` réécrivait alors `uv.lock` : format plus récent (`revision = 3` → `5`), marqueurs simplifiés, ou résolution refaite si le lock était en retard sur `pyproject.toml`. Le fichier modifié finissait dans le prochain `git add .`. Depuis #86, cela arrivait aussi à chaque démarrage où `/tmp` était vidé (docker-in-docker).

Correction (branche `87-devcontainer-uv-sync-réécrit-uvlock-…`) : sync gelé quand le lock existe, avertissement s'il est obsolète, contrôle `uv lock --check` en CI. Appliquée au dépôt et au squelette (R1.5).

Spécification : [commentaire de l'issue #87](https://github.com/castorfou/PyFoundry/issues/87#issuecomment-6399143666).

---

## Constats (uv 0.13.0)

- Un projet généré n'a pas de `uv.lock` avant son premier sync : `postCreateCommand.sh` lance `create_python_environment` avant `setup_git`, donc le lock créé par ce sync entre dans le commit initial. `uv sync --frozen` / `--locked` / `uv lock --check` échouent tous sans lock.
- Une différence de **format seule** (`revision`) ne fait **pas** échouer `uv lock --check` ni `uv sync --locked`. Seul un vrai écart de contenu les fait échouer. Le contrôle CI ne casse donc pas quand la CI a un uv plus récent que le poste.
- Le `uv.lock` de PyFoundry portait `pyfoundry 0.4.0.dev0` alors que `pyproject.toml` était en 1.1.0 : les PR de release changent la version sans relancer `uv lock`. C'était l'essentiel des 24 lignes de l'issue.

---

## Travaux de la branche

### `.devcontainer/scripts/ensure_venv.sh` (identique dans le squelette)

- `uv.lock` présent → `uv sync --frozen --active --all-extras` ; absent → `uv sync --active --all-extras` (crée le lock).
- Après un sync gelé : `uv lock --check` (sortie masquée, n'écrit rien). Échec → `⚠️  uv.lock n'est plus à jour avec pyproject.toml : le venv suit uv.lock.` puis la consigne `uv lock`, `uv sync --active --all-extras`, commit de `uv.lock`. Le script réussit quand même.
- Message de `fail()` : contournement avec `--frozen`.
- **Piège Jinja** : le squelette est rendu par cookiecutter et `ensure_venv.sh` n'est pas dans `_copy_without_render`. `${#tableau[@]}` contient `{#`, qui ouvre un commentaire Jinja (`TemplateSyntaxError: Missing end of comment tag`). Le script utilise donc une chaîne : `frozen=""`, `[ -f uv.lock ] && frozen="--frozen"`, `uv sync ${frozen:+"$frozen"} …`, `[ -n "$frozen" ]`.

### CI

- `.github/workflows/test-template.yml`, job `lint` : étape `🔒 Check uv.lock is up to date` (`uv lock --check`) avant `uv sync`.
- `{{ cookiecutter.project_slug }}/.github/workflows/ci.yml`, job `pre-commit` (le seul job hors matrice) : même étape.
- `uv.lock` de PyFoundry régénéré par `uv lock` (`revision = 5`, version 1.1.0).

### Tests (`tests/test_ensure_venv.py`)

- Faux `uv` : `FAKE_UV_LOCK_STALE=1` fait échouer `uv lock`. La fixture `fake_uv` crée un dossier projet avec `uv.lock` (`PROJECT_DIR`), et `run_ensure_venv` lance le script depuis ce dossier (`cwd`).
- Tests adaptés : appels attendus `sync --frozen --active --all-extras` puis `lock --check`.
- Nouveaux : lock à jour sans avertissement, lock obsolète avec avertissement et code 0, lock absent avec sync normal sans `lock --check`.
- `test_real_uv_leaves_lock_untouched` : vrai `uv` (skip s'il est absent, `UV_OFFLINE=1`, projet sans dépendance), lock passé en `revision = 1` et version du projet changée. Le lock reste identique octet pour octet et l'avertissement s'affiche. Il échouait avant la correction (`revision` 1 → 5).
- `test_ci_checks_lock` (fixture `devcontainer_dir` : dépôt, `default`, `docker_in_docker`) : une étape d'un job lance `uv lock --check`.

---

## Vérifications

- Dans PyFoundry : `ensure_venv.sh --sync` laisse `uv.lock` intact (même md5). Avec `six` ajouté à `pyproject.toml` sans `uv lock`, l'avertissement s'affiche et le lock est intact.
- Test utilisateur sur un projet généré (`use_node=y`, `docker_in_docker=y`) : `uv.lock` identique après création, après redémarrage sans rebuild, et après une dépendance ajoutée à la main (avertissement affiché).
- CI : la matrice de `test-template.yml` lance les tests sous Python 3.11 et 3.12. `test_real_uv_leaves_lock_untouched` imposait `PYTHON_VERSION=3.11`, absent du runner 3.12, et `uv` y était hors ligne (`UV_OFFLINE=1`) : échec de `uv venv`. Le test prend maintenant la version de l'interpréteur qui lance pytest (`sys.version_info`).
- Une simulation de lock obsolète par `sed` sur `version = "1.1.0"` est trompeuse : elle touche aussi d'autres paquets en 1.1.0 et fait échouer `--frozen`. Pour simuler, ajouter une dépendance à `pyproject.toml`.

## Hors périmètre : issue #102

Le même test a montré `.pre-commit-config.yaml` et `mkdocs.yml` modifiés juste après la création :
- le commit de `pre-commit autoupdate` dans `setup_pre-commit` échoue ; piste : pas d'identité git pendant `postCreateCommand`, contrairement à `setup_git` qui a un repli depuis #94 ;
- `update_mkdocs_repo_url.sh` ajoute `repo_url` et rien ne le commite.

Suivi dans [#102](https://github.com/castorfou/PyFoundry/issues/102).
