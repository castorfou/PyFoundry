# 0003 — Propriétaire de chaque fichier lors d'une mise à jour du template

- **Statut** : accepté
- **Date** : 2026-10-25
- **Issue** : [#89](https://github.com/castorfou/PyFoundry/issues/89)

## Contexte

Une mise à jour du template laisse des rejets (`.rej` ou marqueurs de conflit) partout où le projet généré et le template ont modifié les mêmes lignes. Les résoudre à la main demande de savoir, fichier par fichier, si le changement local est une personnalisation à garder ou un reste d'une ancienne version du template. La doc se contentait de « appliquez manuellement les modifications souhaitées ». Les projets générés reçoivent maintenant une skill `/cruft-update`, qui résout ces rejets avec Claude : il faut lui donner une règle.

## Décision

Chaque fichier d'un projet généré a un propriétaire, qui décide du sort de ses rejets :

1. **Fichier du template** (`.devcontainer/`, `.github/workflows/`, `.claude/commands/`, `.claude/skills/`, `.pre-commit-config.yaml`, `docs/cheatsheets/`) : la version du template l'emporte. Si le côté local est une vraie personnalisation, et non une ancienne version du template, Claude demande.
2. **Fichier du projet** (`src/`, `tests/`, `notebooks/`, `data/`, `README.md`, `docs/user/`, `docs/dev/`, `docs/claude/memory/`) : la version locale l'emporte. Un changement du template y est signalé, jamais appliqué.
3. **Fichier mixte** (`pyproject.toml`, `mkdocs.yml`, `CLAUDE.md`, `.gitignore`, `docs/agents/`, `.claude/settings.json`) : on fusionne les deux côtés. `uv.lock` est régénéré par `uv lock`, jamais fusionné.

La liste des motifs vit dans un seul endroit, le script de la skill. Pas de surcharge par projet pour l'instant : la skill demande déjà dès qu'une personnalisation est en jeu.

Pour l'auto-mise à jour de PyFoundry, dont la racine est alignée sur le squelette à chaque modification, chaque rejet reçoit un verdict : déjà appliqué, propre au projet généré, ou trou à combler.

## Options écartées

- **Tout demander à l'utilisateur** : fiable, mais des dizaines de questions par mise à jour, la plupart sans enjeu (un rejet dans `.devcontainer/` est presque toujours un ancien état du template).
- **Tout résoudre sans demander, puis faire relire le diff** : rapide, mais une personnalisation écrasée dans un long diff passe inaperçue.

## Conséquences

- Personnaliser un fichier du template se paie à chaque mise à jour par une question. `docs/user/conventions.md` le dit déjà pour `postCreateCommand.sh`.
- Ajouter un dossier au squelette demande de le classer dans le script de la skill.
