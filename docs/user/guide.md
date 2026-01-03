# Guide complet PyFoundry

PyFoundry est un template Cookiecutter moderne qui automatise la création de projets Data Science en Python avec un environnement de développement reproductible et des outils de qualité de code intégrés.

## 🚀 Démarrage rapide

### Création d'un projet

```bash
# Installation de cruft si nécessaire
pip install cruft

# Génération du projet
cruft create https://github.com/castorfou/PyFoundry.git
```

### Paramètres de configuration

Lors de la création, PyFoundry demande :

- **`project_name`** : Nom affiché du projet
- **`project_slug`** : Nom technique (auto-généré)
- **`description`** : Description du projet
- **`python_version`** : Version Python (3.11 par défaut)
- **`github_username`** : Votre nom d'utilisateur GitHub (pour configuration automatique)
- **`use_node`** : Installation Node.js optionnelle (n/y)

### Ouverture du projet

```bash
# Ouvrir avec VS Code (recommandé)
code mon-projet-data-science
# → VS Code propose "Reopen in Container"
```

## 🐳 Environnement devcontainer

PyFoundry utilise les devcontainers VS Code pour un environnement reproductible.

### Configuration automatique

Le devcontainer configure automatiquement :

- **Environnement Python** avec uv (gestionnaire de paquets moderne)
- **Extensions VS Code** optimisées pour Data Science
- **Configuration Git** héritée du système host
- **GitHub CLI** pour l'intégration GitHub
- **Pre-commit hooks** pour la qualité de code
- **Authentification GitHub** guidée
- **Node.js** (optionnel, si `use_node=y`)

### Support Node.js (optionnel)

Quand `use_node` est activé lors de la création :

- **Node.js LTS** installé automatiquement
- **npm** configuré et prêt à l'emploi
- **package.json** basique créé
- **`.gitignore`** étendu pour Node.js
- Support développement frontend/fullstack en complément de Python

Exemple d'activation :
```bash
cruft create https://github.com/castorfou/PyFoundry.git \
  --extra-context '{"use_node": "y"}'
```

### Fonctionnalités incluses

#### Extensions VS Code intégrées

- **Python** : pylance, python debugger
- **Jupyter** : support notebooks complet avec renderers
- **Qualité** : ruff, mypy integration  
- **Git** : GitLens, GitHub integration
- **Productivité** : GitHub Copilot, YAML, JSON support

#### Variables d'environnement
```bash
PROJECT_NAME="Mon Projet"           # Nom du projet
PYTHONPATH="/workspaces/projet/src" # Path Python automatique
ENVIRONMENT="development"           # Environnement de dev
```

## 🔧 Outils de qualité automatisés

### Configuration Ruff (Linting & Formatage)

Ruff remplace plusieurs outils traditionnels :

- **Linting** (pylint, flake8)
- **Formatage** (black)
- **Import sorting** (isort)
- **Syntaxe moderne** (pyupgrade)

#### Règles adaptées Data Science
```python
# Variables df acceptées (PD901 ignoré)
df = pd.read_csv("data.csv")

# Règles spéciales pour notebooks
# E402 (imports) plus flexibles en .py générés depuis notebooks

# Print() autorisé dans scripts/
print("Configuration terminée")  # OK dans scripts/
```

### Configuration MyPy (Types statiques)

MyPy est configuré en mode **progressif** :
```python
# Types encouragés mais pas forcés au début
def process_data(df: pd.DataFrame) -> pd.DataFrame:  # ✅ Recommandé
    return df.dropna()

def legacy_function(data):  # ⚠️ Permis mais warning
    return data
```

#### Support bibliothèques Data Science

- Types automatiquement ignorés pour `matplotlib`, `seaborn`, `sklearn`
- Notebooks exempts de vérification stricte
- Configuration adaptable selon maturité du projet

### Pre-commit hooks automatiques

Les hooks s'exécutent automatiquement avant chaque commit :

#### Hooks standards

- **Formatage** : suppression espaces, fins de ligne correctes
- **Validation** : syntaxe YAML/TOML/JSON
- **Sécurité** : détection fichiers volumineux, conflits Git

#### Hooks qualité Python

- **Ruff lint** : correction automatique des erreurs
- **Ruff format** : formatage uniforme du code
- **MyPy** : vérification types sur `src/` uniquement

#### Hooks sécurité

- **detect-secrets** : détection tokens/mots de passe dans le code

### Utilisation quotidienne

```bash
# Les hooks s'exécutent automatiquement
git add .
git commit -m "feat: nouvelle fonctionnalité"
# → Ruff, MyPy, formatage exécutés automatiquement

# Exécution manuelle si besoin
pre-commit run --all-files

# Commandes directes
ruff check . --fix      # Linting avec corrections
ruff format .           # Formatage
mypy src/              # Vérification types
```

## 🌐 Intégration GitHub

### Configuration automatique

Si vous fournissez votre `github_username`, PyFoundry configure :

- **Remote origin** : `https://github.com/username/projet.git`
- **Authentification** : `gh auth login` automatique
- **Credential helper** : configuration pour éviter les erreurs d'auth

### Authentification GitHub

Lors du premier setup :

```bash
🔐 Authentification GitHub requise pour push/pull
Lancement de l'authentification...

Note : Vous devrez appuyer sur Entrée pour 'ouvrir' le navigateur.
   Le navigateur ne s'ouvrira pas (limitation devcontainer connue).
   → Entrez manuellement l'URL et le code dans votre navigateur host.

? Authenticate Git with your GitHub credentials? Yes
! First copy your one-time code: 1DD5-FDA2
Press Enter to open https://github.com/login/device in your browser...
```

### Création du dépôt distant

Après l'authentification, créez le dépôt GitHub :

```bash
# Option 1: Création automatique (recommandé)
gh repo create mon-projet --public --source=. --remote=origin --push

# Option 2: Création manuelle
# 1. Créer le dépôt sur https://github.com/username
# 2. Puis: git push -u origin main
```

## 📁 Structure de projet

PyFoundry génère une structure standardisée :

```
mon-projet-data-science/
├── .devcontainer/              # Configuration devcontainer
│   ├── devcontainer.json      # Config VS Code + features
│   └── postCreateCommand.sh   # Setup automatisé
├── .pre-commit-config.yaml    # Hooks qualité de code
├── data/
│   ├── raw/                   # Données brutes
│   ├── processed/             # Données traitées
│   └── external/              # Données externes
├── models/                    # Modèles ML entraînés
├── notebooks/                 # Jupyter notebooks
├── src/                       # Code source Python
├── logs/                      # Fichiers de log
├── .gitignore                 # Exclusions Git adaptées DS
├── pyproject.toml            # Config projet + outils qualité
└── README.md                 # Documentation projet
```

### Dossiers créés automatiquement

- **`data/`** : Organisé par type (raw/processed/external)
- **`models/`** : Stockage modèles entraînés
- **`logs/`** : Fichiers de log du projet
- **`.jupyter/`** : Configuration Jupyter personnalisée

## ⚙️ Configuration avancée

### Personnalisation des règles Ruff

```toml
# Dans pyproject.toml
[tool.ruff]
# Ajouter des règles spécifiques
extend-select = ["C90"]  # Complexité cyclomatique
ignore = ["E203"]        # Ignorer règle spécifique

# Règles par répertoire
[tool.ruff.lint.per-file-ignores]
"src/legacy/*.py" = ["F401"]  # Code legacy plus permissif
```

### Configuration MyPy progressive

```toml
# Devenir plus strict progressivement
[tool.mypy]
disallow_untyped_defs = true         # Activer quand prêt
disallow_any_generics = true         # Types génériques stricts
strict_optional = true               # None explicite
```

### Hooks pre-commit personnalisés

```yaml
# Ajouter dans .pre-commit-config.yaml
- repo: local
  hooks:
    - id: jupyter-nb-clear-output
      name: Clear Jupyter outputs
      entry: jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace
      language: system
      files: \.ipynb$
```

## 🐛 Résolution de problèmes

### Setup devcontainer échoue

```bash
# Vérifier les logs : VS Code > View > Output > Dev Containers
# Causes communes :
# - docker login ghcr.io requis pour feature uv
# - Connexion réseau pour dépendances
# - Authentification GitHub interrompue
```

### Pre-commit hooks échouent

```bash
# Réinstaller si nécessaire
pre-commit clean
pre-commit install-hooks

# Debug détaillé
pre-commit run --all-files --verbose

# Bypass temporaire (non recommandé)
git commit -m "message" --no-verify
```

### Erreurs d'authentification GitHub

```bash
# Vérifier status
gh auth status

# Re-authentifier
gh auth login --git-protocol https --web

# Alternative avec token personnel
git remote set-url origin https://username:token@github.com/user/repo.git
```

### Repository not found

```bash
# Erreur normale si dépôt distant inexistant
remote: Repository not found.

# Solution : créer le dépôt d'abord
gh repo create nom-projet --public --source=. --remote=origin --push
```

### MyPy trop strict

```bash
# Configuration progressive dans pyproject.toml
[tool.mypy]
disallow_untyped_defs = false    # Commencer permissif
disallow_incomplete_defs = true  # Activer progressivement
```

## 🤖 Support Claude Code

PyFoundry intègre le support natif de Claude Code, l'assistant IA d'Anthropic pour le développement.

### Extension VS Code installée

L'extension **Claude Code** (`anthropic.claude-code`) est automatiquement installée dans votre devcontainer, prête à l'emploi.

### Fichiers Claude Code générés

Chaque projet créé inclut :

- **`CLAUDE.md`** : Documentation projet pour Claude Code
  - Description du projet et objectifs
  - Stack technique détaillée
  - Structure du projet
  - Conventions de code
  - Commandes utiles

- **`.claude/commands/`** : Commandes slash pré-configurées
  - `/fix-issue` : Workflow complet pour résoudre une issue GitHub (TDD, tests, doc, CI/CD)
  - `/stocke-memoire` : Sauvegarde des apprentissages dans docs/claude/memory/

### Utilisation avec Claude Code

```bash
# Ouvrir le projet dans VS Code avec Claude Code
code mon-projet-data-science

# Claude Code lit automatiquement CLAUDE.md pour comprendre :
# - L'architecture du projet
# - Les outils et dépendances utilisés
# - Les conventions de code à respecter
# - Les commandes disponibles
```

### Personnalisation CLAUDE.md

Le fichier `CLAUDE.md` est généré avec vos paramètres de projet. Vous pouvez l'enrichir avec :

- Instructions spécifiques à votre domaine
- Règles métier importantes
- Patterns de code à suivre
- Documentation d'APIs utilisées

### Commandes slash incluses

#### `/fix-issue {numéro}`
Workflow TDD complet pour résoudre une issue GitHub :
1. Récupère les détails de l'issue
2. Crée une branche depuis l'issue
3. Implémente en TDD (tests RED puis code)
4. Vérifie qualité (tests, lint, typecheck)
5. Met à jour la documentation
6. Commit et push
7. Vérifie la CI/CD
8. Crée la pull request

#### `/stocke-memoire`
Sauvegarde tes apprentissages et décisions importantes dans `docs/claude/memory/` avec horodatage.

### Création de commandes personnalisées

Créez des fichiers `.md` dans `.claude/commands/` :

```markdown
# Exemple : .claude/commands/test.md
Lance la suite de tests complète avec coverage :
\`\`\`bash
pytest --cov=src --cov-report=html
\`\`\`
```

Puis utilisez `/test` dans Claude Code pour exécuter cette commande.

## 🔄 Mise à jour du template

```bash
# Mise à jour vers version récente
cruft update

# Résoudre conflits éventuels
# Tester le projet mis à jour
```

## 🎯 Workflow recommandé

1. **Création** : `cruft create` avec vos paramètres
2. **Setup** : `code projet` → devcontainer automatique  
3. **Auth GitHub** : Suivre les instructions d'authentification
4. **Dépôt** : `gh repo create` pour créer le dépôt distant
5. **Développement** : Hooks qualité actifs automatiquement
6. **Push** : `git push` fonctionne sans configuration supplémentaire

## 📚 Ressources

- **Template GitHub** : [PyFoundry](https://github.com/castorfou/PyFoundry)
- **Documentation Ruff** : [Configuration](https://docs.astral.sh/ruff/configuration/)
- **MyPy Guide** : [Documentation](https://mypy.readthedocs.io/)
- **Pre-commit** : [Hooks disponibles](https://pre-commit.com/hooks.html)

---

PyFoundry vous offre un environnement Data Science moderne, reproductible et de qualité industrielle en quelques minutes ! 🚀