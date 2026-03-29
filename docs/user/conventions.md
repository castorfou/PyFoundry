Ce template impose quelques conventions. Elles ne sont pas arbitraires : elles garantissent que les outils automatiques (lint, tests, doc, CI) fonctionnent sans configuration supplémentaire.

---

## Structure du projet

```
mon-projet/
├── src/                  # Votre code Python
├── tests/                # Vos tests (pytest)
├── docs/
│   ├── user/             # Doc pour les utilisateurs de votre projet
│   └── dev/              # Doc pour les développeurs de votre projet
├── scripts/              # Scripts utilitaires
├── notebooks/            # Notebooks Jupyter
├── data/                 # Données (ignorées par les linters)
├── models/               # Modèles ML (ignorés par les linters)
├── .devcontainer/        # Configuration Dev Container
├── mkdocs.yml            # Configuration de la documentation
└── pyproject.toml        # Configuration Python et outils
```

Respectez cette structure. Les outils (Ruff, MyPy, pytest, MkDocs) sont configurés pour la chercher.

---

## Python et imports

L'environnement Python est dans `/home/vscode/.venv`. Il est activé automatiquement dans chaque terminal.

Les imports partent de la racine du projet (grâce à `pythonpath = "."` dans `pyproject.toml`) :

```python
# ✅ Correct
from src.mon_module import ma_fonction

# ❌ Ne faites pas ça dans les tests
import sys; sys.path.insert(0, ...)
```

---

## Tests

- Les tests vont dans `tests/`.
- Nommez les fichiers `test_*.py` et les fonctions `test_*`.
- `assert` est autorisé (Ruff le tolère dans `tests/`).
- Les magic numbers sont tolérés dans les tests.

```bash
uv run --active pytest
```

---

## Qualité de code

### Ruff

Ruff remplace flake8, isort et black. Il est configuré dans `pyproject.toml`.

Règles adaptées Data Science :

- `E501` ignoré (les lignes longues sont tolérées)
- `PD901` ignoré (le nom `df` est OK en Data Science)
- Dans les notebooks : imports en désordre et variables inutilisées sont tolérés

### MyPy

Vérification de types en mode non-strict. Les modules Data Science courants (`matplotlib`, `seaborn`, `sklearn`, `scipy`, `plotly`) sont ignorés car souvent mal typés.

### Pre-commit

Tous les hooks tournent automatiquement avant chaque commit. **Ne contournez pas les hooks** avec `--no-verify`. Si un hook bloque, c'est qu'il y a un problème à corriger.

---

## Git

### Branches

Convention recommandée :

- `main` — branche protégée, toujours stable
- `feature/issue-XX-courte-description` — branches de travail
- `chore/template-update` — mises à jour par rapport au template

### Commits

Messages en anglais ou en français, au choix de l'équipe, mais cohérents :

```
feat: ajouter l'export CSV
fix: corriger le calcul de la moyenne pondérée
chore: update pre-commit hooks
docs: compléter la page d'installation
```

---

## Documentation

- Écrivez en Markdown dans `docs/`.
- La navigation est gérée par des fichiers `.nav.yml` dans chaque sous-dossier.
- La doc est construite par MkDocs Material et déployée automatiquement sur Github Pages.
- Séparez la doc **utilisateur** (comment utiliser le projet) de la doc **développeur** (comment le code fonctionne).

---

## Ce que vous ne devez pas toucher (sauf bonne raison)

- **`pyproject.toml`** : les sections `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest]` sont calibrées pour le template. Ajoutez vos dépendances, mais ne modifiez pas la config des outils sans comprendre l'impact.
- **`.devcontainer/postCreateCommand.sh`** : chaque modification rend les futures mises à jour du template plus difficiles (`cruft update` crée des conflits sur les fichiers modifiés).
- **`.pre-commit-config.yaml`** : les hooks sont alignés avec la CI. Si vous en désactivez un, la CI échouera.



## 🎯 Règles d'Or (Les 5 Commandements)

### 1. **Ne JAMAIS utiliser `--no-verify`** 🚫

```bash
# ❌ MAUVAIS - Contourne les Quality Gates
git commit --no-verify

# ✅ BON - Fixe le code pour passer les hooks
git add -A
git commit -m "fix: resolve pre-commit issues"
```

**Philosophie**: "Ne rien mettre sous le tapis, un problème, on tire l'andon et on corrige"

### 2. **Installer des packages avec `--active`** 📦

```bash
# ❌ MAUVAIS - Crée env temporaire
uv add pandas-stubs

# ✅ BON - Installe dans l'env actif
uv add --active pandas-stubs
```

**Pourquoi**: Sans `--active`, uv crée un virtualenv temporaire. Les packages ne sont pas persistants.

### 3. **Accepter le Règne de Ruff** 👑

Ruff est le **formateur dominant** du projet. Ne pas le combattre:

```python
# ❌ Essayer de contourner:
value = some_function(arg1, arg2)  # type: ignore[error] ← Ruff le reformate!

# ✅ Accepter:
# type: ignore[error]
value = some_function(arg1, arg2)  # ← Laissez Ruff faire
```

**Règle**: Si une ligne dépasse 88 chars avec un type: ignore, Ruff le met sur la ligne précédente. C'est OK.

### 4. **Configurer MyPy pour Exclure `src/`** 🎯

```toml
# ✅ TOUJOURS dans pyproject.toml
files = ["scripts", "tests", "app"]  # Pas src/!
namespace_packages = false
```

**Pourquoi**: L'editable install ajoute `/src` au PYTHONPATH. Pas besoin de le scanner deux fois.

### 5. **Corriger les Erreurs, Pas les Ignorer** 🔧

```python
# ❌ Ignorer les vraies erreurs:
# type: ignore[no-untyped-def]
def function_without_types(x):
    pass

# ✅ Fixer la vraie erreur:
def function_with_types(x: str) -> None:
    pass
```

**Exception**: `type: ignore[unused-ignore]` n'existe pas parce que c'est un faux positif causé par Ruff.

---
