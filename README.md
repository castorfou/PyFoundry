# PyFoundry Template

> Un template Cookiecutter de qualité industrielle pour démarrer rapidement des projets de Data Science en Python.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://castorfou.github.io/PyFoundry)
[![Template Tests](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml/badge.svg)](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Démarrage rapide

```bash
# 1. Installer cruft (si pas déjà fait)
pip install cruft

# 2. Créer un nouveau projet
cruft create https://github.com/castorfou/PyFoundry.git

# 3. Ouvrir dans VS Code avec devcontainer
code mon-nouveau-projet
```

## ✨ Fonctionnalités

- **Environnement reproductible** : Devcontainer VS Code avec environnement virtuel `.venv`
- **Outils modernes** : Installation conditionnelle d'uv, Node.js, configuration Git
- **Structure standardisée** : Dossiers `src/`, `data/`, `notebooks/` pré-configurés
- **Documentation complète** : Guide utilisateur et développeur avec MkDocs Material
- **CI/CD prêt** : Workflows GitHub Actions pour tests et déploiement de documentation

## 📚 Documentation

- **[Guide d'installation](https://castorfou.github.io/PyFoundry/user/installation/)** - Comment installer et utiliser le template
- **[Guide d'usage](https://castorfou.github.io/PyFoundry/user/usage/)** - Commandes et workflow recommandés  
- **[Structure du projet](https://castorfou.github.io/PyFoundry/user/structure/)** - Organisation des fichiers et dossiers
- **[Guide développeur](https://castorfou.github.io/PyFoundry/dev/contributing/)** - Comment contribuer au template

## 🛠️ Stack technologique

- **Templating** : Cookiecutter / Cruft
- **Environnement** : Devcontainer (VS Code)
- **Dépendances** : uv & pyproject.toml
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
cruft create https://github.com/guillaume/PyFoundry.git

# Avec paramètres
cruft create https://github.com/guillaume/PyFoundry.git \
  --extra-context '{
    "project_name": "Mon Analyse",
    "use_uv": "y",
    "use_node": "n",
    "setup_git": "y"
  }'

# Valeurs par défaut
cruft create https://github.com/guillaume/PyFoundry.git --no-input
```

## 🎯 Roadmap

- **v0.1** ✅ : Squelette avec environnement reproductible
- **v0.2** : Environnement reproductible avancé (uv.lock, scripts)
- **v0.3** : Qualité de code (pre-commit, ruff)
- **v0.4** : Tests automatisés (pytest, coverage)
- **v0.5** : CI/CD complet (release automation)

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez le [guide de contribution](https://guillaume.github.io/PyFoundry/dev/contributing/) pour démarrer.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

**Créé avec ❤️ pour la communauté Data Science**