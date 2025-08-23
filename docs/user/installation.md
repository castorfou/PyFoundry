# Installation et Configuration

## Pré-requis

### Option 1 : Avec VS Code + Docker (Recommandé)
- [VS Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Extension [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Option 2 : Installation locale
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) pour la gestion des dépendances
- [Cookiecutter](https://cookiecutter.readthedocs.io/) ou [Cruft](https://cruft.github.io/cruft/)

## Installation des outils

### Installer Cruft (recommandé)
```bash
pip install cruft
```

### Installer uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Créer un nouveau projet

### Méthode interactive
```bash
cruft create https://github.com/username/PyFoundry.git
```

Vous serez invité à renseigner :
- **project_name** : Nom affiché du projet (ex: "Analyse des Ventes")
- **project_slug** : Nom technique (généré automatiquement)
- **description** : Description courte du projet
- **python_version** : Version Python (défaut: 3.11)
- **use_uv** : Installer uv pour la gestion des dépendances (recommandé: y)
- **use_node** : Installer Node.js/npm pour des outils web (défaut: n)
- **setup_git** : Configuration Git de base (défaut: y)

### Méthode avec paramètres
```bash
cruft create https://github.com/username/PyFoundry.git \
  --extra-context '{
    "project_name": "Analyse des Ventes",
    "description": "Analyse des données de vente trimestrielles",
    "python_version": "3.11",
    "use_uv": "y",
    "use_node": "n",
    "setup_git": "y"
  }'
```

### Méthode avec valeurs par défaut
```bash
cruft create https://github.com/username/PyFoundry.git --no-input
```

## Démarrage du projet

### Avec VS Code + Devcontainer (Recommandé)
1. Ouvrir le projet dans VS Code
2. Cliquer sur "Reopen in Container" quand proposé
3. Attendre l'installation automatique des dépendances
4. Commencer à développer !

### En local
```bash
cd mon-projet

# L'environnement .venv est déjà créé si vous avez choisi uv
# Sinon, créez-le manuellement :
# python -m venv .venv  # ou uv venv .venv

# Activer l'environnement
source .venv/bin/activate

# Installer les dépendances
uv pip install -e .          # si uv choisi
# ou pip install -e .        # si pip standard

# Installer les dépendances de développement
uv pip install -e ".[dev]"   # si uv choisi
# ou pip install -e ".[dev]" # si pip standard
```

!!! tip "Environnement virtuel automatique"
    Le devcontainer crée automatiquement `.venv` et l'active. En local, vous devez l'activer manuellement avec `source .venv/bin/activate`.

## Vérification de l'installation

```bash
# Vérifier que Jupyter fonctionne
jupyter lab

# Vérifier l'installation des dépendances
python -c "import pandas, numpy; print('✅ Dépendances OK')"
```

## Mise à jour du template

Si le template PyFoundry est mis à jour, vous pouvez synchroniser votre projet :

```bash
cruft update
```

!!! warning "Conflits potentiels"
    La mise à jour peut créer des conflits si vous avez modifié les fichiers de configuration. Résolvez-les manuellement.