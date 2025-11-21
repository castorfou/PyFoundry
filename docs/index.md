# PyFoundry Template

Un template Cookiecutter de qualité industrielle pour démarrer rapidement des projets de Data Science en Python avec un environnement reproductible et des outils de qualité automatisés.

[![Test Template](https://github.com/castorfou/PyFoundry/actions/workflows/test-template.yml/badge.svg)](https://github.com/castorfou/PyFoundry/actions/workflows/test-template.yml)
[![Deploy Documentation](https://github.com/castorfou/PyFoundry/actions/workflows/docs.yml/badge.svg)](https://github.com/castorfou/PyFoundry/actions/workflows/docs.yml)
[![GitHub release](https://img.shields.io/github/v/release/castorfou/PyFoundry)](https://github.com/castorfou/PyFoundry/releases)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://castorfou.github.io/PyFoundry)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

## 🚀 Vision

PyFoundry automatise complètement la création d'environnements Data Science modernes : **environnement reproductible**, **qualité de code**, **intégration Git/GitHub** et **workflow zero-config**.

## ⚡ Démarrage rapide

pour créer un projet suivant le template PyFoundry

```bash
# 1. Activer cruft
mamba activate pyfoundry # un exemple d'activation d'environnement contenant cruft

# 2. Se logger à ghcr.io (pour les features devcontainer)  
docker login ghcr.io

# 3. Créer un nouveau projet (tu devras repondre a quelques questions)
# nom du projet, etc
cruft create https://github.com/castorfou/PyFoundry.git

# 4. Ouvrir dans VS Code (setup automatique complet)
# remplacer mon-nouveau-projet par le vrai nom (project_slug)
code mon-nouveau-projet
# → VS Code propose "Reopen in Container"
# → Configuration Git + GitHub (un connexion à github sera effectuée) + Pre-commit automatique
```

pour pousser vers github.com

```bash
# PROJECT_SLUG est dispo dans les variables env
gh repo create $PROJECT_SLUG --public
git push -u origin main
```

pour recuperer les dernieres modifications de PyFoundry

```bash
# 1. Activer cruft
mamba activate pyfoundry # un exemple d'activation d'environnement contenant cruft

cruft update

cruft check
```

## ✨ Fonctionnalités

- **🐳 Environnement reproductible** : Devcontainer VS Code avec uv, extensions optimisées DS
- **🔧 Qualité de code automatisée** : Ruff + MyPy + Pre-commit hooks pré-configurés  
- **🌐 Intégration GitHub complète** : Authentification automatique, remote configuré
- **📁 Structure** : Organisation standardisée pour projets Data Science
- **⚡ Setup zero-config** : Git init + hooks + auth GitHub en une commande
- **📚 Documentation moderne** : Guide complet avec MkDocs Material
- **🔄 Mise à jour facile** : Template évolutif avec cruft
- **🤖 Claude Code intégré** : CLAUDE.md généré automatiquement avec documentation projet et dossier .claude/commands/ pour commandes personnalisées 

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
mon-nouveau-projet/
├── .claude/              # Config Claude Code
├── .devcontainer/        # Config devcontainer
├── .github/              # Config CI/CD (test/build lib / deploy mkdocs)
├── data/
│   ├── raw/              # Données brutes (gitignorées)
│   └── processed/        # Datasets traités
├── docs/
│   ├── claude/memory/    # Memoire Claude: par feature developpees
│   ├── user/             # Doc user - comment utiliser
│   └── developer/        # Doc developer - comment modifier
├── notebooks/            # Notebooks python REPL 
└── src/                  # Libs python
```

### 🎯 DevContainer Optimisé
- **Image** : Python 3.12 officielle Microsoft avec utilisateur vscode
- **Performance** : Configuration simplifiée, build plus rapide
- **Extensions** : Extensions VS Code essentielles (Python, Jupyter, Git)

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
- **[Test](dev/testing.md)** : Comment tester des devs en cours
- **[Déploiement](dev/deployment.md)** : Publication et release

---

**🚀 Prêt à créer votre projet ? Consultez le [guide complet](user/guide.md) !**