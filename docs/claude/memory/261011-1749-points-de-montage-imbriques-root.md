# Issue #75 — points de montage imbriqués créés en root dans le HOME persistant

## Résumé

Point de départ : sur l'hôte, le HOME persistant d'un projet (`~/.devcontainer/homes/<projet>-<id>`) contenait des dossiers appartenant à root : `.ssh`, `.cache/uv`, `.cache/pre-commit`, `.config/gh`. Il fallait `sudo` pour supprimer le HOME d'un vieux projet.

Cause : ce sont les points de montage des dossiers montés *dans* le HOME. Quand un point de montage manque dans la source du montage parent, Docker le crée lui-même, en root. `initializeCommand` créait `.cache`, `.config` et `.claude`, mais pas `.ssh`, `.cache/uv`, `.cache/pre-commit` ni `.config/gh`.

Correction sur la branche `75-points-de-montage-imbriqués-créés-en-root-dans-le-home-persistant`, appliquée au dépôt et au squelette (R1.5) :

1. **Prévention.** `initializeCommand` crée tous les points de montage imbriqués dans le HOME persistant.
2. **Détection.** `check_mounts.sh --host` signale par un `[WARN]` (non bloquant) les points de montage qui n'appartiennent pas à l'utilisateur, avec la procédure de réparation.

Spécifications validées : [commentaire de l'issue #75](https://github.com/castorfou/PyFoundry/issues/75#issuecomment-6110638419).

---

## Décisions (validées par l'utilisateur)

- **Pas de réparation automatique des HOME existants.** Un seul projet était concerné. Une réparation dans `initializeCommand` (`rmdir` + `mkdir`) aurait détaché le montage d'un conteneur en cours d'exécution : depuis Linux 3.18, un `rmdir` sur un point de montage d'un autre espace de noms réussit et démonte. On a choisi l'alerte de `check_mounts.sh` et une réparation manuelle.
- **`rmdir` suffit, sans `sudo`.** Le dossier root est vide sur l'hôte (son contenu vit dans la source montée), et son parent appartient à l'utilisateur : supprimer une entrée demande le droit d'écriture sur le parent, pas sur le dossier lui-même. `rmdir` échoue sans dommage si le dossier n'est pas vide.
- **Message lisible.** Une première version (un `[WARN]` par dossier, chemins absolus répétés) a été jugée incompréhensible par l'utilisateur. Version retenue : un `[WARN]` par source parente, qui liste les dossiers en chemins relatifs et donne 4 étapes dans l'ordre réel des opérations :
  1. fermer VS Code ;
  2. arrêter le conteneur sur l'hôte : `docker stop $(docker ps -q --filter "label=devcontainer.local_folder=$PWD")` ;
  3. `cd "<source>"` puis `rmdir … && mkdir …` ;
  4. rouvrir le projet.
- **Trouver le conteneur depuis l'hôte.** VS Code étiquette chaque devcontainer avec `devcontainer.local_folder` (dossier du projet sur l'hôte). `check_mounts.sh` tourne à la racine du projet (`cd "${localWorkspaceFolder}"`), donc `$PWD` donne la valeur exacte du label. Depuis l'intérieur du conteneur, l'ID se lit dans `/proc/self/mountinfo` (`docker/containers/<id>`).

---

## Solution

### `devcontainer.json` (dépôt et squelette)

Le premier `mkdir -p` d'`initializeCommand` crée `<HOME persistant>/.ssh`, `/.cache/pre-commit`, `/.cache/uv`, `/.config/gh` et `/.claude`. Ces chemins remplacent `.cache` et `.config`, créés implicitement par `mkdir -p`. `.ssh` reste en `mkdir -p` simple : ce point de montage vide est masqué par le montage readonly. Commentaire au-dessus d'`initializeCommand` mis à jour.

### `.devcontainer/scripts/check_mounts.sh` (dépôt et squelette, identiques)

- La boucle des montages remplit deux tableaux indexés `TARGETS` et `RESOLVED_SOURCES`. Pas de tableau associatif (`declare -A`), absent du bash 3.2 de macOS ; les tableaux indexés gardent en plus l'ordre de `devcontainer.json`.
- Section « Points de montage imbriqués » :
  - pour chaque cible, le parent est la cible d'un autre montage la plus longue qui la préfixe (`"${candidate%/}/"*`) ;
  - le point de montage est la source résolue du parent suivie du chemin relatif ;
  - s'il existe et que son uid diffère de `OWNER_UID`, il est regroupé par source parente dans `FOREIGN[parent_index]`, sinon `[OK]`.
- `owner_of` : `stat -c '%u %U'`, repli `stat -f '%u %Su'` (BSD/macOS).
- `OWNER_UID="${CHECK_MOUNTS_UID:-$(id -u)}"` : `CHECK_MOUNTS_UID` sert de point d'injection pour les tests, car on ne peut pas créer de dossier root sans `sudo` en CI.
- `log_warn` incrémente `WARNINGS` sans toucher à `ERRORS` : code retour 0, résumé « Tous les montages sont valides, N avertissement(s). »

---

## Tests

- `tests/devcontainer_utils.py` : nouveau helper `nested_mountpoints(config)` → `{cible: source du parent + chemin relatif}`.
- `tests/test_persistent_home.py` : `test_initialize_command_creates_nested_mountpoints`, test **générique** dérivé des `mounts` (dépôt, projet par défaut, docker_in_docker). Tout futur montage dans le HOME est couvert sans retoucher le test. Il remplace :
  - `test_initialize_command_creates_claude_mountpoint_in_persistent_home` (`tests/test_claude_auth.py`) ;
  - `test_initialize_command_creates_config_dir_in_persistent_home` (`tests/test_github_auth.py`) ;
  - l'assertion sur `<HOME persistant>/.cache` de `test_initialize_command_creates_mount_sources_then_checks_them`.
- `tests/test_check_mounts.py` :
  - point de montage d'un autre propriétaire (`CHECK_MOUNTS_UID = uid + 1`) → un seul `[WARN]`, avec `cd "<HOME>"`, `rmdir .cache/uv && mkdir .cache/uv` et la ligne `docker stop … label=devcontainer.local_folder=<workspace>` ;
  - point de montage à l'utilisateur, ou absent → pas de `[WARN]` ;
  - `test_repo_configuration_passes_once_sources_exist` exécute désormais les **vrais** `mkdir` d'`initializeCommand` (variables substituées), au lieu d'une liste codée en dur, et vérifie l'absence de `[WARN]`.

---

## Points d'attention

- Préexistants sur `main`, sans rapport avec #75 : le hook ruff de pre-commit signale `PLW1510` dans `tests/test_mkdocs_integration.py:164`, et mypy une erreur `no-untyped-def` dans `tests/test_configurations.py:83`.
- Arrêter le conteneur arrête aussi la session Claude Code qui y tourne. Les fichiers non commités restent dans le dossier de travail sur l'hôte.
- Validé par l'utilisateur sur l'hôte : le `[WARN]` est apparu pour l'ancien HOME `PyFoundry-0u3v…`, et la procédure en 4 étapes l'a réparé.
