# Changelog

Toutes les évolutions notables de PyFoundry sont listées ici. Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et les versions suivent [SemVer](https://semver.org/lang/fr/), avec les règles propres à un template décrites dans le [processus de release](https://castorfou.github.io/PyFoundry/dev/release/).

## [Non publié]

### Corrigé

- Le venv `/tmp/venv` est recréé au démarrage du conteneur s'il manque. Avec Docker-in-Docker, `/tmp` était vidé à chaque redémarrage, ce qui supprimait le venv (`no such file or directory: /tmp/venv/bin/activate`). Le `.zshrc` n'active plus le venv s'il n'existe pas (#86).

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

[Non publié]: https://github.com/castorfou/PyFoundry/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/castorfou/PyFoundry/compare/v0.5.0...v1.0.0
[0.5.0]: https://github.com/castorfou/PyFoundry/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/castorfou/PyFoundry/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/castorfou/PyFoundry/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/castorfou/PyFoundry/releases/tag/v0.2.0
