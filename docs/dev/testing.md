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
# Vérifier que devcontainer.json est valide (JSON avec commentaires)
python -c "
import re, json
content = open('mon-projet-data-science/.devcontainer/devcontainer.json').read()
content = re.sub(r'//[^\n]*', '', content)
json.loads(content)
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

- le montage `~/.config/gh-devcontainers` → `/home/vscode/.config/gh` ; `initializeCommand` crée la source en `700` et crée `.config` dans le HOME persistant ;
- `postCreateCommand.sh` ne contient pas `gh auth login`, et `config_zsh` ajoute le hook `gh_login.sh` à `.zshrc` ;
- `setup_gh_credential_helper` est exécuté dans un dépôt temporaire, avec un faux `gh` puis sans `gh` ;
- `gh_login.sh` est exécuté avec un faux `gh` qui journalise ses appels (`FAKE_GH_LOG`) et un marqueur dans `tmp_path` (`GH_LOGIN_MARKER`). Le test vérifie que le script reste silencieux si un token existe, sans appel à `gh auth status` ; qu'il lance un login `--web` une seule fois par conteneur ; qu'il sort en `0` quand le login échoue ou que `gh` est absent.

Le parcours réel se vérifie sur l'hôte : générer un projet, le rebuild, ouvrir un terminal (le navigateur de l'hôte s'ouvre), puis rebuild à nouveau : `gh auth status` doit rester connecté.

### Tester la config Claude Code partagée

`tests/test_claude_auth.py` couvre le dépôt et les projets générés (défaut et `docker_in_docker=y`) :

- le montage `~/.config/claude-devcontainers` → `/home/vscode/.claude`, `CLAUDE_CONFIG_DIR`, et le montage de `.claude-ide` sur `~/.claude/ide` ;
- `initializeCommand` crée ces dossiers en `700` et le point de montage `.claude` dans le HOME persistant, puis lance `migrate_claude_history.sh` avant `check_mounts.sh` ;
- `migrate_claude_history.sh` est exécuté avec un faux `HOME` (`tmp_path`). Le test vérifie qu'il copie les conversations, la mémoire et les checkpoints sans écraser l'existant, qu'il ajoute `history.jsonl` à la fin, qu'il ne tourne qu'une fois, qu'il ne copie pas la connexion, et qu'il sort en `0` sans ancien historique ou quand le dossier partagé est en lecture seule.

Le parcours réel se vérifie sur l'hôte :

1. Créer un projet depuis `main` (`cruft create … --checkout main`), l'ouvrir et démarrer une conversation.
2. Le mettre à jour vers la branche (`cruft update --checkout <branche>`, qui ne voit que les commits), puis rebuild.
3. Après la connexion, la conversation est là.
4. Au rebuild suivant, la connexion est conservée.

### Tester le HOME persistant

Les tests automatisés couvrent la configuration :

- `tests/test_persistent_home.py` : montages, `initializeCommand`, venv `/tmp/venv` (dont `UV_PROJECT_ENVIRONMENT`) et `seed_home`, sur le devcontainer du dépôt et sur les projets générés.
- `tests/test_check_mounts.py` : exécute `check_mounts.sh` dans un `tmp_path` avec un `HOME` redirigé (source manquante, résolution des variables, permissions `.ssh`).

Le comportement réel ne se vérifie que sur l'hôte. Après un rebuild du conteneur :

```bash
mount | grep /home/vscode   # HOME, .ssh (ro), .cache/pre-commit, .config/gh, .claude, .claude/ide, .cache/uv
echo $VIRTUAL_ENV           # /tmp/venv
```

Puis faites un **second** rebuild : `~/.claude`, `gh auth status` et `~/.zsh_history` doivent être conservés.

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
