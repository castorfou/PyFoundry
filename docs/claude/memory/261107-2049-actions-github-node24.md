# Issue #120 — Actions GitHub sous Node 24, Dependabot

## Résumé

Les runs affichaient `Node.js 20 is deprecated … actions/checkout@v4, actions/configure-pages@v4, actions/upload-artifact@v4, astral-sh/setup-uv@v4`. Chaque action passe à sa dernière majeure, dans `.github/workflows/{test-template,release,docs}.yml` et `{{ cookiecutter.project_slug }}/.github/workflows/{ci,docs}.yml` :

| Action | Avant | Après | Première majeure sous Node 24 |
|--------|-------|-------|-------------------------------|
| `actions/checkout` | v4 | v7 | v5 |
| `astral-sh/setup-uv` | v4 | v10.3.3 (tag exact) | v7 |
| `actions/configure-pages` | v4 | v6 | v6 |
| `actions/upload-pages-artifact` | v3 | v5 | v5 (composite, upload-artifact v7) |
| `actions/deploy-pages` | v4 | v5 | v5 |
| `actions/upload-artifact` | v4 | v7 | v6 |
| `codecov/codecov-action` | v4 | v7 | v6 |

Dependabot (`.github/dependabot.yml`, `github-actions` sur `/`, hebdomadaire, un seul groupe, messages `chore(deps): …`) dans le **dépôt seul**.

Spécification : [commentaire de l'issue #120](https://github.com/castorfou/PyFoundry/issues/120#issuecomment-6712176970).

## Points saillants

### `setup-uv` n'a plus de tag flottant depuis v8

Les tags `v1` à `v7` existent ; `@v8`, `@v9`, `@v10` ne résolvent pas. Astral publie seulement des tags immuables (`v10.3.3`), contre les attaques de chaîne d'approvisionnement (tj-actions). Une majeure épinglée ne reçoit donc plus les patchs : c'est le rôle de Dependabot.

Pour vérifier la version de Node d'une majeure : `gh api "repos/<owner>/<repo>/contents/action.yml?ref=<tag>" --jq .content | base64 -d | grep using`. Un `composite` dépend des actions qu'il appelle.

### Cache de `setup-uv` : les valeurs par défaut suffisent

`enable-cache: true` et `cache-dependency-glob: "pyproject.toml"` sont retirés. Par défaut en v10 : `enable-cache: auto` (cache sur les runners GitHub, coupé pour les événements release, push de tag, `pull_request_target`, `workflow_run`, contre l'empoisonnement du cache) et un glob qui inclut `uv.lock` et `pyproject.toml`. Le cache suit maintenant `uv.lock`.

### Autres changements cassants lus, sans effet ici

- `upload-pages-artifact` v4 exclut les fichiers cachés : un site MkDocs n'en a pas besoin.
- `codecov-action` v5 remplace `file` par `files` : les workflows utilisaient déjà `files`.
- `checkout` v6 garde les identifiants dans un fichier séparé ; v7 refuse les PR de fork en `pull_request_target` (non utilisé).
- `upload-artifact` v5 tournait encore sous Node 20 par défaut : le minimum est v6.

### Dependabot dans le dépôt seul

Dans un projet généré, une PR Dependabot modifierait `ci.yml` et `docs.yml`, qui viennent du template : le `cruft update` suivant produirait des rejets. Les projets générés reçoivent donc les versions par `cruft update`. Dependabot ne voit que `.github/workflows/` du dépôt, pas le squelette : sur une PR Dependabot, recopier les versions dans `{{ cookiecutter.project_slug }}/.github/workflows/`. Le test d'alignement fait échouer la CI tant que ce n'est pas fait.

## Tests

`tests/test_github_actions.py` lit les `uses:` des workflows du dépôt et du projet généré (rendu une fois par module avec `cookiecutter`) :

- majeure ≥ `MIN_MAJOR` pour chaque action ; une action absente de `MIN_MAJOR` fait échouer le test (vérifier son `runs.using` avant de l'ajouter) ;
- `setup-uv` sur un tag `vX.Y.Z` (`EXACT_TAG_ONLY`) ;
- le squelette reprend la référence du dépôt pour chaque action commune ; une seule version par action dans le dépôt ;
- `dependabot.yml` présent dans le dépôt, absent du projet généré.

`actions/upload-artifact` n'est utilisée que dans le squelette : Dependabot ne la met pas à jour, seul le test des minimums la surveille.
