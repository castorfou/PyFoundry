# Issue #102 — projet généré propre après la création (`.pre-commit-config.yaml`, `mkdocs.yml`)

## Résumé

Juste après la création d'un projet, `git status` montrait `.pre-commit-config.yaml` et `mkdocs.yml` modifiés, et `git log` ne contenait que `Initial commit`. Relevé pendant le test manuel de #87.

Deux causes indépendantes :
1. `setup_pre-commit` lance `pre-commit autoupdate`, puis `git commit -- .pre-commit-config.yaml`. Au premier build, le HOME est neuf et n'a pas d'identité git : la copie du `~/.gitconfig` de l'hôte par VS Code n'arrive qu'**après** `postCreateCommand`. Le commit échouait (`Author identity unknown`), puis « ⚠️ Commit impossible ». `setup_git` avait un repli d'identité depuis #94, `setup_pre-commit` n'en avait pas.
2. `run_mkdocs_repo_url_update`, dernière étape de `postCreateCommand.sh`, lançait `update_mkdocs_repo_url.sh`, qui insérait `repo_url` depuis le remote `origin`, et rien ne commitait ce changement.

Correction (branche `102-devcontainer-pre-commit-configyaml-…`) : une fonction commune de commit avec identité de repli, et `repo_url` rendu par Jinja.

Spécification : [commentaire de l'issue #102](https://github.com/castorfou/PyFoundry/issues/102#issuecomment-6402160498).

---

## Travaux de la branche

### `postCreateCommand.sh` (dépôt et squelette, fonctions identiques)

- Nouvelle fonction `git_commit_with_fallback`, définie juste avant `setup_git`, qui prend les arguments de `git commit` :
  - avec une identité (`git config user.email` non vide) → `git commit "$@"` ;
  - sans identité → `git -c user.name="${GITHUB_USERNAME:-PyFoundry}" -c user.email="${GITHUB_USERNAME:-pyfoundry}@users.noreply.github.com" commit "$@"`. Rien n'est écrit dans `.git/config`, où l'identité masquerait ensuite la globale (#94).
  - L'avertissement « Identité Git non configurée : commits faits sous … » n'est affiché qu'une fois par exécution (variable globale `IDENTITY_WARNED`), et seulement si le commit réussit.
- `setup_git` : le commit initial passe par `git_commit_with_fallback -m "Initial commit"`. Le bloc `if/else` d'identité est retiré.
- `setup_pre-commit` : `git_commit_with_fallback -m "chore: update pre-commit hooks to latest versions" -- .pre-commit-config.yaml`. « Commit impossible » reste pour les autres échecs.
- `run_mkdocs_repo_url_update` est supprimée (définition et appel).

### `repo_url`

- `{{ cookiecutter.project_slug }}/mkdocs.yml` : `repo_url: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}`, juste après `site_url`. C'est la même source que le remote construit par `setup_github` (SSH ou HTTPS, que le script normalisait vers la même URL https).
- `.devcontainer/scripts/update_mkdocs_repo_url.sh` est supprimé dans le dépôt et dans le squelette. Le `mkdocs.yml` de PyFoundry avait déjà `repo_url` en dur.

### Tests

- `tests/test_post_create_command.py` :
  - fixture `post_create_script` (dépôt ou projet généré) et helper `extract_functions` ;
  - `setup_precommit` extrait `git_commit_with_fallback` + `setup_pre-commit` ;
  - `without_identity(env)` retire `GIT_AUTHOR*`, `GIT_COMMITTER*`, `GITHUB_*`, `EMAIL`, et pose `GITHUB_USERNAME=octocat` ;
  - `test_hook_update_committed_without_identity` : auteur `octocat <octocat@users.noreply.github.com>`, seul `.pre-commit-config.yaml` commité, pas de `user.` dans `.git/config` ;
  - `test_fresh_project_is_clean_without_identity` : `setup_git` puis `setup_pre-commit` avec le faux pre-commit, puis `git status` vide, 2 commits et un seul avertissement.
- `tests/test_setup_git.py` : la fixture extrait aussi `git_commit_with_fallback`.
- `tests/test_mkdocs_integration.py` :
  - `test_repo_url_rendered_in_mkdocs_yml` lit la ligne par regex, pas avec `yaml.safe_load`, qui refuse les balises `!!python/name` de `mkdocs.yml` ;
  - `test_no_repo_url_update_script` couvre le dépôt et le projet généré.

L'auteur est vérifié, pas seulement la réussite du commit : sur un runner CI dont le nom d'hôte se résout, git déduit une identité tout seul (`runner@…`) et l'ancien code aurait réussi à commiter.

---

## Vérifications

- Reproduction en scratchpad, avant correction (HOME vide, `GIT_CONFIG_NOSYSTEM=1`, `setup_git` puis `setup_pre-commit` avec le vrai `pre-commit`) : `fatal: unable to auto-detect email address`, puis `.pre-commit-config.yaml` modifié.
- Même reproduction après correction : 2 commits sous `castorfou@users.noreply.github.com`, `git status` propre, `repo_url` présent.
- Test utilisateur sur un projet généré (HOME nettoyé par `clean_test_project.sh`) : même résultat.

## Pour les projets existants

`cruft update` supprime `update_mkdocs_repo_url.sh` et l'appel ; `mkdocs.yml` est un fichier mixte, et un `repo_url` déjà présent est gardé. Pas de migration.
