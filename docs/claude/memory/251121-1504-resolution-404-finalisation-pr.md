# Résolution erreur 404 MkDocs serve et finalisation PR #18

**Date** : 2025-11-21 15:04
**Contexte** : Suite de l'issue #14 - Finalisation de l'intégration MkDocs
**Branche** : `14-ajouter-mkdocs`

## Problème identifié

L'utilisateur rapportait une erreur 404 lors de l'exécution de `mkdocs serve` :

```
INFO    -  [15:04:03] Serving on http://127.0.0.1:8000/test-pyfoundry/
WARNING -  [15:04:05] "GET /PyFoundry/ HTTP/1.1" code 404
```

### Analyse

Le problème venait de la configuration `site_url` dans `mkdocs.yml` :

```yaml
site_url: https://{{ cookiecutter.github_username }}.github.io/{{ cookiecutter.project_slug }}
```

Quand `site_url` inclut un chemin de base (comme `/project-slug/`), MkDocs configure le site pour utiliser ce chemin **même en développement local**. C'est le comportement attendu pour garantir la cohérence entre local et production.

### Solution

**Pas de bug** - comportement normal de MkDocs. L'utilisateur doit accéder à l'URL complète affichée dans les logs :
- ✅ `http://127.0.0.1:8000/test-pyfoundry/`
- ❌ `http://127.0.0.1:8000/`

## Modifications apportées

### 1. Configuration explicite dans mkdocs.yml

```yaml
site_url: https://{{ cookiecutter.github_username }}.github.io/{{ cookiecutter.project_slug }}
use_directory_urls: true  # Ajouté pour clarté
```

### 2. Documentation dans README.md

Ajout d'une section expliquant le comportement :

```markdown
### Générer localement

# La documentation sera accessible à l'URL affichée dans les logs
# Example: http://127.0.0.1:8000/{{ cookiecutter.project_slug }}/

!!! note "URL locale"
    Comme `site_url` est configuré pour GitHub Pages avec un chemin de base,
    MkDocs servira la documentation avec ce même chemin en local.
    Accédez à l'URL complète affichée dans les logs (avec le chemin `/{{ cookiecutter.project_slug }}/`).

    Si vous souhaitez servir sans chemin de base pour le développement local,
    commentez temporairement la ligne `site_url` dans `mkdocs.yml`.
```

## Finalisation Pull Request #18

### Statistiques

- **13 commits** sur la branche `14-ajouter-mkdocs`
- **19 fichiers modifiés** : +1156 lignes
- **16 nouveaux tests** d'intégration MkDocs (tous passent)
- **CI/CD verte** : tous les workflows passent

### Contenu de la PR

**Tests** :
- `tests/test_mkdocs_integration.py` - Tests pytest-cookies complets

**Projet généré** :
- Configuration MkDocs avec Material theme
- Structure docs/user/ et docs/dev/
- Workflow CI/CD GitHub Pages
- Dependencies dans pyproject.toml

**Documentation** :
- Guidelines de rédaction (état actuel vs historique)
- Instructions activation GitHub Pages
- Guide de test manuel (cookiecutter vs cruft)

### Points techniques documentés

1. **URL locale avec site_url** - Explication du chemin de base
2. **Exclusion claude/** - Via `exclude_docs` dans mkdocs.yml
3. **GitHub Pages activation** - Via `gh api` POST command
4. **Philosophy** - Documenter l'état actuel, pas l'évolution

## Apprentissages clés

### Comportement MkDocs avec site_url

Quand `site_url` contient un chemin (ex: `https://user.github.io/project/`), MkDocs :
1. Configure tous les liens relatifs avec ce base path
2. Serve localement avec le même base path pour cohérence
3. Évite les surprises entre dev et prod

**Alternative pour dev local** : Commenter `site_url` temporairement si besoin de servir à la racine.

### Structure de documentation user/dev

La séparation en deux audiences permet :
- **user/** - Documentation fonctionnelle, guides utilisateur
- **dev/** - Architecture, contribution, décisions techniques

Inspirée du projet back-office-lmelp, cette structure aide Claude Code à générer la bonne documentation selon le contexte.

### Test de templates Cookiecutter

Différence critique :
- `cruft create` - Utilise Git, ne voit que les fichiers committés
- `cookiecutter` - Utilise filesystem, voit tous les fichiers

Pour tester des modifications non commitées : **utiliser `cookiecutter .`**

## État final

✅ PR #18 créée et prête : https://github.com/castorfou/PyFoundry/pull/18
✅ Tous les tests passent (35/35)
✅ CI/CD verte
✅ Documentation complète
✅ Guidelines de rédaction établies

## Fichiers modifiés dans cette session

- `{{ cookiecutter.project_slug }}/mkdocs.yml` - Ajout `use_directory_urls: true`
- `{{ cookiecutter.project_slug }}/README.md` - Section documentation avec note URL locale

## Prochaines étapes

En attente de review et merge de la PR #18 par l'utilisateur.
