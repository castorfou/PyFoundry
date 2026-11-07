# Issue #117 — docker-in-docker:4, plus de montage du socket Docker de l'hôte

## Résumé

Dans un projet généré avec `docker_in_docker=y`, `dockerd` ne démarrait pas sur un noyau hôte récent (Ubuntu `7.0.0-43-generic`) sans module `ip_tables` :

```
iptables v1.8.9 (legacy): can't initialize iptables table `nat': Table does not exist
```

Correction dans `{{ cookiecutter.project_slug }}/.devcontainer/devcontainer.json` :

- `ghcr.io/devcontainers/features/docker-in-docker:2` devient `:4`, `"moby": false` conservé, `iptablesSwitchAtRuntime` non précisé (vrai par défaut) ;
- montage `source=/var/run/docker.sock,target=/var/run/docker-host.sock` supprimé ;
- écho final de `postCreateCommand.sh` : « daemon Docker propre au conteneur » au lieu du « proxy socat ».

Spécification : [commentaire de l'issue #117](https://github.com/castorfou/PyFoundry/issues/117#issuecomment-6710154987). Remonté depuis [castorfou/docker-lmelp#83](https://github.com/castorfou/docker-lmelp/issues/83).

## Points saillants

### Le tag `:2` est figé pour toujours

`:2` résout 2.17.0, la dernière 2.x. Les correctifs amont arrivent en 3.x puis 4.x. Régénérer `devcontainer-lock.json` ne change rien : il faut changer de majeure.

| Tag | iptables |
|-----|----------|
| `:2` (2.17.0) | choisi **au build** |
| `:3` (3.1.0) | `iptablesSwitchAtRuntime`, faux par défaut |
| `:4` (4.1.3) | `iptablesSwitchAtRuntime` vrai par défaut : legacy seulement si `ip_tables` est chargé, nft sinon |

### Le montage `docker-host.sock` reposait sur une erreur

La mémoire `260403-1827-docker-in-docker.md` affirmait que docker-in-docker détecte `/var/run/docker-host.sock` et monte un proxy socat. C'est faux : ce proxy appartient à la feature **docker-outside-of-docker**. Le montage ne servait à rien et donnait un accès root au Docker de l'hôte. Le daemon tourne dans le conteneur.

### Changelog : patch, pas de rubrique Migration

L'issue proposait une note de migration (régénérer `devcontainer-lock.json`, rebuild). Elle aurait imposé une majeure (`docs/dev/release.md`). Décision : entrée « Corrigé » seule. Le template ne génère pas de lock, et le rebuild après `cruft update` est la norme (comme pour `shutdownAction`, #92).

## Tests

`tests/test_template_generation.py` lit le JSONC rendu avec `parse_jsonc` (`tests/devcontainer_utils.py`, import `from tests.devcontainer_utils`) :

- `test_docker_in_docker_enabled_when_requested` : une seule feature `docker-in-docker:<N>`, `N >= 4`, `moby` à `false`, `iptablesSwitchAtRuntime` absent ou vrai ;
- `test_docker_in_docker_does_not_mount_host_docker_socket` : aucun montage `docker.sock`, pas de `docker-host.sock` ni `socat` dans `postCreateCommand.sh`.

## Validation

Projet de test créé par `cruft create --checkout <branche> --extra-context '{"docker_in_docker": "y"}'`, puis Rebuild : `docker info` affiche Server Version 29.9.3, `docker run --rm hello-world` passe, `/var/run/docker-host.sock` n'existe plus.
