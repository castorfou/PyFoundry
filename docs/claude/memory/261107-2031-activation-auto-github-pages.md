# Issue #116 — activation automatique de GitHub Pages sur les projets générés

## Résumé

Sur un projet généré, GitHub Pages restait désactivé tant que personne ne lançait l'étape manuelle « Activer GitHub Pages (une fois par projet) ». À chaque push sur `main` touchant la doc, `📚 Deploy Documentation` échouait à `📋 Setup Pages` (`Get Pages site failed … HttpError: Not Found`). La PR ne le montrait pas : `Setup Pages` ne tourne que sur `main` ou en lancement manuel. Cas réel : `castorfou/transcripteur`, PyFoundry 1.1.1.

Correction : un script idempotent, `.devcontainer/scripts/enable_pages.sh`, lancé à chaque terminal zsh juste après `gh_login.sh`. Il active Pages avec le compte `gh` de l'utilisateur. Le script est identique dans le dépôt et le squelette (R1.5).

Branche `116-activer-github-pages-automatiquement-sur-les-projets-générés`. Spécifications : [commentaire de l'issue #116](https://github.com/castorfou/PyFoundry/issues/116#issuecomment-6711431017).

---

## Décisions

- **Ni `docs.yml` ni `postCreateCommand`.** `actions/configure-pages` avec `enablement: true` demande un jeton admin (#85), et `postCreateCommand` tourne avant l'authentification `gh` (proposée au premier terminal, #64). Le terminal zsh, juste après `gh_login.sh`, est le premier endroit où `gh` est authentifié.
- **Dépôt public seulement** (choix de l'utilisateur). Sur un dépôt `private` ou `internal`, le script affiche un message d'une ligne qui renvoie à la cheatsheet, puis s'arrête. Activer Pages pourrait publier la doc d'un dépôt privé.
- **Jamais de `PUT`.** Si la source est « Deploy from a branch » (`build_type` = `legacy`), le script affiche une ligne vers la cheatsheet sans rien modifier, car ce réglage peut être voulu.
- **La règle de branche de l'environnement `github-pages` (#63) reste manuelle** (choix de l'utilisateur). Déployer depuis une branche est une option, et l'environnement n'existe qu'après le premier déploiement.
- **`owner/repo` vient de `git remote get-url origin`** (HTTPS, `git@`, `ssh://`, avec ou sans `.git`), et non du joker `{owner}/{repo}` de `gh`. Ce joker peut exiger un `gh repo set-default` quand il y a plusieurs remotes.
- **Marqueur dans `.git/`** (`git rev-parse --git-path pyfoundry-pages`), qui contient `owner/repo`. Il n'est jamais commité et survit au rebuild du conteneur. Si `origin` change, le script refait la vérification. Le marqueur n'est écrit que dans un état final : `workflow`, activation réussie, `legacy`, dépôt non public, pas admin. Il n'est pas écrit quand le dépôt est introuvable (pas encore créé sur GitHub), en cas d'erreur réseau ou de timeout, ou si le `POST` échoue : le script réessaie au terminal suivant. La variable `PAGES_MARKER` remplace son chemin pour les tests.
- **Coût à l'ouverture d'un terminal** : les vérifications hors réseau passent d'abord (`gh` absent, `gh auth token`, `origin`, marqueur). Ensuite, deux appels au plus, chacun sous `timeout 5` : `gh api repos/O/R --jq '.visibility, .permissions.admin, .has_pages'`, puis le `POST` si `has_pages` est faux, ou `GET …/pages --jq .build_type` s'il est vrai. Mesures réelles : environ 1 s au premier passage, 60 ms une fois le marqueur posé.
- **Jamais d'échec du shell** : sortie toujours en `0`, rien sur stderr, au plus une ligne sur stdout.
- **Pas de syntaxe Jinja dans le script** (`{{`, `{%`, `{#`, y compris `${#var}`), puisqu'il est rendu dans le squelette sans figurer dans `_copy_without_render`.

---

## Fichiers modifiés

- `.devcontainer/scripts/enable_pages.sh` et `{{ cookiecutter.project_slug }}/.devcontainer/scripts/enable_pages.sh` (identiques, exécutables)
- `.devcontainer/postCreateCommand.sh` et `{{ cookiecutter.project_slug }}/.devcontainer/postCreateCommand.sh` : `config_zsh` ajoute `ensure_zshrc_line 'bash "$WORKSPACE_FOLDER/.devcontainer/scripts/enable_pages.sh"'` après le hook `gh_login.sh`
- `tests/test_enable_pages.py`
- Documentation (usage, cheatsheets, troubleshooting, `CLAUDE.md`, `CHANGELOG.md`) : décrit l'activation automatique et garde les commandes manuelles en repli

---

## Tests (`tests/test_enable_pages.py`)

- Faux `gh` (cf. `FAKE_GH` de `tests/test_github_auth.py`) qui journalise ses appels et répond selon `FAKE_GH_TOKEN`, `FAKE_REPO` (lignes visibility/admin/has_pages, ou `fail`), `FAKE_BUILD_TYPE` et `FAKE_POST`.
- Un dépôt git temporaire avec un `origin` réglable ; `WORKSPACE_FOLDER` est toujours fixé, car le vrai environnement du devcontainer en définit un.
- `run_script` vérifie dans chaque cas : code `0`, stderr vide, au plus une ligne sur stdout.
- Cas : activation, `workflow` silencieux, `legacy` sans `-X`, `private`/`internal`, pas admin, dépôt introuvable puis nouvel essai, `POST` en échec, marqueur (même dépôt → aucun appel, autre `origin` → nouvelle vérification, emplacement par défaut dans `.git/`), terminal ouvert hors du projet, 4 formes d'URL, silence sans authentification, sans `origin`, avec un `origin` hors GitHub, hors dépôt git, sans `gh`.
- Script identique entre dépôt et squelette, hook placé après `gh_login.sh` (paramétré `repo`, `default`, `docker_in_docker`), mention de `enable_pages.sh` dans la doc.
- Piège ruff : `PLW1510` demande `check=` explicite sur chaque `subprocess.run`.

---

## Validation utilisateur

Projet généré avec `cruft create … --checkout <branche>`. Premier terminal avant la création du dépôt : silencieux, pas de marqueur. Après `gh repo create --public` et un push, un nouveau terminal affiche `✅ GitHub Pages activé…` et `build_type` vaut `workflow`. Le terminal suivant est silencieux, et `docs.yml` passe `Setup Pages`.

Les avertissements vus dans le run (Node.js 20 obsolète pour les actions en `@v4`, panne du cache GitHub, `ubuntu-latest` → Ubuntu 26) ne viennent pas de ce changement.

---

## Projets existants

Le script et le hook arrivent avec `cruft update`, mais `.zshrc` n'est réécrit qu'au rebuild du conteneur (`postCreateCommand`). Il faut donc un rebuild après la mise à jour. Pas de migration manuelle.
