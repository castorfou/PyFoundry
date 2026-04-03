# Guide de Test du Template PyFoundry

Ce guide explique comment tester le template PyFoundry lors du développement.

## Types de Tests

### 1. Tests Automatisés (pytest)

Les tests automatisés utilisent `pytest-cookies` pour générer des projets temporaires et vérifier leur configuration.

```bash
# Depuis le devcontainer PyFoundry
source /home/vscode/.venv/bin/activate && pytest tests -v

# Un fichier spécifique
pytest tests/test_template_generation.py -v

# Un test spécifique
pytest tests/test_template_generation.py::test_node_enabled_when_requested -v
```

**Avantages** :

- Rapide et automatisé
- Vérifie la structure et la configuration
- Couverture complète (37+ tests)

**Limitations** :

- Ne teste pas l'expérience utilisateur complète
- Ne vérifie pas que les outils fonctionnent réellement dans le projet généré

### 2. Test Manuel du Projet Généré

Pour tester avec vos modifications locales (y compris non commitées), utiliser `cookiecutter` plutôt que `cruft`.

#### Différence cruciale : cruft vs cookiecutter

- **`cruft create`** : utilise Git, ne voit que les fichiers **commités**
- **`cookiecutter`** : lit le filesystem, voit **tous les fichiers** (commités ou non)

#### Workflow de test manuel

```bash
# 1. Nettoyer
rm -rf ~/temp/mon-projet-data-science

# 2. Générer avec cookiecutter (modifications non commitées visibles)
cd ~/temp
cookiecutter /workspaces/PyFoundry --no-input

# 3. Avec des options spécifiques
cookiecutter /workspaces/PyFoundry --no-input \
  --extra-context '{"docker_in_docker": "y"}'

# 4. Ouvrir dans VS Code et tester le devcontainer
code ~/temp/mon-projet-data-science
# → "Reopen in Container" dans VS Code
```

#### Test depuis une branche commitée (via cruft)

```bash
# Depuis l'hôte, après avoir pushé la branche
cd ~/temp && rm -rf mon-projet-data-science
cruft create https://github.com/castorfou/PyFoundry.git \
  -c 44-integrer-docker-in-docker \
  --no-input \
  --extra-context '{"docker_in_docker": "y"}'
code mon-projet-data-science
```

## Tests Spécifiques par Fonctionnalité

### Tester une option conditionnelle (ex. `docker_in_docker`)

```bash
# Option désactivée (défaut)
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input
grep -c "docker-in-docker" mon-projet-data-science/.devcontainer/devcontainer.json
# → doit retourner 0

# Option activée
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input --extra-context '{"docker_in_docker": "y"}'
grep "docker-in-docker" mon-projet-data-science/.devcontainer/devcontainer.json
# → doit montrer la feature
```

### Tester le devcontainer

```bash
# Vérifier que devcontainer.json est valide (JSON avec commentaires)
python -c "
import re, json
content = open('mon-projet-data-science/.devcontainer/devcontainer.json').read()
content = re.sub(r'//[^\n]*', '', content)
json.loads(content)
print('JSON valide')
"

# Tester réellement : ouvrir dans VS Code
code ~/temp/mon-projet-data-science
# Puis "Reopen in Container"
```

### Tester MkDocs

```bash
cd ~/temp/mon-projet-data-science
uv sync --active --extra doc
uv run --active mkdocs build --strict
```

### Tester la qualité du code

```bash
cd ~/temp/mon-projet-data-science
uv sync --active --all-extras
uv run --active ruff check .
uv run --active pytest
```

## Bonnes Pratiques

### Avant de commiter

```bash
# 1. Tests automatisés
source /home/vscode/.venv/bin/activate && pytest tests -v

# 2. Lint
ruff check tests/ docs/ --fix

# 3. Test manuel rapide
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input
```

### Nettoyage

```bash
rm -rf ~/temp/mon-projet-data-science
```

## Debugging

### Les tests échouent

```bash
# Vérifier depuis le dossier template
cd /workspaces/PyFoundry
pytest tests/ -v --tb=short
```

### Le projet généré manque des fichiers

- Si vous utilisez `cruft create` : les fichiers non commités ne sont pas inclus
- Solution : utiliser `cookiecutter` à la place, ou commiter vos changements

### Erreurs de template Jinja2

```bash
# Générer avec mode verbeux
cookiecutter /workspaces/PyFoundry --no-input -v 2>&1 | head -50
```

## Ressources

- [pytest-cookies documentation](https://pytest-cookies.readthedocs.io/)
- [Cookiecutter documentation](https://cookiecutter.readthedocs.io/)
- [Cruft documentation](https://cruft.github.io/cruft/)
