# Roadmap PyFoundry

## Vue d'ensemble

PyFoundry suit une approche de développement **graduelle et itérative**. Chaque version apporte une couche de fonctionnalités cohérente et utilisable en production.

## Versions planifiées

### ✅ v0.1 : Squelette (Actuel)
**Objectif** : Structure de base fonctionnelle avec environnement reproductible

**Fonctionnalités** :
- ✅ Structure de projet standardisée (`src/`, `data/`, `notebooks/`)
- ✅ Configuration devcontainer VS Code avec script externe
- ✅ Environnement virtuel `.venv` automatique
- ✅ Installation conditionnelle d'outils (uv, Node.js, Git)
- ✅ Variables cookiecutter configurables
- ✅ `pyproject.toml` avec dépendances essentielles
- ✅ Documentation utilisateur et développeur complète
- ✅ `.gitignore` adapté Data Science

**Dépendances incluses** :
- `ipykernel`, `ipywidgets` : Support Jupyter
- `python-dotenv` : Configuration par variables d'environnement  
- `gitpython` : Intégration Git programmatique
- `pre-commit` : Préparation pour v0.3

**Configuration** :
- uv : Installation via devcontainer feature (obligatoire)
- `use_node` : Installation Node.js/npm (optionnel)
- `setup_git` : Configuration Git de base (optionnel)

---

### ✅ v0.2 : Environnement Reproductible (En cours)
**Objectif** : Garantir la reproductibilité totale et optimiser l'expérience développeur

**Fonctionnalités implémentées** :
- ✅ Fichiers de verrouillage des dépendances (requirements.lock, requirements-full.lock)
- ✅ Scripts de setup automatisés multi-plateformes (`scripts/setup.sh`, `scripts/setup.ps1`)
- ✅ Support Windows, macOS, Linux avec détection automatique
- ✅ Configuration d'environnement avancée avec `.env.template`
- ✅ pyproject.toml enrichi avec métadonnées complètes
- ✅ Dépendances étendues pour data science (pandas, numpy, matplotlib, seaborn)

**Améliorations devcontainer** :
- ✅ Variables d'environnement configurables (containerEnv)
- ✅ Optimisation des performances (mounts cached, exclusions)
- ✅ Extensions VS Code étendues (GitLens, formatters, tests)
- ✅ Configuration Jupyter avancée intégrée
- ✅ Features devcontainer (Git, GitHub CLI, Node.js conditionnel)
- ✅ Ports configurés avec labels (8888, 8889, 8080, 3000)
- ✅ Structure de projet automatisée (dossiers data/, models/, logs/)

**Scripts avancés** :
- ✅ Détection OS automatique et installation adaptée
- ✅ Gestion robuste des erreurs avec logs colorés
- ✅ Timer de performance et diagnostics
- ✅ Configuration Git automatisée avec .gitignore intelligent
- ✅ Support uv natif avec fallback pip

---

### ✅ v0.3 : Qualité de Code (Complété)
**Objectif** : Automatiser la qualité et la cohérence du code

**Fonctionnalités implémentées** :
- ✅ Configuration complète `.pre-commit-config.yaml` avec 4 repos
- ✅ Configuration `ruff` adaptée Data Science dans `pyproject.toml`
- ✅ Integration `mypy` progressive pour le typing
- ✅ Formatage automatique (ruff format) 
- ✅ Linting avancé avec règles spécialisées (pandas-vet, numpy)
- ✅ Initialisation git automatique avec branche main
- ✅ Authentification GitHub automatique (gh auth login)
- ✅ Pre-commit hooks pré-installés pour performance

**Outils intégrés** :
```yaml
# .pre-commit-config.yaml (versions auto-mises à jour)
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks  # v6.0.0
  - repo: https://github.com/astral-sh/ruff-pre-commit     # v0.12.10
  - repo: https://github.com/pre-commit/mirrors-mypy      # v1.17.1  
  - repo: https://github.com/Yelp/detect-secrets         # v1.5.0
```

**Workflow zero-config** :
1. `cruft create` → Génération avec paramètre github_username
2. `code projet` → Ouverture devcontainer
3. Tout configuré automatiquement : Git + Pre-commit + GitHub auth
4. Premier commit créé avec hooks actifs

---

### 🧪 v0.4 : Tests Automatisés
**Objectif** : Framework de tests complet

**Fonctionnalités prévues** :
- [ ] Structure de tests avec `pytest`
- [ ] Tests du template avec `pytest-cookies`
- [ ] Coverage reporting avec `pytest-cov`
- [ ] Tests d'intégration pour workflows complets
- [ ] Fixtures et utilitaires de test

**Structure de tests** :
```
tests/
├── __init__.py
├── conftest.py                 # Configuration pytest
├── test_template_generation.py # Tests de génération
├── test_project_structure.py   # Tests de structure
├── test_dependencies.py        # Tests d'installation
└── integration/
    └── test_full_workflow.py   # Tests end-to-end
```

---

### 🚀 v0.5 : CI/CD GitHub Actions
**Objectif** : Automatisation complète et déploiement

**Fonctionnalités prévues** :
- [ ] Workflows GitHub Actions pour tests
- [ ] Tests automatisés sur Pull Requests
- [ ] Publication automatique de la documentation
- [ ] Release automation avec semantic versioning
- [ ] Notifications et reporting

**Workflows** :
```yaml
# .github/workflows/test.yml
name: Test Template
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
```

---

## Fonctionnalités futures (v1.0+)

### Templates spécialisés
- **PyFoundry-ML** : Template pour Machine Learning
- **PyFoundry-API** : Template pour APIs (FastAPI)
- **PyFoundry-Viz** : Template pour visualisation de données

### Intégrations avancées
- [ ] Support cloud providers (AWS, GCP, Azure)
- [ ] Integration MLflow/Weights & Biases
- [ ] Support Kubernetes/Docker orchestration
- [ ] Template de déploiement (Streamlit, Gradio)

### Outils de développement
- [ ] CLI PyFoundry pour la gestion de projets
- [ ] Plugin VS Code dédié
- [ ] Templates de notebooks pré-configurés
- [ ] Générateur de rapports automatiques

## Critères de qualité

### Définition of Done par version

#### v0.2
- [ ] Tests de génération passent sur Windows/macOS/Linux
- [ ] Devcontainer démarre en moins de 2 minutes
- [ ] Documentation mise à jour
- [ ] Pas de régression v0.1

#### v0.3  
- ✅ Pre-commit hooks configurés et fonctionnels
- ✅ Code généré passe tous les linters (0 warnings par défaut)
- ✅ Performance : hooks pré-installés, exécution <5s
- ✅ Workflow automatisé complet Git + GitHub
- ✅ Documentation utilisateur et troubleshooting complètes

#### v0.4
- [ ] Coverage > 90% pour les tests du template
- [ ] Tests d'intégration end-to-end
- [ ] Performance : tests complets en moins de 5 minutes
- [ ] Documentation tests et mocking

#### v0.5
- [ ] CI/CD workflows testés et documentés
- [ ] Déploiement automatique documentation
- [ ] Release process validé
- [ ] Monitoring et alerting basiques

## Calendrier prévisionnel

```mermaid
gantt
    title Roadmap PyFoundry
    dateFormat  YYYY-MM-DD
    section v0.1
    Squelette            :done, v01, 2024-01-01, 2024-01-15
    section v0.2  
    Environnement        :active, v02, 2024-01-15, 2024-02-01
    section v0.3
    Qualité de code      :v03, 2024-02-01, 2024-02-15
    section v0.4
    Tests                :v04, 2024-02-15, 2024-03-01
    section v0.5
    CI/CD                :v05, 2024-03-01, 2024-03-15
```

## Contribution aux versions

### Comment contribuer à v0.2
1. **Issues étiquetées** `v0.2` dans GitHub
2. **Focus** : reproductibilité et environnement
3. **Tests manuels** sur différents OS requis

### Priorisation des features
1. **Impact utilisateur** : Facilite-t-elle l'usage quotidien ?
2. **Complexité technique** : Effort de développement
3. **Maintenance** : Coût de maintenance long terme
4. **Feedback communauté** : Demandes utilisateurs

## Métriques de succès

### v0.2
- **Adoption** : 10+ projets générés et utilisés
- **Performance** : Setup en < 5 minutes
- **Compatibilité** : Fonctionne sur 3 OS majeurs

### v0.3
- **Qualité** : ✅ 0 warning sur code généré par défaut
- **Productivité** : ✅ Setup qualité 100% automatisé (0 intervention)
- **Performance** : ✅ Pre-commit hooks pré-installés 
- **GitHub** : ✅ Authentification et remote configurés automatiquement

### v0.4
- **Fiabilité** : 100% tests template passent
- **Couverture** : >90% code coverage

### v0.5
- **Automation** : 100% releases automatisées
- **Monitoring** : Métriques usage disponibles