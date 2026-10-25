# Architecture du template

## Vision et principes

PyFoundry suit ces principes d'architecture :

### 🎯 Source de vérité unique
- **`pyproject.toml`** centralise toutes les configurations
- Évite la duplication entre `requirements.txt`, `setup.py`, etc.
- Configuration des outils (ruff, pytest) dans le même fichier

### 🔄 Reproductibilité
- **Devcontainer** garantit l'environnement identique
- **uv via devcontainer feature** pour des résolutions de dépendances déterministes
- **Versions épinglées** des outils critiques

### 🚀 Démarrage rapide
- **Configuration minimale** requise de l'utilisateur
- **Defaults intelligents** pour tous les outils
- **Automatisation maximale** du setup

## Structure technique

### Template Cookiecutter

```
PyFoundry/                                    # Dépôt du template
├── cookiecutter.json                        # Variables de templating
├── {{ cookiecutter.project_slug }}/         # Contenu généré
│   ├── .devcontainer/devcontainer.json     # Config environnement
│   ├── pyproject.toml                       # Config centralisée
│   └── ...
├── docs/                                     # Documentation MkDocs
├── tests/                                    # Tests du template
└── mkdocs.yml                               # Config documentation
```

### Variables Cookiecutter

```json
{
    "project_name": "Nom affiché",
    "project_slug": "nom-technique",
    "description": "Description courte",
    "python_version": "Version Python",
    "use_node": "Support Node.js (y/n)",
    "docker_in_docker": "Docker dans le Dev Container (y/n)"
}
```

**Logique de transformation** :
- `project_slug` auto-généré depuis `project_name`
- Normalisation des noms (minuscules, tirets)
- Validation des versions Python supportées

### Configuration devcontainer

```json
{
    "name": "{{ cookiecutter.project_name }}",
    "image": "mcr.microsoft.com/devcontainers/python:{{ cookiecutter.python_version }}-bookworm",
    "customizations": {
        "vscode": {
            "settings": {
                "python.defaultInterpreterPath": "/tmp/venv/bin/python",
                "python.venvPath": "/tmp"
            }
        }
    },
    "postCreateCommand": "chmod +x .devcontainer/postCreateCommand.sh && .devcontainer/postCreateCommand.sh"
}
```

**Choix techniques** :
- **Image officielle Microsoft** Python 3.12 pour la compatibilité
- **Devcontainer features** pour l'installation standardisée des outils
- **Script postCreateCommand** simplifié pour la configuration
- **Environnement virtuel `/tmp/venv`**, hors du HOME persistant, recréé à chaque rebuild, et au démarrage s'il manque
- **Features officielles** (uv) au lieu d'installation manuelle
- **Fuseau horaire de l'hôte** : fichier `/etc/localtime` de l'hôte monté à côté de celui du conteneur, appliqué par `setup_timezone`

### Devcontainer Features

```json
{
    "features": {
        "ghcr.io/astral-sh/uv/devcontainer-feature:latest": {}
    }
}
```

**Avantages des features** :
- **Installation standardisée** via les registres officiels
- **Gestion des dépendances** automatique
- **Chemins PATH** configurés correctement
- **Versions** gérées de manière cohérente
- **Maintenance** par les mainteneurs officiels

### Configuration de la timezone

Le devcontainer reprend le fuseau horaire de l'hôte. Le fichier `/etc/localtime` de l'hôte est monté en lecture seule sur `/etc/localtime.host` :

```json
"mounts": [
    "source=/etc/localtime,target=/etc/localtime.host,type=bind,consistency=cached,readonly"
]
```

La fonction `setup_timezone` de `postCreateCommand.sh` tourne juste après la mise à jour des paquets :

1. Elle cherche dans `/usr/share/zoneinfo` (hors `posix/` et `right/`) le fichier identique à `/etc/localtime.host`.
2. Si elle le trouve, `/etc/localtime` devient un lien vers cette zone (ex. `Europe/Paris`), dont le nom est écrit dans `/etc/timezone`. Le nom de zone sert aux bibliothèques qui le lisent (`tzlocal`, pandas), et tzdata conserve ce réglage lors de ses mises à jour.
3. Sinon, `/etc/localtime` pointe directement vers `/etc/localtime.host` : l'heure est juste, mais la zone n'a pas de nom.
4. Sans fichier de l'hôte, le conteneur reste en UTC.

**Deux pièges évités** :

- **Monter directement sur `/etc/localtime`.** Dans l'image, `/etc/localtime` est un lien vers `zoneinfo/Etc/UTC`, et Docker suit ce lien. Le fichier de l'hôte écraserait donc `Etc/UTC` : `TZ=UTC` ou `ZoneInfo("UTC")` donneraient l'heure locale, et la mise à jour de tzdata échouerait (`Invalid cross-device link`).
- **Transmettre `TZ` avec `${localEnv:TZ}`.** Quand `TZ` n'est pas défini sur l'hôte, ce qui est le cas courant, le conteneur reçoit `TZ=` vide, que glibc interprète comme UTC. `TZ` n'est donc pas défini dans le conteneur, et `/etc/localtime` fait foi.

### HOME persistant

Le HOME du conteneur (`/home/vscode`) est un bind mount d'un dossier de l'hôte propre au projet :

```json
"mounts": [
    "source=${localEnv:HOME}/.devcontainer/homes/${localWorkspaceFolderBasename}-${devcontainerId},target=/home/vscode,type=bind",
    "source=${localEnv:HOME}/.cache/pre-commit-devcontainers,target=/home/vscode/.cache/pre-commit,type=bind",
    "source=${localEnv:HOME}/.config/gh-devcontainers,target=/home/vscode/.config/gh,type=bind",
    "source=${localEnv:HOME}/.config/claude-devcontainers,target=/home/vscode/.claude,type=bind",
    "source=${localEnv:HOME}/.devcontainer/homes/${localWorkspaceFolderBasename}-${devcontainerId}/.claude-ide,target=/home/vscode/.claude/ide,type=bind",
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly",
    "source=${localEnv:HOME}/.cache/uv,target=/home/vscode/.cache/uv,type=bind,consistency=cached"
]
```

L'historique du shell et `~/.vscode-server` survivent ainsi aux rebuilds. Les caches pre-commit et uv, la config `gh` (connexion GitHub) et la config Claude Code sont partagés entre tous les devcontainers de l'hôte. Voir [Authentification GitHub](#authentification-github) et [Config Claude Code partagée](#config-claude-code-partagee).

Trois mécanismes complètent le montage :

- **`initializeCommand`**, exécuté sur l'hôte avant le montage, crée les dossiers sources et les points de montage imbriqués dans le HOME (`.ssh`, `.cache/uv`, `.cache/pre-commit`, `.config/gh`, `.claude`), pour que Docker ne les crée pas en root ; `~/.ssh`, `~/.config/gh-devcontainers`, `~/.config/claude-devcontainers` et `.claude-ide` sont créés en `700`. Il lance `.devcontainer/scripts/migrate_claude_history.sh` (voir [Config Claude Code partagée](#config-claude-code-partagee)), puis `.devcontainer/scripts/check_mounts.sh --host`. Ce script lit les `mounts` de `devcontainer.json` (JSONC : commentaires partout et virgules finales, les chaînes étant gardées intactes), résout `${localEnv:HOME}`, `${localWorkspaceFolderBasename}` et `${devcontainerId}`, signale chaque source absente avec la commande pour la créer, et contrôle les permissions de `~/.ssh`. Il sort en erreur si un montage est invalide. Il signale aussi, par un `[WARN]` non bloquant, chaque point de montage imbriqué qui n'appartient pas à l'utilisateur, avec la procédure pour le recréer (`rmdir` puis `mkdir`, conteneur arrêté).
- **`seed_home`** dans `postCreateCommand.sh` : le bind mount masque le HOME de l'image, donc `cp -rn /etc/skel/. "$HOME"` recopie `.bashrc`, `.profile`… sans écraser l'existant.
- **Venv dans `/tmp/venv`** : il reste hors du HOME persistant et est recréé à chaque rebuild depuis `uv.lock`, ce qui évite de conserver un venv lié à une ancienne image Python. Avec Docker-in-Docker, `/tmp` est un tmpfs vidé à chaque démarrage du conteneur : `postStartCommand` lance `.devcontainer/scripts/ensure_venv.sh`, qui recrée le venv si son interpréteur manque et ne fait rien sinon. `postCreateCommand.sh` passe par le même script, avec `--sync`. Le `.zshrc` n'active le venv que s'il existe (`[[ ! -f /tmp/venv/bin/activate ]] || source …`), car un terminal peut s'ouvrir avant la fin de `postStartCommand` (issue #86).

`~/.gitconfig` n'est plus monté : VS Code copie celui de l'hôte au démarrage.

Au premier build, il n'y a donc pas encore d'identité git. `setup_git` fait alors le commit initial avec une identité ponctuelle (`git -c user.name=… -c user.email=… commit`) : `<GITHUB_USERNAME>@users.noreply.github.com`, ou `pyfoundry@users.noreply.github.com` sans `GITHUB_USERNAME`. Rien n'est écrit dans `.git/config`, où l'identité masquerait ensuite la globale. Sur un dépôt existant, `setup_git` retire l'ancienne identité par défaut (`Default User`) que les versions précédentes y écrivaient (issue #94).

Le choix est détaillé dans l'ADR [0001 — HOME persistant](../adr/0001-persist-development-home.md).

### Authentification GitHub

`postCreateCommand.sh` ne lance pas `gh auth login`. Les commandes de cycle de vie (`postCreateCommand`, `postStartCommand`) tournent hors des terminaux VS Code, donc sans la variable `BROWSER` : `gh` ne pourrait pas ouvrir le navigateur, et le build attendrait l'utilisateur. Le conteneur n'ayant pas d'affichage graphique, la copie du code dans le presse-papiers échoue aussi, avec ou sans `xclip`.

- **`setup_gh_credential_helper`** (dans `setup_github`) délègue l'authentification HTTPS de `github.com` à `gh`, en config Git locale au projet. Il est configuré même sans token, car celui-ci peut arriver plus tard ou venir d'un autre devcontainer.
- **`.devcontainer/scripts/gh_login.sh`** est appelé par `~/.zshrc`, donc seulement dans les shells interactifs. S'il manque un token, ce que vérifie `gh auth token` sans appel réseau, il lance `gh auth login --web`. Dans un terminal VS Code, `BROWSER` ouvre la page dans le navigateur de l'hôte. Un marqueur dans `/tmp` limite la proposition à une fois par conteneur, et le script sort toujours en `0`, pour ne jamais casser le shell.
- **`~/.config/gh`** est monté depuis `~/.config/gh-devcontainers` sur l'hôte, comme le cache pre-commit : une seule connexion pour tous les devcontainers, qui survit aux rebuilds. Sans keyring dans le conteneur, le token y est stocké en clair, d'où la création du dossier en `700`.

### Config Claude Code partagée

Le dossier de config Claude Code est partagé par tous les devcontainers, comme la config `gh` : on se connecte une fois pour tous les projets.

- **`~/.claude`** est monté depuis `~/.config/claude-devcontainers` sur l'hôte, créé en `700` car il contient les tokens OAuth (`.credentials.json`).
- **`CLAUDE_CONFIG_DIR=/home/vscode/.claude`** (`containerEnv`) y place aussi `.claude.json` (le compte), qui est sinon à la racine du HOME. L'extension VS Code respecte cette variable.
- **Un dossier, et non des fichiers** : Claude Code réécrit `.credentials.json` et `.claude.json` par renommage atomique, ce qui casse un bind mount de fichier.
- **`~/.claude/ide`** reste propre au projet : il est monté depuis `<HOME persistant>/.claude-ide`. Un verrou `ide/*.lock` ne contient que le PID et le port de l'IDE. Vu d'un autre conteneur, ce PID est invisible et le verrou pourrait être supprimé comme périmé.

Ce qui devient commun : la connexion, les réglages utilisateur, les plugins installés et l'historique des prompts. Les conversations, la mémoire automatique et les réglages par projet restent séparés, car Claude Code les range par chemin (`/workspaces/<projet>`), comme sur l'hôte.

**Migration de l'historique.** Avant ce partage, l'historique vivait dans le `~/.claude` du HOME persistant. Le nouveau montage le masque dans le conteneur. `.devcontainer/scripts/migrate_claude_history.sh`, lancé sur l'hôte par `initializeCommand`, le recopie donc dans le dossier partagé :

- il copie `projects/` (conversations, mémoire automatique) et `file-history/` (checkpoints `/rewind`) sans écraser de fichier, puis ajoute `history.jsonl` à la fin de l'existant ;
- il ne copie pas la connexion : on se reconnecte une fois ;
- un marqueur `.migrated-to-claude-devcontainers` dans l'ancien `.claude` limite la copie à une fois par projet ;
- il sort toujours en `0` : un échec n'empêche pas l'ouverture du conteneur, et la copie est retentée la fois suivante ;
- il n'utilise pas `cp -n`, qui sort en erreur dès qu'il saute un fichier sur coreutils 9.2 à 9.4.

### Configuration Claude Code

Le projet généré contient un dossier `.claude/` :

- `commands/` : commandes slash du projet (`fix-issue`, `stocke-memoire`)
- `settings.json` : active le plugin `mattpocock-skills@claude-plugins-official` via la clé `enabledPlugins`. Comme le dit la [doc Claude Code](https://code.claude.com/docs/en/plugins/install#choose-an-install-scope), ce réglage active le plugin pour le dépôt mais ne le télécharge pas : chaque utilisateur l'installe une fois via `/plugins` (la CLI `claude` n'est pas présente dans le conteneur, donc `postCreateCommand.sh` ne peut pas s'en charger).

La configuration que lisent ces skills est pré-remplie, ce qui évite de lancer `/setup-matt-pocock-skills` :

- `docs/agents/issue-tracker.md` : issues GitHub dans `{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}`
- `docs/agents/triage-labels.md` : les 5 labels de triage par défaut
- `docs/agents/domain.md` : documentation du domaine à contexte unique
- section `## Agent skills` du `CLAUDE.md` généré, qui pointe vers ces trois fichiers

## Choix technologiques

### uv vs pip/poetry/pipenv

**Pourquoi uv** :
- ✅ **Performance** : 10-100x plus rapide
- ✅ **Compatibilité** : Standards Python (PEP 621)
- ✅ **Simplicité** : Une seule commande pour installer
- ✅ **Moderne** : Support des dernières PEP

### Cookiecutter vs Copier

**Pourquoi Cookiecutter** :
- ✅ **Maturité** : Standard de facto
- ✅ **Écosystème** : Nombreux templates existants
- ✅ **Cruft** : Support mise à jour des templates
- ✅ **Simplicité** : Syntaxe Jinja2 familière

### Material for MkDocs

**Pourquoi Material** :
- ✅ **Esthétique** : Design moderne et responsive
- ✅ **Fonctionnalités** : Navigation, recherche, dark mode
- ✅ **Maintenance** : Très bien maintenu
- ✅ **GitHub Pages** : Intégration native

## Patterns de développement

### Convention sur configuration
```python
# Plutôt que de demander tous les paramètres
cookiecutter.json = {
    "database_host": "localhost",
    "database_port": "5432",
    "database_name": "mydb",
    "database_user": "user"
}

# On utilise des defaults intelligents
cookiecutter.json = {
    "project_name": "Mon Projet",
    "python_version": "3.11"  # Le reste est dérivé ou par défaut
}
```

### Progressive disclosure
- **v0.1** : Structure de base + devcontainer
- **v0.2** : Environnement avancé (poetry lock, etc.)
- **v0.3** : Qualité de code (pre-commit, ruff config)
- **v0.4** : Tests (pytest, coverage)
- **v0.5** : CI/CD (GitHub Actions)

### Template composable
```bash
# Structure modulaire pour futures extensions
{{ cookiecutter.project_slug }}/
├── .devcontainer/           # Module: Environnement
├── .github/workflows/       # Module: CI/CD
├── .pre-commit-config.yaml  # Module: Qualité
├── tests/                   # Module: Tests
└── pyproject.toml           # Configuration centrale
```

## Extensibilité

### Hooks Cookiecutter
```python
# hooks/pre_gen_project.py
import re
import sys

project_slug = '{{ cookiecutter.project_slug }}'
if not re.match(r'^[a-z][a-z0-9-]*$', project_slug):
    print(f'❌ project_slug "{project_slug}" invalide')
    sys.exit(1)

# hooks/post_gen_project.py
import os
import subprocess

# Initialiser Git
subprocess.run(['git', 'init'])
subprocess.run(['git', 'add', '.'])
subprocess.run(['git', 'commit', '-m', 'Initial commit from PyFoundry'])
```

### Configuration conditionnelle
```json
{
    "include_docker": "y",
    "include_fastapi": ["y", "n"],
    "cloud_provider": ["none", "aws", "gcp", "azure"]
}
```

```yaml
# docker-compose.yml (généré seulement si include_docker == "y")
{% if cookiecutter.include_docker == "y" %}
version: '3.8'
services:
  app:
    build: .
{% endif %}
```

## Maintenance et évolution

### Tests du template
- **pytest-cookies** : Tests fonctionnels
- **Tests de génération** : Validation de la structure
- **Tests d'intégration** : Installation et commandes
- **Tests de régression** : Non-breaking changes

### Versioning sémantique
- **MAJOR** : Breaking changes dans l'API du template
- **MINOR** : Nouvelles fonctionnalités backward-compatible
- **PATCH** : Bug fixes et améliorations mineures

### Migration strategy
```bash
# Mise à jour automatique avec cruft
cruft update

# Résolution manuelle des conflits si nécessaire
git mergetool
```
