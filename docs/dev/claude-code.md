# commande custom parametrables

vous pouvez utiliser le mot-clé spécial $ARGUMENTS dans vos commandes custom pour les rendre paramétrables.

## exemple de fix-issue

pour celle-ci le pré-requis est d'avoir gh installé

créez `.claude/commands/fix-issue.md` et mettez ça dedans :

```
Analyse et corrige l'issue GitHub numéro : $ARGUMENTS

1. Utilise `gh issue view` pour récupérer les détails, assigne-toi cette issue

2. Cree une branche pour bosser sur cette issue, en la referancant

3. Comprends le problème décrit

4. Cherche les fichiers concernés dans le codebase

5. Implémente la correction

6. Assure-toi que la doc user et dev est à jour, modifie la au besoin

7. Écris et lance les tests

8. Vérifie que tout passe (lint, typecheck), reboucle entre les etapes 3 à 8 si probleme

9. Commit avec un message descriptif

10. Crée une PR qui référence l'issue

11. Demande a l'utilisateur une validation finale avant de faire le merge et detruire la branche
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
# Initialize conda and run tests in pyfoundry environment
eval "$(conda shell.bash hook)" && conda activate pyfoundry && pytest tests -v
```

### règle R1.2 - ruff

il faut donc appeler ruff de cette façon

```bash
# Run ruff linting in pyfoundry environment on non-template files and fix issues
eval "$(conda shell.bash hook)" && conda activate pyfoundry && ruff check tests/ docs/ --fix
```

## tester localement

```bash
# avec les valeurs par defaut sauf une
# creation du projet sous /tmp
mamba activate pyfoundry && \
cd /tmp && \
rm -rf /tmp/mon-projet-data-science && \
cruft create /home/guillaume/git/PyFoundry --no-input --extra-context '{"use_node": "y"}' && \
code mon-projet-data-science
```

et ensuite un Rebuild and Reopen container depuis vscode