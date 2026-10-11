# Issue #65 — fuseau horaire du devcontainer et échec de tzdata

## Résumé

Point de départ : à chaque build du devcontainer, `apt upgrade` échouait sur tzdata (`unable to make backup link of './usr/share/zoneinfo/Etc/UTC' … Invalid cross-device link`). Correction sur la branche `65-devcontainer-apt-upgrade-échoue-sur-tzdata-à-cause-du-montage-etclocaltime`, appliquée au dépôt et au squelette :

1. Le `/etc/localtime` de l'hôte est monté sur **`/etc/localtime.host`** au lieu de `/etc/localtime`.
2. La nouvelle fonction **`setup_timezone`** de `postCreateCommand.sh`, appelée juste après `update_system`, fait pointer `/etc/localtime` vers la zone de même contenu.
3. **`"TZ": "${localEnv:TZ}"` est retiré** de `containerEnv`.

---

## Diagnostic

### Le montage écrasait Etc/UTC

- Dans l'image, `/etc/localtime` est un lien vers `/usr/share/zoneinfo/Etc/UTC`. Docker suit ce lien : le fichier de l'hôte (Europe/Paris) se retrouvait monté **sur `Etc/UTC`**, ce qui se voit dans `/proc/self/mountinfo` :
  `/usr/share/zoneinfo/Europe/Paris /usr/share/zoneinfo/Etc/UTC ro`
- Pendant la mise à jour de tzdata, dpkg crée un lien physique de sauvegarde, ce qui est impossible sur un point de montage.
- **Effet non signalé dans l'issue** : UTC ne valait plus UTC. `TZ=UTC date` affichait CEST, et `datetime.now(ZoneInfo('UTC'))` renvoyait `+02:00`. Pour un template Data Science, ce sont des timestamps faux sans aucun message d'erreur.
- C'est pour cette raison que la piste `apt-mark hold tzdata` (piste 1 de l'issue) a été écartée : elle fait disparaître l'erreur sans corriger UTC.

### TZ vide = UTC (découvert pendant le test utilisateur)

- `"TZ": "${localEnv:TZ}"` produit `TZ=` (vide) lorsque TZ n'est pas défini sur l'hôte, ce qui est le cas courant sous Ubuntu. Le constat a été fait dans `/proc/<pid>/environ` des processus VS Code et des terminaux zsh.
- glibc interprète un TZ vide comme UTC : `date` affichait UTC alors que `/etc/localtime` pointait correctement vers Europe/Paris.
- Ce défaut était masqué avant le correctif, puisque « UTC » valait alors Paris.
- Le shell de l'outil Bash de Claude Code n'hérite pas de ce `TZ=` vide. Les vérifications de fuseau sont donc à faire dans un vrai terminal VS Code.

---

## Solution

### `setup_timezone` (`.devcontainer/postCreateCommand.sh`, et même code dans le squelette)

- Paramètres surchargeables pour les tests : `HOST_LOCALTIME` (défaut `/etc/localtime.host`), `ZONEINFO_DIR` (défaut `/usr/share/zoneinfo`), `ETC_DIR` (défaut `/etc`).
- La fonction cherche le premier fichier de zoneinfo identique au fichier de l'hôte (`find … -exec cmp -s … -print -quit`), en ignorant `posix/` et `right/`. La recherche prend 0,14 s.
- Si une zone est trouvée : `ln -sfn zoneinfo/<zone> /etc/localtime`, et `<zone>` est écrit dans `/etc/timezone`.
  - Garder le nom de la zone sert à `tzlocal`/pandas.
  - Le script `config` de tzdata relit ce lien, donc un `apt upgrade` ultérieur conserve le fuseau.
- Si aucune zone ne correspond, `/etc/localtime` pointe vers `/etc/localtime.host` : l'heure est juste, mais le nom de la zone est inconnu.
- Si le fichier de l'hôte est absent ou vide : avertissement, le conteneur reste en UTC, `return 0`.
- La fonction tourne **après** `update_system`, donc après la mise à jour de tzdata.
- Un hôte en UTC peut être identifié comme `Etc/GMT`, ce qui est sans conséquence.

### devcontainer.json (dépôt et squelette)

- Montage : `source=/etc/localtime,target=/etc/localtime.host,type=bind,consistency=cached,readonly`. La source n'a pas changé, donc `check_mounts.sh` reste inchangé.
- `TZ` est supprimé de `containerEnv`.

---

## Tests

`tests/test_timezone.py`, paramétré sur `repo`, `default` et `docker_in_docker` :

- montage vers `/etc/localtime.host`, aucun montage avec la cible `/etc/localtime`
- `TZ` absent de `containerEnv` et de `remoteEnv`
- `setup_timezone` appelé sur la ligne qui suit `update_system`
- exécution réelle de la fonction extraite (`extract_function` de `tests/test_post_create_command.py`) avec un faux `sudo` (`exec "$@"`) et un faux zoneinfo dans `tmp_path` : zone connue (posix/ ignoré, Etc/UTC intact), zone inconnue, fichier de l'hôte absent ou vide

`test_timezone_configuration` a été retiré de `tests/test_template_generation.py` : il vérifiait la présence de `TZ` et faisait doublon.

---

## Validation utilisateur

Rebuild du devcontainer PyFoundry :

- `Setting up tzdata (2026c…)` passe sans erreur
- `✅ Fuseau horaire : Europe/Paris`
- `date` affiche CEST, et `TZ=UTC date` affiche UTC
- `ZoneInfo('UTC')` renvoie `+00:00`

---

## Leçons

- Un bind mount dont la cible est un lien symbolique monte en réalité sur la cible du lien. Il ne faut jamais monter sur `/etc/localtime` d'une image Debian.
- `${localEnv:VAR}` dans `containerEnv` produit une variable **vide**, et non absente, quand VAR manque sur l'hôte. Pour TZ, la différence compte : une valeur vide signifie UTC.
