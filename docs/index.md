# PyFoundry Template

Un template Cookiecutter de qualité industrielle pour démarrer rapidement des projets de Data Science en Python avec un **environnement reproductible avancé** et une **expérience développeur optimisée**.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://castorfou.github.io/PyFoundry)
[![Template Tests](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml/badge.svg)](https://github.com/castorfou/PyFoundry/actions/workflows/test.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v0.2-green.svg)](https://github.com/castorfou/PyFoundry/releases/tag/v0.2.0)

## 🚀 Vision

PyFoundry vise à garantir la **reproductibilité totale**, la **qualité du code** et un **démarrage rapide** (50-60% plus rapide qu'avant) grâce à une configuration complète et automatisée sur toutes les plateformes.

## ⚡ Démarrage rapide

```bash
# 1. Installer cruft
pip install cruft

# 2. Créer un nouveau projet
cruft create https://github.com/castorfou/PyFoundry.git

# 3. Setup automatique multi-plateforme
cd mon-nouveau-projet
./scripts/setup.sh        # Linux/macOS
# ou .\scripts\setup.ps1   # Windows

# 4. Ou utiliser devcontainer (recommandé)
code mon-nouveau-projet    # VS Code propose "Reopen in Container"
```

!!! success "**Nouveau v0.2** : Setup 50-60% plus rapide !"
    Avec les nouveaux scripts automatisés et le devcontainer optimisé, créer un projet prend maintenant 2-4 minutes au lieu de 5-8 minutes !

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

## ✨ Fonctionnalités v0.2 - Environnement Reproductible Avancé

### 🚀 Scripts Multi-Plateformes
- **Linux/macOS** : `scripts/setup.sh` avec détection d'OS automatique
- **Windows** : `scripts/setup.ps1` avec support PowerShell natif  
- **Features** : Logs colorés, gestion d'erreurs robuste, diagnostics de performance

### 📦 Reproductibilité Totale
- **Verrouillage automatique** : `requirements.lock` et `requirements-full.lock`
- **Export uv complet** : Métadonnées et versions exactes préservées
- **pyproject.toml enrichi** : Dépendances versionnées et groupes optionnels

### 🔧 Configuration Avancée
- **Template .env** : 40+ variables d'environnement pré-configurées
- **Variables devcontainer** : PYTHONPATH, DATA_DIR, configuration intégrée
- **Configuration Jupyter** : Lab settings et répertoires runtime automatiques

### 🏗️ Structure Intelligente
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
- **Ports** : Multi-port (8888, 8889, 8080, 3000) avec labels automatiques
- **Environment** : Variables intégrées et feature uv officielle

## 📊 Performances v0.2

| Plateforme | Avant (v0.1) | Maintenant (v0.2) | Amélioration |
|------------|--------------|-------------------|--------------|
| **Linux**  | ~5 minutes   | ~2 minutes        | **60% plus rapide** |
| **macOS**  | ~6 minutes   | ~3 minutes        | **50% plus rapide** |
| **Windows**| ~8 minutes   | ~4 minutes        | **50% plus rapide** |

## 🗺️ Roadmap

- **v0.1** ✅ : Squelette avec environnement reproductible
- **v0.2** ✅ : **Environnement reproductible avancé** (scripts, uv.lock, devcontainer optimisé)
- **v0.2.1** ✅ : **Simplification** (uv obligatoire, devcontainer Python 3.12 fixe)
- **v0.3** 🚧 : Qualité de code (pre-commit, ruff, mypy)
- **v0.4** 📋 : Tests automatisés (pytest, coverage)
- **v0.5** 🎯 : CI/CD complet (GitHub Actions automation)

## 🎉 Nouveautés v0.2

!!! info "**[📖 Guide complet des nouveautés v0.2](user/v0.2-features.md)**"
    Découvrez en détail toutes les améliorations : scripts automatisés, reproductibilité, devcontainer optimisé, et benchmarks de performance.

## 📚 Documentation

### Pour les Utilisateurs
- **[Guide d'installation](user/installation.md)** : Pré-requis et création de projet
- **[Nouveautés v0.2](user/v0.2-features.md)** : Scripts, reproductibilité, performances
- **[Guide d'usage](user/usage.md)** : Commandes et workflow quotidien  
- **[Structure du projet](user/structure.md)** : Organisation des fichiers et dossiers

### Pour les Développeurs  
- **[Architecture](dev/architecture.md)** : Design et choix techniques du template
- **[Guide de contribution](dev/contributing.md)** : Comment contribuer au projet
- **[Déploiement](dev/deployment.md)** : Publication et release avec GitHub CLI
- **[Roadmap](dev/roadmap.md)** : Planification des versions futures

---

**🚀 Prêt à créer votre projet ? Suivez le [guide d'installation](user/installation.md) !**