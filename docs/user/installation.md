# Installation et Configuration

## Pré-requis

### Obligatoire
- **Python 3.11+**
- **[Cruft](https://cruft.github.io/cruft/)** - Pour créer des projets depuis le template

### Option 1 : Avec VS Code + Docker (Recommandé)
- [VS Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Extension [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Option 2 : Installation locale
- [uv](https://github.com/astral-sh/uv) sera installé automatiquement par les scripts de setup

## Installation des outils

### Installer Cruft (requis)

Cruft est **obligatoire** pour utiliser le template PyFoundry. Choisissez une méthode d'installation :

#### Option 1 : Installation globale avec pip
```bash
pip install cruft
```

#### Option 2 : Environnement conda/mamba dédié (recommandé)
```bash
# Créer un environnement pour les outils de templating
mamba create -y -n pyfoundry -c conda-forge python=3.11

# Activer l'environnement
mamba activate pyfoundry

# Installer cruft et autres outils utiles
mamba install cruft mkdocs-material --yes

# Vérification de l'installation
cruft --version
```

#### Option 3 : Installation avec uv
```bash
# Installer uv d'abord
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installer cruft avec uv
uv pip install cruft
```

!!! warning "Installation obligatoire"
    **Cruft doit être installé et accessible** avant de pouvoir utiliser le template. Vérifiez avec `cruft --version`.

### Vérification rapide
```bash
# Vérifier que cruft est installé
cruft --version
# Devrait afficher : cruft, version X.X.X

# Vérifier que Python est accessible
python --version
# Devrait afficher : Python 3.11.X ou plus récent
```

Si ces commandes échouent, suivez les instructions d'installation ci-dessus.

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
- *uv est maintenant installé automatiquement*
- **use_node** : Installer Node.js/npm pour des outils web (défaut: n)
- **setup_git** : Configuration Git de base (défaut: y)

### Méthode avec paramètres
```bash
cruft create https://github.com/username/PyFoundry.git \
  --extra-context '{
    "project_name": "Analyse des Ventes",
    "description": "Analyse des données de vente trimestrielles",
    "python_version": "3.11",
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