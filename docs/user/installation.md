# Installation et Configuration

## Pré-requis

### Obligatoire
- **Python 3.11+**
- **[Cruft](https://cruft.github.io/cruft/)** - Pour créer des projets depuis le template
- **VS Code + Docker**
  - Extension [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

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
- **use_node** : Installer Node.js/npm pour des outils web (défaut: n)

### Méthode avec paramètres
```bash
cruft create https://github.com/username/PyFoundry.git \
  --extra-context '{
    "project_name": "Analyse des Ventes",
    "description": "Analyse des données de vente trimestrielles",
    "python_version": "3.11",
    "use_node": "n"
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