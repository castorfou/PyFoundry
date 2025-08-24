# PyFoundry Template

Un template Cookiecutter de qualité industrielle pour démarrer rapidement des projets de Data Science en Python avec un environnement reproductible et des outils de qualité automatisés.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://castorfou.github.io/PyFoundry)
[![Template Tests](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml/badge.svg)](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v0.3.0-green.svg)](https://github.com/castorfou/PyFoundry/releases/tag/v0.3.0)

## 🚀 Vision

PyFoundry automatise complètement la création d'environnements Data Science modernes : **environnement reproductible**, **qualité de code**, **intégration Git/GitHub** et **workflow zero-config**.

## ⚡ Démarrage rapide

pour créer un projet suivant le template PyFoundry

```bash
# 1. Activer cruft
mamba activate pyfoundry # un exemple d'activation d'environnement contenant cruft

# 2. Se logger à ghcr.io (pour les features devcontainer)  
docker login ghcr.io

# 3. Créer un nouveau projet
cruft create https://github.com/castorfou/PyFoundry.git

# 4. Ouvrir dans VS Code (setup automatique complet)
code mon-nouveau-projet
# → VS Code propose "Reopen in Container"
# → Configuration Git + GitHub (un connexion à github sera effectuée) + Pre-commit automatique
```

## ✨ Fonctionnalités

- **🐳 Environnement reproductible** : Devcontainer VS Code avec uv, extensions optimisées DS
- **🔧 Qualité de code automatisée** : Ruff + MyPy + Pre-commit hooks pré-configurés  
- **🌐 Intégration GitHub complète** : Authentification automatique, remote configuré
- **📁 Structure** : Organisation standardisée pour projets Data Science
- **⚡ Setup zero-config** : Git init + hooks + auth GitHub en une commande
- **📚 Documentation moderne** : Guide complet avec MkDocs Material
- **🔄 Mise à jour facile** : Template évolutif avec cruft

## 🛠️ Stack technologique

- **Templating** : Cookiecutter / Cruft pour templates évolutifs
- **Environnement** : Devcontainer VS Code avec features officielles
- **Dépendances** : uv & pyproject.toml avec verrouillage automatique
- **Qualité de code** : Ruff (linting + formatage) + MyPy (types statiques)
- **Hooks** : Pre-commit avec 4 repos optimisés pour Data Science
- **Git/GitHub** : Authentification automatique + configuration seamless
- **Documentation** : MkDocs & mkdocs-material
- **CI/CD** : GitHub Actions

### 🏗️ Structure 
```
mon-projet/
├── data/
│   ├── raw/              # Données brutes (gitignorées)
│   ├── processed/        # Datasets traités
│   └── external/         # Références externes
├── models/               # Modèles entraînés
├── logs/                 # Logs d'application
├── reports/              # Rapports générés
├── notebooks/
│   ├── exploratory/      # Notebooks d'exploration
│   ├── preprocessing/    # Préparation des données
│   ├── modeling/         # Développement de modèles
│   └── reporting/        # Rapports finaux
└── scripts/              # Automation setup
    ├── setup.sh          # Linux/macOS
    └── setup.ps1         # Windows
```

### 🎯 DevContainer Optimisé
- **Image** : Python 3.12 officielle Microsoft avec utilisateur vscode
- **Performance** : Configuration simplifiée, build plus rapide
- **Extensions** : Extensions VS Code essentielles (Python, Jupyter, Git)

## 🗺️ Roadmap

- **v0.1** ✅ : Squelette avec environnement reproductible
- **v0.2** ✅ : Environnement reproductible avancé (scripts, devcontainer optimisé)
- **v0.3** ✅ : **Qualité de code automatisée** (ruff, mypy, pre-commit, git/github integration)
- **v0.4** ✅ : Tests automatisés (pytest, pytest-cookies, coverage)
- **v0.5** 🎯 : CI/CD complet (GitHub Actions, release automation)


## 📚 Documentation

### Pour les Utilisateurs
- **[Guide complet](user/guide.md)** : Toutes les fonctionnalités et workflow de A à Z
- **[Installation](user/installation.md)** : Pré-requis et setup initial
- **[Structure du projet](user/structure.md)** : Organisation des fichiers et dossiers

### Pour les Développeurs  
- **[Architecture](dev/architecture.md)** : Design et choix techniques du template
- **[Roadmap](dev/roadmap.md)** : Historique et évolutions du template
- **[Implémentation v0.3](dev/v0.3-implementation.md)** : Détails techniques v0.3
- **[Contribution](dev/contributing.md)** : Comment contribuer au projet
- **[Déploiement](dev/deployment.md)** : Publication et release

---

**🚀 Prêt à créer votre projet ? Consultez le [guide complet](user/guide.md) !**