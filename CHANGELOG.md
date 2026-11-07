# Changelog

Toutes les évolutions notables de PyFoundry sont listées ici. Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et les versions suivent [SemVer](https://semver.org/lang/fr/), avec les règles propres à un template décrites dans le [processus de release](https://castorfou.github.io/PyFoundry/dev/release/).

## [Non publié]

### Ajouté

- Le devcontainer active GitHub Pages tout seul, avec la source **GitHub Actions**. À chaque ouverture d'un terminal, après l'authentification `gh`, `.devcontainer/scripts/enable_pages.sh` active Pages sur le dépôt `origin` s'il est public et que vous en êtes admin. Sans Pages, `📚 Deploy Documentation` échouait à `Setup Pages` (`Get Pages site failed`) à chaque push sur `main`. Le script ne modifie jamais une source « Deploy from a branch » et n'active rien sur un dépôt privé : il affiche alors une ligne qui renvoie aux commandes manuelles. Il réessaie tant que le dépôt GitHub n'existe pas, puis ne fait plus d'appel réseau une fois le dépôt réglé. Sur un projet existant, il s'applique au rebuild qui suit `cruft update`, y compris si Pages n'a jamais été activé (#116).

### Modifié

- Les workflows des projets générés (`ci.yml`, `docs.yml`) utilisent des actions qui tournent sous Node 24 : `actions/checkout@v7`, `astral-sh/setup-uv@v10.3.3`, `actions/configure-pages@v6`, `actions/upload-pages-artifact@v5`, `actions/deploy-pages@v5`, `actions/upload-artifact@v7` et `codecov/codecov-action@v7`. Les runs n'affichent plus l'avertissement `Node.js 20 is deprecated`, et ne casseront pas au retrait de Node 20 des runners GitHub. `setup-uv` utilise ses réglages de cache par défaut, qui suivent `uv.lock` en plus de `pyproject.toml`. Le dépôt du template a maintenant Dependabot pour ses actions ; les projets générés reçoivent les nouvelles versions par `cruft update` (#120).
- Le hook pre-commit mypy tourne dans le venv du projet (`uv run --active mypy`) au lieu de l'environnement isolé de `mirrors-mypy`. Il voit les dépendances de `uv.lock` : une dépendance typée ajoutée au projet ne fait plus échouer le hook alors que `uv run mypy` passe. Le hook, la CI et `mypy` lancé à la main vérifient le même périmètre, `src/` et `tests/` (`[tool.mypy] files`) ; avant, le hook et la CI ne vérifiaient que `src/`, et `mypy` que `tests/`. Les stubs `pandas-stubs`, `types-requests` et `types-python-dateutil` passent dans les extras `dev`. Un projet neuf contient `src/<package>/__init__.py` et `tests/test_<package>.py`, pour que mypy ait des fichiers à vérifier. Sur un projet existant, `mypy` vérifie désormais aussi `tests/` et peut y trouver des erreurs. Si vous aviez ajouté des `additional_dependencies` au hook, reportez-les dans les extras `dev` de `pyproject.toml` en résolvant le rejet de `cruft update`, puis lancez `uv lock` (#112).

### Corrigé

- Une dépendance publiée sans wheel, comme `scikit-surprise`, compile de nouveau dans le devcontainer. Le venv est créé avec un Python géré par uv (`--managed-python`) au lieu du Python Debian de l'image, qui n'a pas `Python.h`. Le premier build télécharge ce Python, conservé ensuite dans le HOME persistant (#113).
- Avec `docker_in_docker=y`, `dockerd` démarre de nouveau sur un noyau hôte sans module `ip_tables` (erreur `can't initialize iptables table 'nat'`). La feature passe de `docker-in-docker:2`, figée à 2.17.0, à `docker-in-docker:4`, qui choisit iptables `nft` ou `legacy` au démarrage. Le socket Docker de l'hôte n'est plus monté sur `/var/run/docker-host.sock` : la feature ne s'en servait pas, et il donnait un accès root au Docker de l'hôte. Le daemon tourne dans le conteneur. La correction s'applique au rebuild qui suit `cruft update` ; si le projet a un `.devcontainer/devcontainer-lock.json`, régénérez-le d'abord (`npx @devcontainers/cli upgrade --workspace-folder .`). Voir le [dépannage](https://castorfou.github.io/PyFoundry/user/troubleshooting/) (#117).

## [1.1.1] - 2026-10-25

### Ajouté

- Script `scripts/clean_test_project.sh <dossier>` pour les contributeurs du template : il supprime le devcontainer d'un projet de test (retrouvé par le label `devcontainer.local_folder`), puis son dossier et son HOME persistant. Supprimer le dossier seul laissait le conteneur tourner (#92).
- La CI des projets générés vérifie que `uv.lock` est à jour avec `pyproject.toml` (`uv lock --check`). Une simple différence de format, due à une version d'`uv` plus récente, ne la fait pas échouer. Si cette étape échoue après `cruft update`, lancez `uv lock` et commitez `uv.lock` (#87).

### Corrigé

- Fermer la fenêtre VS Code arrête maintenant le devcontainer (`"shutdownAction": "stopContainer"`). Avec `none`, un conteneur ouvert une fois tournait jusqu'au prochain `docker stop` et pouvait occuper un cœur à 100 %. Sur un projet existant, le réglage s'applique au rebuild qui suit `cruft update` (#92).
- Les commits d'un projet généré ne sont plus signés `Default User` à la place de l'identité git de l'utilisateur. Sans identité au premier build, le commit initial est fait sous `<GITHUB_USERNAME>@users.noreply.github.com`, sans rien écrire dans `.git/config`, et un avertissement indique comment configurer la sienne. Sur les projets existants, le rebuild qui suit `cruft update` retire l'ancienne identité de `.git/config` (#94).
- Le cheatsheet Docker utilise un registre public (`ghcr.io`) au lieu d'un registre interne (#94).
- Un projet tout juste créé n'a plus rien à commiter. Sans identité git au premier build, la mise à jour des hooks pre-commit est commitée sous la même identité de repli que le commit initial (`<GITHUB_USERNAME>@users.noreply.github.com`), au lieu de rester modifiée. `repo_url` est écrit dans `mkdocs.yml` à la génération ; le script `update_mkdocs_repo_url.sh`, qui le modifiait sans le commiter, est supprimé. Si le dépôt change d'adresse, corrigez `repo_url` à la main (#102).
- La doc explique qu'il faut régler la source GitHub Pages sur **GitHub Actions** (et non « Deploy from a branch », proposé par défaut), une fois par projet, dans l'interface ou avec `gh api`. Sans ce réglage, GitHub lance à chaque push un run `pages build and deployment` qui échoue dans « Build with Jekyll ». Le guide d'utilisation, le dépannage et l'aide-mémoire MkDocs des projets générés décrivent la procédure (#85).
- La création et le démarrage du devcontainer ne modifient plus `uv.lock`. Le venv est installé depuis le lock tel quel (`uv sync --frozen`) : ni une version d'`uv` plus récente ni un `pyproject.toml` modifié sans `uv lock` ne réécrivent le fichier. Dans ce second cas, un avertissement indique de lancer `uv lock` (#87).

## [1.1.0] - 2026-10-25

### Ajouté

- Skill Claude Code `/cruft-update` dans les projets générés : elle lance `cruft update`, résume les nouveautés et les migrations du CHANGELOG, résout les rejets (`.rej`, marqueurs de conflit) selon le propriétaire de chaque fichier, vérifie le résultat et commite. Elle se déclenche aussi sur « mets à jour le projet depuis le template » (#89).
- Règle de propriété des fichiers lors d'une mise à jour du template : fichiers du template, du projet ou mixtes (ADR 0003, #89).
- Fichier `TEMPLATE_VERSION` à la racine des projets générés : la version PyFoundry du projet, mise à jour par `cruft update` (#90).

### Modifié

- Les releases de PyFoundry sont publiées automatiquement au merge d'une PR de release (hausse de version dans `pyproject.toml`), avec le tag et les notes du CHANGELOG. La CI des pull requests refuse une PR de release incohérente. Les autres merges ne publient rien (ADR 0004, #90).

### Corrigé

- Le venv `/tmp/venv` est recréé au démarrage du conteneur s'il manque. Avec Docker-in-Docker, `/tmp` était vidé à chaque redémarrage, ce qui supprimait le venv (`no such file or directory: /tmp/venv/bin/activate`). Le `.zshrc` n'active plus le venv s'il n'existe pas (#86).
- Le guide utilisateur décrit les workflows réellement fournis au projet généré (`ci.yml`, `docs.yml`), et non ceux du dépôt PyFoundry (#90).

## [1.0.0] - 2026-10-12

Première release depuis la 0.5.0. Elle impose une migration manuelle aux projets existants (HOME persistant), d'où la version majeure.

### Migration

- **HOME persistant** : avant le premier rebuild qui suit `cruft update`, sauvegardez le HOME de l'ancien conteneur, sinon l'historique Claude Code, la connexion `gh` et l'historique du shell sont perdus. Voir [Passer au HOME persistant](https://castorfou.github.io/PyFoundry/user/usage/#passer-au-home-persistant).
- **Config Claude Code partagée** : l'historique est copié automatiquement au premier démarrage. Voir [Passer à la config Claude Code partagée](https://castorfou.github.io/PyFoundry/user/usage/#passer-a-la-config-claude-code-partagee).
- **Variable `setup_git` supprimée** : Git est toujours configuré. Elle peut rester dans `.cruft.json`, elle est ignorée.

### Ajouté

- Version du template enregistrée dans `.cruft.json` des projets générés (`_pyfoundry_version`), `CHANGELOG.md` et processus de release documenté (#62).
- HOME du conteneur persistant sur l'hôte, venv dans `/tmp/venv`, caches uv et pre-commit partagés entre projets (#59).
- Config Claude Code partagée entre devcontainers, avec copie automatique de l'historique existant (#73).
- Authentification `gh` proposée au premier terminal, partagée entre devcontainers (#64).
- `check_mounts.sh` signale les sources de montage manquantes, les permissions de `~/.ssh` et les points de montage imbriqués appartenant à root (#59, #75).
- Skills Matt Pocock pré-configurés pour Claude Code (#58).
- Intégration de Claude Code : `CLAUDE.md`, commandes `/fix-issue` et `/stocke-memoire` (#16).
- Documentation MkDocs du projet généré, avec docs utilisateur, développeur et cheatsheets (#18).
- Publication de la doc d'une branche sur GitHub Pages par lancement manuel de `docs.yml` (#63).
- Option `docker_in_docker`.
- Option `use_node` pour installer Node.js (#7).
- Fuseau horaire de l'hôte dans le devcontainer (#9, #65).
- Cache uv monté dans le devcontainer (#51) et noyau Jupyter validé (#50).
- zsh par défaut avec le thème Powerlevel10k.
- Hook pre-commit qui refuse un `.venv` à la racine du projet (#70).

### Modifié

- Branche principale renommée de `master` en `main` (#21).
- `~/.gitconfig` n'est plus monté : VS Code copie celui de l'hôte.
- Un rebuild ne commite plus que `.pre-commit-config.yaml`, jamais le travail en cours (#68).

### Corrigé

- Fichiers générés conformes aux hooks pre-commit (`trailing-whitespace`, `end-of-file-fixer`, `check-json`) (#68).
- Extension VS Code `ms-python.isort` retirée, redondante avec ruff (#70).
- Le fuseau de l'hôte n'écrase plus `/etc/localtime` (#65).
- Points de montage imbriqués créés avec le bon propriétaire dans le HOME (#75).
- `check_mounts.sh` lit le JSONC complet : commentaires en fin de ligne, virgules finales (#80).
- Compatibilité avec un hôte Ubuntu 25.10 (#12).

## [0.5.0] - 2025-08-24

### Ajouté

- Workflows GitHub Actions : tests du template, déploiement de la doc sur GitHub Pages, release automatique depuis un tag `v*.*.*`.
- Workflow CI et badges pour les projets générés.

## [0.4.0] - 2025-08-24

### Ajouté

- Tests automatisés du template avec pytest-cookies.
- CI GitHub Actions sur Python 3.11 et 3.12.
- Guide des tests dans la documentation développeur.

## [0.3.0] - 2025-08-24

### Ajouté

- Qualité de code automatisée : ruff et mypy configurés pour la Data Science, hooks pre-commit.
- Authentification GitHub et configuration Git dans le devcontainer.

## [0.2.0] - 2025-08-23

### Ajouté

- Environnement reproductible : fichiers de lock uv, `.env.template`, devcontainer optimisé, configuration Jupyter.

[Non publié]: https://github.com/castorfou/PyFoundry/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/castorfou/PyFoundry/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/castorfou/PyFoundry/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/castorfou/PyFoundry/compare/v0.5.0...v1.0.0
[0.5.0]: https://github.com/castorfou/PyFoundry/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/castorfou/PyFoundry/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/castorfou/PyFoundry/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/castorfou/PyFoundry/releases/tag/v0.2.0
