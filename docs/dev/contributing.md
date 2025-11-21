# Guide de contribution

## Configuration de développement

### Pré-requis
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- [cruft](https://cruft.github.io/cruft/) 
- Git

### Setup initial

#### 1. Créer l'environnement de développement
```bash
# Créer un environnement conda/mamba pour le développement du template
mamba create -y -n pyfoundry -c conda-forge python=3.11

# Activer l'environnement
mamba activate pyfoundry

# Installer les outils nécessaires pour développer le template
mamba install nb_conda_kernels cruft mkdocs-material pytest pytest-cookies pytest-cov pre-commit ruff mypy --yes
```

#### 2. Cloner et configurer le projet
```bash
# Cloner le dépôt
git clone https://github.com/username/PyFoundry.git
cd PyFoundry

# Installer les dépendances de développement (si applicables)
# uv pip install -e ".[dev]"  # Sera disponible en v0.4

# Installer les hooks pre-commit (quand disponibles v0.3)
# pre-commit install
```

!!! info "Environnement pyfoundry"
    L'environnement `pyfoundry` est utilisé pour développer et tester le template lui-même. Les projets générés par le template auront leurs propres environnements.

### Environnement de test
```bash
# Générer un projet test
cruft create . --no-input

# Tester le projet généré
cd mon-projet-data-science
uv pip install -e .
```

### Documentation

#### Développement local
```bash
# Installer les dépendances de documentation
mamba install mkdocs-material --yes

# Serveur local avec rechargement automatique
mkdocs serve

# Accessible sur http://127.0.0.1:8000
```

#### Build de production
```bash
# Générer les fichiers statiques
mkdocs build

# Les fichiers sont générés dans le dossier site/
ls site/
```

#### Déploiement GitHub Pages
```bash
# Déploiement automatique (nécessite droits push)
mkdocs gh-deploy

# Ou via GitHub Actions (recommandé pour la production)
```

### Publication sur GitHub

#### Installation GitHub CLI
```bash
# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh

# macOS
brew install gh

# Windows
winget install --id GitHub.cli
```

#### Authentification GitHub
```bash
# Configuration initiale
gh auth login

# Choisir:
# - GitHub.com
# - HTTPS
# - Authentification via browser ou token
# - Upload SSH key (optionnel)
```

#### Création du repository
```bash
# Depuis le dossier PyFoundry
cd /path/to/PyFoundry

# Créer le repository directement
gh repo create PyFoundry --public --source=. --remote=origin --push

# Alternative avec paramètres complets
gh repo create PyFoundry \
  --description "Template Cookiecutter de qualité industrielle pour projets Data Science Python" \
  --homepage "https://guillaume.github.io/PyFoundry" \
  --public \
  --source=. \
  --remote=origin \
  --push
```

#### Configuration GitHub Pages
```bash
# Activer GitHub Pages via CLI
gh api repos/:owner/:repo/pages \
  --method POST \
  --field source[branch]=main \
  --field source[path]="/" \
  --field build_type="workflow"

# Vérifier le statut
gh api repos/:owner/:repo/pages
```

## Workflow de développement

### Structure des contributions

```
PyFoundry/
├── {{ cookiecutter.project_slug }}/     # Template du projet généré
├── docs/                                 # Documentation (cette section)
├── tests/                                # Tests du template
├── hooks/                                # Hooks Cookiecutter
├── cookiecutter.json                    # Configuration du template
└── mkdocs.yml                           # Configuration documentation
```

### Cycle de développement

1. **Issue/Feature** : Créer ou prendre une issue GitHub
2. **Branche** : `git checkout -b feature/nom-feature`
3. **Développement** : Modifier le template
4. **Test** : Générer et tester un projet
5. **Documentation** : Mettre à jour la doc si nécessaire
6. **PR** : Ouvrir une Pull Request

### Types de modifications

#### 1. Modification du template généré
```bash
# Modifier les fichiers dans {{ cookiecutter.project_slug }}/
vim "{{ cookiecutter.project_slug }}/pyproject.toml"

# Tester la génération
cruft create . --no-input
cd mon-projet-data-science
# Valider les changements
```

#### 2. Ajout de variables Cookiecutter
```json
{
    "project_name": "Mon Projet Data Science",
    "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-') }}",
    "description": "Description du projet",
    "python_version": "3.11",
    "nouvelle_variable": "valeur_par_defaut"
}
```

#### 3. Documentation
```bash
# Modifier la documentation
vim docs/user/usage.md

# Prévisualiser localement
mkdocs serve

# Accessible sur http://127.0.0.1:8000
```

## Standards de qualité

### Messages de commit
Format : `type(scope): description`

**Types** :
- `feat` : Nouvelle fonctionnalité
- `fix` : Correction de bug
- `docs` : Documentation seulement
- `style` : Formatting, missing semicolons, etc.
- `refactor` : Refactoring de code
- `test` : Ajout de tests
- `chore` : Maintenance, deps, etc.

**Exemples** :
```bash
feat(devcontainer): ajouter support pour uv
fix(template): corriger chemin dans .gitignore  
docs(user): améliorer guide installation
chore(deps): mettre à jour mkdocs-material
```

### Structure des templates

#### Variables Cookiecutter
- **snake_case** pour les variables techniques
- **Descriptions claires** pour l'utilisateur final
- **Valeurs par défaut sensées**
- **Validation** dans les hooks si nécessaire

#### Fichiers générés
- **Cohérence** : même style dans tous les fichiers
- **Comments** : expliquer les choix non évidents
- **Extensibilité** : faciliter les modifications futures

### Tests automatisés (v0.4)

#### Architecture des tests
Les tests utilisent `pytest-cookies` pour valider la génération du template dans un environnement isolé :

```
tests/
├── __init__.py                    # Package tests
├── conftest.py                    # Fixtures pytest
├── test_template_generation.py   # Tests de génération du template
└── test_configurations.py        # Tests de validation des configurations
```

#### Types de tests

**Tests de génération** (`test_template_generation.py`) :
- Génération sans erreur avec différents contextes
- Structure de projet créée (dossiers `src/`, `data/`, `notebooks/`)
- Fichiers essentiels présents (`README.md`, `pyproject.toml`, `.gitignore`)
- Transformation correcte du `project_slug`
- Intégration `github_username` dans les URLs

**Tests de validation** (`test_configurations.py`) :
- `pyproject.toml` : syntaxe TOML valide, structure projet, configuration ruff/mypy
- `.pre-commit-config.yaml` : YAML valide, repos attendus (ruff, mypy, hooks)
- `devcontainer.json` : structure devcontainer, éléments essentiels
- `.gitignore` : patterns Data Science essentiels
- Configuration Ruff : règles pandas/numpy, line-length
- Configuration MyPy : mode progressif, overrides Data Science

#### Lancement des tests

```bash
# Activer l'environnement
mamba activate pyfoundry

# Lancer tous les tests avec couverture
pytest tests/ -v --cov=. --cov-report=term-missing

# Lancer un fichier de test spécifique
pytest tests/test_template_generation.py -v

# Lancer un test spécifique
pytest tests/test_configurations.py::test_pyproject_toml_valid -v

# Tests sans couverture (plus rapide)
pytest tests/ -v
```

#### Modifier et enrichir les tests

**Ajouter un nouveau test de génération** :
```python
# Dans tests/test_template_generation.py
def test_nouvelle_fonctionnalite(cookies, default_template_context):
    """Test de la nouvelle fonctionnalité."""
    result = cookies.bake(extra_context=default_template_context)
    
    # Vérifier le projet généré
    assert result.exit_code == 0
    assert (result.project_path / "nouveau_fichier.txt").exists()
```

**Ajouter un test de validation** :
```python
# Dans tests/test_configurations.py  
def test_nouvelle_config_valid(cookies, minimal_template_context):
    """Test que nouvelle_config.yml est valide."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    config_path = result.project_path / "nouvelle_config.yml"
    assert config_path.exists()
    
    content = yaml.safe_load(config_path.read_text())
    assert "expected_key" in content
```

**Créer un nouveau contexte de test** :
```python
# Dans tests/conftest.py
@pytest.fixture
def nouveau_contexte():
    """Contexte spécialisé pour tests spécifiques."""
    return {
        "project_name": "Test Spécialisé",
        "nouvelle_option": "valeur_test",
        # ... autres paramètres
    }
```

#### CI/CD GitHub Actions

Les tests s'exécutent automatiquement via `.github/workflows/test-template.yml` :
- Déclenchement sur `push` et `pull_request`
- Test sur Python 3.11 et 3.12
- Validation du projet généré avec `uv`, `ruff`, `mypy`
- Upload de couverture vers Codecov

#### Bonnes pratiques

1. **Fixtures** : Utiliser `minimal_template_context` pour tests rapides, `default_template_context` pour tests complets
2. **Isolation** : Chaque test génère un projet dans un dossier temporaire
3. **Performance** : Préférer les tests de structure aux tests d'exécution
4. **Validation** : Tester la syntaxe des fichiers de configuration
5. **Couverture** : Viser 100% de couverture des tests critiques

#### Tests manuels end-to-end

##### Test depuis la branche main (locale)

```bash
# Depuis la racine de PyFoundry
cruft create . --no-input

# Vérifier le projet généré
cd mon-projet-data-science
ls -la

# Vérifier les fichiers clés
cat CLAUDE.md
ls .claude/commands/
cat .devcontainer/devcontainer.json | grep claude-code
```

##### Test depuis une branche de développement

Lorsque vous développez une nouvelle fonctionnalité sur une branche, vous pouvez tester le template avant de merger :

```bash
# Option 1: Test depuis la branche locale
# (nécessite que la branche soit pushée sur GitHub)
cruft create https://github.com/castorfou/PyFoundry.git \
  --checkout 15-ajouter-claude-code \
  --no-input

# Option 2: Test avec paramètres personnalisés
cruft create https://github.com/castorfou/PyFoundry.git \
  --checkout ma-branche-feature \
  --extra-context '{"project_name": "Test Ma Feature", "use_node": "n"}'

# Option 3: Test interactif depuis une branche
cruft create https://github.com/castorfou/PyFoundry.git \
  --checkout ma-branche-feature
```

##### Workflow de test complet depuis une branche

```bash
# 1. Créer et pousser votre branche de développement
git checkout -b feature/nouvelle-fonctionnalite
# ... faire vos modifications ...
git add .
git commit -m "feat: ajouter nouvelle fonctionnalité"
git push origin feature/nouvelle-fonctionnalite

# 2. Générer un projet test depuis cette branche
cd /tmp  # ou tout autre répertoire de test
cruft create https://github.com/castorfou/PyFoundry.git \
  --checkout feature/nouvelle-fonctionnalite \
  --no-input

# 3. Vérifier le projet généré
cd mon-projet-data-science

# 4. Tester dans le devcontainer
code .
# → Accepter "Reopen in Container" dans VS Code

# 5. Vérifier les fonctionnalités
# - Extensions installées
# - Fichiers de configuration corrects
# - Scripts de setup fonctionnels
# - Documentation à jour
```

##### Checklist de validation end-to-end

Après avoir généré un projet test, vérifier :

- [ ] **Structure** : Tous les dossiers attendus sont créés
- [ ] **Fichiers** : `CLAUDE.md`, `.claude/commands/`, `.devcontainer/`, etc.
- [ ] **Variables Cookiecutter** : Nom du projet, description correctement injectés
- [ ] **Devcontainer** : Se construit sans erreur
- [ ] **Extensions VS Code** : Claude Code et autres installées
- [ ] **Scripts setup** : `postCreateCommand.sh` s'exécute correctement
- [ ] **Git** : Repository initialisé, `.gitignore` approprié
- [ ] **Dependencies** : `uv pip sync` fonctionne
- [ ] **Quality tools** : `ruff check .` et `mypy src/` passent
- [ ] **Tests** : `pytest` trouve et exécute les tests
- [ ] **Documentation** : README.md correct avec bonnes URLs

!!! tip "Astuce : Test rapide depuis une PR"
    Vous pouvez tester directement depuis une Pull Request avant de merger :
    ```bash
    cruft create https://github.com/castorfou/PyFoundry.git \
      --checkout refs/pull/42/head \
      --no-input
    ```

!!! warning "Important : cruft et les fichiers committés"
    **cruft ne voit que les fichiers committés dans Git**. Pour tester des modifications :

    1. Faire les modifications au template
    2. **Committer les changements** : `git add . && git commit -m "test: modifications template"`
    3. **Pousser sur GitHub** : `git push origin ma-branche`
    4. Tester avec cruft depuis la branche distante

    Les fichiers non committés ou non pushés ne seront pas inclus dans le projet généré !

## Roadmap et priorités

### v0.2 : Environnement reproductible
- [ ] Fichier `uv.lock` pour lock des dépendances
- [ ] Scripts de setup automatisés
- [ ] Support multi-OS (Windows, macOS, Linux)

### v0.3 : Qualité de code
- [ ] Configuration pre-commit complète
- [ ] Configuration ruff dans pyproject.toml
- [ ] Intégration mypy pour le typing
- [ ] Formatage automatique (black/ruff format)

### v0.4 : Tests
- [ ] Structure de tests avec pytest
- [ ] Tests du template avec pytest-cookies
- [ ] Coverage reporting
- [ ] Tests d'intégration CI/CD

### v0.5 : CI/CD
- [ ] GitHub Actions workflows
- [ ] Tests automatisés sur PR
- [ ] Publication automatique documentation
- [ ] Release automation

## Bonnes pratiques

### Documentation
- **Toujours** documenter les nouveautés
- **Screenshots** pour les changements UI/UX
- **Exemples concrets** plutôt qu'abstraits
- **Mise à jour** de la roadmap

### Backward compatibility
- **Pas de breaking changes** sans version majeure
- **Deprecation warnings** avant suppression
- **Migration guide** pour les changements majeurs

### Performance
- **Template léger** : éviter les dépendances lourdes par défaut
- **Génération rapide** : optimiser les hooks
- **Documentation efficace** : structure claire, recherche facile

## Résolution de problèmes

### Template ne se génère pas
```bash
# Vérifier la syntaxe JSON
python -m json.tool cookiecutter.json

# Tester avec debug
cruft create . --no-input --verbose
```

### Erreurs de devcontainer  
```bash
# Valider le JSON
python -m json.tool "{{ cookiecutter.project_slug }}/.devcontainer/devcontainer.json"

# Tester l'image Docker
docker run -it mcr.microsoft.com/devcontainers/python:3.11-bookworm bash
```

### Documentation ne se build pas
```bash
# Vérifier la config MkDocs
mkdocs build --strict

# Tester localement
mkdocs serve --dev-addr=127.0.0.1:8000
```

## Ressources

- [Cookiecutter Documentation](https://cookiecutter.readthedocs.io/)
- [Dev Containers Specification](https://containers.dev/)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- [uv Documentation](https://github.com/astral-sh/uv)