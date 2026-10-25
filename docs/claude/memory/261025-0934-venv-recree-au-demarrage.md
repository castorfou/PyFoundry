# Issue #86 — `/tmp/venv` recréé au démarrage du conteneur

## Résumé

Avec la feature `ghcr.io/devcontainers/features/docker-in-docker:2`, `/tmp` est un **tmpfs** monté à chaque démarrage du conteneur. Après un redémarrage sans rebuild (Docker ou machine), `/tmp/venv` avait disparu : plus de `python`/`pytest`/`ruff`, et chaque terminal affichait `/home/vscode/.zshrc:source:21: no such file or directory: /tmp/venv/bin/activate`. Le venv n'était créé que par `postCreateCommand.sh`, qui ne tourne qu'à la création du conteneur.

Correction (option 1 de l'issue, branche `86-devcontainer-tmpvenv-disparaît-…`) : le venv reste dans `/tmp/venv` et `postStartCommand` le recrée s'il manque. Appliquée au dépôt et au squelette (R1.5), même si le dépôt n'a pas docker-in-docker.

Spécification : [commentaire de l'issue #86](https://github.com/castorfou/PyFoundry/issues/86#issuecomment-6395136774).

---

## Travaux de la branche

### Nouveau script `.devcontainer/scripts/ensure_venv.sh`

Identique dans `.devcontainer/scripts/` et `{{ cookiecutter.project_slug }}/.devcontainer/scripts/` (testé).

- `VENV_HOME="${VENV_HOME:-/tmp/venv}"`, `PYTHON_VERSION="${PYTHON_VERSION:-3.11}"` (fourni par `containerEnv`). Les deux sont surchargeables pour les tests.
- Teste `-x "$VENV_HOME/bin/python"`, pas le dossier : un venv à moitié créé est refait.
- Venv absent : `uv venv "$VENV_HOME" --python "$PYTHON_VERSION"`, puis `VIRTUAL_ENV="$VENV_HOME" uv sync --active --all-extras`.
- Venv présent : ne fait rien (démarrage normal instantané, sans réseau), sauf avec `--sync`.
- Échec d'`uv` : message avec la commande de contournement, `exit 1`.

### `devcontainer.json` (dépôt et squelette)

`"postStartCommand": "bash .devcontainer/scripts/ensure_venv.sh && echo '🚀 … - Environnement prêt!'"`, avec un commentaire JSONC au-dessus.

### `postCreateCommand.sh` (dépôt et squelette)

- `create_python_environment` délègue à `bash .devcontainer/scripts/ensure_venv.sh --sync`, puis `source /tmp/venv/bin/activate` : les étapes suivantes (`setup_pre-commit`) utilisent `pre-commit` du venv.
- Nouvelle fonction `setup_venv_activation`, appelée par `config_zsh` : supprime l'ancienne ligne exacte `source /tmp/venv/bin/activate` du `.zshrc` (`sed -i '\#^source /tmp/venv/bin/activate$#d'`), puis ajoute `[[ ! -f /tmp/venv/bin/activate ]] || source /tmp/venv/bin/activate` via `ensure_zshrc_line`.

### Tests

- `tests/test_ensure_venv.py` (nouveau, 23 tests) :
  - câblage : `postStartCommand`, script identique, délégation de `create_python_environment` (fixture `devcontainer_dir` : `repo` / `default` / `docker_in_docker`) ;
  - `ensure_venv.sh` avec un faux `uv` dans `PATH` qui journalise `"$*|VIRTUAL_ENV=…"` et crée `bin/python` sur `uv venv` : venv absent, présent, `--sync`, dossier sans interpréteur, échec d'`uv` ;
  - `.zshrc` : `ensure_zshrc_line` + `setup_venv_activation` extraites par regex (même `extract_function` que `tests/test_post_create_command.py`) et exécutées avec `HOME=tmp_path`.
- `tests/test_persistent_home.py` : `test_post_create_builds_venv_in_tmp` suit le nouvel invariant (défaut `VENV_HOME` du script, appel `--sync`, ligne protégée).

---

## Apprentissages clés

### Le tmpfs n'existe qu'avec docker-in-docker réellement installé

`/usr/local/share/docker-init.sh` (installé par la feature) monte le tmpfs au démarrage. Premier test utilisateur : `findmnt /tmp` vide, pas de `docker` ni de `docker-init.sh`. VS Code avait rouvert un ancien conteneur du même dossier (`/tmp/mon-projet-data-science`), construit sans la feature. Il a fallu « Rebuild Container Without Cache ». Pour diagnostiquer : `command -v docker && findmnt /tmp` doit afficher `tmpfs`.

### Le venv tient dans le tmpfs dès la création

Le point d'entrée monte le tmpfs avant `postCreateCommand` : le venv est créé dans le tmpfs, et un redémarrage l'efface toujours. Vérifié de bout en bout : venv daté 09:23, redémarrage, venv recréé à 09:33 par `postStartCommand`, terminal sans erreur.

### `UV_PYTHON` pointe sur l'interpréteur du venv

`containerEnv` définit `UV_PYTHON=/tmp/venv/bin/python`, absent quand le venv manque : `uv venv` doit recevoir `--python` explicitement.

### Un mot dans un commentaire peut casser un test négatif

`test_docker_in_docker_disabled_by_default` vérifie que `"docker-in-docker"` n'apparaît pas dans le `devcontainer.json` généré par défaut. Un commentaire qui citait la feature l'a fait échouer : il a été reformulé (« /tmp peut être un tmpfs vidé au démarrage »).

### Un essai réel d'`uv sync` dans le dépôt réécrit `uv.lock`

Lancer `ensure_venv.sh` dans `/workspaces/PyFoundry` avec uv 0.13.0 a réécrit `uv.lock` (`revision = 3` → `5`, marqueurs simplifiés). C'est un effet de bord de l'essai, annulé par `git checkout -- uv.lock`. Le comportement existait déjà dans `postCreateCommand.sh` (`uv sync` sans `--frozen`).

### Ancienne ligne du `.zshrc`

Le HOME est persistant (#59) : `ensure_zshrc_line` ne fait qu'ajouter, il aurait laissé l'ancienne ligne non protégée à côté de la nouvelle. D'où le `sed` de migration avant l'ajout.

---

## Vérification

- `pytest tests` : 247 passed, 1 skipped.
- `ruff check tests/ docs/`, `mypy`, `pre-commit run` sur les fichiers modifiés : propres.
- Essai réel du script avec uv : 10 s pour recréer le venv, puis aucune action au démarrage suivant.
- Test utilisateur sur un projet généré avec `docker_in_docker=y` : `/tmp` en tmpfs, redémarrage sans rebuild, venv recréé, `python`/`pytest`/`ruff` dans `/tmp/venv/bin`, aucune erreur au terminal.
