# Issue #90 — Automatiser les releases et exposer la version du template généré

## Résumé

Point de départ (#62) : une release partait quand le mainteneur poussait à la main un tag `vX.Y.Z` après le merge de la PR de release. Les projets générés ne connaissaient la version du template que par `_pyfoundry_version` dans `.cruft.json`.

Travail sur la branche `90-automatiser-les-releases-et-exposer-la-version-du-template-généré`.

Spécifications validées : [commentaire de l'issue #90](https://github.com/castorfou/PyFoundry/issues/90#issuecomment-6398176924).

Décisions de l'utilisateur :

- **Plus de tag poussé à la main** : un seul déclencheur, le push sur `main`. Le merge de la PR de release publie.
- **La décision de faire une release reste manuelle** (question explicite de l'utilisateur). Seule une PR qui augmente la version de `pyproject.toml` publie, et seule une PR de release le fait. Un merge ordinaire ne publie rien.
- **Erreurs vues dès la PR** : le même contrôle tourne dans la CI des PR vers `main`.

L'utilisateur n'a pas compris la première formulation des questions (« déclenchement sur tag », « contrôle de la PR »). La reformulation en termes concrets (« aujourd'hui tu tapes `git push origin v1.1.0`, demain… ») a fonctionné.

---

## Solution

### `release.py plan --base <ref>` (`.github/scripts/release.py`)

- Version précédente : `git show <ref>:pyproject.toml`. Version courante : l'arbre de travail. Tags : `git tag --list v*`.
- Fonction `plan(root, previous, tags) -> (release, erreurs)` :
  - version identique : `(False, [])`, message « Version inchangée (X.Y.Z) : pas de release », code 0 ;
  - baisse : `baisse de version : A → B` ;
  - hausse : `check_tag` (cookiecutter, section du CHANGELOG) est réutilisé, et s'y ajoutent une section vide, un tag déjà existant (« version déjà publiée ») et une version qui ne dépasse pas la plus haute release taguée.
- Écrit `release=true|false` et `version=X.Y.Z` dans `$GITHUB_OUTPUT` s'il est défini. Chaque erreur donne une ligne `[ERREUR]`, et le code de sortie est 1.
- Comparaison des versions avec des tuples d'entiers (`parse_version`), pas en chaînes (`1.10.0 > 1.9.0`).
- `check-tag` et `notes` sont conservés : `notes` sert toujours à la publication.

### `.github/workflows/release.yml` réécrit

- `on: push: branches: [main]`, `permissions: contents: read` au niveau du workflow, `concurrency: release` sans annulation.
- `plan` : checkout `fetch-depth: 0` pour avoir le commit précédent et les tags, `release.py plan --base "$BASE"` avec `BASE: ${{ github.event.before }}` passé en `env`, jamais interpolé dans `run` (injection).
- `run-tests` : réutilise `test-template.yml` (`workflow_call`), avec `if: needs.plan.outputs.release == 'true'`.
- `publish` : seul job en `contents: write`. Il lance une seule commande, `gh release create "v$VERSION" --target "$GITHUB_SHA" --notes-file …`. GitHub crée le tag et la release ensemble, donc pas de publication partielle. Rien ne dépend d'un workflow déclenché par le tag : un tag créé avec `GITHUB_TOKEN` ne déclenche aucun workflow.
- Supprimés : le déclencheur sur tag, la détection de pré-release (déjà refusée par le SemVer strict), le commentaire de commit (`github-script`) et les permissions `issues` / `pull-requests`.
- Reprise après échec : « Re-run failed jobs » rejoue le même `github.event.before`.

### `.github/workflows/test-template.yml`

- Nouveau job `release-plan`, avec `if: github.event_name == 'pull_request'` et `BASE: origin/${{ github.base_ref }}`. Quand `release.yml` appelle `test-template.yml`, `event_name` vaut `push` (l'événement de l'appelant), donc le job est sauté.

### `TEMPLATE_VERSION`

- `{{ cookiecutter.project_slug }}/TEMPLATE_VERSION` = `{{ cookiecutter._pyfoundry_version }}` + saut de ligne.
- Vérifié dans le code de cruft (`cruft/_commands/update.py`, `utils/generate.py:_generate_output`) : sans `--refresh-private-variables`, les clés `_*` ne sont pas réinjectées comme `extra_context`, donc le nouveau template fournit sa propre valeur. L'option `--refresh-private-variables` sert seulement à forcer une mise à jour quand le commit n'a pas changé. Après `cruft update`, `TEMPLATE_VERSION` passe à la nouvelle version.
- Catégorie `template` dans `CATEGORIES` de `template_update.py` (ADR 0003), recopié à l'identique dans le squelette.
- À la racine de PyFoundry, le fichier arrivera par le `/cruft-update` qui suit le merge, pas à la main.

---

## Tests (`tests/test_versioning.py`)

- `release_repo` : dépôt git temporaire construit depuis `release_root`, tagué à la version courante. `bump(root, version, notes=…, cookiecutter=…)` simule une PR de release.
- `run_release` retire `GITHUB_OUTPUT` de l'environnement hérité : en CI, le script écrirait sinon dans les sorties du vrai job.
- Les workflows sont lus avec PyYAML, qui lit la clé `on` comme le booléen `True` (`workflow.get("on", workflow.get(True))`). Les références `github.*` passant par `env`, on les cherche dans `str(job)`, pas seulement dans `run`.
- `test_template_version_follows_cruft_update` : mini-template git (copie du vrai `TEMPLATE_VERSION`), puis `python -m cruft create`, passage de la version à 1.1.0 et `cruft update --skip-apply-ask`. cruft exige un projet sous git et propre.
- mypy : les helpers YAML renvoient `Any`. L'erreur des stubs `yaml` existait déjà.

## Vérification

- 302 tests passent, ruff est propre, `release.py plan --base origin/main` affiche « Version inchangée (1.0.0) ».
- La vraie publication automatique ne sera vérifiable qu'à la prochaine PR de release.
