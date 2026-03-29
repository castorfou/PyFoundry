
Vous êtes probablement ici parce que quelque chose ne marche pas. Cherchez votre symptôme ci-dessous.

---

## Dev Container

### Le conteneur ne démarre pas : "bind mount failed"

```
Error: bind mount /home/user/.ssh failed: No such file or directory
```

Le Dev Container monte des dossiers de votre machine hôte (`~/.ssh`, `~/.gitconfig`). Si l'un n'existe pas, Docker refuse de démarrer.

```bash
# Sur votre machine hôte (pas dans le conteneur)
mkdir -p ~/.ssh
touch ~/.gitconfig
```

Puis relancez le conteneur.


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

**Cause probable** : vous avez oublié `--active`. Sans cette option, `uv` crée un venv éphémère au lieu d'utiliser `/home/vscode/.venv`.

```bash
# Vérifier quel venv est actif
echo $VIRTUAL_ENV
# Doit afficher : /home/vscode/.venv

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
