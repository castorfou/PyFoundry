# Issue #85 — source GitHub Pages réglée sur « GitHub Actions »

## Résumé

Demande : expliquer qu'il faut régler la source de GitHub Pages sur **GitHub Actions**. La doc le supposait seulement, dans une demi-phrase de « Publier la doc d'une branche sur GitHub Pages » (`docs/user/usage.md`).

Dans **Settings → Pages**, GitHub propose par défaut « Deploy from a branch ». Avec `main` / `(root)`, la doc semble publiée, car `docs.yml` la déploie quand même avec `actions/deploy-pages`. Mais à chaque push, GitHub lance en plus un run `pages build and deployment` qui construit tout le dépôt avec Jekyll et échoue à l'étape « Build with Jekyll » (sur `CLAUDE.md`, les cheatsheets…). Ce run n'est pas un workflow du projet, d'où une cause difficile à trouver. Cas réel : `castorfou/google-to-synology-photos`, généré avec PyFoundry 1.0.0.

Correction purement documentaire, sur la branche `85-docs-expliquer-quil-faut-régler-la-source-github-pages-sur-github-actions`, appliquée au dépôt et au squelette (R1.5).

Spécifications : [commentaire de l'issue #85](https://github.com/castorfou/PyFoundry/issues/85#issuecomment-6402549845).

---

## Décisions

- **Pas d'automatisation dans `docs.yml`.** `actions/configure-pages` avec `enablement: true` demande un jeton admin du dépôt ; le `GITHUB_TOKEN` des workflows ne suffit pas. Le réglage reste manuel, une fois par projet, comme la règle de branche de l'environnement `github-pages` (#63).
- **Commandes CLI** (API REST Pages, champ `build_type`) :
  - `gh api -X POST "repos/{owner}/{repo}/pages" -f build_type=workflow` si Pages n'est pas encore activé (répond `409` s'il l'est déjà) ;
  - `gh api -X PUT "repos/{owner}/{repo}/pages" -f build_type=workflow` si Pages utilise « Deploy from a branch » ;
  - `gh api "repos/{owner}/{repo}/pages" --jq .build_type` doit afficher `workflow` (vérifié sur PyFoundry).
  Comme pour #63, la doc dit de copier `{owner}`/`{repo}` tels quels.
- **Pas de note de migration** : réglage de dépôt, rien à faire après `cruft update`.

---

## Modifications

- `docs/user/usage.md` : sous-section `#### Activer GitHub Pages (une fois par projet)` dans « Pipeline CI/CD », onglets Interface / CLI `gh`. « Autoriser les branches » renvoie à cette ancre (`#activer-github-pages-une-fois-par-projet`) au lieu de supposer le réglage.
- `docs/user/getting_started.md` : avertissement « une fois par projet » sous le pipeline CI/CD, lien vers la même ancre.
- `docs/user/troubleshooting.md`, section MkDocs : entrée « Run `pages build and deployment` en échec dans « Build with Jekyll » » (symptôme, cause, correction).
- `docs/cheatsheets/mkdocs.md` et `{{ cookiecutter.project_slug }}/docs/cheatsheets/mkdocs.md` : section `### Activer GitHub Pages (une fois par projet)` identique, avant « Publier la doc d'une branche ».
- `{{ cookiecutter.project_slug }}/CLAUDE.md`, « Déploiement automatique » : prérequis source Pages = GitHub Actions.

## Tests

`tests/test_mkdocs_integration.py`, bloc « Source GitHub Pages réglée sur « GitHub Actions » (issue #85) » :

- `test_pages_source_commands_documented`, paramétré sur `usage.md`, la cheatsheet de la racine et celle du projet généré : les trois commandes de `PAGES_SOURCE_COMMANDS`, « Source : GitHub Actions » et « Build with Jekyll » sont présents.
- `test_troubleshooting_explains_failing_jekyll_build` : l'entrée existe et pointe vers `usage.md#activer-github-pages-une-fois-par-projet`.

RED avant la doc (4 échecs), puis 343 passés, 1 ignoré. `mkdocs build --strict` passe ; l'ancre a été vérifiée dans `site/user/usage/index.html` (mkdocs ne valide pas les ancres en strict par défaut).

## À retenir

- Le `ruff format` du hook reformate les nouveaux tests : lancer `ruff format tests/` avant de commiter.
- Un réglage de dépôt GitHub (Pages, environnements) n'est dans aucun fichier : le documenter côté utilisateur PyFoundry, dans la cheatsheet du projet généré et dans son `CLAUDE.md`.
