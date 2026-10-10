# Issue #58 — Activer les skills Matt Pocock

## Résumé

Le plugin [mattpocock-skills](https://github.com/mattpocock/skills) (`mattpocock-skills@claude-plugins-official`, marketplace officiel Anthropic) est rendu disponible dans PyFoundry et dans les projets générés. Sa configuration (issues, labels de triage, docs du domaine) est **pré-remplie** dans le projet généré : `/setup-matt-pocock-skills` devient facultatif.

---

## Commits de la branche `58-activer-matt-pocock-skills`

- `7becd3d` activer les tools todo de claude code : `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` dans `containerEnv` de `.devcontainer/devcontainer.json` (PyFoundry et squelette), mise à jour de `.devcontainer/devcontainer-lock.json`
- `69a877d` chore : montée de version des hooks dans `.pre-commit-config.yaml`
- `7d59187` (intitulé « chore: update pre-commit hooks », mais contient aussi le début de l'issue) :
  - `.claude/settings.json` et `{{ cookiecutter.project_slug }}/.claude/settings.json` : `enabledPlugins` avec le plugin
  - `.devcontainer/Dockerfile` et `{{ cookiecutter.project_slug }}/.devcontainer/Dockerfile` : image `python:1-3.12-bullseye` → `python:1-3.12-bookworm`
  - 3 tests (`test_claude_settings_json_created`, `test_mattpocock_skills_plugin_enabled`, `test_claude_md_mentions_mattpocock_skills`)
  - section « Skills Matt Pocock » dans `{{ cookiecutter.project_slug }}/CLAUDE.md`
- Commit de clôture (cette session) : pré-remplissage, docs, R1.5, corrections GitLab

---

## Fichiers modifiés (session de clôture)

### Template (squelette)

- `{{ cookiecutter.project_slug }}/docs/agents/issue-tracker.md` : GitHub, dépôt `{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}`, CLI `gh`
- `{{ cookiecutter.project_slug }}/docs/agents/triage-labels.md` : 5 labels par défaut (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`)
- `{{ cookiecutter.project_slug }}/docs/agents/domain.md` : contexte unique (`CONTEXT.md` + `docs/adr/`, créés au besoin)
- `{{ cookiecutter.project_slug }}/CLAUDE.md` : section `## Agent skills` (avant `## Ressources`), arbre mis à jour, procédure d'installation manuelle du plugin

Les trois fichiers sont les modèles du skill `setup-matt-pocock-skills` (v1.2.3), seule la ligne du dépôt est adaptée.

### PyFoundry

- `CLAUDE.md` : section `## Agent skills`, règle **R1.5** (aligner template et projet généré, valider le projet rendu), arbre du projet généré (`.claude/settings.json`, `docs/agents/`)
- `docs/agents/*.md` : produits par `/setup-matt-pocock-skills` exécuté sur PyFoundry (GitHub `castorfou/PyFoundry`, labels par défaut, contexte unique)

### Tests

- `tests/test_template_generation.py` : 3 nouveaux tests
  - `test_agent_skills_docs_created`
  - `test_agent_skills_issue_tracker_points_to_github_repo`
  - `test_claude_md_has_agent_skills_section`

### Documentation

- `README.md` : ligne « Skills Matt Pocock » dans les fonctionnalités
- `docs/cheatsheets/claude.md` : section « skills Matt Pocock » (activation, installation, configuration, skills principaux)
- `docs/dev/architecture.md` : sous-section « Configuration Claude Code »
- `docs/user/getting_started.md` : étape « Activer les skills Claude Code »
- Corrections de restes GitLab : `glab` → `gh` dans `docs/user/getting_started.md:69`, titre « CLI GitHub (`gh`) » dans `docs/user/usage.md:220`, « GitHub : CI/CD et CLI » dans `docs/user/README.md:20`

---

## Apprentissages clés

### `enabledPlugins` n'installe pas le plugin

Hypothèse initiale fausse : on pensait que Claude Code proposerait l'installation à l'ouverture du projet. La [doc officielle](https://code.claude.com/docs/en/plugins/install#choose-an-install-scope) est claire : une entrée projet dans `.claude/settings.json` **active** le plugin mais ne le **télécharge pas**. Chaque utilisateur l'installe une fois : `/plugins` → onglet **Plugins** → `mattpocock-skills` → **Install** → **Install for this project**.

Issues liées : [#32606](https://github.com/anthropics/claude-code/issues/32606), [#41669](https://github.com/anthropics/claude-code/issues/41669) (pas de prompt pour `claude-plugins-official`), [#90937](https://github.com/anthropics/claude-code/issues/90937).

L'automatisation via `claude plugin install ... --scope project` dans `postCreateCommand.sh` est impossible tant que la CLI `claude` n'est pas dans le conteneur.

### Pré-remplir plutôt que lancer le setup

Décision utilisateur : pré-remplir `docs/agents/` dans le squelette. Le template est conçu pour GitHub (`setup_github`, `gh`, GitHub Actions), donc le choix GitHub est cohérent. Pour changer : éditer `docs/agents/*.md` ou relancer `/setup-matt-pocock-skills`.

### Pas de `glab` dans le template

Aucun `postCreateCommand.sh` ne configure `glab`. Les mentions GitLab de la doc utilisateur étaient des restes du template d'origine.

### Validation du projet rendu

`mkdocs build --strict` d'un projet rendu hors dépôt git échoue à cause de `git-revision-date-localized-plugin` (warning « Unable to find a git directory »). Faire `git init && git add -A && git commit` avant de construire (c'est ce que fait `postCreateCommand.sh` en vrai). Les pages `docs/agents/*.md` hors `nav` ne génèrent qu'un INFO.
