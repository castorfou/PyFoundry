# Project: PyFoundry Template

## Description

Un template Cookiecutter de qualité industrielle pour démarrer des projets de Data Science en Python. Il vise à garantir la reproductibilité, la qualité du code et un démarrage rapide grâce à une configuration complète et automatisée.

- **GitHub** : https://github.com/castorfou/PyFoundry
- **Documentation** : https://castorfou.github.io/PyFoundry
- **Version** : celle de `pyproject.toml`, détaillée dans `CHANGELOG.md` (processus dans `docs/dev/release.md`)

## La Stack

- **Templating** : Cookiecutter / Cruft
- **Environnement** : Devcontainer (VS Code)
- **Dépendances** : uv & pyproject.toml
- **Qualité de Code** : pre-commit & ruff & mypy
- **Tests du Template** : pytest & pytest-cookies
- **Documentation** : MkDocs & mkdocs-material
- **CI/CD** : GitHub Actions

## Architecture

### Structure du Template (Dépôt PyFoundry)

```
PyFoundry/
├── .claude/
│   ├── commands/                        # Commandes slash (fix-issue, stocke-memoire)
│   ├── skills/cruft-update/             # Skill de mise à jour du template (identique dans le squelette)
│   └── settings.json                    # Plugins activés (mattpocock-skills)
├── .devcontainer/                       # Environnement de dev pour travailler sur le template
│   └── scripts/
│       ├── check_mounts.sh              # Vérification des montages (sur l'hôte, via initializeCommand)
│       ├── ensure_venv.sh               # Recrée /tmp/venv s'il manque (postStartCommand)
│       ├── gh_login.sh                  # Authentification gh au premier terminal zsh
│       └── migrate_claude_history.sh    # Historique Claude Code vers la config partagée (sur l'hôte)
├── .github/
│   ├── scripts/release.py               # Contrôle du tag et notes de release tirées du CHANGELOG
│   └── workflows/
│       ├── test-template.yml            # CI : lint + tests sur toutes les branches
│       ├── docs.yml                     # Déploiement documentation GitHub Pages
│       └── release.yml                  # Publication des releases
├── docs/                                # Fichiers source MkDocs
│   ├── adr/                             # Architecture Decision Records
│   ├── agents/                          # Config des skills Matt Pocock (issues, labels, domaine)
│   ├── cheatsheets/                     # Claude, GitHub, Docker, uv, VSCode, MkDocs...
│   ├── dev/                             # Docs développeur (architecture, tests, contribution)
│   └── user/                            # Docs utilisateur (getting started, conventions)
├── tests/
│   ├── conftest.py                      # Fixtures pytest (contextes de génération)
│   ├── devcontainer_utils.py            # Parseur JSONC de devcontainer.json
│   ├── test_template_generation.py      # Tests de génération (structure, fichiers)
│   ├── test_configurations.py           # Validation (TOML, YAML, JSON), conformité aux hooks pre-commit
│   ├── test_mkdocs_integration.py       # Tests MkDocs (config, build)
│   ├── test_persistent_home.py          # HOME persistant, montages, venv /tmp/venv
│   ├── test_ensure_venv.py              # Venv recréé au démarrage, activation dans .zshrc
│   ├── test_check_mounts.py             # Script check_mounts.sh
│   ├── test_post_create_command.py      # setup_pre-commit de postCreateCommand.sh
│   ├── test_timezone.py                 # Fuseau de l'hôte : montage, setup_timezone
│   ├── test_github_auth.py              # Authentification gh : montage partagé, gh_login.sh
│   ├── test_claude_auth.py              # Config Claude Code partagée, migration de l'historique
│   ├── test_versioning.py               # Version, CHANGELOG, release.py, release.yml
│   └── test_cruft_update_skill.py       # Skill /cruft-update et son script
├── {{ cookiecutter.project_slug }}/     # Contenu du projet généré
├── CHANGELOG.md                         # Évolutions par version (Keep a Changelog)
├── CONTEXT.md                           # Glossaire du domaine (template, projet généré, rejet…)
├── cookiecutter.json                    # Variables du template (dont _pyfoundry_version)
├── mkdocs.yml
└── pyproject.toml                       # Dépendances et config outils (ruff, mypy, pytest)
```

### Variables Cookiecutter

```json
{
    "project_name": "Mon Projet Data Science",
    "project_slug": "<auto-généré depuis project_name>",
    "description": "Description courte",
    "python_version": "3.11",
    "github_username": "castorfou",
    "use_node": "n",
    "docker_in_docker": "n",
    "_pyfoundry_version": "<version de pyproject.toml>"
}
```

`_pyfoundry_version` est privée : cruft la relit dans le nouveau template à chaque `cruft update`, donc le `.cruft.json` d'un projet généré porte la version du template dont il vient.

### Structure du Projet Généré

```
mon-projet-data-science/
├── .claude/
│   ├── commands/                  # Commandes slash (fix-issue, stocke-memoire)
│   ├── skills/cruft-update/       # Mise à jour du template (cruft update, rejets)
│   └── settings.json              # Plugins activés (mattpocock-skills)
├── .devcontainer/                  # Environnement de dev reproductible
├── .github/workflows/              # CI/CD du projet généré
├── data/
│   ├── raw/
│   └── processed/
├── docs/                           # Documentation MkDocs du projet
│   ├── user/
│   ├── dev/
│   ├── agents/                    # Config pré-remplie des skills Matt Pocock
│   └── claude/memory/             # Mémoire Claude Code
├── notebooks/
├── src/
├── tests/
├── .gitignore
├── .pre-commit-config.yaml
├── CLAUDE.md
└── pyproject.toml
```

## Environnement de Développement

Pour travailler sur le template PyFoundry lui-même, deux options :

### Option 1 : Devcontainer (recommandé)

Le dépôt PyFoundry a son propre devcontainer. Ouvrir dans VS Code → "Reopen in Container".

### Option 2 : Environnement conda/mamba `pyfoundry`

```bash
# Créer l'environnement (une seule fois)
mamba create -y -n pyfoundry -c conda-forge python=3.11
mamba activate pyfoundry
mamba install nb_conda_kernels cruft mkdocs-material pytest pytest-cookies pytest-cov pre-commit ruff mypy --yes

# Activer l'environnement
source ~/miniforge3/etc/profile.d/conda.sh && conda activate pyfoundry
```

## Commandes Utiles

### Lancer les tests

```bash
# Via conda (règle R1.1)
eval "$(conda shell.bash hook)" && conda activate pyfoundry && pytest tests -v

# Via uv
uv sync --active --all-extras
uv run --active pytest tests/
```

### Linter / Formater

```bash
# Via conda (règle R1.2)
eval "$(conda shell.bash hook)" && conda activate pyfoundry && ruff check tests/ docs/ --fix

# Via uv
uv run --active ruff check . --fix
```

### Générer un projet de test localement

```bash
# cookiecutter lit le filesystem (voit les fichiers non commités) — pour test rapide
cd ~/temp && rm -rf mon-projet-data-science
cookiecutter /workspaces/PyFoundry --no-input

# cruft utilise Git (ne voit que les fichiers commités) — pour test fidèle à la prod
cruft create . --no-input

# Avec paramètres personnalisés
cruft create . --no-input --extra-context '{"use_node": "y"}'
```

### Documentation

```bash
uv sync --active --extra doc
uv run --active mkdocs serve        # Prévisualiser sur http://localhost:8000
uv run --active mkdocs build --strict
```

## Règles Importantes pour Claude Code

### R1.1 — Lancer pytest

```bash
source /tmp/venv/bin/activate && pytest tests -v
```

### R1.2 — Lancer ruff

```bash
ruff check tests/ docs/ --fix
```

### R1.3 — Tester localement le projet généré

```bash
mamba activate pyfoundry && \
cd /tmp && \
rm -rf /tmp/mon-projet-data-science && \
cruft create /workspaces/PyFoundry --no-input --extra-context '{"use_node": "y"}' && \
code mon-projet-data-science
```

Puis "Rebuild and Reopen in Container" depuis VS Code.

### R1.4 — cruft vs cookiecutter

- **`cruft create`** : utilise Git → ne voit que les fichiers **commités**
- **`cookiecutter`** : lit le filesystem → voit **tous** les fichiers

Pour tester des modifications non commitées, utiliser `cookiecutter` directement.

### R1.5 — Aligner le template et le projet généré

Ce dépôt contient le template lui-même et le squelette du projet généré, sous `{{ cookiecutter.project_slug }}/`. Pour chaque modification de l'un, vérifier si l'autre demande la même modification, et les garder alignés quand c'est pertinent. Après une modification du squelette, valider le projet rendu (R1.3, ou `cookiecutter` pour des fichiers non commités, voir R1.4).

### R1.6 — Tenir le CHANGELOG

Chaque changement visible pour un utilisateur du template va dans la section `## [Non publié]` de `CHANGELOG.md`, avec le numéro de l'issue. Si les projets existants doivent faire une action manuelle en plus de `cruft update`, ajouter une note dans `### Migration` : la prochaine release sera une majeure. Ne pas modifier la version hors d'une PR de release (voir `docs/dev/release.md`).

## Conventions & Style de Code

- **Source de vérité unique** : `pyproject.toml` pour toutes les configurations.
- **Formatage & Linting** : `ruff` configuré dans `pyproject.toml`.
- **Templating** : syntaxe `{{ cookiecutter.variable }}` pour les fichiers dynamiques.
- **Exclusion ruff** : le dossier `{{ cookiecutter.project_slug }}` est exclu via `extend-exclude = ["[{][{]*"]`. Pour un fichier identique à la racine et dans le squelette (skill, scripts), `ruff format` ne modifie que la copie de la racine : recopie-la ensuite dans le squelette, sinon les tests d'égalité échouent.
- **Commits** : convention `type(scope): message` — `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.

## Stratégie de Test

### Fichiers de tests

| Fichier | Rôle |
|---------|------|
| `conftest.py` | Fixtures : `default_template_context`, `minimal_template_context` |
| `test_template_generation.py` | Structure générée, fichiers présents, variables injectées |
| `test_configurations.py` | Validité TOML/YAML/JSON, config ruff/mypy/devcontainer, fichiers générés conformes à `trailing-whitespace`, `end-of-file-fixer` et `check-json`, pas d'extension isort, hook `no-venv-at-root` |
| `test_mkdocs_integration.py` | Config mkdocs.yml, build documentation, `docs.yml` (dépôt et projet généré) : publication sur `main` ou sur lancement manuel depuis n'importe quelle branche, jamais sur une pull request |
| `test_persistent_home.py` | HOME persistant, montages, `initializeCommand` (dont chaque point de montage imbriqué, déduit des `mounts`), venv `/tmp/venv` et `UV_PROJECT_ENVIRONMENT` (dépôt et projet généré) |
| `test_ensure_venv.py` | `ensure_venv.sh` (identique dans le dépôt et le squelette) lancé par `postStartCommand` : recrée `/tmp/venv` s'il manque ou sans interpréteur, ne fait rien sinon, `--sync` force la synchronisation, échec d'`uv` signalé avec le contournement ; `create_python_environment` lui délègue ; `.zshrc` n'active le venv que s'il existe et perd l'ancienne ligne non protégée |
| `test_check_mounts.py` | `check_mounts.sh` : sources manquantes, résolution des variables, permissions `.ssh`, `[WARN]` sur les points de montage imbriqués d'un autre propriétaire (`CHECK_MOUNTS_UID`), lecture JSONC (commentaires en fin de ligne, marqueurs dans les chaînes, virgules finales) alignée sur `parse_jsonc` |
| `test_post_create_command.py` | `setup_pre-commit` : un rebuild ne commite que `.pre-commit-config.yaml`, jamais le travail en cours |
| `test_timezone.py` | Fuseau de l'hôte monté sur `/etc/localtime.host` (jamais sur `/etc/localtime`, qui écraserait `Etc/UTC`), pas de `TZ` transmis (vide = UTC), `setup_timezone` relie `/etc/localtime` à la zone de même contenu |
| `test_github_auth.py` | Config gh partagée entre devcontainers (`~/.config/gh-devcontainers`, créé en `700`), aucun `gh auth login` dans `postCreateCommand`, `setup_gh_credential_helper`, `gh_login.sh` (silencieux si authentifié, sans réseau, une seule tentative par conteneur, jamais d'échec du shell) |
| `test_versioning.py` | Version de `pyproject.toml` en SemVer strict, égale à `_pyfoundry_version` de `cookiecutter.json` ; `CHANGELOG.md` (section « Non publié » en tête, section datée pour la version courante) ; `release.py check-tag` et `notes` ; `release.yml` les appelle ; étape CHANGELOG de `/fix-issue`, identique dans le dépôt et le squelette |
| `test_cruft_update_skill.py` | Skill `/cruft-update` identique dans le dépôt et le projet généré (donc non rendue par Jinja, `_copy_without_render`), frontmatter (model-invoked), `template_update.py` : `categorie` (catégories de l'ADR 0003), `rejets` (`.rej` et vrai conflit `git apply -3`), `changelog` (template local ou clone léger depuis `.cruft.json`) |
| `test_claude_auth.py` | Config Claude Code partagée entre devcontainers (`~/.config/claude-devcontainers` monté sur `~/.claude`, créé en `700`), `CLAUDE_CONFIG_DIR`, verrous `~/.claude/ide` propres au projet, `migrate_claude_history.sh` (copie sans écraser, une seule fois, jamais la connexion, jamais d'échec) |

### CI/CD GitHub Actions

| Workflow | Déclencheur | Rôle |
|----------|-------------|------|
| `test-template.yml` | Push toutes branches, PR main | Lint ruff + tests pytest |
| `docs.yml` | Push main (docs/ ou mkdocs.yml), lancement manuel depuis n'importe quelle branche | Déploiement GitHub Pages |
| `release.yml` | Tag `v*.*.*` | Vérifie le tag (`release.py check-tag`), lance les tests, publie la release avec la section du CHANGELOG |

## Skills Matt Pocock

Le plugin [mattpocock-skills](https://github.com/mattpocock/skills) est activé dans `.claude/settings.json`. Ce réglage active le plugin pour le dépôt mais ne le télécharge pas : chaque utilisateur doit l'installer une fois sur sa machine. Dans VS Code : `/plugins` → onglet **Plugins** → rechercher `mattpocock-skills` → **Install** → **Install for this project**.

La configuration attendue par les skills d'ingénierie est déjà pré-remplie (voir [Agent skills](#agent-skills)) : issues sur GitHub, labels de triage par défaut, documentation du domaine à contexte unique. Pour changer ces choix, modifie directement `docs/agents/*.md` ou relance `/setup-matt-pocock-skills`.

Skills les plus utiles :

- `/grill-me`, `/grill-with-docs` : Claude te pose des questions pour clarifier un besoin avant d'écrire du code
- `/to-spec`, `/to-tickets` : transformer une discussion en spécification, puis en issues
- `/tdd` : boucle RED → GREEN → REFACTOR
- `/triage` : trier les issues GitHub à l'aide des labels
- `/diagnosing-bugs` : enquêter méthodiquement sur un bug

## Agent skills

### Issue tracker

Les issues sont suivies dans GitHub Issues (`castorfou/PyFoundry`), via la CLI `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

Labels par défaut : `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Contexte unique : `CONTEXT.md` et `docs/adr/` à la racine, créés au besoin. See `docs/agents/domain.md`.

## Ressources

- [Cookiecutter docs](https://cookiecutter.readthedocs.io/)
- [Cruft docs](https://cruft.github.io/cruft/)
- [uv docs](https://github.com/astral-sh/uv)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- [pytest-cookies](https://pytest-cookies.readthedocs.io/)
