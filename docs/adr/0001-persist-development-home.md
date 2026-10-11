# 0001 — HOME persistant pour les devcontainers

- **Statut** : accepté
- **Date** : 2026-10-11
- **Issue** : [#59](https://github.com/castorfou/PyFoundry/issues/59)

## Contexte

Le HOME `/home/vscode` vivait dans la couche du conteneur. Chaque rebuild l'effaçait : connexion et historique Claude Code (`~/.claude`, `~/.claude.json`), connexion `gh` (`~/.config/gh`), historique du shell, `~/.vscode-server`. Il fallait se reconnecter partout et la mémoire des conversations Claude Code était perdue.

La même solution a été validée dans un dépôt d'entreprise jumeau, puis portée ici.

## Décision

1. **HOME par projet sur l'hôte** : `~/.devcontainer/homes/${localWorkspaceFolderBasename}-${devcontainerId}` est monté sur `/home/vscode`. Le nom du dossier du projet et l'identifiant du devcontainer garantissent qu'aucun projet ne partage son HOME avec un autre.
2. **Caches partagés entre projets** : `~/.cache/uv` et `~/.cache/pre-commit-devcontainers` (monté sur `~/.cache/pre-commit`). `~/.vscode-server` n'est pas partagé : il reste dans le HOME du projet.
3. **Venv hors du HOME** : `/tmp/venv`, recréé à chaque rebuild par `postCreateCommand.sh` depuis `uv.lock`. Il dépend de l'interpréteur de l'image ; le conserver d'une image à l'autre le casserait.
4. **Plus de montage `~/.gitconfig`** : VS Code copie le `.gitconfig` de l'hôte au démarrage (voir aussi #61).
5. **Création et vérification côté hôte** : `initializeCommand` crée les dossiers sources (sinon Docker les crée en root, y compris `.cache` dans le HOME) puis lance `.devcontainer/scripts/check_mounts.sh --host`, qui signale chaque source manquante avec la commande pour la créer et contrôle les permissions de `~/.ssh` selon les règles de `ssh`.
6. **`seed_home`** : le bind mount masque le HOME de l'image ; `postCreateCommand.sh` recopie `/etc/skel` sans écraser l'existant.

Le template et le devcontainer du dépôt PyFoundry appliquent la même configuration.

## Conséquences

- Les connexions, l'historique et la mémoire Claude Code survivent aux rebuilds.
- Le premier rebuild après la mise à jour du template démarre avec un HOME vide. La migration est décrite dans [Passer au HOME persistant](../user/usage.md#passer-au-home-persistant).
- Les dossiers `~/.devcontainer/homes/<projet>-*` s'accumulent sur l'hôte : ils ne sont pas supprimés avec le projet. Supprimer l'un d'eux remet le HOME du projet à zéro.
- Une configuration cassée dans le HOME (shell, extension) n'est plus réparée par un rebuild : il faut supprimer le dossier.
- Un package installé hors `uv add --active` disparaît au rebuild suivant, puisque le venv est recréé.
- Le cache pre-commit partagé peut contenir un clone interrompu (`InvalidManifestError`) : `pre-commit clean` le vide.
