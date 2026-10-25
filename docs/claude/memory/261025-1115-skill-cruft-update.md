# Issue #89 — skill `/cruft-update`

## Résumé

Skill Claude Code qui guide la **mise à jour du template** dans un projet généré : `cruft update`, lecture du CHANGELOG, résolution des **rejets** (`.rej` et marqueurs de conflit) selon le propriétaire de chaque fichier, migrations, vérifications, commit, puis accord avant push. Livrée dans le squelette et dans PyFoundry (qui la reçoit par son auto-mise à jour).

Parcours : `/ask-matt` → `/grill-with-docs` (22 décisions en 3 rounds) → [issue #89](https://github.com/castorfou/PyFoundry/issues/89) → `/fix-issue 89`. Plan d'implémentation en [commentaire de l'issue](https://github.com/castorfou/PyFoundry/issues/89#issuecomment-6395908538). Issue annexe ouverte pendant #86 : [#87](https://github.com/castorfou/PyFoundry/issues/87) (`uv sync --frozen`).

---

## Fichiers de la branche `89-skill-cruft-update`

### Skill (identique dans `.claude/skills/cruft-update/` et `{{ cookiecutter.project_slug }}/.claude/skills/cruft-update/`)

- `SKILL.md` : model-invoked (pas de `disable-model-invocation`), description qui déclenche sur « mettre à jour depuis le template » et sur des rejets présents. 8 étapes, chacune avec son critère de fin : reprendre ou démarrer (`rejets` non vide → reprise), dépôt propre, `cruft update -y`, CHANGELOG, résolution par catégorie, migrations, vérifications, commit puis accord avant push/PR.
- `AUTO-MISE-A-JOUR.md` : lu seulement si `{{ cookiecutter.project_slug }}/` existe (divulgation progressive). Verdicts : déjà appliqué, propre au projet généré, trou à combler.
- `scripts/template_update.py` : stdlib, `mypy --strict` propre, **seule source des catégories** (`CATEGORIES`, préfixes de dossiers ou fichiers exacts, du plus précis au plus général). Sous-commandes :
  - `categorie CHEMIN` → `template` | `mixte` | `projet` | `inconnu` (un `.rej` suit son fichier) ;
  - `rejets` → `catégorie<TAB>forme<TAB>chemin`, `forme` = `rej` (`rglob("*.rej")` hors `.git`) ou `conflit` (`git ls-files -u` ∪ `git grep` des marqueurs) ;
  - `changelog AVANT APRES [--template-path DIR]` → lignes ajoutées à `CHANGELOG.md` entre deux commits du template ; sans `--template-path`, clone `--filter=blob:none --no-checkout` de l'URL de `.cruft.json` dans un dossier temporaire.

### Autres

- `cookiecutter.json` : `.claude/skills/cruft-update/*` et `.claude/skills/cruft-update/scripts/*` dans `_copy_without_render`. Sans ça, Jinja remplace `{{ cookiecutter.project_slug }}` écrit dans la skill par le nom du projet.
- `CONTEXT.md` (nouveau, racine) : glossaire du domaine — template, squelette, projet généré, mise à jour du template, auto-mise à jour, rejet, fichier du template / du projet / mixte, verdict.
- `docs/adr/0003-proprietaire-des-fichiers-mise-a-jour.md` : règle de propriété (template l'emporte / local l'emporte / fusion, `uv.lock` régénéré), options écartées (tout demander, tout résoudre puis relire).
- `tests/test_cruft_update_skill.py` : 34 tests — égalité dépôt / projet généré (preuve de `_copy_without_render`), frontmatter, renvois de `SKILL.md`, `categorie` sur 21 chemins, `rejets` (dépôt propre, `.rej`, vrai conflit `git apply -3`), `changelog` (template local et clone via URL `file://`).

---

## Apprentissages clés

### Cruft produit deux formes de rejet

`cruft/_commands/update.py` : `git apply -3` d'abord ; s'il échoue sur un dépôt propre, « Retrying again with a different update strategy » et `git apply --reject`. Le test réel a donné ce second cas : `patch failed` puis un `postCreateCommand.sh.rej`. Ces messages effraient : `SKILL.md` précise maintenant qu'ils sont normaux.

### L'état git du début de conversation peut être périmé

Claude Code injecte un instantané de `git status` au début de la conversation. Pendant le test, Claude s'y est fié (dépôt « sale ») alors que l'utilisateur avait commité depuis, puis s'est corrigé. L'étape 2 exige maintenant de lancer `git status --porcelain`.

### Le HOME persistant garde les anciennes lignes

La fusion du rejet de `postCreateCommand.sh` (personnalisation `source /tmp/venv/bin/activate && echo venv actif` contre `setup_venv_activation` de #86) ne suffisait pas : `setup_venv_activation` ne retire que la ligne exacte du template, la ligne personnalisée restait dans `~/.zshrc` et aurait reproduit l'erreur de #86. L'étape 6 demande de signaler et de nettoyer ce que l'ancien `postCreateCommand.sh` a écrit dans le HOME.

### ruff ne formate que la copie du dépôt

Le squelette est exclu de ruff (`extend-exclude = ["[{][{]*"]`) : `ruff format` a modifié `template_update.py` à la racine seulement, et le test d'égalité a échoué. Recopier la version de la racine vers le squelette après chaque passage de ruff.

### Tester une skill d'un projet généré

- `cruft create … --checkout <ancien commit>` donne un projet à mettre à jour, mais enregistre `checkout` dans `.cruft.json` : le remettre à `null`, sinon `cruft update` reste sur ce commit.
- Une personnalisation volontaire d'une ligne touchée par le template provoque un vrai rejet.
- Depuis un devcontainer, `code <dossier>` n'ouvre pas de fenêtre : préparer le projet sur l'hôte puis « Reopen in Container ». Le CLI `claude` (binaire de l'extension) marche, mais l'utilisateur veut voir les fichiers pendant le test.
- Dans ce conteneur neuf, l'installation de l'extension Claude Code est restée bloquée (téléchargement suspendu, `Extension is already requested to install` dans `remoteagent.log`) ; le serveur VS Code y vit dans `/vscode/vscode-server/…` et `code` n'était pas dans le `PATH`. Un `pkill -f vscode-server` empêche la reconnexion : il faut « Reload Window ». À éviter.

---

## Vérification

- `pytest tests` : 281 passed, 1 skipped ; ruff, `mypy --strict` du script et pre-commit propres.
- Script lancé sur PyFoundry : `rejets` vide, `changelog` depuis `29e0478` correct.
- Test utilisateur bout en bout dans un projet généré depuis `4b76852` (GUI VS Code, devcontainer) : skill déclenchée par Claude, branche `chore/template-update-e010b85`, CHANGELOG résumé, rejet classé `template` et question posée, fusion protégée appliquée, `.zshrc` nettoyé, pre-commit et mkdocs verts, avertissement de rebuild, commit, question avant push.
