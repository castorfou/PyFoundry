# 0002 — Gestion des versions et des releases

- **Statut** : accepté
- **Date** : 2026-10-12
- **Issue** : [#62](https://github.com/castorfou/PyFoundry/issues/62)

## Contexte

`pyproject.toml` affichait `0.4.0-dev` alors que `v0.4.0` et `v0.5.0` étaient taguées, et 128 commits avaient suivi sans release. `release.yml` tirait ses notes de `git log`, sans lien avec `pyproject.toml`. Faute de changelog, la doc utilisateur ne pouvait pas dire « à partir de la version X » pour une migration. Les projets générés ne connaissaient que le commit du template (`_commit` dans `.cruft.json`).

## Décision

1. **`pyproject.toml` est la source de vérité**. La version y est modifiée à la main, dans une PR de release. Version dérivée du tag (hatch-vcs, setuptools-scm) écartée : PyFoundry n'est pas un package publié, et `cookiecutter.json` ne peut pas lire une version dynamique.
2. **`_pyfoundry_version` dans `cookiecutter.json`** recopie la version. cruft relit les variables privées dans le nouveau template à chaque `cruft update` : le `.cruft.json` d'un projet porte ainsi la version du template dont il vient.
3. **SemVer adapté au template** : majeure si les projets existants doivent agir à la main en plus de `cruft update`, ou si une variable cookiecutter disparaît ; mineure pour une fonctionnalité ou une option ; patch pour une correction.
4. **`CHANGELOG.md` tenu à la main** (Keep a Changelog), section « Non publié » complétée dans chaque PR. Génération depuis les commits écartée : l'historique est hétérogène, et les notes de migration doivent être rédigées pour un humain.
5. **Releases par lots** : PR de release, puis tag posé par le mainteneur. Outil d'automatisation (release-please, commitizen) écarté pour l'instant.
6. **Contrôles** : `tests/test_versioning.py` vérifie la cohérence à chaque CI ; `.github/scripts/release.py check-tag` refuse un tag incohérent dans `release.yml`, et `release.py notes` y fournit les notes depuis le CHANGELOG.

La première release de ce processus est la **1.0.0**, majeure en raison de la migration imposée par le HOME persistant ([ADR 0001](0001-persist-development-home.md)).

## Conséquences

- La doc utilisateur peut renvoyer à une version précise (« projets générés avant PyFoundry 1.0.0 »).
- Chaque PR doit compléter le CHANGELOG : c'est une étape de `/fix-issue`.
- Une release demande trois modifications cohérentes (`pyproject.toml`, `cookiecutter.json`, `CHANGELOG.md`). Un oubli fait échouer les tests ou `check-tag`, jamais une release incohérente.
- Pas de pré-releases tant que `pyproject.toml` exige du SemVer strict.
- Le processus est décrit dans [Versions et releases](../dev/release.md).
