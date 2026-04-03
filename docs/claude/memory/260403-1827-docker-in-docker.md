# Issue #44 — Intégration Docker-in-Docker dans PyFoundry

## Résumé

Ajout de l'option `docker_in_docker` au template PyFoundry, permettant d'utiliser Docker à l'intérieur d'un Dev Container (builder des images, lancer des conteneurs de test).

---

## Fichiers modifiés

### Template

- `cookiecutter.json` : ajout de `"docker_in_docker": "n"` (notation cohérente avec `use_node`)
- `{{ cookiecutter.project_slug }}/.devcontainer/devcontainer.json` :
  - Feature conditionnelle `ghcr.io/devcontainers/features/docker-in-docker:2` avec `"moby": false`
  - Montage conditionnel du socket Docker de l'hôte **vers `/var/run/docker-host.sock`** (pas `/var/run/docker.sock`)
- `{{ cookiecutter.project_slug }}/.devcontainer/postCreateCommand.sh` :
  - Section d'exécution et echo final conditionnels pour `docker_in_docker`

### Tests

- `tests/conftest.py` : ajout de `docker_in_docker_template_context` fixture
- `tests/test_template_generation.py` : 2 nouveaux tests
  - `test_docker_in_docker_disabled_by_default`
  - `test_docker_in_docker_enabled_when_requested`

### Documentation

- `docs/user/getting_started.md` : `docker_in_docker` dans le tableau des options
- `docs/user/usage.md` :
  - Section "Options du template" complétée avec tableau + descriptions
  - Exemple `cruft update --variables-to-update` mis à jour
  - Section Docker mise à jour (suppression référence issue #44)
- `docs/dev/architecture.md` : variables Cookiecutter mises à jour
- `docs/dev/contributing.md` : guide complet "Ajouter une option Cookiecutter" avec checklist
- `docs/dev/testing.md` : réécriture complète (chemins hardcodés `/home/guillaume`, conda obsolète)
- `CLAUDE.md` :
  - Variable `docker_in_docker` ajoutée dans les Variables Cookiecutter
  - R1.1 corrigé : `source /home/vscode/.venv/bin/activate && pytest tests -v`
  - R1.2 corrigé : `ruff check tests/ docs/ --fix`

---

## Décision technique clé : chemin du socket

**Problème rencontré** : en montant `/var/run/docker.sock` directement (target = `/var/run/docker.sock`), le GID du socket hôte (ex: 984) ne correspondait pas au GID du groupe `docker` dans le container (ex: 997), causant `permission denied`.

**Solution** : monter vers `/var/run/docker-host.sock` (comme dans le projet de référence `castorfou/lmelp`). La feature `docker-in-docker:2` détecte ce fichier et configure automatiquement un **proxy socat** entre le daemon Docker interne (`/var/run/docker.sock`) et le socket hôte. Plus de problème de GID.

```json
"source=/var/run/docker.sock,target=/var/run/docker-host.sock,type=bind"
```

---

## Homogénéité `use_node`

La variable `use_node` utilise la notation `"y"/"n"` (pas `"yes"/"no"`). Conserver cette convention pour toute nouvelle option booléenne du template.

---

## Commandes de test

```bash
# Tests automatisés
source /home/vscode/.venv/bin/activate && pytest tests -v

# Test manuel avec docker_in_docker activé
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input --extra-context '{"docker_in_docker": "y"}'
code mon-projet-data-science
# → Rebuild container → docker ps doit fonctionner

# Activer l'option sur un projet existant
cruft update --variables-to-update '{"docker_in_docker": "y"}'
```
