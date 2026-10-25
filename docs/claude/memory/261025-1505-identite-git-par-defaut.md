# Issue #94 — L'identité git par défaut restait dans `.git/config`

## Résumé

Dans un projet généré, tous les commits avaient pour auteur `Default User`, avec une adresse du domaine d'entreprise,, même après la configuration d'une identité globale. Constaté sur `castorfou/google-to-synology-photos` (PyFoundry 1.0.0).

Cause : au premier build, le HOME est neuf et il n'y a pas d'identité globale. `setup_git` écrivait donc une identité par défaut dans la config **locale** pour que « Initial commit » réussisse. Elle y restait, et la config locale l'emporte sur la globale. Rien ne le signalait.

Travail sur la branche `94-postcreatecommand-lidentité-git-par-défaut-default-user-defaultmichelincom-reste-dans-gitconfig`.

Spécifications validées : [commentaire de l'issue #94](https://github.com/castorfou/PyFoundry/issues/94#issuecomment-6398593754).

Décisions de l'utilisateur :

- **Nettoyage automatique** des projets déjà générés au rebuild, plutôt qu'une procédure manuelle. Il n'y a donc pas de note de migration et la prochaine release n'est pas une majeure.
- **Cheatsheet docker** : remplacer le registre interne par un exemple public.

---

## Solution

### `setup_git` (`.devcontainer/postCreateCommand.sh`, dépôt et squelette, code identique)

- **Nouveau dépôt** : `git init`, `git add .`, puis :
  - si `git config user.email` renvoie une identité, `git commit` normal ;
  - sinon, identité ponctuelle `git -c user.name=… -c user.email=… commit`, jamais écrite dans `.git/config` : `$GITHUB_USERNAME <$GITHUB_USERNAME@users.noreply.github.com>` (variable déjà dans `containerEnv`), sinon `PyFoundry <pyfoundry@users.noreply.github.com>`. Un avertissement `⚠️` affiche ensuite les deux `git config --global` à lancer.
- **Dépôt existant** : si la config locale porte exactement `Default User` **et** l'ancienne adresse par défaut, les deux clés sont retirées (`git config --local --unset`). Toute autre identité locale reste intacte.

### `docs/cheatsheets/docker.md` (dépôt et squelette, identiques)

`docker login ghcr.io` avec un token GitHub, image `ghcr.io/astral-sh/uv:python3.11-bookworm-slim`, conteneur `mon-conteneur`. La note sur l'umask, propre à l'image interne, a été retirée.

---

## Tests — `tests/test_setup_git.py`

Fixture `setup_git` paramétrée `repo`/`skeleton`, avec `extract_function` de `tests/test_post_create_command.py` (même modèle que `setup_pre-commit`).

Isolation de l'environnement git :

- `GIT_CONFIG_GLOBAL` pointe vers un fichier temporaire vide, avec `GIT_CONFIG_NOSYSTEM=1` ;
- les variables `GIT_*`, `GITHUB_*` et `EMAIL` sont retirées de l'environnement, sinon git ou le script trouvent une identité.

Cas couverts :

- sans identité, avec `GITHUB_USERNAME` : adresse noreply, rien en local, avertissement affiché ;
- sans identité ni `GITHUB_USERNAME` : identité PyFoundry ;
- avec une identité globale : elle est utilisée, sans avertissement ;
- rebuild avec l'ancienne identité : elle est retirée ;
- rebuild avec une autre identité locale : elle est conservée ;
- `test_no_internal_domain` : aucun fichier du dépôt (`git ls-files --cached --others --exclude-standard`) ni du projet généré ne contient le domaine, sauf `postCreateCommand.sh` (nettoyage) et `CHANGELOG.md`.

Pièges :

- Le fichier de test contenait lui-même le domaine. La chaîne est donc assemblée (nom et extension concaténés).
- Un premier `rglob` sur la racine ramassait `__pycache__` et les caches. `git ls-files` évite ce problème.
- `REPO_DEVCONTAINER` s'importe depuis `tests.devcontainer_utils`, pas depuis `test_post_create_command` : sinon mypy signale `attr-defined`.

---

## Points saillants

- Pour qu'un commit initial réussisse sans identité, utiliser `git -c user.name=… -c user.email=… commit` : rien n'est écrit dans `.git/config`.
- Tester l'identité **effective** avec `git config user.email`, pas seulement `--global` : une identité locale ou système suffit.
- `mypy tests/` remontait 5 erreurs avant ce travail (stubs `yaml`, une annotation dans `test_configurations.py`). Aucune n'a été ajoutée.
