# PyFoundry Template

> Un template Cookiecutter de qualité industrielle pour démarrer rapidement des projets de Data Science en Python avec un environnement reproductible et des outils de qualité automatisés.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://castorfou.github.io/PyFoundry)
[![Template Tests](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml/badge.svg)](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v0.3.0-green.svg)](https://github.com/castorfou/PyFoundry/releases/tag/v0.3.0)

## 🚀 Démarrage rapide

```bash
# 1. Installer cruft
pip install cruft

# 2. Se logger à ghcr.io (pour les features devcontainer)
docker login ghcr.io

# 3. Créer un nouveau projet
cruft create https://github.com/castorfou/PyFoundry.git

# 4. Ouvrir dans VS Code (setup automatique complet)
code mon-nouveau-projet
# → VS Code propose "Reopen in Container"
# → Configuration Git + GitHub + Pre-commit automatique
```

## ✨ Fonctionnalités

- **🐳 Environnement reproductible** : Devcontainer VS Code avec uv, extensions optimisées DS
- **🔧 Qualité de code automatisée** : Ruff + MyPy + Pre-commit hooks pré-configurés  
- **🌐 Intégration GitHub complète** : Authentification automatique, remote configuré
- **📁 Structure intelligente** : Organisation standardisée pour projets Data Science
- **⚡ Setup zero-config** : Git init + hooks + auth GitHub en une commande
- **📚 Documentation moderne** : Guide complet avec MkDocs Material
- **🔄 Mise à jour facile** : Template évolutif avec cruft

## 📚 Documentation

- **[Guide complet](https://castorfou.github.io/PyFoundry/user/guide/)** - Toutes les fonctionnalités et workflow
- **[Installation](https://castorfou.github.io/PyFoundry/user/installation/)** - Pré-requis et setup initial
- **[Structure du projet](https://castorfou.github.io/PyFoundry/user/structure/)** - Organisation des fichiers et dossiers
- **[Guide développeur](https://castorfou.github.io/PyFoundry/dev/contributing/)** - Comment contribuer au template
- **[Roadmap](https://castorfou.github.io/PyFoundry/dev/roadmap/)** - Historique et évolutions du template

## 🛠️ Stack technologique

- **Templating** : Cookiecutter / Cruft pour templates évolutifs
- **Environnement** : Devcontainer VS Code avec features officielles
- **Dépendances** : uv & pyproject.toml avec verrouillage automatique
- **Qualité de code** : Ruff (linting + formatage) + MyPy (types statiques)
- **Hooks** : Pre-commit avec 4 repos optimisés pour Data Science
- **Git/GitHub** : Authentification automatique + configuration seamless
- **Documentation** : MkDocs & mkdocs-material
- **CI/CD** : GitHub Actions

## 📦 Installation

### Pré-requis
- [Cruft](https://cruft.github.io/cruft/) : `pip install cruft`
- [VS Code](https://code.visualstudio.com/) + [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Utilisation

```bash
# Méthode interactive
cruft create https://github.com/castorfou/PyFoundry.git

# Avec paramètres
cruft create https://github.com/castorfou/PyFoundry.git \
  --extra-context '{
    "project_name": "Mon Analyse",
    "use_node": "n",
    "setup_git": "y"
  }'

# Valeurs par défaut
cruft create https://github.com/castorfou/PyFoundry.git --no-input
```

## 🎯 Roadmap

- **v0.1** ✅ : Squelette avec environnement reproductible  
- **v0.2** ✅ : Environnement reproductible avancé (scripts, devcontainer optimisé)
- **v0.3** ✅ : **Qualité de code automatisée** (ruff, mypy, pre-commit, git/github integration)
- **v0.4** 📋 : Tests automatisés (pytest, pytest-cookies, coverage)
- **v0.5** 🎯 : CI/CD complet (GitHub Actions, release automation)

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez le [guide de contribution](https://castorfou.github.io/PyFoundry/dev/contributing/) pour démarrer.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

**Créé avec ❤️ pour la communauté Data Science**