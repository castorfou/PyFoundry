# Versions et releases

Cette page décrit comment PyFoundry numérote ses versions, tient son changelog et publie une release. La décision est documentée dans l'[ADR 0002](../adr/0002-gestion-des-versions.md).

## Source de vérité

La version est celle de `pyproject.toml` (`[project].version`). Elle est recopiée à deux endroits, et des contrôles bloquent tout écart :

| Emplacement | Rôle | Contrôle |
|---|---|---|
| `cookiecutter.json` → `_pyfoundry_version` | Inscrit la version du template dans le `.cruft.json` de chaque projet généré | `tests/test_versioning.py`, `release.py check-tag` |
| `CHANGELOG.md` → `## [X.Y.Z] - AAAA-MM-JJ` | Notes de la release | `tests/test_versioning.py`, `release.py check-tag` |
| Tag Git `vX.Y.Z` | Déclenche `release.yml` | `release.py check-tag` |

`_pyfoundry_version` est une variable privée (préfixe `_`). cruft ne la réinjecte pas depuis l'ancien `.cruft.json` : il la relit dans le nouveau template à chaque `cruft update`. Une variable publique resterait figée à sa valeur de création.

Entre deux releases, la version reste celle de la dernière release. Un projet généré depuis `main` entre deux releases porte donc cette version, et son `_commit` donne la position exacte.

## Règles de numérotation

PyFoundry suit [SemVer](https://semver.org/lang/fr/). Pour un template, le « contrat » est ce que `cruft update` fait seul sur un projet existant :

| Type | Quand | Exemple |
|---|---|---|
| **Majeure** (`X`) | Les projets existants doivent faire une action manuelle en plus de `cruft update`, ou une variable cookiecutter est supprimée ou renommée | HOME persistant (#59) : sauvegarde du HOME avant le rebuild |
| **Mineure** (`Y`) | Nouvelle fonctionnalité ou nouvelle option, appliquée par `cruft update` seul | Option `docker_in_docker` |
| **Patch** (`Z`) | Correction ou documentation, sans nouvelle fonctionnalité | `check_mounts.sh` lit le JSONC complet (#80) |

Les pré-releases (`v1.1.0-rc1`) ne sont pas utilisées : `release.py check-tag` les refuse, car `pyproject.toml` contient une version SemVer stricte.

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

Les releases se font par lots, quand le mainteneur le décide.

### 1. PR de release

Depuis `main` à jour :

```bash
git checkout -b release/vX.Y.Z
```

1. Choisir le numéro à partir de la section « Non publié » (présence de `Migration` → majeure, `Ajouté` → mineure, sinon patch).
2. Modifier la version dans `pyproject.toml` et `_pyfoundry_version` dans `cookiecutter.json`.
3. Dans `CHANGELOG.md`, renommer `## [Non publié]` en `## [X.Y.Z] - AAAA-MM-JJ` et recréer au-dessus une section `## [Non publié]` vide.
4. En bas du fichier, mettre à jour les liens de comparaison :

    ```markdown
    [Non publié]: https://github.com/castorfou/PyFoundry/compare/vX.Y.Z...HEAD
    [X.Y.Z]: https://github.com/castorfou/PyFoundry/compare/vA.B.C...vX.Y.Z
    ```

5. Vérifier localement :

    ```bash
    pytest tests/test_versioning.py
    python3 .github/scripts/release.py check-tag vX.Y.Z
    python3 .github/scripts/release.py notes vX.Y.Z
    ```

6. Commiter (`chore(release): vX.Y.Z`), ouvrir la PR et la merger.

### 2. Tag

Sur le commit de release de `main` :

```bash
git checkout main && git pull
git tag -a vX.Y.Z -m "PyFoundry vX.Y.Z"
git push origin vX.Y.Z
```

### 3. Vérification

```bash
gh run list --workflow release.yml --limit 1
gh run watch <run-id>
gh release view vX.Y.Z
```

## Ce que fait `release.yml`

Le workflow se déclenche sur un tag `v*.*.*` :

1. **`validate-tag`** : `python3 .github/scripts/release.py check-tag "$VERSION"` échoue si le tag ne correspond pas à `pyproject.toml`, à `_pyfoundry_version`, ou si le CHANGELOG n'a pas la section de la version. Chaque écart est signalé par une ligne `[ERREUR]`.
2. **`run-tests`** : appelle `test-template.yml` (lint et tests).
3. **`create-release`** : `release.py notes` extrait la section du CHANGELOG, complétée par les commandes `cruft create --checkout` et `cruft update --checkout`, puis la release GitHub est publiée.

Si `validate-tag` échoue, supprimer le tag, corriger dans une PR, puis reposer le tag :

```bash
git push --delete origin vX.Y.Z
git tag -d vX.Y.Z
```
