# Issue #64 — authentification GitHub (gh) au build du devcontainer

## Résumé

Point de départ : `setup_github` lançait `gh auth login --web` pendant le `postCreateCommand`. Le build attendait l'utilisateur, le navigateur ne s'ouvrait pas (`xdg-open … not found`), le code ne pouvait pas être copié (`No clipboard utilities available`), et il fallait se réauthentifier pour chaque nouveau projet. Correction sur la branche `64-ameliorer-le-setup-git-au-build-du-devcontainer`, appliquée au dépôt et au squelette :

1. **Plus de login dans `postCreateCommand`.** Le login est proposé au premier terminal zsh par le nouveau script `.devcontainer/scripts/gh_login.sh`, appelé depuis `~/.zshrc`.
2. **La config gh est partagée entre devcontainers** : `~/.config/gh-devcontainers` (hôte) est monté sur `/home/vscode/.config/gh`, sur le modèle du cache pre-commit.
3. **Le credential helper Git est configuré systématiquement**, par la nouvelle fonction `setup_gh_credential_helper`.

---

## Diagnostic

- **Le navigateur.** Les terminaux intégrés VS Code reçoivent `BROWSER=…/bin/helpers/browser.sh`, qui ouvre l'URL dans le navigateur de l'**hôte**, et `gh` respecte `$BROWSER`. Les commandes de cycle de vie (`postCreateCommand`, et aussi `postStartCommand`) tournent hors de ces terminaux : sans `$BROWSER`, `gh` cherche `xdg-open` et échoue. Déplacer le login dans `postStartCommand` ne règle donc rien.
- **Le presse-papiers.** Installer `xclip`, `xsel` ou `wl-clipboard`, comme le suggérait le commentaire de l'issue, ne sert à rien : le conteneur n'a pas d'affichage X ou Wayland. Le code reste à coller à la main.
- **#61** (montage readonly de `~/.gitconfig`) était déjà résolu dans le code : le montage avait été retiré par le commit `722f486`.

---

## Solution

### `.devcontainer/scripts/gh_login.sh` (même contenu dans le dépôt et le squelette, exécutable)

- Si `gh` est absent, le script sort silencieusement.
- S'il est déjà authentifié, il sort aussi silencieusement. Le test passe par **`gh auth token`**, qui lit `hosts.yml` sans réseau. `gh auth status` interroge l'API, ce qui coûterait un appel réseau à chaque ouverture de terminal.
- Marqueur `${GH_LOGIN_MARKER:-/tmp/.gh-login-attempted}` : le login est tenté **une seule fois par conteneur**. Ensuite, le script affiche une ligne d'aide (`gh auth login --web`).
- Commande lancée : `gh auth login --hostname github.com --git-protocol https --web --skip-ssh-key`.
- Le script termine toujours par `exit 0` : un échec ou un Ctrl-C ne casse jamais le shell.
- Hook : `ensure_zshrc_line 'bash "$WORKSPACE_FOLDER/.devcontainer/scripts/gh_login.sh"'` dans `config_zsh`. `.zshrc` n'est lu que par les shells interactifs, ce qui exclut l'outil Bash de Claude Code et les tâches.

### `postCreateCommand.sh` (dépôt et squelette)

- `setup_gh_credential_helper` (si `gh` existe) écrit en config locale au projet `credential.helper ""` puis `credential.https://github.com.helper "!gh auth git-credential"`. La configuration est faite même sans token, puisque celui-ci peut arriver plus tard ou venir d'un autre devcontainer.
- `setup_github` affiche soit « ✅ Déjà authentifié », soit « 🔐 … ouvrez un terminal ».

### `devcontainer.json` (dépôt et squelette)

- Montage : `source=${localEnv:HOME}/.config/gh-devcontainers,target=/home/vscode/.config/gh,type=bind`.
- `initializeCommand` :
  - `mkdir -p -m 700` sur `~/.config/gh-devcontainers`, car ce dossier contient le token en clair (pas de keyring dans le conteneur) ;
  - `mkdir -p` de `homes/<projet>-<id>/.config`, faute de quoi Docker crée `/home/vscode/.config` en root pour y faire le montage. C'est le même piège que `.cache`.
- `check_mounts.sh` vérifie la nouvelle source sans modification.

---

## Tests

`tests/test_github_auth.py`, paramétré sur `repo`, `default` et `docker_in_docker` :

- montage gh partagé ; `initializeCommand` crée la source en `700` et crée `.config` dans le HOME persistant
- `gh auth login` absent de `postCreateCommand.sh` ; hook présent dans `config_zsh` ; script identique dans le dépôt et le projet
- `setup_gh_credential_helper` exécuté sur un dépôt git temporaire avec un faux `gh`, puis avec un PATH sans `gh`, où rien n'est configuré
- `gh_login.sh` avec un faux `gh` qui journalise ses appels : silencieux si authentifié ; pas d'appel à `auth status` ; login `--web` puis marqueur ; une seule tentative ; échec → code de sortie 0 ; `gh` absent → silencieux

`tests/test_check_mounts.py::test_repo_configuration_passes_once_sources_exist` reprend en dur les `mkdir` de `initializeCommand` : il faut l'ajuster à chaque nouveau dossier.

Piège de lint : le ruff de pre-commit applique `PLW1510` (`subprocess.run` sans `check` explicite). `ruff check tests/` en local ne le signale pas.

---

## Validation utilisateur

Projet généré sur l'hôte (`cookiecutter /home/guillaume/git/PyFoundry --no-input`, puis Rebuild) : le build ne bloque plus, et au second rebuild l'utilisateur est déjà authentifié.

À noter : la commande de test doit tourner **sur l'hôte**. Le conteneur n'a ni `code` ni le chemin hôte du dépôt.

---

## Leçons

- Tout ce qui ouvre un navigateur depuis un devcontainer doit tourner dans un terminal VS Code, qui fournit `$BROWSER`, et non dans une commande de cycle de vie.
- Pour monter une cible sous le HOME persistant (`~/.config/x`, `~/.cache/x`), il faut créer le dossier parent côté hôte, sinon il appartient à root.
