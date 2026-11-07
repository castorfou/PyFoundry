# Issue #110 — Nom et description échappés dans les fichiers structurés du projet généré

## Résumé

Le squelette écrivait `description` et `project_name` sans guillemets ni échappement dans des fichiers YAML, TOML et JSON. Une description contenant « : » donnait un `mkdocs.yml` invalide (`mapping values are not allowed here`), donc `mkdocs build --strict` et `docs.yml` échouaient dès la génération (cas réel : castorfou/transcripteur#14). Un `"` ou un `\` cassait de la même façon `pyproject.toml`, `devcontainer.json` et le `package.json` écrit par `postCreateCommand.sh`.

Décisions de l'utilisateur :
- **Pas de `tojson`**, contrairement à la proposition de l'issue : il écrit `é` et `'` à la place des accents et des apostrophes. On échappe seulement `\` puis `"`, entre guillemets doubles.
- **Périmètre élargi** : la description (`mkdocs.yml`, `pyproject.toml`, `package.json`), et aussi `project_name` (`site_name`, `devcontainer.json`).

Spécification : [commentaire de l'issue #110](https://github.com/castorfou/PyFoundry/issues/110#issuecomment-6714094778).

## Changements

| Fichier | Changement |
|---------|------------|
| `{{ cookiecutter.project_slug }}/mkdocs.yml` | `site_name` et `site_description` entre guillemets doubles, avec le filtre d'échappement |
| `{{ cookiecutter.project_slug }}/pyproject.toml` | `description` avec le filtre |
| `{{ cookiecutter.project_slug }}/.devcontainer/devcontainer.json` | `name` et `containerEnv.PROJECT_NAME` avec le filtre ; `postStartCommand` affiche `$PROJECT_NAME` (variable de `containerEnv`) au lieu d'insérer le nom dans une chaîne shell entre apostrophes |
| `{{ cookiecutter.project_slug }}/.devcontainer/postCreateCommand.sh` | heredoc du `package.json` en `<< 'EOF'` (plus d'expansion de `$`, `` ` ``, `\`), description avec le filtre |
| `tests/test_special_characters.py` | génération avec un nom et une description contenant `:`, `"`, `\`, `'`, accents, `$HOME`, `` `ls` `` : relecture de `mkdocs.yml` (loader qui ignore `!!python/name`), `pyproject.toml` (`tomllib`), `devcontainer.json` (`parse_jsonc`), exécution de l'`echo` de `postStartCommand` et du heredoc du `package.json`, `mkdocs build --strict` |

## Points saillants

- Le filtre, valable à la fois en YAML (chaîne double-quoted), en TOML (basic string) et en JSON :
  `"{{ cookiecutter.x | replace('\\', '\\\\') | replace('"', '\\"') }}"`. Échapper `\` avant `"`, sinon les `\` ajoutés sont doublés.
- Les littéraux Jinja traitent les `\` comme Python : `'\\'` vaut un seul `\`.
- Pour lire `mkdocs.yml` dans un test, `yaml.safe_load` échoue sur `!!python/name:` : sous-classer `yaml.SafeLoader` et ajouter un `add_multi_constructor("tag:yaml.org,2002:python/name:", …)`.
- Hors d'un dépôt git, `mkdocs build --strict` échoue sur l'avertissement de `git-revision-date-localized`. Un projet généré à la main pour un test doit d'abord passer par `git init` et un commit.
- Hors périmètre : l'`echo` de la ligne 9 de `postCreateCommand.sh`, le slug déduit d'un nom qui contient « : ».
- Pas de migration : `cruft update` suffit.
