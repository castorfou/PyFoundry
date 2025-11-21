# Guide de Test du Template PyFoundry

Ce guide explique comment tester le template PyFoundry lors du développement.

## Types de Tests

### 1. Tests Automatisés (pytest)

Les tests automatisés utilisent `pytest-cookies` pour générer des projets temporaires et vérifier leur configuration.

```bash
# Activer l'environnement
source ~/miniforge3/etc/profile.d/conda.sh && conda activate pyfoundry

# Lancer tous les tests
pytest tests/

# Lancer un fichier de test spécifique
pytest tests/test_mkdocs_integration.py -v

# Lancer un test spécifique
pytest tests/test_mkdocs_integration.py::test_mkdocs_yml_created -v
```

**Avantages** :
- Rapide et automatisé
- Vérifie la structure et la configuration
- Couverture complète avec 35+ tests

**Limitations** :
- Ne teste pas l'expérience utilisateur complète
- Ne vérifie pas que les outils fonctionnent réellement dans le projet généré

### 2. Test Manuel du Projet Généré

Pour tester le template avec vos modifications locales (même non commitées), utilisez `cookiecutter` directement plutôt que `cruft`.

#### Différence importante : cruft vs cookiecutter

- **`cruft create`** : Utilise Git, ne voit que les fichiers **commités**
- **`cookiecutter`** : Lit directement le filesystem, voit **tous les fichiers** (commités ou non)

#### Workflow de test manuel

```bash
# 1. Nettoyer le dossier de test (si nécessaire)
rm -rf ~/temp/mon-projet-data-science

# 2. Créer un projet test avec cookiecutter
cd ~/temp
cookiecutter /home/guillaume/git/PyFoundry --no-input

# 3. Aller dans le projet généré
cd mon-projet-data-science

# 4. Vérifier que les fichiers attendus existent
ls -la mkdocs.yml           # Configuration MkDocs
ls -la docs/                # Structure documentation
ls -la .github/workflows/   # CI/CD workflows

# 5. Initialiser git (si nécessaire pour certains tests)
git init
git add .
git commit -m "Initial commit"

# 6. Installer les dépendances de développement
uv sync --extra dev

# 7. Tester que les outils fonctionnent
uv run ruff check .
uv run pytest --collect-only  # Vérifie que pytest trouve les tests
uv run mkdocs serve           # Lance la documentation
```

#### Tester avec des valeurs personnalisées

Si vous voulez tester avec des valeurs spécifiques plutôt que les valeurs par défaut :

```bash
# Mode interactif (vous pose les questions)
cd ~/temp
cookiecutter /home/guillaume/git/PyFoundry

# Ou avec des valeurs en ligne de commande
cookiecutter /home/guillaume/git/PyFoundry \
  project_name="My Test Project" \
  python_version="3.12" \
  use_node="y"
```

## Tests Spécifiques par Fonctionnalité

### Tester MkDocs

```bash
cd ~/temp/mon-projet-data-science

# Installer les dépendances docs
uv sync --extra docs

# Vérifier que mkdocs.yml est valide
uv run mkdocs build --strict

# Prévisualiser la documentation
uv run mkdocs serve
# Ouvrir http://localhost:8000 dans le navigateur

# Vérifier la structure
ls -la docs/user/
ls -la docs/dev/
cat docs/index.md
```

### Tester les Workflows CI/CD

Les workflows GitHub Actions ne peuvent être testés complètement qu'une fois pushés sur GitHub, mais vous pouvez :

```bash
# Vérifier la syntaxe YAML
cd ~/temp/mon-projet-data-science
cat .github/workflows/ci.yml | python -c "import yaml, sys; yaml.safe_load(sys.stdin)"
cat .github/workflows/docs.yml | python -c "import yaml, sys; yaml.safe_load(sys.stdin)"

# Simuler les étapes localement
uv sync --extra dev
uv run ruff check .
uv run pytest
uv run mypy src/
```

### Tester le DevContainer

```bash
cd ~/temp/mon-projet-data-science

# Vérifier que devcontainer.json est valide
cat .devcontainer/devcontainer.json | python -c "import json, sys; json.load(sys.stdin)"

# Pour tester réellement : ouvrir dans VS Code
code .
# Puis "Reopen in Container" depuis la palette de commandes
```

### Tester pre-commit

```bash
cd ~/temp/mon-projet-data-science

# Installer les hooks
uv sync --extra dev
uv run pre-commit install

# Tester sur tous les fichiers
uv run pre-commit run --all-files

# Faire un commit de test pour vérifier que les hooks s'exécutent
git add .
git commit -m "test: vérification pre-commit"
```

## Bonnes Pratiques

### Avant de commiter

1. **Lancer les tests automatisés**
   ```bash
   cd /home/guillaume/git/PyFoundry
   source ~/miniforge3/etc/profile.d/conda.sh && conda activate pyfoundry
   pytest tests/ -v
   ```

2. **Faire un test manuel complet**
   ```bash
   cd ~/temp
   rm -rf mon-projet-data-science
   cookiecutter /home/guillaume/git/PyFoundry --no-input
   cd mon-projet-data-science
   uv sync --extra dev
   # Tester les fonctionnalités ajoutées/modifiées
   ```

3. **Vérifier le linting**
   ```bash
   cd /home/guillaume/git/PyFoundry
   ruff check tests/
   mypy tests/
   ```

### Nettoyage

Après vos tests, pensez à nettoyer :

```bash
# Supprimer les projets de test
rm -rf ~/temp/mon-projet-data-science
rm -rf ~/temp/my-test-project

# Les tests pytest créent des fichiers temporaires qui sont automatiquement nettoyés
```

## Debugging

### Les tests échouent mais le projet généré semble bon

Vérifiez que vous testez bien la bonne version :

```bash
# Test automatisé : teste depuis le dossier du template
cd /home/guillaume/git/PyFoundry
pytest tests/test_mkdocs_integration.py -v

# Test manuel : régénérer le projet
cd ~/temp
rm -rf mon-projet-data-science
cookiecutter /home/guillaume/git/PyFoundry --no-input
```

### Le projet généré manque des fichiers

- Si vous utilisez `cruft create` : les fichiers non commités ne sont pas inclus
- Solution : utiliser `cookiecutter` à la place, ou commiter vos changements

### MkDocs ne se lance pas

```bash
# Vérifier que les dépendances sont installées
cd ~/temp/mon-projet-data-science
uv sync --extra docs

# Vérifier qu'il n'y a pas d'erreur de config
uv run mkdocs build --strict

# Vérifier les logs détaillés
uv run mkdocs serve --verbose
```

## Ressources

- [pytest-cookies documentation](https://pytest-cookies.readthedocs.io/)
- [Cookiecutter documentation](https://cookiecutter.readthedocs.io/)
- [Cruft documentation](https://cruft.github.io/cruft/)
