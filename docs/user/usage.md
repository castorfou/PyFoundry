# Guide d'utilisation

## Mise à jour vers la dernière version du template

Le template évolue (corrections, nouvelles fonctionnalités, nouvelles options). Le fichier `.cruft.json` à la racine du projet fait le lien avec le commit du template utilisé lors de la génération.

### Vérifier si une mise à jour est disponible

```bash
cruft check
```
Pour voir le détail des changements sans rien appliquer :

```bash
cruft diff
```

### Appliquer la mise à jour

Partir d'un dépôt Git propre (aucun fichier non commité), de préférence sur une branche dédiée :

```bash
git checkout -b chore/template-update
cruft update
```

L'assistant propose de voir les changements (`v`) ou d'accepter (`y`). Cruft applique les modifications sur les fichiers du projet.

Si les mêmes lignes ont été modifiées dans le projet et dans le template, Cruft ne peut pas fusionner automatiquement. Il crée des fichiers `.rej` (rejets). Il faut alors :

1. Ouvrir chaque fichier `.rej` pour voir ce que le template voulait changer.
2. Appliquer manuellement les modifications souhaitées dans le fichier concerné.
3. Supprimer les fichiers `.rej`.
4. Vérifier que les tests passent et que la doc se construit.
5. Commiter et créer une Merge Request.

### Activer une option ajoutée après la création du projet

Quand le template ajoute une option (par exemple `install_claude_code`), le projet existant n'a pas cette variable dans `.cruft.json`. Deux possibilités :

```bash
# Directement dans la commande
cruft update --variables-to-update '{ "install_claude_code": "yes" }'

# Ou : modifier .cruft.json manuellement, puis
cruft update --variables-to-update-file .cruft.json
```

---

## MkDocs : documentation du projet

Le projet inclut MkDocs Material, configuré et prêt à écrire. Les fichiers Markdown vivent dans `docs/`.

### Prévisualiser en local

```bash
mkdocs serve
```

La documentation est accessible dans le navigateur à l'adresse affichée (par défaut `http://127.0.0.1:8000`). Les modifications sont rechargées automatiquement.

```bash
# Sur un autre port si le 8000 est occupé
mkdocs serve -a localhost:8010
```

### Construire pour vérifier

```bash
mkdocs build --strict
```

Le mode `--strict` fait échouer le build sur les warnings (liens cassés, fichiers manquants dans la navigation). C'est ce que la CI utilise.

### Ajouter une page

1. Créer un fichier `.md` dans le bon sous-dossier de `docs/` (par exemple `docs/user/ma-page.md`).
2. L'ajouter dans le fichier `.nav.yml` du sous-dossier correspondant.

### Liens entre pages

MkDocs utilise les chemins URL (pas les chemins de fichiers). La syntaxe Markdown classique fonctionne :

```markdown
<!-- Lien vers une page (chemin URL absolu) -->
[Texte du lien](/user/usage/)

<!-- Lien vers une section précise (ancre) -->
[Texte du lien](/user/usage/#ajouter-une-page)

<!-- Lien vers une section de la même page -->
[Texte du lien](#fonctionnalités-disponibles)
```

ou alors une convention plus classique basée sur les fichiers

```markdown
<!-- Lien vers un fichier markdown (chemin URL relatif) -->
[Texte du lien](troubleshooting.md/#dev-container)
```

Cette convention est préférable car elle ne crée pas de warning absolute link lors de `mkdocs build`


!!! note "Génération automatique des ancres"
    Les ancres sont générées automatiquement depuis les titres : en minuscules, espaces remplacés par des tirets, accents supprimés. Par exemple `## Créer un nouveau projet` devient `#creer-un-nouveau-projet`.

!!! tip "Vérifier les liens"
    `mkdocs build --strict` détecte les liens cassés. Lancez-le avant de pousser.

### Fonctionnalités disponibles

La configuration MkDocs du projet active :

- **Admonitions** : blocs `!!! tip`, `!!! warning`, `!!! info` etc.
- **Onglets** : contenu tabulé avec `=== "Onglet 1"`
- **Diagrammes Mermaid** : dans des blocs ` ```mermaid `
- **Latex** : formules en ligne `$x^2$` ou en bloc `$$\sum_{i=1}^n$$`
- **Annotations de code** : annotations numérotées dans les blocs de code `# (1)`
- **Copie de code** : bouton de copie sur les blocs de code
- **Mode clair / sombre** : bascule dans le header
- **Dates Git** : chaque page affiche la date de dernière modification (depuis l'historique Git)

---

## Environnement Python avec `uv`

Le projet utilise `uv` pour gérer les dépendances Python. L'environnement virtuel est dans `/home/vscode/.venv` et est activé automatiquement dans chaque terminal.

### Ajouter un package

```bash
# Dépendance principale
uv add --active pandas

# Dépendance de développement
uv add --active --dev hypothesis
```

### Synchroniser après un `git pull`

```bash
uv sync --active --all-extras
```

Cela installe exactement les versions du `uv.lock` commité.

### Lancer une commande dans l'environnement

```bash
uv run --active pytest
uv run --active python mon_script.py
```

!!! warning "Toujours `--active`"
    Sans `--active`, `uv` crée un venv temporaire sous `.venv` dans le dossier du projet au lieu d'utiliser `/home/vscode/.venv`. Les packages installés semblent disparaître au terminal suivant.

!!! info "`uv run` facultatif"
    Comme un `source /home/vscode/.venv/bin/activate` est fait dans `~/.zshrc`, par défaut toutes les commandes s'entendent dans le contexte du venv actif.
    Donc `uv run --active pytest` et `pytest` sont complétement équivalents.

### Outils de qualité de code

Quelques outils sont configurés dans `pyproject.toml` ou `.pre-commit-config.yaml` et s'exécutent automatiquement via les hooks pre-commit :

| Outil                       | Rôle                                             | Déclenchement       |
| --------------------------- | ------------------------------------------------ | ------------------- |
| **Ruff**                    | Lint + formatage (remplace flake8, isort, black) | Chaque `git commit` |
| **MyPy**                    | Vérification de types                            | Chaque `git commit` |
| **nbdev-clean**             | Nettoyage des notebooks (métadonnées, outputs)   | Chaque `git commit` |
| **detect-secrets**          | Détection de secrets dans le code                | Chaque `git commit` |
| **check-added-large-files** | Bloque les fichiers volumineux dans les commits  | Chaque `git commit` |

Pour lancer manuellement :

```bash
# Tous les hooks sur tous les fichiers
pre-commit run --all-files

# Ruff seul
ruff check .
ruff format .
```

Les règles Ruff sont adaptées pour la datascience :
le nom de variable `df` est autorisé, les imports dans les notebooks sont souples, les `assert` dans les tests sont acceptés.

---

## Installer des applications dans le Dev Container

Le conteneur est basé sur Debian. L'utilisateur `vscode` a les droits `sudo`.

```bash
# Installer un paquet système
sudo apt-get update && sudo apt-get install -y <nom-du-paquet>
```

L'installation est **éphémère** : elle disparaît si le conteneur est reconstruit. Pour rendre un paquet permanent :

- L'ajouter dans `.devcontainer/postCreateCommand.sh` (pour les outils installés via script).

Puis reconstruire le conteneur (`Ctrl+Shift+P` → `Dev Containers: Rebuild Container`).

---

## GitHub : CI/CD et CLI

### Pipeline CI/CD

Le projet inclut un repertoire `.github/workflows` pré-configuré. Dès le premier `git push`, GitHub déclenche un pipeline :

- 📚 Deploy Documentation : (docs.yml) — build MkDocs strict et déploiement automatique sur GitHub Pages à chaque push sur main touchant docs/ ou mkdocs.yml.
- 🚀 Release Automation : (release.yml) — déclenché sur un tag v*.*.* : réexécute les tests, génère des release notes automatiques depuis le git log, et publie une GitHub Release (stable ou pre-release selon le format du tag).
- 🧪 Test Template : (test-template.yml) — déclenché sur toutes les branches : lint ruff, pre-commit hooks, génération du projet via cruft et validation sur Python 3.11 et 3.12.

Le pipeline est visible sous **Actions** sur la page du projet GitHub.

### CLI GitLab (`gh`)

`gh` est installé dans le conteneur. Commandes utiles au quotidien :

```bash
# vérifier l'état de l'authentification
gh auth status

# le cas échéant
gh auth login
```

Et quand l'authentification est active :

```bash
# Visualiser une issue
gh issue view <numéro> --comments

# Créer une Pull Request
git push --set-upstream origin ma-branche
gh pr create --fill

# Voir les runs CI/CD au format json
gh run list --json status,name,databaseId,conclusion

# Voir le détail d'une PR
gh pr view <numéro>
```

!!! tip "Éviter les pagers interactifs"
    gh ouvre par défaut un pager interactif. Préfixer avec GH_PAGER=cat ou utiliser --json pour un output brut. Surtout utile pour nos assistants IA qui ne comprennent pas tout.

---

## 🤖 Support Claude Code

PyFoundry intègre le support natif de Claude Code, l'assistant IA d'Anthropic pour le développement.

### Extension VS Code installée

L'extension **Claude Code** (`anthropic.claude-code`) est automatiquement installée dans votre devcontainer, prête à l'emploi.

### Fichiers Claude Code générés

Chaque projet créé inclut :

- **`CLAUDE.md`** : Documentation projet pour Claude Code
  - Description du projet et objectifs
  - Stack technique détaillée
  - Structure du projet
  - Conventions de code
  - Commandes utiles

- **`.claude/commands/`** : Commandes slash pré-configurées
  - `/fix-issue` : Workflow complet pour résoudre une issue GitHub (TDD, tests, doc, CI/CD)
  - `/stocke-memoire` : Sauvegarde des apprentissages dans docs/claude/memory/

### Utilisation avec Claude Code

```bash
# Ouvrir le projet dans VS Code avec Claude Code
code mon-projet-data-science

# Claude Code lit automatiquement CLAUDE.md pour comprendre :
# - L'architecture du projet
# - Les outils et dépendances utilisés
# - Les conventions de code à respecter
# - Les commandes disponibles
```

### Personnalisation CLAUDE.md

Le fichier `CLAUDE.md` est généré avec vos paramètres de projet. Vous pouvez l'enrichir avec :

- Instructions spécifiques à votre domaine
- Règles métier importantes
- Patterns de code à suivre
- Documentation d'APIs utilisées

### Commandes slash incluses

#### `/fix-issue {numéro}`
Workflow TDD complet pour résoudre une issue GitHub :
1. Récupère les détails de l'issue
2. Crée une branche depuis l'issue
3. Implémente en TDD (tests RED puis code)
4. Vérifie qualité (tests, lint, typecheck)
5. Met à jour la documentation
6. Commit et push
7. Vérifie la CI/CD
8. Crée la pull request

#### `/stocke-memoire`
Sauvegarde tes apprentissages et décisions importantes dans `docs/claude/memory/` avec horodatage.

### Création de commandes personnalisées

Créez des fichiers `.md` dans `.claude/commands/` :

```markdown
# Exemple : .claude/commands/test.md
Lance la suite de tests complète avec coverage :
\`\`\`bash
pytest --cov=src --cov-report=html
\`\`\`
```

Puis utilisez `/test` dans Claude Code pour exécuter cette commande.



## Docker

Le Dev Container tourne dans Docker.

Pas encore d'integration docker-in-docker

https://github.com/castorfou/PyFoundry/issues/44

---

## Autres fonctionnalités

### Notebooks Jupyter

Les extensions Jupyter sont installées dans VS Code. Les notebooks `.ipynb` s'ouvrent directement dans l'éditeur avec le kernel Python du venv `/home/vscode/.venv`.

Le hook pre-commit `nbdev-clean` nettoie automatiquement les métadonnées et les outputs des notebooks avant chaque commit, pour garder des diffs lisibles.

### ZSH et Powerlevel10k

Le shell par défaut dans le conteneur est ZSH avec :

- Le thème Powerlevel10k (prompt riche avec branche Git, statut, etc.)
- Oh-my-zsh avec les plugins : `git`, `python`, `history`, `history-substring-search`, `zsh-autosuggestions`, `zsh-completions`
- Le venv Python est activé automatiquement à chaque ouverture de terminal

### Pre-commit

Les hooks pre-commit sont installés et pré-chargés par `postCreateCommand.sh`. Ils s'exécutent automatiquement à chaque `git commit`. Si un hook modifie un fichier (Ruff qui reformate, par exemple), il faut `git add` les modifications et recommiter.

```bash
# Mettre à jour les hooks vers les dernières versions
pre-commit autoupdate

# Forcer un passage sur tous les fichiers
pre-commit run --all-files
```

### repo_url MkDocs

Le script `scripts/update_mkdocs_repo_url.sh` met à jour automatiquement le champ `repo_url` dans `mkdocs.yml` à partir de l'URL du remote `origin`. Il s'exécute au démarrage du Dev Container. Pour le relancer manuellement (après avoir changé de remote par exemple) :

```bash
./scripts/update_mkdocs_repo_url.sh
```

---

## Options du template

Options choisies à la création du projet (`cruft create`). Elles modifient la configuration du Dev Container.
