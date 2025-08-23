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
mamba install nb_conda_kernels cruft mkdocs-material --yes
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

### Tests requis

#### Tests unitaires (à venir v0.4)
```bash
# Tester la génération du template
pytest tests/test_generation.py

# Tester le contenu généré  
pytest tests/test_project_structure.py

# Tester les commandes dans le projet généré
pytest tests/test_project_commands.py
```

#### Tests manuels
1. **Génération** : `cruft create . --no-input`
2. **Devcontainer** : Ouvrir dans VS Code
3. **Installation** : `uv pip install -e .`
4. **Jupyter** : `jupyter lab` fonctionne
5. **Git** : Repository initialisé correctement

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