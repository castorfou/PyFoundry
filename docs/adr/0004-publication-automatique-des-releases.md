# 0004 — Publication automatique des releases

- **Statut** : accepté
- **Date** : 2026-10-25
- **Issue** : [#90](https://github.com/castorfou/PyFoundry/issues/90)
- **Remplace** : le point 5 de l'[ADR 0002](0002-gestion-des-versions.md) (tag posé par le mainteneur)

## Contexte

Avec l'ADR 0002, une release demandait deux gestes : merger la PR de release, puis créer et pousser le tag `vX.Y.Z` à la main. Le second geste pouvait être oublié ou appliqué au mauvais commit. Les contrôles de cohérence (`release.py check-tag`) ne tournaient qu'après le push du tag : une PR de release incohérente était mergée avant d'être refusée. Enfin, un projet généré ne montrait sa version du template que dans `.cruft.json`, à lire avec `jq`.

## Décision

1. **Le merge publie.** `release.yml` tourne à chaque push sur `main`. `release.py plan --base <commit précédent>` compare la version de `pyproject.toml` avant et après. Seule une hausse publie : la décision de faire une release reste celle du mainteneur, prise en ouvrant une PR de release (releases par lots, ADR 0002).
2. **Une seule commande crée le tag et la release** : `gh release create vX.Y.Z --target <commit testé>`. Pas de publication partielle (tag sans release), pas de doublon (la commande échoue si la release existe). Aucun workflow ne dépend du tag : un tag créé avec `GITHUB_TOKEN` ne déclenche pas d'autre workflow.
3. **Plus de tag poussé à la main** : un seul chemin de publication.
4. **Contrôle dès la PR** : le même `release.py plan` tourne dans la CI des pull requests vers `main`. Une baisse de version, un tag existant, un `cookiecutter.json` désaligné ou une section du CHANGELOG absente ou vide font échouer la PR avant le merge.
5. **Permissions minimales** : le workflow est en lecture seule, sauf le job `publish` (`contents: write`). `concurrency` empêche deux publications simultanées.
6. **`TEMPLATE_VERSION` dans le projet généré**, rendu depuis `_pyfoundry_version`. C'est un fichier du template ([ADR 0003](0003-proprietaire-des-fichiers-mise-a-jour.md)) : `cruft update` le met à jour, car cruft relit les variables privées dans le nouveau template.

Écartés : release-please et semantic-release, qui décident du numéro à partir des commits (l'ADR 0002 garde un CHANGELOG rédigé à la main) ; un workflow déclenché par le tag, qui supposerait un jeton personnel pour que le tag créé par la CI le déclenche.

## Conséquences

- Publier une release, c'est merger une PR de release ; il n'y a plus de commande à lancer après le merge.
- Une PR d'issue ne doit pas modifier la version : son merge publierait une release. `/fix-issue` le rappelle.
- Un échec passager des tests ou de `publish` se rattrape par « Re-run failed jobs », qui rejoue la même décision. Un échec de `plan` se corrige par une nouvelle PR de release.
- La première publication automatique a lieu à la prochaine PR de release.
