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

Et maintenant vous pouvez juste taper `/project:fix-issue 1234` et Claude s’occupera de tout ! 

