# Issue #73 — partager la config Claude Code entre devcontainers

## Résumé

Point de départ : la connexion Claude Code (`~/.claude/.credentials.json`, compte dans `~/.claude.json`) vivait dans le HOME persistant propre à chaque projet. Il fallait donc se reconnecter dans chaque nouveau projet, comme pour `gh` avant #64. Correction sur la branche `73-partager-lauthentification-claude-code-entre-devcontainers` (commit `e61bfbd`), appliquée au dépôt et au squelette :

1. **Tout le dossier de config est partagé.** `~/.config/claude-devcontainers` (hôte) est monté sur `/home/vscode/.claude`, et `CLAUDE_CONFIG_DIR=/home/vscode/.claude` y place aussi `.claude.json`.
2. **Les verrous IDE restent propres au projet.** `<HOME persistant>/.claude-ide` est monté sur `/home/vscode/.claude/ide`.
3. **L'historique est migré automatiquement**, une fois par projet, par le nouveau script `.devcontainer/scripts/migrate_claude_history.sh` qu'`initializeCommand` lance sur l'hôte. La connexion n'est pas migrée : on se reconnecte une fois, pour tous les projets.

Spécifications validées : [commentaire de l'issue #73](https://github.com/castorfou/PyFoundry/issues/73#issuecomment-6110227088).

---

## Décisions (validées par l'utilisateur)

- **Partage complet, et non un token seul.** L'alternative, `CLAUDE_CODE_OAUTH_TOKEN` via `claude setup-token`, isolerait les projets, mais le token est à renouveler chaque année, à exporter sur l'hôte, et ne donne qu'une portée d'inférence.
  - Devient commun : la connexion, les réglages utilisateur, les plugins (installés une fois) et `history.jsonl`.
  - Reste séparé de fait, car indexé par chemin (`/workspaces/<projet>`) : les sessions, la mémoire automatique et les réglages par projet. Deux projets portant le même nom de dossier partageraient ces données.
- **Cible `~/.claude`**, et non `~/.config/claude` : les chemins ne changent pas. L'ancien `~/.claude` du HOME est masqué, mais il reste sur l'hôte.
- **Un dossier, pas des fichiers.** `.credentials.json` et `.claude.json` sont réécrits par renommage atomique, ce qui casse un bind mount de fichier (et un lien symbolique).
- **Verrous `ide/` isolés.** Un `.lock` contient `pid`, port et `authToken`. Vu d'un autre conteneur, le PID est invisible et le verrou risque d'être supprimé comme périmé. Ce point n'a pas pu être vérifié dans le binaire du CLI : le classifieur a bloqué la lecture, qu'il a classée comme exploration d'identifiants. Les sessions (`~/.claude/sessions/*.json`), elles, portent un `pidDomain` : elles sont conçues pour être partagées.
- **Historique migré, connexion non migrée.** L'utilisateur voulait retrouver ses conversations.

---

## Vérifié dans l'extension (`anthropic.claude-code-2.1.296`, `extension.js`)

- Dossier de config : `process.env.CLAUDE_CONFIG_DIR || join(homedir(), ".claude")`.
- Config globale : `join(process.env.CLAUDE_CONFIG_DIR || homedir(), ".claude.json")`.
- L'extension crée elle-même `ide/` en mode `0700` (`mode: 448`).
- `containerEnv` est transmis au serveur VS Code, donc à l'extension et aux terminaux.

---

## Solution

### `devcontainer.json` (dépôt et squelette, identiques sur ces lignes)

- `containerEnv` : `"CLAUDE_CONFIG_DIR": "/home/vscode/.claude"`.
- Montages :
  - `source=${localEnv:HOME}/.config/claude-devcontainers,target=/home/vscode/.claude,type=bind` ;
  - `source=<HOME persistant>/.claude-ide,target=/home/vscode/.claude/ide,type=bind`. Docker monte la cible parente en premier.
- `initializeCommand`, qui crée tout avant le montage, faute de quoi Docker le crée en root :
  - `mkdir -p` de `<HOME persistant>/.claude`, le point de montage ;
  - `mkdir -p -m 700` de `~/.config/claude-devcontainers`, de `~/.config/claude-devcontainers/ide` (point de montage imbriqué) et de `<HOME persistant>/.claude-ide` (tokens IDE) ;
  - appel de `DEVCONTAINER_WORKSPACE_FOLDER_BASENAME=… DEVCONTAINER_ID=… bash "${localWorkspaceFolder}/.devcontainer/scripts/migrate_claude_history.sh"`, inséré **avant** le `(cd … check_mounts.sh --host)` final, que `tests/test_persistent_home.py` vérifie par `endswith`.
- Les deux `devcontainer.json` ont été modifiés par un même script Python de remplacements exacts (`assert count == 1`).

### `.devcontainer/scripts/migrate_claude_history.sh` (dépôt et squelette, exécutable)

- Variables : `OLD=$HOME/.devcontainer/homes/<basename>-<id>/.claude`, `SHARED=$HOME/.config/claude-devcontainers`.
- Marqueur `OLD/.migrated-to-claude-devcontainers` : s'il existe, ou si `DEVCONTAINER_ID` est vide, le script sort aussitôt.
- Copie les fichiers absents de `projects/` (sessions, mémoire automatique) et de `file-history/` (checkpoints `/rewind`), puis ajoute `history.jsonl` à la fin de celui du dossier partagé.
- **Pas de `cp -n`** : avec coreutils 9.2 à 9.4 (Ubuntu 24.04 a la 9.4), il sort en erreur dès qu'il saute un fichier existant. La fonction `copy_missing` fait une boucle `find … | while read` qui saute les fichiers existants. Le conteneur a la 9.1, le piège n'y est pas visible.
- Le marqueur n'est posé qu'en cas de succès : un échec est retenté à l'ouverture suivante. Le script finit toujours par `exit 0`.
- Ne copie ni `.credentials.json` ni `.claude.json`.

Rien dans `postCreateCommand.sh` : l'écran de connexion de l'extension suffit, sans équivalent de `gh_login.sh`.

---

## Tests

`tests/test_claude_auth.py`, sur le modèle de `tests/test_github_auth.py` (fixture `devcontainer_dir` sur `repo`, `default` et `docker_in_docker`) :

- configuration : montage partagé, `CLAUDE_CONFIG_DIR`, montage `ide/`, dossiers `700`, point de montage `.claude`, migration lancée avant `check_mounts.sh`, script identique dans le dépôt et le projet ;
- script, exécuté avec un faux `HOME` (`tmp_path`) :
  - copie des sessions, de la mémoire et des checkpoints ;
  - aucun écrasement ;
  - ajout en fin de `history.jsonl` ;
  - une seule exécution (marqueur) ;
  - connexion non copiée ;
  - absence d'ancien historique sans effet ;
  - dossier partagé en lecture seule : sortie 0, et pas de marqueur.

`tests/test_check_mounts.py::test_repo_configuration_passes_once_sources_exist` : ajout de `.config/claude-devcontainers/ide` et de `.claude-ide` à l'hôte simulé.

Validation de bout en bout dans le conteneur : rendu `cookiecutter` dans le scratchpad, puis exécution du vrai `initializeCommand` (variables remplacées) sur un faux HOME de l'hôte contenant un ancien historique. Les dossiers sont créés en `700`, la migration est faite une seule fois et `check_mounts.sh` réussit.

---

## Validation utilisateur

Protocole proposé par l'utilisateur, plus fidèle qu'un rebuild de PyFoundry, qui risquait de perdre « nos conversations » :

1. `cruft create /home/guillaume/git/PyFoundry --checkout main` d'un projet `test-claude-historique`, ouverture, connexion et création d'une conversation ;
2. `cruft update --checkout <branche>`, ce qui exige que le code soit **commité** (un commit local suffit, cruft lit le dépôt de l'hôte) ;
3. rebuild : après la connexion, l'historique apparaît directement ; `CLAUDE_CONFIG_DIR`, `.claude.json` et `.credentials.json` sont dans le dossier partagé, le `.lock` est présent ;
4. 2ᵉ rebuild : pas de nouvelle demande de connexion.

Constat annexe, à l'origine de l'issue [#75](https://github.com/castorfou/PyFoundry/issues/75) : les points de montage imbriqués **antérieurs** (`.ssh`, `.cache/uv`, `.cache/pre-commit`, `.config/gh`) sont créés en root par Docker dans le HOME persistant. Ils sont invisibles dans le conteneur, mais on ne peut les supprimer qu'avec `sudo`. Les nouveaux points de montage Claude sont pré-créés et ne sont pas concernés.

---

## Leçons

- Pour un montage imbriqué, il faut créer côté hôte le **point de montage lui-même**, pas seulement son parent. Cela vaut aussi à l'intérieur d'un autre montage (`claude-devcontainers/ide`).
- Un script lancé sur l'hôte doit rester portable (coreutils 9.x, BSD/macOS) et ne jamais faire échouer `initializeCommand`.
- Pour lire des données masquées par un montage, il faut passer par l'hôte, avant le montage, donc par `initializeCommand`.
