# Issue #63 — déploiement manuel GitHub Pages depuis une branche

## Résumé

Demande : pouvoir publier sur GitHub Pages la doc d'une branche autre que `main`, en lançant le workflow à la main depuis GitHub Actions.

Deux verrous bloquaient cette publication :

1. **Le workflow** (`docs.yml`, dans le code). `workflow_dispatch` existait déjà, mais `Setup Pages`, `Upload artifact` et le job `deploy` étaient conditionnés par `github.ref == 'refs/heads/main'`. Lancé à la main sur une branche, le workflow construisait la doc puis sautait la publication. Le run restait vert sans rien publier.
2. **L'environnement GitHub `github-pages`** (réglage du dépôt, dans aucun fichier). Quand Pages utilise la source « GitHub Actions », GitHub crée cet environnement avec une règle « Deployment branches » qui n'autorise que la branche par défaut. Sur PyFoundry, les branches autorisées étaient `main` et `master`. Depuis une autre branche, le job `deploy` échoue avec `Branch "…" is not allowed to deploy to github-pages due to environment protection rules`.

Correction sur la branche `63-cicd-doit-permettre-le-deploiement-manuel-gh-pages-depuis-une-branche`, appliquée au dépôt et au squelette (R1.5).

Spécifications : [commentaire de l'issue #63](https://github.com/castorfou/PyFoundry/issues/63#issuecomment-6112382892).

---

## Décisions (validées par l'utilisateur)

- **Verrou 1 corrigé dans le code.** Les trois conditions deviennent `github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'`. Une pull request (`refs/pull/N/merge`) construit toujours la doc sans la publier.
- **Verrou 2 documenté, pas modifié par Claude** (option « b »). L'utilisateur voulait appliquer le réglage lui-même en suivant la doc, pour la tester. Claude n'a donc pas lancé le `POST` sur l'environnement.
- **Doc ciblée sur les projets générés.** Après une première version centrée sur le dépôt PyFoundry, l'utilisateur a rappelé qu'il fallait surtout expliquer à un projet utilisant PyFoundry comment activer la fonctionnalité. Le guide complet est dans la doc utilisateur PyFoundry. Le projet généré en a une version courte dans son aide-mémoire MkDocs et son `CLAUDE.md`.
- **Placeholders `{owner}`/`{repo}` de `gh api`.** L'utilisateur les a remplacés à la main et a fait une faute de frappe (`castor_fou` au lieu de `castorfou`), d'où un `Not Found (HTTP 404)`. La doc dit maintenant explicitement de copier la commande telle quelle (`gh` remplace lui-même `{owner}` et `{repo}` depuis le dossier du projet) et qu'un 404 vient le plus souvent d'un propriétaire ou d'un dépôt mal saisi.
- **Une seule doc en ligne.** Publier une branche remplace la doc de `main` jusqu'au prochain déploiement depuis `main`. La doc l'indique dans un avertissement.

---

## Solution

### `.github/workflows/docs.yml` et `{{ cookiecutter.project_slug }}/.github/workflows/docs.yml`

- Nouvelle condition sur `Setup Pages`, `Upload artifact` et le job `deploy`. Dans le squelette, l'expression reste entourée de `{% raw %}…{% endraw %}`.
- Commentaire de `workflow_dispatch` : « Déploiement manuel, depuis n'importe quelle branche ».

### Réglage de l'environnement (procédure documentée)

```bash
gh api -X POST "repos/{owner}/{repo}/environments/github-pages/deployment-branch-policies" -f name='*'
gh api "repos/{owner}/{repo}/environments/github-pages/deployment-branch-policies" --jq '.branch_policies[].name'
```

Ou dans l'interface : Settings → Environments → github-pages → Deployment branches and tags → Add deployment branch or tag rule, motif `*`. Un motif plus restreint (`docs/*`) est possible.

Publication : `gh workflow run docs.yml --ref <branche>`, ou Actions → 📚 Deploy Documentation → Run workflow.

---

## Tests

`tests/test_mkdocs_integration.py`, fixture `docs_workflow` paramétrée `repo` / `generated`. Elle parse le `docs.yml` du dépôt (`REPO_ROOT` de `tests/devcontainer_utils.py`) ou d'un projet cuit avec PyYAML.

- `evaluate_if` évalue une expression `if` GitHub Actions simple : les `github.*` sont remplacés par leur valeur (`repr`), puis `||` et `&&` par `or` et `and`, avant un `eval` sans builtins. On teste ainsi le comportement des conditions, pas la présence d'une chaîne.
- `test_docs_workflow_can_be_triggered_manually` : `workflow_dispatch` est dans les déclencheurs. PyYAML lit la clé `on` comme `True`, d'où `docs_workflow.get("on", docs_workflow.get(True))`.
- `test_docs_workflow_deploys_only_from_main_or_manual_run`, paramétré : push sur main et lancement manuel sur main → publication ; lancement manuel sur une branche → publication (seul cas RED avant la correction) ; pull request → pas de publication.
- Pre-commit (règle PLW1510) bloquait le commit à cause du `subprocess.run` déjà présent dans `test_mkdocs_can_build` : ajout de `check=False`, le test lisant déjà `returncode`.

Résultat : 195 tests passent, 1 ignoré.

---

## Documentation

- `docs/user/usage.md` : section « Publier la doc d'une branche sur GitHub Pages » (autoriser les branches, une fois par projet ; publier une branche ; une seule doc en ligne ; `cruft update` pour les projets plus anciens). Mention dans la description du pipeline.
- `docs/user/getting_started.md` : mention du lancement manuel dans la description du pipeline.
- `docs/user/troubleshooting.md` : entrée « Déploiement refusé : `not allowed to deploy to github-pages` ».
- `docs/dev/deployment.md` : section « Publier la doc d'une branche » (comportement, tests, renvoi au guide).
- `docs/cheatsheets/mkdocs.md` et sa copie dans le squelette (identiques) : la section « Doc et CICD » parlait d'un « pipeline gitlab », elle donne maintenant la procédure.
- `{{ cookiecutter.project_slug }}/CLAUDE.md` : lancement manuel et prérequis dans « Déploiement automatique ».
- `CLAUDE.md` racine : ligne `test_mkdocs_integration.py` de la table des tests.

---

## Vérifications

- `mkdocs build --strict` passe sur PyFoundry et sur un projet généré avec `cookiecutter`.
- Piège : sans dépôt git, le plugin `git-revision-date-localized` émet un warning qui fait échouer le build strict du projet généré. Faire `git init` et un commit avant de construire.
- **Test réel par l'utilisateur** : règle `*` ajoutée sur l'environnement de PyFoundry, puis lancement manuel de `docs.yml` sur la branche. La doc de la branche a bien été publiée sur https://castorfou.github.io/PyFoundry.

---

## Commits de la branche

- `adceac2` `fix(ci): publier la doc GitHub Pages depuis une branche sur lancement manuel (#63)`. Les deux commits prévus (correctif + tests, puis doc) n'en font qu'un : des fichiers de doc étaient déjà dans l'index au moment du premier `git add`, et ils ont été embarqués. Vérifier `git status` / `git diff --cached` avant de commiter.
- Commit de cette mémoire.
