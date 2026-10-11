
Vous êtes probablement ici parce que quelque chose ne marche pas. Cherchez votre symptôme ci-dessous.

---

## Dev Container

### Le conteneur ne démarre pas : "bind mount failed"

```
Error: bind mount /home/user/.ssh failed: No such file or directory
```

Le Dev Container monte des dossiers de votre machine hôte (HOME persistant, `~/.ssh`, caches). Si l'un n'existe pas, Docker refuse de démarrer.

Normalement `initializeCommand` les crée avant le démarrage, puis `check_mounts.sh` vérifie chaque montage. Lisez la sortie du build : chaque montage en erreur est signalé par `[FAIL]` avec la commande à lancer (`mkdir -p`, `touch`, `chmod`).

Pour relancer la vérification à la main :

```bash
# Sur votre machine hôte (pas dans le conteneur), à la racine du projet
bash .devcontainer/scripts/check_mounts.sh --host
```

Corrigez les `[FAIL]` signalés, puis relancez le conteneur.

### Le conteneur refuse de démarrer : permissions de `~/.ssh`

`check_mounts.sh` applique les mêmes règles que `ssh` : le dossier `~/.ssh` et `~/.ssh/config` ne doivent pas être modifiables par le groupe ou les autres, et les clés privées ne doivent être lisibles que par vous. Le message `[FAIL]` donne la commande `chmod` exacte pour chaque fichier fautif, par exemple :

```bash
# Sur votre machine hôte
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
```

Les clés publiques (`*.pub`) et `known_hosts` ne sont pas contrôlées.

### `gh` n'est pas authentifié, ou le navigateur ne s'ouvre pas

Le build ne lance pas `gh auth login` : la connexion est proposée à l'ouverture du premier terminal zsh, une seule fois par conteneur. Si vous l'avez interrompue, ou si Claude Code signale que `gh` n'est pas connecté juste après le premier build, ouvrez un terminal VS Code et lancez :

```bash
gh auth login --web
```

- **Le navigateur ne s'ouvre pas** (`Failed opening a web browser … xdg-open`) : la commande a été lancée hors d'un terminal VS Code, par exemple par un script de build ou par l'outil Bash de Claude Code. Seuls les terminaux VS Code reçoivent la variable `BROWSER`, qui ouvre l'URL dans le navigateur de l'hôte. À défaut, ouvrez `https://github.com/login/device` à la main.
- **`Failed to copy one-time code to clipboard`** : c'est sans conséquence, collez le code affiché à la main. Installer `xclip`, `xsel` ou `wl-clipboard` ne servirait à rien, car le conteneur n'a pas d'affichage graphique.

L'authentification est partagée par tous les devcontainers PyFoundry (`~/.config/gh-devcontainers` sur l'hôte). Pour repartir de zéro, lancez `gh auth logout` dans un conteneur, ou supprimez ce dossier sur l'hôte.

### Claude Code redemande la connexion

La connexion Claude Code est partagée par tous les devcontainers PyFoundry (`~/.config/claude-devcontainers` sur l'hôte, monté sur `~/.claude`). Si le panneau redemande la connexion dans chaque projet, le projet n'a pas encore ce montage : mettez à jour le template (voir [Passer à la config Claude Code partagée](usage.md#passer-a-la-config-claude-code-partagee)).

Pour repartir de zéro, lancez `/logout` dans Claude Code, ou supprimez `~/.config/claude-devcontainers/.credentials.json` sur l'hôte. Supprimer tout le dossier efface aussi les conversations et la mémoire de tous les projets.

### Repartir d'un HOME vierge

Le HOME du conteneur est conservé sur l'hôte, dans `~/.devcontainer/homes/<projet>-<identifiant>`. Si une configuration y est cassée (shell, extension VS Code), supprimez ce dossier puis reconstruisez le conteneur :

```bash
# Sur votre machine hôte, conteneur arrêté
rm -rf ~/.devcontainer/homes/<projet>-*
```

Vous perdez alors l'historique du shell. La connexion et les conversations Claude Code, comme la connexion `gh`, sont conservées : elles sont stockées hors de ce dossier.

Ce dossier n'est pas supprimé avec le projet : pensez à le retirer quand vous supprimez un projet.

### pre-commit échoue : `InvalidManifestError`

```
An error has occurred: InvalidManifestError:
==> File /home/vscode/.cache/pre-commit/repo.../.pre-commit-hooks.yaml
```

Le cache pre-commit est partagé entre tous vos devcontainers. Un clone interrompu (build coupé, réseau instable) peut y rester à moitié écrit. Videz le cache, puis réinstallez les hooks :

```bash
pre-commit clean
pre-commit install-hooks
```


### Le build échoue sur les features (ghcr.io)

```
failed to fetch image ghcr.io/va-h/devcontainers-features/uv:1
```

Le Dev Container utilise des features hébergées sur `ghcr.io` (GitHub Container Registry). Si le réseau bloque `ghcr.io` ou que la connexion est instable, le build échoue. Vérifiez votre accès Internet et relancez le build.

### Le conteneur se construit mais tout est lent

Premier build : c'est normal. Docker télécharge l'image de base, installe les features, exécute `postCreateCommand.sh` (dépendances Python, hooks pre-commit). Comptez 5 à 15 minutes selon la connexion.

Les builds suivants utilisent le cache et prennent moins d'une minute.

Si c'est lent à chaque fois : vérifiez que Docker a assez de ressources (4 Go de RAM minimum, 4 CPUs recommandé).

---

## Python et `uv`

### Package introuvable après installation

Vous avez installé un package mais Python ne le trouve pas :

```
ModuleNotFoundError: No module named 'pandas'
```

**Cause probable** : vous avez oublié `--active`. Sans cette option, `uv` crée un venv éphémère au lieu d'utiliser `/tmp/venv`.

```bash
# Vérifier quel venv est actif
echo $VIRTUAL_ENV
# Doit afficher : /tmp/venv

# Réinstaller proprement
uv sync --active --all-extras
```

### Conflit de versions / lockfile cassé

```
requirement spec 'package==X.Y.Z' cannot be satisfied
```

```bash
# Regénérer le lockfile depuis les contraintes de pyproject.toml
uv lock --upgrade
uv sync --active --all-extras
```

### `uv` introuvable

Le Dev Container installe `uv` via la feature `ghcr.io/va-h/devcontainers-features/uv`. Si `uv` n'est pas disponible :

1. Vérifiez votre connexion à `ghcr.io`
2. Reconstruisez le conteneur (`Dev Containers: Rebuild Container`)

En dépannage immédiat :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.cargo/env
```

### Les imports échouent dans les tests

```
ModuleNotFoundError: No module named 'utils'
```

Le `pyproject.toml` configure `pythonpath = "."` pour pytest. Les imports dans les tests se font **sans** le préfixe `src/` :

```python
# ✅ Correct
from utils.mon_module import ma_fonction

# ❌ Incorrect
from src.utils.mon_module import ma_fonction
```

Voir [Conventions — Imports Python](conventions.md#python-et-imports).

---

## Pre-commit

### Un hook échoue et bloque le commit

C'est le comportement normal. Lisez le message d'erreur :

- **Ruff** : il a probablement déjà corrigé le fichier. Faites `git add` sur les fichiers modifiés et recommitez.
- **MyPy** : erreur de type dans votre code. Corrigez l'erreur indiquée, puis recommitez.
- **detect-secrets** : un secret potentiel a été détecté. Si c'est un faux positif, mettez à jour le fichier `.secrets.baseline`. Si c'est un vrai secret, retirez-le du code.
- **check-added-large-files** : un fichier dépasse la taille autorisée. Retirez-le du staging (`git reset HEAD <fichier>`) ou ajoutez-le dans `.gitignore`.

```bash
# Voir tous les problèmes d'un coup
pre-commit run --all-files
```

### Les hooks sont très lents la première fois

Normal. pre-commit télécharge et installe les environnements de chaque hook au premier lancement. Le `postCreateCommand.sh` fait un `pre-commit install-hooks` pour pré-charger le tout, mais ça prend quand même 2 à 5 minutes.

Les exécutions suivantes sont quasi-instantanées.

### MyPy se plaint de librairies externes

```
error: Skipping analyzing "matplotlib": module is installed, but missing library stubs
```

Le `pyproject.toml` ignore déjà les librairies Data Science courantes (`matplotlib`, `seaborn`, `sklearn`, `scipy`, `plotly`). Si vous utilisez une autre librairie sans stubs, ajoutez-la dans la section `[[tool.mypy.overrides]]` du `pyproject.toml` :

```toml
[[tool.mypy.overrides]]
module = "ma_librairie.*"
ignore_missing_imports = true
```


### 1. Mypy "found twice" - Détection En Double des Modules

**Symptôme**: Mypy rapportait le même module trouvé à deux chemins différents:
```
app/dashboard.py:1: error: Source file "app/dashboard.py" found twice under different module names ("app.dashboard" and "src.app.dashboard")
```

**Root Cause**:
- `uv sync --active` ajoute automatiquement `/src` au `PYTHONPATH` via editable install
- Mypy scannait AUSSI les fichiers directement (via args: [scripts, tests, app])
- Résultat: Chaque module détecté depuis deux chemins

**Solution** ✅:
```toml
# pyproject.toml - [tool.mypy]
files = ["scripts", "tests", "app"]  # Exclure src/ car déjà dans PYTHONPATH
namespace_packages = false            # Éviter la détection duplicate
```

**Clé**: Laisser PYTHONPATH gérer `src/` et scanner uniquement les dossiers "application".

---

### 2. Cycle Infini Ruff-Mypy

**Symptôme**: Pre-commit échouait après chaque commit avec des erreurs "unused-ignore":
```
tests/unit/test_reporter.py:48: error: Unused "type: ignore" comment [unused-ignore]
```

**Pourquoi ça se produisait**:

```python
# Ligne trop longue (88+ chars):
some_function(arg1, arg2)  # type: ignore[specific-error]
```

**Ruff reformatait à**:
```python
# type: ignore[specific-error]  ← Ligne précédente!
some_function(arg1, arg2)
```

**Mypy voyait le commentaire sur la mauvaise ligne** → erreur "unused-ignore"

Commit suivant: on remet sur la même ligne → Ruff reformate à nouveau → cycle infini 🔄

**Solution** ✅:
```yaml
# .pre-commit-config.yaml - Hook mypy
- id: mypy
  args: [--config-file=pyproject.toml, --no-warn-unused-ignores, scripts, tests, app]
```

**Philosophie**: Accepter que Ruff gagne la "bataille de formatage". Il a raison:
- Limite de 88 chars = convention Python
- Ruff place le commentaire de manière lisible (ligne précédente)
- Mypy reconnaît désormais que c'est normal → `--no-warn-unused-ignores`

---

### 3. Pandas-stubs Manquant dans Pre-commit

**Symptôme**: Hook mypy échouait avec:
```
app/dashboard.py:7: error: Library stubs not installed for "pandas" [import-untyped]
```

**Root Cause**:
- pandas-stubs était installé dans l'environnement local (`uv add --active pandas-stubs`)
- Mais le hook pre-commit crée un **environment isolé** sans dépendances supplémentaires
- Mypy dans ce nouvel environment ne trouvait pas les stubs

**Solution** ✅:
```yaml
# .pre-commit-config.yaml - Hook mypy
additional_dependencies: ["pandas-stubs"]
```

**Clé**: Les `additional_dependencies` dans pre-commit sont installées dans le virtualenv temporaire du hook.

---

### 4. Annotations de Type Manquantes

**Symptôme**: Après correction du cycle ruff-mypy, mypy détectait des **vraies** erreurs:
```
tests/unit/test_reporter.py:49: error: Function is missing a type annotation for one or more arguments [no-untyped-def]
def test_create_report_for_success(successful_solver_result, tmp_path: Path) -> None:
```

**Root Cause**: Erreurs réelles de typage, pas des faux positifs

**Solution** ✅:
```python
# Avant
def test_create_report_for_success(successful_solver_result, tmp_path: Path) -> None:

# Après
def test_create_report_for_success(successful_solver_result: dict, tmp_path: Path) -> None:
```

**Important**: Ces erreurs devaient être CORRIGÉES, pas ignorées avec `# type: ignore`.


---

## MkDocs

### `mkdocs build --strict` échoue

Le mode `--strict` transforme les warnings en erreurs. C'est le mode utilisé par la CI. Les causes fréquentes :

- **Fichier référencé dans `.nav.yml` mais absent** : vérifiez que chaque fichier listé dans la navigation existe dans `docs/`.
- **Lien interne cassé** : un `[texte](chemin.md)` pointe vers un fichier qui n'existe pas ou a été renommé.
- **Include manquant** : une directive `include` Jinja pointe vers un fichier absent.

```bash
# Tester en local avant de pousser
mkdocs build --strict
```

### `repo_url` absent ou faux

Le script `scripts/update_mkdocs_repo_url.sh` s'exécute au démarrage du conteneur. Si le remote `origin` n'existait pas encore à ce moment-là, le champ `repo_url` est absent de `mkdocs.yml`.

```bash
# Une fois origin configuré
./scripts/update_mkdocs_repo_url.sh
```

### Le serveur local ne détecte pas les changements

`mkdocs serve` recharge automatiquement sur modification d'un `.md`. Si ça ne fonctionne pas :

- Vérifiez que le fichier modifié est bien sous `docs/`
- Arrêtez et relancez `mkdocs serve`
- Sur certaines configurations Docker, le polling de fichier peut être lent (délai de 2-3 secondes normal)

---

## `cruft update`

### "SHA ... could not be resolved"

Le SHA dans `.cruft.json` pointe vers un commit qui n'existe plus dans le dépôt du template — typiquement après un squash merge ou un rebase.

**Solution** : éditez `.cruft.json` et remplacez le SHA par un commit existant sur `main` du dépôt du template.

### `cruft update` crée des fichiers `.rej`

Cruft n'a pas réussi à merger automatiquement certains fichiers (ils ont trop divergé entre votre projet et le template).

1. Ouvrez chaque fichier `.rej` pour voir ce que le template voulait changer.
2. Appliquez manuellement les modifications souhaitées dans le fichier concerné.
3. Supprimez les fichiers `.rej`.
4. Vérifiez que les tests passent (`pytest`) et que la doc se construit (`mkdocs build --strict`).
5. Commitez.

### `cruft check` trouve des différences inattendues

`cruft check` compare votre projet au template. Des différences sont normales si vous avez personnalisé votre projet (ajouté des dépendances, modifié des fichiers). Utilisez `cruft diff` pour voir le détail et vérifier qu'il n'y a rien d'anormal.

---

## Rien de tout ça ne correspond

1. Reconstruisez le conteneur : `Ctrl+Shift+P` → `Dev Containers: Rebuild Container`
2. Si ça ne résout pas : ouvrez une [issue](https://github.com/castorfou/PyFoundry/issues) sur le dépôt du template avec le message d'erreur **complet**.
