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
- **Environnement virtuel `/tmp/venv`**, hors du HOME persistant, recréé à chaque rebuild
- **Features officielles** (uv) au lieu d'installation manuelle
- **Héritage timezone du host** via montages `/etc/timezone` et `/etc/localtime`

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

Le devcontainer hérite automatiquement de la timezone du système hôte :

```json
{
    "containerEnv": {
        "TZ": "${localEnv:TZ}"
    },
    "mounts": [
        "source=/etc/timezone,target=/etc/timezone,type=bind,consistency=cached,readonly",
        "source=/etc/localtime,target=/etc/localtime,type=bind,consistency=cached,readonly"
    ]
}
```

**Méthodes d'héritage** :
- **Variable d'environnement TZ** : Utilisée par les processus Python/Node.js
- **Montage /etc/timezone** : Configuration système Linux
- **Montage /etc/localtime** : Fichier de timezone binaire utilisé par le système

### HOME persistant

Le HOME du conteneur (`/home/vscode`) est un bind mount d'un dossier de l'hôte propre au projet :

```json
"mounts": [
    "source=${localEnv:HOME}/.devcontainer/homes/${localWorkspaceFolderBasename}-${devcontainerId},target=/home/vscode,type=bind",
    "source=${localEnv:HOME}/.cache/pre-commit-devcontainers,target=/home/vscode/.cache/pre-commit,type=bind",
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly",
    "source=${localEnv:HOME}/.cache/uv,target=/home/vscode/.cache/uv,type=bind,consistency=cached"
]
```

La connexion Claude Code (`~/.claude`, `~/.claude.json`), la connexion `gh`, l'historique du shell et `~/.vscode-server` survivent ainsi aux rebuilds. Les caches pre-commit et uv sont partagés entre tous les devcontainers de l'hôte.

Trois mécanismes complètent le montage :

- **`initializeCommand`**, exécuté sur l'hôte avant le montage, crée les dossiers sources (dont `.cache` dans le HOME, pour que Docker ne crée pas les points de montage imbriqués en root) puis lance `.devcontainer/scripts/check_mounts.sh --host`. Ce script lit les `mounts` de `devcontainer.json`, résout `${localEnv:HOME}`, `${localWorkspaceFolderBasename}` et `${devcontainerId}`, signale chaque source absente avec la commande pour la créer, et contrôle les permissions de `~/.ssh`. Il sort en erreur si un montage est invalide.
- **`seed_home`** dans `postCreateCommand.sh` : le bind mount masque le HOME de l'image, donc `cp -rn /etc/skel/. "$HOME"` recopie `.bashrc`, `.profile`… sans écraser l'existant.
- **Venv dans `/tmp/venv`** : il reste hors du HOME persistant et est recréé à chaque rebuild depuis `uv.lock`, ce qui évite de conserver un venv lié à une ancienne image Python.

`~/.gitconfig` n'est plus monté : VS Code copie celui de l'hôte au démarrage.

Le choix est détaillé dans l'ADR [0001 — HOME persistant](../adr/0001-persist-development-home.md).

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
