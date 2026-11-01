# Issue #113 — Venv créé avec un Python géré par uv

## Résumé

Au rebuild d'un projet généré, une dépendance sans wheel (`scikit-surprise`) échouait sur `Python.h: No such file or directory`. L'image `python:1-3.12-bookworm` fournit 3.12 avec ses en-têtes dans `/usr/local`, mais en 3.11 uv ne trouve que le Python Debian (`/usr/bin/python3.11`), sans `python3.11-dev`.

Correction : `uv venv ... --managed-python` dans `.devcontainer/scripts/ensure_venv.sh` (dépôt et squelette, identiques).

Spécification : [commentaire de l'issue #113](https://github.com/castorfou/PyFoundry/issues/113#issuecomment-6560654665).

## Points saillants

### Pourquoi le bug est apparu au passage au HOME persistant

Hypothèse non vérifiée : uv préfère un Python géré déjà installé. Un HOME vide n'en a pas, uv se rabat alors sur le Python Debian. C'est aussi pourquoi le test reste vert sans le flag sur une machine où un Python géré existe déjà.

### `--managed-python` et `UV_PYTHON_PREFERENCE` sont incompatibles

`uv` refuse les deux ensemble (`the argument --managed-python cannot be used with --python-preference`). Un test ne peut donc pas simuler un HOME neuf avec cette variable : `test_missing_venv_is_created_then_synced` (faux `uv`) garantit le flag, `test_real_uv_python_has_headers` garantit le résultat.

### Tests avec le vrai `uv` hors ligne

Avec `UV_OFFLINE=1`, le script exige un Python géré déjà présent. `real_uv_env` dans `tests/test_ensure_venv.py` ignore le test sinon, au lieu d'échouer sur une machine neuve. Pour vérifier ce cas : `UV_PYTHON_INSTALL_DIR=<dossier vide> pytest tests/test_ensure_venv.py`.

### Pas de repli sur le Python Debian

Un repli silencieux recréerait le bug de façon intermittente. Sans accès à GitHub au premier build, le script échoue et affiche la commande. `UV_PYTHON_INSTALL_MIRROR` permet d'indiquer un miroir.

### `scikit-surprise` 1.1.4 et numpy

Il compile contre numpy 1 et plante à l'import avec numpy 2 : contrainte `numpy<2` à déclarer dans le projet qui l'utilise.
