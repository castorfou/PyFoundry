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

11. Demande a l'utilisateur une validation finale et s'il veut en faire une version/tag

12. Fait le merge et detruit la branche. Et si besoin crée la release note, tag la version (n'oublie pas de completer la doc à ce propos)