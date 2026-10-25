# Issue #92 — Devcontainers de test orphelins qui font chauffer le laptop

## Résumé

Le 25/10, deux devcontainers de test (`/tmp/mon-projet-data-science`, `/tmp/test-cruft`) tournaient depuis des heures après la fermeture de VS Code, leur `agentHost` à ~100 % CPU.

Deux causes :

1. `"shutdownAction": "none"` dans `.devcontainer/devcontainer.json` (dépôt et squelette) : fermer la fenêtre n'arrêtait jamais le conteneur.
2. Le processus de test (R1.3, `docs/dev/testing.md`) faisait `rm -rf` du dossier du projet, jamais `docker rm` : le conteneur restait, orphelin.

Travail sur la branche `92-tests-du-template-arrêter-le-devcontainer-au-nettoyage-et-shutdownaction-stopcontainer`.

Spécifications validées : [commentaire de l'issue #92](https://github.com/castorfou/PyFoundry/issues/92#issuecomment-6398807850).

Décisions de l'utilisateur :

- **Un script testé** plutôt que trois commandes recopiées dans chaque doc.
- **Le HOME persistant est supprimé par défaut** : un projet de test n'a rien à garder.
- **Les tests manuels se font parfois sur l'hôte, parfois dans le devcontainer PyFoundry** : les docs donnent les deux chemins, `~/git/PyFoundry/scripts/…` (clone sur l'hôte) et `/workspaces/PyFoundry/scripts/…`.

---

## Solution

### `shutdownAction: stopContainer`

`.devcontainer/devcontainer.json` et `{{ cookiecutter.project_slug }}/.devcontainer/devcontainer.json` : `"shutdownAction": "stopContainer"`, avec un commentaire (#92). Limite : seule une fermeture propre de la fenêtre arrête le conteneur ; un VS Code tué ou planté le laisse actif.

### `scripts/clean_test_project.sh <dossier>`

Dans le dépôt PyFoundry seulement : outil de dev du template, absent des projets générés (vérifié par `cookiecutter`). Il supprime dans cet ordre :

1. **le conteneur**, retrouvé par `docker ps -aq --filter "label=devcontainer.local_folder=<chemin absolu>"`, puis `docker rm -f`. Le chemin est rendu absolu (`cd && pwd`, ou `$PWD/` devant un relatif) même si le dossier n'existe plus ;
2. **le dossier** du projet ;
3. **le HOME** `~/.devcontainer/homes/<nom>-<id>`. Le `devcontainerId` est en base 32, sans tiret : un suffixe contenant un tiret est ignoré, donc nettoyer `projet` ne touche pas `projet-2-<id>`.

Garde-fous et messages :

- sans argument, ou avec `/` ou `$HOME` : usage ou refus, code 1, rien de supprimé ;
- sans `docker` (cas du devcontainer PyFoundry) : avertissement avec la commande `docker rm -f $(docker ps -aq --filter …)` exacte à lancer sur l'hôte, puis le reste du nettoyage, code 0 ;
- suppression impossible (dossiers root) : `❌ … sudo rm -rf <chemin>`, code 1, après avoir fait le reste ;
- rien trouvé : `ℹ️  Rien à supprimer`.

`CLEAN_TEST_PROJECT_DOCKER` remplace la commande `docker` (tests). Un faux `docker` dans le `PATH` ne suffisait pas : sur les runners GitHub, le vrai `docker` est dans `/usr/bin`, avec `bash` et `rm`, et on ne peut pas retirer ce dossier du `PATH`.

---

## Tests

- `tests/test_configurations.py` : `test_devcontainer_stops_when_window_closes`, paramétré `repo`/`generated` comme `test_devcontainer_has_no_isort_extension`.
- `tests/test_clean_test_project.py` (10 tests, script lancé en `subprocess`, faux `docker` qui journalise ses appels et note si le dossier existe encore au moment du `rm`) : refus sans argument, `$HOME` et `/` ; conteneur supprimé **avant** le dossier ; pas de `docker rm` sans conteneur ; chemin relatif rendu absolu ; dossier déjà supprimé (le cas de l'issue) ; HOME ciblé uniquement ; sans docker ; HOME non supprimable (ignoré en root).

---

## Leçon du test manuel

Premier test sur l'hôte : après fermeture de la fenêtre, `gracious_elion` (le conteneur de l'issue) était toujours là, « Up About a minute ».

Cause : VS Code retrouve le conteneur d'un dossier par le label `devcontainer.local_folder`. L'ancien `rm -rf` ne l'avait pas supprimé, et le projet régénéré avait le même chemin : VS Code a **redémarré l'ancien conteneur** au lieu d'en créer un. Or les réglages de `devcontainer.json` sont figés dans le label `devcontainer.metadata` à la création :

```bash
docker inspect <conteneur> --format '{{ index .Config.Labels "devcontainer.metadata" }}' | grep -o '"shutdownAction":"[^"]*"'
# "shutdownAction":"none"
```

Conséquences :

- après `clean_test_project.sh`, un projet régénéré au même chemin a un conteneur neuf : le conteneur n'apparaissait plus après fermeture ;
- pour les **projets existants**, `cruft update` ne suffit pas : il faut un **Rebuild Container** pour que `stopContainer` s'applique. C'est le rebuild habituel après `cruft update` (comme pour #94), pas une migration au sens de R1.6.

---

## Documentation

- `CLAUDE.md` : R1.3 en deux variantes (hôte, devcontainer), arborescence (`scripts/`), tableau des tests.
- `docs/dev/testing.md` : le script dans chaque section qui faisait `rm -rf` ; « Nettoyage » explique pourquoi supprimer le dossier ne suffit pas, avec les commandes brutes équivalentes.
- `docs/dev/contributing.md` : idem.
- `docs/user/troubleshooting.md` : entrée sur les conteneurs oubliés (lister, arrêter, limite de `stopContainer`, rebuild nécessaire sur un projet existant).
- `CHANGELOG.md`, `## [Non publié]` (#92).
