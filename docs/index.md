# PyFoundry Template

Un template Cookiecutter pour démarrer rapidement des projets de Data Science en Python avec un **environnement reproductible**.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://castorfou.github.io/PyFoundry)
[![Template Tests](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml/badge.svg)](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v0.2-green.svg)](https://github.com/castorfou/PyFoundry/releases/tag/v0.2.0)

## 🚀 Vision

PyFoundry vise à garantir la **reproductibilité totale**, et la **qualité du code** en s'appuyant sur des outils modernes: uv, devcontainer, cruft/cookie cutter, pre-commit, ruff, ...

## ⚡ Démarrage rapide

```bash
# 1. Installer cruft
pip install cruft

# 2. Créer un nouveau projet
cruft create https://github.com/castorfou/PyFoundry.git

# 3. Builder devcontainer 
code mon-nouveau-projet    # VS Code propose "Reopen in Container"
```

## 🛠️ Stack technologique

- **Templating** : Cookiecutter / Cruft pour templates évolutifs
- **Environnement** : Devcontainer VS Code (Python 3.12) avec features officielles
- **Dépendances** : uv via devcontainer feature & pyproject.toml avec métadonnées complètes
- **Reproductibilité** : Verrouillage automatique des dépendances (requirements.lock)
- **Configuration** : Templates .env et configuration Jupyter intégrée
- **Qualité de Code** : pre-commit & ruff (préparation v0.3)
- **Tests du Template** : pytest & pytest-cookies
- **Documentation** : MkDocs & mkdocs-material
- **CI/CD** : GitHub Actions avec tests multi-plateformes

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
- **v0.2** ✅ : **Environnement reproductible avancé** (scripts, uv.lock, devcontainer optimisé)
- **v0.2.1** ✅ : **Simplification** (uv obligatoire, devcontainer Python 3.12 fixe)
- **v0.3** 🚧 : Qualité de code (pre-commit, ruff, mypy)
- **v0.4** 📋 : Tests automatisés (pytest, coverage)
- **v0.5** 🎯 : CI/CD complet (GitHub Actions automation)


## 📚 Documentation

### Pour les Utilisateurs
- **[Guide d'installation](user/installation.md)** : Pré-requis et création de projet
- **[Guide d'usage](user/usage.md)** : Commandes et workflow quotidien  
- **[Structure du projet](user/structure.md)** : Organisation des fichiers et dossiers

### Pour les Développeurs  
- **[Architecture](dev/architecture.md)** : Design et choix techniques du template
- **[Guide de contribution](dev/contributing.md)** : Comment contribuer au projet
- **[Déploiement](dev/deployment.md)** : Publication et release avec GitHub CLI
- **[Roadmap](dev/roadmap.md)** : Planification des versions futures

---

**🚀 Prêt à créer votre projet ? Suivez le [guide d'installation](user/installation.md) !**