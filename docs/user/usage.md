# Guide d'utilisation

## Mise à jour vers la dernière version du template

Le template évolue (corrections, nouvelles fonctionnalités, nouvelles options). Le fichier `.cruft.json` à la racine du projet fait le lien avec le commit du template utilisé lors de la génération.

### Connaître la version du template

Le fichier `TEMPLATE_VERSION`, à la racine du projet, indique la version du template utilisée lors de la génération ou de la dernière mise à jour :

```bash
cat TEMPLATE_VERSION
```

`cruft update` le met à jour avec le reste du template : après la mise à jour, il porte la nouvelle version. Ne le modifiez pas à la main.

Un projet généré avant l'apparition de ce fichier le reçoit à sa prochaine mise à jour. En attendant, la même information est dans `.cruft.json` depuis PyFoundry 1.0.0 :

```bash
jq -r '.context.cookiecutter._pyfoundry_version' .cruft.json
```

Un résultat `null` signifie que le projet date d'avant la 1.0.0. Le champ `commit` de `.cruft.json` donne le commit exact du template, utile entre deux releases : un projet mis à jour depuis `main` porte la version de la dernière release.

Les nouveautés de chaque version, et les étapes de migration qu'elles demandent, sont dans le [changelog](../changelog.md). Avant une mise à jour, lisez les sections des versions entre la vôtre et la dernière, en particulier les rubriques **Migration**.

Pour viser une version précise plutôt que la dernière :

```bash
cruft update --checkout v1.0.0
```

### Vérifier si une mise à jour est disponible

```bash
cruft check
```
Pour voir le détail des changements sans rien appliquer :

```bash
cruft diff
```

### Appliquer la mise à jour

#### Avec Claude Code (recommandé)

Dans le projet, demandez à Claude Code : « mets à jour le projet depuis le template », ou tapez `/cruft-update`. La skill `cruft-update`, livrée avec le template dans `.claude/skills/cruft-update/` :

1. s'arrête si le dépôt contient du travail non commité ;
2. crée une branche `chore/template-update-<commit>` et lance `cruft update` vers la tête de `main` du template ;
3. résume les nouveautés du CHANGELOG et dresse la liste des migrations ;
4. résout les rejets selon le propriétaire de chaque fichier (voir [ADR 0003](../adr/0003-proprietaire-des-fichiers-mise-a-jour.md)) : la version du template l'emporte dans `.devcontainer/` ou `.github/workflows/`, la vôtre dans `src/` ou `notebooks/`, les deux sont fusionnées dans `pyproject.toml` ou `CLAUDE.md`. Elle vous demande dès qu'une personnalisation est en jeu ;
5. fait les migrations possibles dans le conteneur et vous décrit celles à faire sur l'hôte ;
6. lance pre-commit, pytest et `mkdocs build --strict`, et vous prévient si un rebuild du devcontainer est nécessaire ;
7. commite avec un tableau des décisions, puis vous demande avant de pousser.

Si une mise à jour lancée à la main a laissé des rejets, la skill reprend à partir de leur résolution.

La skill arrive dans le projet avec la mise à jour du template qui l'introduit : pour cette première fois, faites la mise à jour à la main.

#### À la main

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

Quand le template ajoute une nouvelle option (par exemple `docker_in_docker`), le projet existant n'a pas cette variable dans `.cruft.json`. Deux possibilités :

```bash
# Directement dans la commande
cruft update --variables-to-update '{ "docker_in_docker": "y" }'

# Ou : modifier .cruft.json manuellement, puis
cruft update --variables-to-update-file .cruft.json
```

### Passer au HOME persistant

Le template stocke désormais le HOME du conteneur (`/home/vscode`) sur l'hôte, dans `~/.devcontainer/homes/<projet>-<identifiant>`. Il survit aux rebuilds : historique du shell, `~/.gitconfig`. La connexion `gh` et la config Claude Code (connexion, conversations) sont stockées à part, dans `~/.config/gh-devcontainers` et `~/.config/claude-devcontainers` sur l'hôte, partagés par tous les devcontainers.

Cette section concerne les projets générés avant PyFoundry 1.0.0. Si `cruft diff` montre l'ajout de la ligne `target=/home/vscode` dans `.devcontainer/devcontainer.json`, votre projet est concerné.

Le **premier** rebuild après la mise à jour supprime l'ancien conteneur et démarre avec un HOME vide. Sans précaution, vous perdez l'historique Claude Code (conversations, mémoire, checkpoints), la connexion `gh` et l'historique du shell. Pour les conserver, sauvegardez le HOME de l'ancien conteneur **avant** le rebuild.

La copie automatique de l'historique Claude Code (voir [Passer à la config Claude Code partagée](#passer-a-la-config-claude-code-partagee)) ne vous aide pas ici : elle part du HOME persistant, que votre projet n'avait pas encore.

Toutes les commandes se lancent **sur l'hôte**, dans le **même terminal** : les variables définies à l'étape 1 servent jusqu'à la fin.

1. Placez-vous à la racine du projet et définissez les variables. `CONTAINER_ID` est retrouvé à partir du dossier du projet :



    ```bash
    # cd ~/chemin/vers/<projet>                 # racine du projet sur l'hôte
    export PROJET=$(basename "$PWD")
    export CONTAINER_ID=$(docker ps -aq --filter "label=devcontainer.local_folder=$PWD")
    export BACKUP=/tmp/$PROJET-home-backup
    echo "projet=$PROJET conteneur=$CONTAINER_ID"   # un seul identifiant attendu
    ```

    Si `CONTAINER_ID` est vide ou contient plusieurs identifiants, repérez le bon conteneur (colonne de droite : dossier du projet) et définissez-le à la main :

    ```bash
    docker ps -a --format '{{.ID}}  {{.Label "devcontainer.local_folder"}}'
    export CONTAINER_ID=<ID>
    ```

2. Repérez ce que vous voulez garder. La commande suivante liste les dossiers et fichiers du HOME modifiés depuis 30 jours, du plus récent au plus ancien, sur deux niveaux (`.config/gh`, `.claude/projects`…). Les points de montage (`.ssh`, `.cache/uv`…) sont exclus : ils sont déjà sur l'hôte. Le conteneur doit être démarré : sinon lancez d'abord `docker start "$CONTAINER_ID"`.

    ```bash
    docker exec "$CONTAINER_ID" sh -c '
        prune=$(awk "\$2 ~ \"^/home/vscode/\" { printf \"-path %s -prune -o \", \$2 }" /proc/self/mounts)
        find /home/vscode -mindepth 1 $prune -type f -mtime -30 -printf "%TY-%Tm-%Td %TH:%TM %P\n"
    ' | sort -r | awk '{ split($3, p, "/"); k = p[1]; if (p[2] != "" && p[3] != "") k = k "/" p[2]
                         if (!(k in vu)) { vu[k] = 1; print $1, $2, k } }'
    ```

    Changez `-mtime -30` pour remonter plus ou moins loin (en jours).

    Copiez ensuite dans `$BACKUP` uniquement ce que vous voulez garder. Ne copiez pas tout `/home/vscode` : `docker cp` copierait aussi le contenu des montages, dont le cache `uv` qui pèse plusieurs Go.

    ```bash
    for item in .claude .config/gh .zsh_history; do   # ajoutez vos propres dossiers
        mkdir -p "$BACKUP/$(dirname "$item")"
        docker cp "$CONTAINER_ID:/home/vscode/$item" "$BACKUP/$item" || echo "absent : $item"
    done
    ```

    `/tmp` est vidé au redémarrage de l'hôte : enchaînez les étapes suivantes sans redémarrer.

    Le reste du HOME est recréé au rebuild (`.oh-my-zsh`, `.vscode-server`, caches…) ou fourni par l'hôte (`.ssh`, `.gitconfig` copié par VS Code). Ne copiez pas `.zshrc` : il active l'ancien venv `/home/vscode/.venv`. Si vous y aviez ajouté des lignes personnelles (alias, exports), recopiez-les à la main.

3. Appliquez la mise à jour du template, comme décrit dans [Appliquer la mise à jour](#appliquer-la-mise-a-jour) : `cruft update`, résolution des éventuels fichiers `.rej`, puis commit.

    ```bash
    cruft update
    git add . && git commit -m "chore: update template (HOME persistant)"
    ```

4. Reconstruisez le conteneur (`Ctrl+Shift+P` → `Dev Containers: Rebuild Container`). Le dossier `~/.devcontainer/homes/$PROJET-<identifiant>` est créé sur l'hôte.

5. Recopiez la sauvegarde. `.claude` et `.config/gh` vont dans les dossiers partagés : dans le conteneur, ils sont montés par-dessus le HOME, qui ne les voit donc pas. `-n` n'écrase rien de ce qui s'y trouve déjà, en particulier une connexion faite depuis un autre projet. Le reste va dans le nouveau HOME.

    ```bash
    cp -an "$BACKUP/.claude/." ~/.config/claude-devcontainers/
    cp -an "$BACKUP/.config/gh/." ~/.config/gh-devcontainers/
    rm -rf "$BACKUP/.claude" "$BACKUP/.config/gh"   # copiés ci-dessus, inutiles dans le HOME
    export NEW_HOME=$(ls -d ~/.devcontainer/homes/"$PROJET"-*)
    echo "$NEW_HOME"                          # un seul dossier attendu
    cp -a "$BACKUP/." "$NEW_HOME/"
    ```

    Selon la version de `cp`, un fichier déjà présent dans un dossier partagé est signalé par `not replacing` : c'est attendu, il est simplement conservé.

6. Rechargez la fenêtre VS Code (`Ctrl+Shift+P` → `Developer: Reload Window`), puis vérifiez :

    - `gh auth status` : connecté ;
    - `/resume` dans Claude Code : vos conversations sont là. Si le panneau demande de vous connecter, faites-le : la connexion Claude Code n'est pas reprise de l'ancien conteneur, une seule connexion sert à tous les projets.

    Vous pouvez ensuite supprimer la sauvegarde : `rm -rf "$BACKUP"`.

!!! info "Le venv n'est plus dans le HOME"
    L'environnement Python passe de `/home/vscode/.venv` à `/tmp/venv`. Il n'est pas conservé : il est recréé à chaque rebuild par `postCreateCommand.sh`, et au démarrage du conteneur s'il manque. Il n'y a rien à migrer.


### Passer à la config Claude Code partagée

La connexion et la config Claude Code sont désormais partagées par tous les devcontainers : le dossier `~/.config/claude-devcontainers` de l'hôte est monté sur `~/.claude`. Vous vous connectez une fois pour tous les projets.

Cette section concerne les projets générés avant PyFoundry 1.0.0 qui ont déjà le HOME persistant. Si `cruft diff` montre l'ajout de `claude-devcontainers` dans `.devcontainer/devcontainer.json`, votre projet est concerné.

Il n'y a rien à sauvegarder :

1. Appliquez la mise à jour du template (`cruft update`, puis commit), comme décrit dans [Appliquer la mise à jour](#appliquer-la-mise-a-jour).
2. Reconstruisez le conteneur. Avant le démarrage, `.devcontainer/scripts/migrate_claude_history.sh` copie sur l'hôte l'historique du projet dans le dossier partagé : conversations, mémoire, checkpoints et historique des prompts. La copie n'écrase rien et n'a lieu qu'une fois par projet.
3. Connectez-vous dans le panneau Claude Code. La connexion n'est pas copiée : cette étape n'est à faire qu'une fois, pour le premier projet mis à jour.
4. Vérifiez avec `/resume` que vos conversations sont là.

L'ancienne config reste sur l'hôte, dans `~/.devcontainer/homes/<projet>-<identifiant>/.claude` et `.claude.json`. Le conteneur ne la voit plus. Une fois la migration vérifiée, vous pouvez la supprimer.

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

### Publier la doc d'une branche sur GitHub Pages

À chaque push sur `main`, la doc est publiée automatiquement. Pour publier celle d'une autre branche, par exemple pour relire un chantier en cours dans son rendu final, on lance le workflow à la main. Il faut d'abord l'autoriser, une seule fois par projet.

#### Autoriser les branches (une fois par projet)

Quand GitHub Pages utilise la source « GitHub Actions », GitHub crée l'environnement `github-pages`. Par défaut, cet environnement n'accepte que les déploiements depuis la branche par défaut. Ce réglage appartient au dépôt GitHub et ne figure dans aucun fichier du projet : il faut l'ouvrir aux autres branches.

=== "Interface GitHub"

    1. Sur la page du projet : **Settings → Environments → github-pages**.
    2. Dans **Deployment branches and tags**, cliquez sur **Add deployment branch or tag rule**.
    3. Gardez **Ref type : Branch**, saisissez le motif `*`, puis **Add rule**.

=== "CLI `gh`"

    ```bash
    # Autoriser toutes les branches à déployer sur GitHub Pages
    gh api -X POST "repos/{owner}/{repo}/environments/github-pages/deployment-branch-policies" -f name='*'

    # Vérifier : la liste doit contenir *
    gh api "repos/{owner}/{repo}/environments/github-pages/deployment-branch-policies" --jq '.branch_policies[].name'
    ```

    Copiez ces commandes telles quelles, sans remplacer `{owner}` ni `{repo}` : lancées depuis le dossier du projet, `gh` les remplace lui-même par le propriétaire et le nom du dépôt courant. Une réponse `Not Found (HTTP 404)` signale le plus souvent un propriétaire ou un nom de dépôt mal saisi.

!!! tip "Limiter les branches autorisées"
    Le motif `*` autorise toutes les branches. Pour n'en autoriser qu'une partie, utilisez un motif plus restreint, par exemple `docs/*`. Dans tous les cas, seules les personnes ayant les droits d'écriture sur le dépôt peuvent lancer le workflow.

#### Publier une branche

=== "Interface GitHub"

    **Actions → 📚 Deploy Documentation → Run workflow**, choisissez la branche dans **Use workflow from**, puis **Run workflow**.

=== "CLI `gh`"

    ```bash
    gh workflow run docs.yml --ref ma-branche
    gh run watch   # suivre l'exécution
    ```

La doc publiée est visible à l'adresse habituelle du projet, `https://<utilisateur>.github.io/<projet>`.

!!! warning "Une seule doc en ligne à la fois"
    GitHub Pages n'héberge qu'un site par dépôt : la doc de la branche remplace celle de `main`. Elle y reste jusqu'au prochain déploiement depuis `main`, automatique au prochain push touchant `docs/` ou `mkdocs.yml`, ou manuel :

    ```bash
    gh workflow run docs.yml --ref main
    ```

!!! note "Projets créés avant PyFoundry 1.0.0"
    Le déploiement depuis une branche demande la version à jour de `.github/workflows/docs.yml`. Récupérez-la avec `cruft update` (voir [Mise à jour vers la dernière version du template](#mise-a-jour-vers-la-derniere-version-du-template)).

---

## Environnement Python avec `uv`

Le projet utilise `uv` pour gérer les dépendances Python. L'environnement virtuel est dans `/tmp/venv` et est activé automatiquement dans chaque terminal. Il est recréé à chaque rebuild depuis `uv.lock`, et au démarrage du conteneur s'il manque : avec Docker-in-Docker, `/tmp` est vidé à chaque démarrage.

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
    Sans `--active`, `uv` crée un venv temporaire sous `.venv` dans le dossier du projet au lieu d'utiliser `/tmp/venv`. Les packages installés semblent disparaître au terminal suivant.

!!! info "`uv run` facultatif"
    Comme un `source /tmp/venv/bin/activate` est fait dans `~/.zshrc`, par défaut toutes les commandes s'entendent dans le contexte du venv actif.
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
| **no-venv-at-root**         | Bloque si un `.venv` existe (venv dans `/tmp/venv`) | Chaque `git commit` |

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

- 📚 Deploy Documentation : (docs.yml) — build MkDocs strict et déploiement automatique sur GitHub Pages à chaque push sur main touchant docs/ ou mkdocs.yml. Peut aussi être lancé à la main pour publier la doc d'une autre branche (voir [Publier la doc d'une branche sur GitHub Pages](#publier-la-doc-dune-branche-sur-github-pages)).
- 🔄 Continuous Integration : (ci.yml) — déclenché sur les push vers main et develop, et sur les pull requests vers main : lint ruff, tests pytest, mypy, pre-commit hooks et build du package, sur la version Python du projet et 3.12.

Le pipeline est visible sous **Actions** sur la page du projet GitHub.

### CLI GitHub (`gh`)

`gh` est installé dans le conteneur. Commandes utiles au quotidien :

```bash
# vérifier l'état de l'authentification
gh auth status

# le cas échéant, depuis un terminal VS Code (le navigateur de l'hôte s'ouvre)
gh auth login --web
```

L'authentification est stockée dans `~/.config/gh`, partagé par tous les devcontainers PyFoundry : une seule connexion suffit pour tous vos projets.

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

Le Dev Container tourne dans Docker. Avec l'option `docker_in_docker`, il est possible d'utiliser Docker à l'intérieur du conteneur (ex. : builder des images, lancer des conteneurs de test).

La feature `docker-in-docker:2` installe un daemon Docker interne et configure automatiquement un proxy socat vers le socket de l'hôte (`/var/run/docker-host.sock`). Aucune configuration manuelle de permissions n'est nécessaire.

---

## Autres fonctionnalités

### Notebooks Jupyter

Les extensions Jupyter sont installées dans VS Code. Les notebooks `.ipynb` s'ouvrent directement dans l'éditeur avec le kernel Python du venv `/tmp/venv`.

Le hook pre-commit `nbdev-clean` nettoie automatiquement les métadonnées et les outputs des notebooks avant chaque commit, pour garder des diffs lisibles.

### ZSH et Powerlevel10k

Le shell par défaut dans le conteneur est ZSH avec :

- Le thème Powerlevel10k (prompt riche avec branche Git, statut, etc.)
- Oh-my-zsh avec les plugins : `git`, `python`, `history`, `history-substring-search`, `zsh-autosuggestions`, `zsh-completions`
- Le venv Python est activé automatiquement à chaque ouverture de terminal

### Pre-commit

Les hooks pre-commit sont installés et pré-chargés par `postCreateCommand.sh`. Ils s'exécutent automatiquement à chaque `git commit`. Si un hook modifie un fichier (Ruff qui reformate, par exemple), il faut `git add` les modifications et recommiter.

À chaque rebuild, `postCreateCommand.sh` lance `pre-commit autoupdate`. Si des hooks ont une nouvelle version, il commite **uniquement** `.pre-commit-config.yaml` (« chore: update pre-commit hooks to latest versions »). Votre travail en cours, indexé ou non, n'est jamais commité : vous pouvez faire un rebuild en pleine séance de travail. Si ce commit échoue, la config mise à jour reste simplement non commitée.

Un projet tout juste généré passe `pre-commit run --all-files` sans aucune modification.

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

| Option             | Description                                                      | Défaut |
| ------------------ | ---------------------------------------------------------------- | ------ |
| `use_node`         | Installer Node.js/npm (extensions VS Code, outils web)           | `"n"`  |
| `docker_in_docker` | Activer Docker dans le Dev Container (accès au daemon de l'hôte) | `"n"`  |

### `docker_in_docker`

Active la feature `docker-in-docker:2` et monte le socket Docker de l'hôte vers `/var/run/docker-host.sock`. Un proxy socat est configuré automatiquement par la feature — aucune configuration manuelle de permissions n'est nécessaire.

```bash
# Créer un projet avec Docker-in-Docker activé
cruft create https://github.com/castorfou/PyFoundry.git --extra-context '{"docker_in_docker": "y"}'
```

### `use_node`

Installe Node.js LTS et npm dans le Dev Container. Génère aussi un `package.json` basique.

```bash
# Créer un projet avec Node.js activé
cruft create https://github.com/castorfou/PyFoundry.git --extra-context '{"use_node": "y"}'
```
