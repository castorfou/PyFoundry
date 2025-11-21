# Intégration de MkDocs dans le Template PyFoundry

**Date**: 2025-11-21 13:45
**Issue**: #14 - Ajouter mkdocs
**Branche**: 14-ajouter-mkdocs

## Contexte

Ajout de MkDocs au template PyFoundry pour permettre aux projets générés d'avoir une documentation professionnelle avec déploiement automatique sur GitHub Pages.

## Décisions d'Architecture

### Structure de Documentation: user/ vs dev/

Choix de séparer la documentation en deux sections distinctes :
- **`docs/user/`** : Pour les utilisateurs du projet (installation, utilisation, guides)
- **`docs/dev/`** : Pour les développeurs qui contribuent (architecture, contribution, API interne)

**Justification** : Cette séparation reflète deux audiences avec des besoins différents et permet une documentation plus ciblée et efficace.

### Dépendances dans pyproject.toml

MkDocs ajouté dans un groupe optionnel séparé `[project.optional-dependencies].docs` plutôt que dans `dev`.

**Justification** :
- Permet aux développeurs de choisir d'installer ou non les dépendances de documentation
- Installation avec `uv sync --extra docs`
- Groupe séparé car la documentation n'est pas nécessaire pour le développement quotidien

### Thème et Plugins

- **Thème**: `mkdocs-material` (moderne, feature-rich)
- **Plugins**: `mkdocs-git-revision-date-localized-plugin` (dates de modification automatiques)

Configuration dans mkdocs.yml avec :
- Navigation user/dev
- Dark mode
- Extensions markdown (admonitions, code highlighting, tabs)

## Implémentation

### Fichiers Créés dans `{{ cookiecutter.project_slug }}/`

1. **mkdocs.yml** - Configuration MkDocs avec thème Material
2. **docs/index.md** - Page d'accueil expliquant l'organisation
3. **docs/user/README.md** - Documentation utilisateur avec bonnes pratiques
4. **docs/dev/README.md** - Documentation développeur avec bonnes pratiques
5. **.github/workflows/docs.yml** - CI/CD pour déploiement automatique sur GitHub Pages

### Modifications des Fichiers Existants

1. **pyproject.toml** :
   - Ajout groupe `[project.optional-dependencies].docs`
   - Mise à jour URL Documentation vers GitHub Pages

2. **CLAUDE.md** :
   - Section complète sur la documentation
   - Bonnes pratiques de rédaction (état actuel vs historique)
   - Organisation user/ vs dev/
   - Commandes MkDocs

3. **README.md** :
   - Section Documentation avec lien GitHub Pages
   - Commandes pour générer localement

### Tests

Nouveau fichier `tests/test_mkdocs_integration.py` avec 16 tests :
- Création fichiers/dossiers
- Configuration correcte
- Contenu documentation
- Workflow GitHub Actions
- Build MkDocs (avec skip si plugins non installés)

**Résultats** : 35 tests passed, 1 skipped, couverture 99%

## Bonnes Pratiques de Rédaction Documentées

### Principe Central

**Décrire l'état actuel** du système, pas son évolution historique.

### À Éviter

- ❌ Références historiques : "L'issue #X a amélioré..."
- ❌ Récits d'évolution : "Nous avons d'abord implémenté X, puis Y..."
- ❌ Marqueurs temporels : "Nouvelle fonctionnalité", "Récemment ajouté"
- ❌ Métriques de tests dans la documentation

### Où Placer les Références Historiques

- ✅ Sections "Historique" ou "Notes de développement" en fin de document
- ✅ Messages de commit et pull requests
- ✅ Commentaires de code expliquant des décisions techniques
- ✅ Fichiers `docs/claude/memory/` pour la mémoire contextuelle
- ❌ **Jamais** dans la documentation fonctionnelle principale

### Exemple

**❌ Mauvais** :
> "Nouvelle dans l'issue #42 : L'authentification JWT est maintenant disponible. C'est une amélioration majeure par rapport à l'ancienne méthode OAuth."

**✅ Bon** :
> "L'authentification utilise des tokens JWT signés avec RS256. Les tokens ont une durée de vie de 24h et peuvent être renouvelés via le refresh token."

## Apprentissages Techniques

### Différence cruft vs cookiecutter pour les Tests

**Découverte importante** : `cruft create` utilise Git et ne voit que les fichiers commités, tandis que `cookiecutter` lit directement le filesystem.

**Impact** : Pour tester le template avec des modifications non commitées, il faut utiliser :
```bash
cookiecutter /home/guillaume/git/PyFoundry --no-input
```

**Documentation créée** : `docs/dev/testing.md` pour guider les développeurs

### Test avec pytest-cookies vs Test Manuel

Les tests automatisés avec `pytest-cookies` vérifient la structure mais ne testent pas l'expérience utilisateur complète. Le test manuel reste nécessaire pour :
- Vérifier que `mkdocs serve` fonctionne
- Tester l'expérience développeur complète
- Valider le rendu visuel de la documentation

### Skip Conditionnel dans les Tests

Pour le test `test_mkdocs_can_build`, ajout d'un skip conditionnel si les plugins MkDocs ne sont pas installés :

```python
if "is not installed" in build_result.stderr:
    pytest.skip("mkdocs plugins not installed in test environment")
```

Cela permet d'exécuter les tests même si l'environnement n'a pas tous les plugins installés.

## Workflow CI/CD

Configuration `.github/workflows/docs.yml` :
- Déclenché sur push main/master modifiant `docs/` ou `mkdocs.yml`
- Utilise `uv sync --extra docs` pour installer les dépendances
- Build avec `mkdocs build --strict` (échoue si erreur)
- Déploiement automatique sur GitHub Pages

## Commandes Clés

```bash
# Installer dépendances documentation
uv sync --extra docs

# Prévisualiser localement
uv run mkdocs serve

# Build production
uv run mkdocs build --strict

# Tester le template (avec modifs non commitées)
cd ~/temp
cookiecutter /home/guillaume/git/PyFoundry --no-input
cd mon-projet-data-science
uv sync --extra dev
uv run mkdocs serve
```

## Points d'Attention pour l'Avenir

1. **Documentation vide par défaut** : Les fichiers `docs/user/README.md` et `docs/dev/README.md` contiennent des instructions mais pas de contenu spécifique. C'est volontaire car le template ne sait pas ce que sera le projet utilisateur.

2. **Bonnes pratiques de rédaction** : Les instructions détaillées dans `docs/user/README.md` et `docs/dev/README.md` doivent être maintenues synchronisées avec celles dans `CLAUDE.md`.

3. **Thème personnalisable** : Le thème Material offre de nombreuses options de personnalisation. Les utilisateurs peuvent modifier `mkdocs.yml` selon leurs besoins.

4. **GitHub Pages** : Nécessite d'activer Pages dans les settings du repo GitHub. La workflow échouera silencieusement si Pages n'est pas activé.

## Références

- Issue #14 : https://github.com/castorfou/PyFoundry/issues/14
- Inspiration : Projet back-office-lmelp de l'utilisateur pour les bonnes pratiques de documentation
- MkDocs Material : https://squidfunk.github.io/mkdocs-material/
