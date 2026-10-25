# Versions et releases

Cette page décrit comment PyFoundry numérote ses versions, tient son changelog et publie une release. Les décisions sont documentées dans l'[ADR 0002](../adr/0002-gestion-des-versions.md) (versions) et l'[ADR 0004](../adr/0004-publication-automatique-des-releases.md) (publication automatique).

## Source de vérité

La version est celle de `pyproject.toml` (`[project].version`). Elle est recopiée à deux endroits, et des contrôles bloquent tout écart :

| Emplacement | Rôle | Contrôle |
|---|---|---|
| `cookiecutter.json` → `_pyfoundry_version` | Inscrit la version du template dans le `.cruft.json` et le fichier `TEMPLATE_VERSION` de chaque projet généré | `tests/test_versioning.py`, `release.py plan` |
| `CHANGELOG.md` → `## [X.Y.Z] - AAAA-MM-JJ` | Notes de la release | `tests/test_versioning.py`, `release.py plan` |
| Tag Git `vX.Y.Z` | Créé par `release.yml` avec la release | `release.py plan` (le tag ne doit pas exister) |

`_pyfoundry_version` est une variable privée (préfixe `_`). cruft ne la réinjecte pas depuis l'ancien `.cruft.json` : il la relit dans le nouveau template à chaque `cruft update`, et `TEMPLATE_VERSION` suit. Une variable publique resterait figée à sa valeur de création.

Entre deux releases, la version reste celle de la dernière release. Un projet généré depuis `main` entre deux releases porte donc cette version, et son `_commit` donne la position exacte.

## Règles de numérotation

PyFoundry suit [SemVer](https://semver.org/lang/fr/). Pour un template, le « contrat » est ce que `cruft update` fait seul sur un projet existant :

| Type | Quand | Exemple |
|---|---|---|
| **Majeure** (`X`) | Les projets existants doivent faire une action manuelle en plus de `cruft update`, ou une variable cookiecutter est supprimée ou renommée | HOME persistant (#59) : sauvegarde du HOME avant le rebuild |
| **Mineure** (`Y`) | Nouvelle fonctionnalité ou nouvelle option, appliquée par `cruft update` seul | Option `docker_in_docker` |
| **Patch** (`Z`) | Correction ou documentation, sans nouvelle fonctionnalité | `check_mounts.sh` lit le JSONC complet (#80) |

Les pré-releases (`v1.1.0-rc1`) ne sont pas utilisées : `tests/test_versioning.py` exige une version SemVer stricte dans `pyproject.toml`.

## Tenir le CHANGELOG

`CHANGELOG.md` suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Il est inclus dans la doc ([Changelog](../changelog.md)) et sert de notes à la release GitHub.

Dans chaque PR (étape 11 de `/fix-issue`), ajouter les changements visibles pour l'utilisateur dans la section `## [Non publié]`, avec le numéro de l'issue :

```markdown
## [Non publié]

### Ajouté

- Option `use_gpu` pour les images CUDA (#90).

### Corrigé

- `check_mounts.sh` accepte un HOME avec des espaces (#91).
```

Rubriques possibles : `Migration`, `Ajouté`, `Modifié`, `Corrigé`, `Supprimé`. `Migration` décrit les actions manuelles, avec un lien vers la section du guide utilisateur ; sa présence impose une version majeure.

Les liens vers la doc sont **absolus** (`https://castorfou.github.io/PyFoundry/...`) : le même texte est affiché sur GitHub, dans MkDocs et dans la release, où un lien relatif serait cassé.

## Publier une release

Les releases se font par lots, quand le mainteneur le décide. La décision est la PR de release : seul le merge d'une **hausse de version** de `pyproject.toml` publie. Les autres merges sur `main` ne publient rien, et une PR d'issue ne modifie jamais la version.

### 1. PR de release

Depuis `main` à jour :

```bash
git checkout -b release/vX.Y.Z
```

1. Choisir le numéro à partir de la section « Non publié » (présence de `Migration` → majeure, `Ajouté` → mineure, sinon patch).
2. Modifier la version dans `pyproject.toml` et `_pyfoundry_version` dans `cookiecutter.json`, puis lancer `uv lock` : `uv.lock` contient la version du projet, et l'étape `uv lock --check` de la CI échoue s'il n'est pas à jour.
3. Dans `CHANGELOG.md`, renommer `## [Non publié]` en `## [X.Y.Z] - AAAA-MM-JJ` et recréer au-dessus une section `## [Non publié]` vide.
4. En bas du fichier, mettre à jour les liens de comparaison :

    ```markdown
    [Non publié]: https://github.com/castorfou/PyFoundry/compare/vX.Y.Z...HEAD
    [X.Y.Z]: https://github.com/castorfou/PyFoundry/compare/vA.B.C...vX.Y.Z
    ```

5. Vérifier localement (`git fetch --tags` d'abord : sans les tags distants, `plan` ne voit pas une version déjà publiée) :

    ```bash
    git fetch origin --tags
    pytest tests/test_versioning.py
    python3 .github/scripts/release.py plan --base origin/main   # « publication de vX.Y.Z »
    python3 .github/scripts/release.py notes vX.Y.Z
    ```

6. Commiter (`chore(release): vX.Y.Z`) et ouvrir la PR. Le job **Release plan** de la CI lance le même contrôle : il échoue, avec ses lignes `[ERREUR]`, si la PR n'est pas publiable.

Exemple : la section « Non publié » contient des rubriques `Ajouté`, sans `Migration`. Depuis la 1.0.0, la release est une mineure, la **1.1.0** :

- `pyproject.toml` : `version = "1.1.0"` ; `cookiecutter.json` : `"_pyfoundry_version": "1.1.0"` ;
- `CHANGELOG.md` : `## [1.1.0] - 2026-10-26` sous une nouvelle section `## [Non publié]` vide, et en bas :

    ```markdown
    [Non publié]: https://github.com/castorfou/PyFoundry/compare/v1.1.0...HEAD
    [1.1.0]: https://github.com/castorfou/PyFoundry/compare/v1.0.0...v1.1.0
    ```

- `release.py plan --base origin/main` affiche « Hausse de version 1.0.0 → 1.1.0 : publication de v1.1.0 ».

### 2. Merge

Merger la PR. `release.yml` crée le tag `vX.Y.Z` et la release GitHub sur le commit de merge, une fois les tests passés. Aucun tag à poser à la main.

### 3. Vérification

```bash
gh run list --workflow release.yml --limit 1
gh run watch <run-id>
gh release view vX.Y.Z
```

## Ce que fait `release.yml`

Le workflow se déclenche à chaque push sur `main` :

1. **`plan`** : `release.py plan --base <commit précédent>` compare la version de `pyproject.toml` avant et après le push.
    - Version inchangée : « Version inchangée (X.Y.Z) : pas de release ». Les jobs suivants sont sautés.
    - Hausse cohérente : « publication de vX.Y.Z ».
    - Sinon, une ligne `[ERREUR]` par écart, et le workflow échoue sans rien publier : baisse de version, `_pyfoundry_version` différente, section du CHANGELOG absente ou vide, tag `vX.Y.Z` déjà existant, version qui ne dépasse pas la dernière release.
2. **`run-tests`** : appelle `test-template.yml` (lint et tests) sur le commit qui sera tagué.
3. **`publish`** : `release.py notes` extrait la section du CHANGELOG, complétée par les commandes `cruft create --checkout` et `cruft update --checkout`. Puis `gh release create vX.Y.Z --target <commit>` crée le tag et la release **en une seule opération** : jamais de tag sans release, et une release déjà publiée n'est jamais dupliquée.

Seul `publish` a le droit d'écrire dans le dépôt (`contents: write`) ; le reste du workflow est en lecture seule. Deux exécutions ne tournent jamais en même temps (`concurrency: release`). Le workflow ne compte sur aucun déclenchement par le tag : un tag créé avec `GITHUB_TOKEN` ne lance pas d'autre workflow.

### En cas d'échec

- **`plan` en erreur** : rien n'a été publié. Corriger dans une nouvelle PR de release (par exemple, passer à la version suivante si le tag existe déjà).
- **Tests ou `publish` en échec pour une cause passagère** : relancer avec **Re-run failed jobs** sur le run. Le run rejoue le même commit de référence, donc la même décision.
