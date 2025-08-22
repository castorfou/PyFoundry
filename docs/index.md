# PyFoundry Template

Un template Cookiecutter de qualité industrielle pour démarrer rapidement des projets de Data Science en Python.

## 🚀 Vision

PyFoundry vise à garantir la **reproductibilité**, la **qualité du code** et un **démarrage rapide** grâce à une configuration complète et automatisée.

## ⚡ Démarrage rapide

```bash
# Créer un nouveau projet
cruft create https://github.com/username/PyFoundry.git

# Ouvrir dans VS Code avec devcontainer
code mon-nouveau-projet
```

!!! tip "Environnement reproductible"
    Le template inclut une configuration devcontainer pour VS Code qui garantit un environnement de développement identique pour tous les contributeurs.

## 🛠️ Stack technologique

- **Templating** : Cookiecutter / Cruft
- **Environnement** : Devcontainer (VS Code)
- **Dépendances** : uv & pyproject.toml
- **Qualité de Code** : pre-commit & ruff
- **Tests du Template** : pytest & pytest-cookies
- **Documentation** : MkDocs & mkdocs-material
- **CI/CD** : GitHub Actions

## 📋 Fonctionnalités actuelles (v0.1)

- ✅ Structure de projet standardisée
- ✅ Configuration devcontainer VS Code
- ✅ Configuration pyproject.toml avec dépendances essentielles
- ✅ Documentation utilisateur et développeur
- ✅ .gitignore adapté Data Science

## 🗺️ Roadmap

- **v0.2** : Environnement reproductible avancé
- **v0.3** : Qualité de code (pre-commit, ruff)
- **v0.4** : Tests automatisés
- **v0.5** : CI/CD GitHub Actions

## 📚 Navigation

- **[Guide Utilisateur](user/installation.md)** : Comment utiliser le template
- **[Guide Développeur](dev/architecture.md)** : Comment contribuer au template