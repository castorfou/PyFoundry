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
    "setup_git": "Configuration Git (y/n)"
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
                "python.defaultInterpreterPath": "./.venv/bin/python",
                "python.terminal.activateEnvironment": true
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
- **Environnement virtuel .venv** avec version Python dynamique
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