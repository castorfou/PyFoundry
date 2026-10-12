# Issue #62 — Remettre à plat la gestion des versions et le processus de release

## Résumé

Point de départ : `pyproject.toml` et `CLAUDE.md` annonçaient `0.4.0-dev`, alors que les tags `v0.4.0` et `v0.5.0` existaient depuis le 24/08/2025. 128 commits avaient suivi sans release ni CHANGELOG. `release.yml` tirait ses notes de `git log`, sans lien avec `pyproject.toml`. La doc citait à tort « avant PyFoundry 0.4.0 » pour des changements postérieurs à v0.5.0. Les projets générés ne connaissaient que leur `_commit`.

Travail sur la branche `62-remettre-à-plat-la-gestion-des-versions-et-le-processus-de-release`.

Spécifications validées : [commentaire de l'issue #62](https://github.com/castorfou/PyFoundry/issues/62#issuecomment-6128506297).

Décisions de l'utilisateur, toutes conformes aux recommandations :

- **Source de vérité** : `pyproject.toml`, modifiée à la main dans une PR de release. Des tests et `release.yml` vérifient la cohérence. hatch-vcs a été écarté (PyFoundry n'est pas un package publié, et `cookiecutter.json` ne peut pas lire une version dynamique), ainsi que release-please (historique de commits hétérogène).
- **Première release : 1.0.0**, car le HOME persistant (#59) impose une migration manuelle.
- **CHANGELOG.md tenu à la main** (Keep a Changelog, en français), avec une section « Non publié » complétée dans chaque PR.
- **Releases par lots** : PR `chore(release): vX.Y.Z`, puis tag sur `main` posé par le mainteneur.

Règles SemVer d'un template : **majeure** si un projet existant doit faire une action manuelle en plus de `cruft update`, ou si une variable cookiecutter est supprimée ou renommée ; **mineure** pour une fonctionnalité ou une option applicable par `cruft update` seul ; **patch** pour une correction ou de la doc. Entre deux releases, la version reste celle de la dernière release ; `_commit` donne la position exacte.

---

## Solution

### Version connue des projets générés : `_pyfoundry_version`

Point vérifié dans le code de cruft (`cruft/_commands/utils/generate.py:77`) : `_generate_output` ne réinjecte pas les clés commençant par `_` comme `extra_context`. Une variable privée de `cookiecutter.json` est donc relue dans le **nouveau** template à chaque `cruft update`. À l'inverse, une variable publique garderait la valeur figée dans `.cruft.json`. `"_pyfoundry_version": "1.0.0"` dans `cookiecutter.json` suit donc la version du template dans le `.cruft.json` de chaque projet.

### `.github/scripts/release.py` (stdlib seulement)

- `check-tag vX.Y.Z` : renvoie le code 1, avec un `[ERREUR]` par écart, si le tag ne vaut pas `v` + version de `pyproject.toml`, si `_pyfoundry_version` diffère, ou si `CHANGELOG.md` n'a pas de section `## [X.Y.Z]`.
- `notes vX.Y.Z` (ou `X.Y.Z`) : affiche le corps de la section du CHANGELOG, sans le titre, jusqu'à la section suivante ou aux liens de comparaison (`[x]: https://…`).
- L'option `--root` sert aux tests (copie des fichiers dans `tmp_path`).
- Piège argparse : un argument positionnel du parser principal, déclaré après `add_subparsers`, n'est jamais rempli, car le sous-parser consomme le reste de la ligne. `version` est donc déclaré sur chaque sous-commande.

### `.github/workflows/release.yml`

- Job `validate-tag` : étape `release.py check-tag "$VERSION"` avant les tests.
- Job `create-release` : notes = `release.py notes`, suivies d'un bloc Usage (`cruft create … --checkout`, `cruft update --checkout`). Le `git log` et le bloc « Template Features » codé en dur sont supprimés, ainsi que le `fetch-depth: 0` devenu inutile.

### `CHANGELOG.md`

- Sections `[Non publié]`, `[1.0.0] - 2026-10-12` (Migration / Ajouté / Modifié / Corrigé, reconstruite depuis `git log v0.5.0..HEAD`), et `[0.5.0]`, `[0.4.0]`, `[0.3.0]`, `[0.2.0]` résumées depuis les releases GitHub et le message du tag v0.3.0.
- Liens **absolus** vers la doc publiée (`https://castorfou.github.io/PyFoundry/…`) : le même texte sert sur GitHub, dans MkDocs (inclus par `docs/changelog.md`) et dans les notes de release, où un lien relatif serait cassé.
- La variable `setup_git` a disparu depuis v0.5.0 : c'est signalé dans Migration.

### `/fix-issue` (dépôt et squelette, identiques)

Nouvelle étape 11 : « Met à jour `CHANGELOG.md` s'il existe ». Les étapes passent de 17 à 18, et les boucles sont renumérotées (4 à 7, 3 à 14, 3 à 15). Le « s'il existe » garde le fichier identique entre le dépôt et le projet généré, qui n'a pas de CHANGELOG.

---

## Tests

`tests/test_versioning.py` (21 tests, tous RED avant l'implémentation) :

- version de `pyproject.toml` en SemVer strict, égale à `_pyfoundry_version`, présente dans `result.context` du projet généré ;
- CHANGELOG : commence par `## [Non publié]`, a une section datée pour la version courante, couvre 1.0.0, 0.5.0 et 0.4.0 ;
- `release.py` : `check-tag` (accepte la version, refuse une autre version, un tag sans `v`, un `cookiecutter.json` désaligné, une version absente du CHANGELOG), `notes` (corps exact de la section, préfixe `v` accepté, version inconnue → code 1) ;
- `release.yml` appelle `check-tag` et `notes`, sans `git log` ;
- `fix-issue.md` contient l'étape CHANGELOG et reste identique dans le dépôt et le squelette.

Suite complète : 224 passed, 1 skipped. ruff et pre-commit sont verts ; ruff demande `check=False` explicite sur `subprocess.run` (PLW1510).

---

## Points d'attention

- **Avant chaque release** : modifier la version dans `pyproject.toml` **et** dans `cookiecutter.json`, et renommer « Non publié » en `[X.Y.Z] - date` en recréant une section vide au-dessus. Les tests et `check-tag` bloquent tout oubli.
- Le tag `v1.0.0` se pose **après** le merge, sur le commit de `main`. Si la date de merge diffère, ajuster la date de la section `[1.0.0]`.
- Les pré-releases (`v1.0.0-rc1`) ne passent pas `check-tag` tant que `pyproject.toml` exige du SemVer strict.
- La procédure `cookiecutter` sans cruft ne crée pas de `.cruft.json` : `_pyfoundry_version` n'y est visible qu'avec `cruft create`.
