## Prérequis système

### Sur la machine hôte

- **Visual Studio Code** [Télécharger et installer](https://code.visualstudio.com/) avec l'extension [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- **Docker Desktop** (ou équivalent)
- **`cruft`** dans un environnement Python accessible depuis le terminal hôte :

```bash
# avec pip
pip install cruft

# avec uv
uv pip install cruft

# avec mamba (environnement dédié)
mamba create -n pyfoundry python=3.11
mamba activate pyfoundry
mamba install -c conda-forge cruft
```

### Dossiers et fichiers montés par le Dev Container

Le conteneur monte des chemins de la machine hôte pour partager la configuration Git, SSH et le cache uv. **Ils doivent exister sur l'hôte avant le premier lancement**, sinon devcontainer refusera de démarrer.

| Chemin hôte    | Type    | Rôle                      |
| -------------- | ------- | ------------------------- |
| `~/.ssh`       | Dossier | Clés SSH pour Git         |
| `~/.gitconfig` | Fichier | Configuration Git globale |
| `~/.cache/uv ` | Dossier | Cache UV                  |


---

## Créer un nouveau projet

### Générer le projet

Depuis le terminal de la machine hôte, dans le dossier parent souhaité (par exemple `~/git`) :

```bash
cruft create https://github.com/castorfou/PyFoundry.git
```

L'assistant pose des questions pour personnaliser le projet :

| Option            | Description                                                     | Défaut                           |
| ----------------- | --------------------------------------------------------------- | -------------------------------- |
| `project_name`    | Nom lisible du projet                                           | "Mon Projet Data Science"        |
| `project_slug`    | Identifiant technique (minuscules, tirets)                      | Généré depuis `project_name`     |
| `description`     | Courte description                                              | "Description de votre projet..." |
| `python_version`  | Version Python du conteneur                                     | "3.11"                           |
| `github_username` | Votre nom d'utilisateur GitHub (pour configuration automatique) | "castorfou"                      |
| `use_node`        | Installer Node.js/npm pour des outils web                       | "n"                              |

### Ouvrir dans le Dev Container

```bash
code mon-projet-data-science
```

VS Code détecte `.devcontainer/` et propose **"Reopen in Container"** (ou `Ctrl+Shift+P` → `Dev Containers: Reopen in Container`).

Le premier build prend quelques minutes. Le script `postCreateCommand.sh` :

- crée l'environnement Python dans `/home/vscode/.venv` via `uv`
- installe toutes les dépendances du projet en les récupérant depuis `pyproject.toml`
- configure `pre-commit`, `zsh`, `glab`, Git
- initialise le dépôt Git local avec un premier commit

### Vérifier que tout fonctionne

Dans le terminal du conteneur :

```bash
uv run --active pytest
uv run --active mkdocs build
```

Les deux commandes doivent passer sans erreur.

### Integration github automatique

Le dépôt Git local est déjà initialisé par `postCreateCommand.sh`. Il reste à créer le dépôt distant sur GitHub et à pousser le code.

#### 1. S'authentifier

```bash
gh auth login
```

#### 2. Créer le dépôt distant

**Repo personnel** :

```bash
gh repo create mon-projet --public --source=. --remote=origin --push
```

#### 3. Pousser le code

`gh` configure le remote `origin` automatiquement. Vérifiez avec `git remote -v`, puis :

```bash
git push -u origin main
```

#### Pipeline CI/CD

Le projet inclut un repertoire `.github/workflows` pré-configuré. Dès le premier `git push`, GitHub déclenche un pipeline :

- 📚 Deploy Documentation : (docs.yml) — build MkDocs strict et déploiement automatique sur GitHub Pages à chaque push sur main touchant docs/ ou mkdocs.yml.
- 🚀 Release Automation : (release.yml) — déclenché sur un tag v*.*.* : réexécute les tests, génère des release notes automatiques depuis le git log, et publie une GitHub Release (stable ou pre-release selon le format du tag).
- 🧪 Test Template : (test-template.yml) — déclenché sur toutes les branches : lint ruff, pre-commit hooks, génération du projet via cruft et validation sur Python 3.11 et 3.12.

Le pipeline est visible sous **Actions** sur la page du projet GitHub.

---

## Lier un projet pré-existant au template

Un projet Python existe déjà mais n'a pas été créé avec ce template. Il est possible de le rattacher pour bénéficier du Dev Container, de la CI, et des mises à jour futures.

### Principe

Deux étapes : `cruft link` enregistre la liaison avec le template, puis `cruft update` génère le squelette par-dessus le projet existant. Un travail de merge manuel est ensuite nécessaire pour réconcilier les fichiers.

### Procédure

Travailler sur une branche dédiée. Le dépôt Git doit être propre (aucun fichier non commité).

```bash
git checkout -b chore/adopt-template
```

Il y a ensuite 3 étapes.

**1. Créer la liaison :**

```bash
cruft link https://github.com/castorfou/PyFoundry.git
```

Répondre aux questions (nom du projet, slug, options). Cela crée le fichier `.cruft.json` qui permet à `cruft update` de fonctionner par la suite.

**2. Modifier le fichier `.cruft.json` :**

Dans la 3e ligne, remplacer `  "commit": "<commit_ID>",` par `  "commit": "d85a7f28e5fa23ab9044148766da0044f77425bc",`

??? note "pourquoi `d85a7f28e5fa23ab9044148766da0044f77425bc` ?"
    Il faut indiquer à cruft que nous partons du tout premier commit de PyFoundry. Et qu'iul faut donc appliquer l'integralite des modifications du projet PyFoundry à notre projet cible. Et quel est le commit_ID de ce 1er commit ? `d85a7f28e5fa23ab9044148766da0044f77425bc`
    Pour trouver ce commit :
    ```bash
    git clone --bare https://github.com/castorfou/PyFoundry.git /tmp/pyfoundry && \n git -C /tmp/pyfoundry log --reverse --format="%H" | head -1\n
    ```

**3. Appliquer le squelette du template sur le projet :**

```bash
cruft update
```

### Après la génération

Un travail de merge s'impose :

- Inspecter les fichiers modifiés ou ajoutés avec `git diff` et `git status`.
- Conserver les fichiers métier existants, adopter les fichiers d'infrastructure du template (`.devcontainer/`, `.pre-commit-config.yaml`, `mkdocs.yml`…).
- Adapter `pyproject.toml` : garder les dépendances du projet, reprendre la configuration des outils (ruff, mypy, pytest) du template.
- Commiter le résultat et ouvrir une Merge Request pour revue.

Le projet peut ensuite recevoir les mises à jour du template via `cruft update` (voir [Mise à jour vers la dernière version du template](usage.md/#mise-a-jour-vers-la-derniere-version-du-template) dans le guide d'utilisation).
