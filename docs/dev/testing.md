# Guide de Test du Template PyFoundry

Ce guide explique comment tester le template PyFoundry lors du développement.

## Types de Tests

### 1. Tests Automatisés (pytest)

Les tests automatisés utilisent `pytest-cookies` pour générer des projets temporaires et vérifier leur configuration.

```bash
# Depuis le devcontainer PyFoundry
source /tmp/venv/bin/activate && pytest tests -v

# Un fichier spécifique
pytest tests/test_template_generation.py -v

# Un test spécifique
pytest tests/test_template_generation.py::test_node_enabled_when_requested -v
```

**Avantages** :

- Rapide et automatisé
- Vérifie la structure et la configuration
- Couverture complète (37+ tests)

**Limitations** :

- Ne teste pas l'expérience utilisateur complète
- Ne vérifie pas que les outils fonctionnent réellement dans le projet généré

### 2. Test Manuel du Projet Généré

Pour tester avec vos modifications locales (y compris non commitées), utiliser `cookiecutter` plutôt que `cruft`.

#### Différence cruciale : cruft vs cookiecutter

- **`cruft create`** : utilise Git, ne voit que les fichiers **commités**
- **`cookiecutter`** : lit le filesystem, voit **tous les fichiers** (commités ou non)

#### Workflow de test manuel

```bash
# 1. Nettoyer
rm -rf ~/temp/mon-projet-data-science

# 2. Générer avec cookiecutter (modifications non commitées visibles)
cd ~/temp
cookiecutter /workspaces/PyFoundry --no-input

# 3. Avec des options spécifiques
cookiecutter /workspaces/PyFoundry --no-input \
  --extra-context '{"docker_in_docker": "y"}'

# 4. Ouvrir dans VS Code et tester le devcontainer
code ~/temp/mon-projet-data-science
# → "Reopen in Container" dans VS Code
```

#### Test depuis une branche commitée (via cruft)

```bash
# Depuis l'hôte, après avoir pushé la branche
cd ~/temp && rm -rf mon-projet-data-science
cruft create https://github.com/castorfou/PyFoundry.git \
  -c 44-integrer-docker-in-docker \
  --no-input \
  --extra-context '{"docker_in_docker": "y"}'
code mon-projet-data-science
```

## Tests Spécifiques par Fonctionnalité

### Tester une option conditionnelle (ex. `docker_in_docker`)

```bash
# Option désactivée (défaut)
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input
grep -c "docker-in-docker" mon-projet-data-science/.devcontainer/devcontainer.json
# → doit retourner 0

# Option activée
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input --extra-context '{"docker_in_docker": "y"}'
grep "docker-in-docker" mon-projet-data-science/.devcontainer/devcontainer.json
# → doit montrer la feature
```

### Tester le devcontainer

```bash
# Vérifier que devcontainer.json est valide (JSONC), depuis la racine du dépôt PyFoundry
python -c "
from pathlib import Path
from tests.devcontainer_utils import parse_jsonc
parse_jsonc(Path.home() / 'temp/mon-projet-data-science/.devcontainer/devcontainer.json')
print('JSON valide')
"

# Tester réellement : ouvrir dans VS Code
code ~/temp/mon-projet-data-science
# Puis "Reopen in Container"
```

### Tester la conformité pre-commit du projet généré

Le `.pre-commit-config.yaml` de PyFoundry exclut `{{ cookiecutter.project_slug }}/` de tous les hooks, à cause de la syntaxe Jinja. Les fichiers du squelette ne sont donc jamais nettoyés au commit. Ces tests prennent le relais en CI :

- `tests/test_configurations.py` rend le template (défaut, `use_node=y`, `docker_in_docker=y`) et vérifie ce que contrôlent `end-of-file-fixer`, `trailing-whitespace` et `check-json` : un seul retour à la ligne final, aucun espace en fin de ligne, JSON valides. Les exclusions sont lues dans le `.pre-commit-config.yaml` généré, et seuls les fichiers que git suivrait sont vérifiés.
- `tests/test_configurations.py` exécute aussi la commande du hook local `no-venv-at-root` (dépôt et projet généré) dans un dossier temporaire, avec et sans `.venv`.
- `tests/test_post_create_command.py` exécute `setup_pre-commit` (dépôt et projet généré) dans un dépôt temporaire, avec un faux `pre-commit` et du travail en cours : un rebuild ne doit commiter que `.pre-commit-config.yaml`.

Si un test signale une fin de fichier incorrecte sur un fichier qui se termine par un bloc Jinja, vérifier le rendu des deux branches : un `{% if %}` faux en fin de fichier laisse souvent une ligne vide en trop. Le contrôle d'espaces Jinja (`{%- if %}`, `{%- endif %}`) règle le problème.

### Tester l'identité git

`tests/test_setup_git.py` exécute `setup_git` (dépôt et projet généré) dans un dossier temporaire, avec une config globale vide (`GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`). Les variables `GIT_*`, `GITHUB_*` et `EMAIL` sont retirées de l'environnement, sinon git trouve une identité :

- sans identité : commit initial sous l'adresse noreply de `GITHUB_USERNAME`, ou sous `PyFoundry`, avec un avertissement, et rien dans `.git/config` ;
- avec une identité globale : elle est utilisée, sans avertissement ;
- au rebuild : l'ancienne identité `Default User` est retirée, toute autre identité locale est conservée ;
- aucun fichier du dépôt ni du projet généré ne cite le domaine interne, sauf `postCreateCommand.sh` (pour le nettoyage) et `CHANGELOG.md`.

### Tester le fuseau horaire

`tests/test_timezone.py` couvre le dépôt et les projets générés (défaut et `docker_in_docker=y`) :

- le `/etc/localtime` de l'hôte est monté sur `/etc/localtime.host`, jamais sur `/etc/localtime` ;
- `TZ` n'est pas transmis par `containerEnv` ni par `remoteEnv` ;
- `setup_timezone` est appelé juste après `update_system` ;
- `setup_timezone` est exécuté réellement, avec un faux `sudo` et de faux dossiers `zoneinfo` et `/etc` créés dans `tmp_path` (variables `HOST_LOCALTIME`, `ZONEINFO_DIR`, `ETC_DIR`). Trois cas : zone connue, zone inconnue, fichier de l'hôte absent ou vide.

Dans le conteneur, on vérifie depuis un terminal VS Code :

```bash
date                                       # heure locale de l'hôte
TZ=UTC date                                # heure UTC
readlink /etc/localtime; cat /etc/timezone # zone de l'hôte, ex. Europe/Paris
```

Pour vérifier avec le vrai pre-commit :

```bash
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input
cd mon-projet-data-science && git init -q && git add -A && pre-commit run --all-files
```

### Tester l'authentification GitHub

`tests/test_github_auth.py` couvre le dépôt et les projets générés (défaut et `docker_in_docker=y`) :

- le montage `~/.config/gh-devcontainers` → `/home/vscode/.config/gh` ; `initializeCommand` crée la source en `700` ;
- `postCreateCommand.sh` ne contient pas `gh auth login`, et `config_zsh` ajoute le hook `gh_login.sh` à `.zshrc` ;
- `setup_gh_credential_helper` est exécuté dans un dépôt temporaire, avec un faux `gh` puis sans `gh` ;
- `gh_login.sh` est exécuté avec un faux `gh` qui journalise ses appels (`FAKE_GH_LOG`) et un marqueur dans `tmp_path` (`GH_LOGIN_MARKER`). Le test vérifie que le script reste silencieux si un token existe, sans appel à `gh auth status` ; qu'il lance un login `--web` une seule fois par conteneur ; qu'il sort en `0` quand le login échoue ou que `gh` est absent.

Le parcours réel se vérifie sur l'hôte : générer un projet, le rebuild, ouvrir un terminal (le navigateur de l'hôte s'ouvre), puis rebuild à nouveau : `gh auth status` doit rester connecté.

### Tester la config Claude Code partagée

`tests/test_claude_auth.py` couvre le dépôt et les projets générés (défaut et `docker_in_docker=y`) :

- le montage `~/.config/claude-devcontainers` → `/home/vscode/.claude`, `CLAUDE_CONFIG_DIR`, et le montage de `.claude-ide` sur `~/.claude/ide` ;
- `initializeCommand` crée ces dossiers en `700`, puis lance `migrate_claude_history.sh` avant `check_mounts.sh` ;
- `migrate_claude_history.sh` est exécuté avec un faux `HOME` (`tmp_path`). Le test vérifie qu'il copie les conversations, la mémoire et les checkpoints sans écraser l'existant, qu'il ajoute `history.jsonl` à la fin, qu'il ne tourne qu'une fois, qu'il ne copie pas la connexion, et qu'il sort en `0` sans ancien historique ou quand le dossier partagé est en lecture seule.

Le parcours réel se vérifie sur l'hôte :

1. Créer un projet depuis `main` (`cruft create … --checkout main`), l'ouvrir et démarrer une conversation.
2. Le mettre à jour vers la branche (`cruft update --checkout <branche>`, qui ne voit que les commits), puis rebuild.
3. Après la connexion, la conversation est là.
4. Au rebuild suivant, la connexion est conservée.

### Tester la gestion des versions

`tests/test_versioning.py` garde cohérentes les trois copies de la version (voir [Versions et releases](release.md)) :

- la version de `pyproject.toml` est en SemVer strict et égale à `_pyfoundry_version` de `cookiecutter.json`. Le projet généré a cette variable dans son contexte et dans son fichier `TEMPLATE_VERSION`. Un vrai `cruft update`, sur un mini-template git passé de 1.0.0 à 1.1.0, met `TEMPLATE_VERSION` à jour ;
- `CHANGELOG.md` commence par `## [Non publié]`, a une section datée pour la version courante et couvre l'historique depuis la 0.4.0 ;
- `.github/scripts/release.py` est lancé en sous-processus, avec `--root` pointant vers une copie des fichiers dans `tmp_path`. `check-tag` refuse un tag d'une autre version, un tag sans `v`, un `cookiecutter.json` désaligné ou une version absente du CHANGELOG. `notes` renvoie le corps exact d'une section ;
- `release.py plan` tourne dans un dépôt git temporaire, tagué à la version courante, où `bump()` simule une PR de release. Il ne publie pas si la version est inchangée ; il publie sur une hausse cohérente (`release=true` dans `GITHUB_OUTPUT`) ; il échoue sur une baisse, un tag existant, une version sous la dernière release, un `cookiecutter.json` désaligné, une section du CHANGELOG absente ou vide. `GITHUB_OUTPUT` est retiré de l'environnement hérité, pour ne jamais écrire dans les sorties du job de CI ;
- `release.yml` se déclenche sur un push vers `main`, compare au commit précédent (`fetch-depth: 0`), ne teste et ne publie que si `plan` a décidé une release, crée tag et release par un seul `gh release create --target`, n'accorde `contents: write` qu'à `publish` et tire ses notes de `notes`, sans `git log`. `test-template.yml` lance `plan` sur les pull requests ;
- `/fix-issue` contient l'étape CHANGELOG et reste identique dans le dépôt et le squelette.

### Tester le HOME persistant

Les tests automatisés couvrent la configuration :

- `tests/test_persistent_home.py` : montages, `initializeCommand`, venv `/tmp/venv` (dont `UV_PROJECT_ENVIRONMENT`) et `seed_home`, sur le devcontainer du dépôt et sur les projets générés. `test_initialize_command_creates_nested_mountpoints` déduit des `mounts` chaque point de montage imbriqué dans la source d'un autre montage (helper `nested_mountpoints` de `tests/devcontainer_utils.py`), et vérifie qu'`initializeCommand` le crée. Un nouveau montage dans le HOME est couvert sans modifier le test.
- `tests/test_ensure_venv.py` : `ensure_venv.sh`, lancé par `postStartCommand`, exécuté avec un faux `uv` dans `PATH` qui journalise ses appels et crée `bin/python` sur `uv venv`. `VENV_HOME` redirige le venv dans un `tmp_path`. Les cas couverts : venv absent, présent, `--sync`, dossier sans interpréteur, échec d'`uv`. `setup_venv_activation` est extraite de `postCreateCommand.sh` et exécutée avec un `HOME` redirigé, pour vérifier la ligne protégée du `.zshrc` et le retrait de l'ancienne.
- `tests/test_cruft_update_skill.py` : la skill `/cruft-update` est identique dans le dépôt et dans un projet généré, ce qui prouve que `_copy_without_render` empêche Jinja de rendre le `{{ cookiecutter.project_slug }}` qu'elle cite. Le script `template_update.py` est lancé en `subprocess` dans des dépôts git temporaires : `categorie` sur des chemins de chaque catégorie, `rejets` sur un `.rej` et sur un vrai conflit produit par `git apply -3` (comme cruft), `changelog` sur un faux template à deux commits, en local et par clone depuis l'URL `file://` de `.cruft.json`. Le cycle complet, avec un vrai `cruft update`, se teste à la main : projet généré depuis un ancien commit (`cruft create --checkout <commit>`, puis `checkout` remis à `null` dans `.cruft.json`), une ligne touchée par le template personnalisée, puis « mets à jour le projet depuis le template ».
- `tests/test_check_mounts.py` : exécute `check_mounts.sh` dans un `tmp_path` avec un `HOME` redirigé (source manquante, résolution des variables, permissions `.ssh`, points de montage imbriqués). La classe `TestJsonc` passe les mêmes échantillons JSONC (commentaire en fin de ligne, `//` et `/* */` dans des chaînes, virgules finales) au script et à `parse_jsonc` de `tests/devcontainer_utils.py`, pour garder les deux parseurs alignés. Un dossier root ne se crée pas sans `sudo` : `CHECK_MOUNTS_UID` remplace l'uid attendu pour simuler un autre propriétaire. `test_repo_configuration_passes_once_sources_exist` exécute les vrais `mkdir` d'`initializeCommand`, puis vérifie que la config du dépôt passe sans `[WARN]`.

Le comportement réel ne se vérifie que sur l'hôte. Après un rebuild du conteneur :

```bash
mount | grep /home/vscode   # HOME, .ssh (ro), .cache/pre-commit, .config/gh, .claude, .claude/ide, .cache/uv
echo $VIRTUAL_ENV           # /tmp/venv
```

Pour le venv recréé au démarrage, générez un projet avec `docker_in_docker=y`, vérifiez `findmnt /tmp` (`tmpfs`), puis redémarrez le conteneur sans rebuild : `/tmp/venv/bin/python` doit exister et le terminal s'ouvrir sans erreur.

Puis faites un **second** rebuild : `~/.claude`, `gh auth status` et `~/.zsh_history` doivent être conservés.

Sur l'hôte, aucun dossier du HOME persistant ne doit appartenir à root :

```bash
find ~/.devcontainer/homes -mindepth 1 -maxdepth 3 -user root   # sortie vide
```

Pour vérifier les montages sans rebuild, sur l'hôte à la racine du projet :

```bash
bash .devcontainer/scripts/check_mounts.sh --host
```

### Tester MkDocs

```bash
cd ~/temp/mon-projet-data-science
uv sync --active --extra doc
uv run --active mkdocs build --strict
```

### Tester la qualité du code

```bash
cd ~/temp/mon-projet-data-science
uv sync --active --all-extras
uv run --active ruff check .
uv run --active pytest
```

## Bonnes Pratiques

### Avant de commiter

```bash
# 1. Tests automatisés
source /tmp/venv/bin/activate && pytest tests -v

# 2. Lint
ruff check tests/ docs/ --fix

# 3. Test manuel rapide
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input
```

### Nettoyage

```bash
rm -rf ~/temp/mon-projet-data-science
```

## Debugging

### Les tests échouent

```bash
# Vérifier depuis le dossier template
cd /workspaces/PyFoundry
pytest tests/ -v --tb=short
```

### Le projet généré manque des fichiers

- Si vous utilisez `cruft create` : les fichiers non commités ne sont pas inclus
- Solution : utiliser `cookiecutter` à la place, ou commiter vos changements

### Erreurs de template Jinja2

```bash
# Générer avec mode verbeux
cookiecutter /workspaces/PyFoundry --no-input -v 2>&1 | head -50
```

## Ressources

- [pytest-cookies documentation](https://pytest-cookies.readthedocs.io/)
- [Cookiecutter documentation](https://cookiecutter.readthedocs.io/)
- [Cruft documentation](https://cruft.github.io/cruft/)
