# commande custom parametrables

vous pouvez utiliser le mot-clé spécial $ARGUMENTS dans vos commandes custom pour les rendre paramétrables.

## exemple de fix-issue

pour celle-ci le pré-requis est d'avoir gh installé

créez `.claude/commands/fix-issue.md` et mettez ça dedans :

```
Analyse et corrige l'issue GitHub numéro : $ARGUMENTS

1. Utilise `gh issue view` pour récupérer les détails

2. Comprends le problème décrit

3. Cherche les fichiers concernés dans le codebase

4. Implémente la correction

5. Écris et lance les tests

6. Vérifie que tout passe (lint, typecheck)

7. Commit avec un message descriptif

8. Crée une PR qui référence l'issue
```

Et maintenant vous pouvez juste taper `/fix-issue 1234` et Claude s’occupera de tout ! 

# les environnements d'execution

## besoin de pyfoundry

pour les commandes ayant besoin de python, cruft, pytest, mkdocs, il faut d'abord se placer dans l'environnement conda/mamba pyfoundry qui est disponible et a été créé ainsi

```bash
mamba create -y -n pyfoundry -c conda-forge python=3.11 --yes
mamba activate pyfoundry
mamba install nb_conda_kernels cruft mkdocs-material pytest pytest-cookies pytest-cov pre-commit ruff mypy --yes
```

### règle R1.1 - pytest

il faut donc appeler pytest de cette façon

```bash
conda activate pyfoundry
pytest tests/ -v
```