# Issue #80 — check_mounts.sh échoue sur un commentaire JSONC en fin de ligne

## Résumé

Point de départ : au rebuild du devcontainer de `docker-lmelp` (projet généré), `initializeCommand` échouait. `check_mounts.sh --host` affichait une traceback Python (`JSONDecodeError: Expecting ',' delimiter: line 12 column 60`), puis `[FAIL] .devcontainer/devcontainer.json: impossible de lire la section mounts`. Le conteneur ne pouvait plus démarrer.

Cause : la ligne 12 du `devcontainer.json` de docker-lmelp se termine par un commentaire ajouté par detect-secrets :

```jsonc
"CONTAINER_NAME=vscode-dev-container_docker-lmelp" // pragma: allowlist secret
```

`parse_mounts` ne retirait que les `//` en **début de ligne**, pour ne pas casser les `http://` dans les chaînes. Un commentaire en fin de ligne restait dans le texte, que `json.loads` refusait. Le même regex naïf avait deux autres failles : un `*/` ou un `/*` dans une chaîne (glob `"**/*.pyc"`) était pris pour un commentaire de bloc, et les virgules finales (acceptées par VS Code) faisaient échouer la lecture.

Correction sur la branche `80-checkmount-error-during-devcontainer-rebuild`, appliquée au dépôt et au squelette (R1.5).

Spécifications validées : [commentaire de l'issue #80](https://github.com/castorfou/PyFoundry/issues/80#issuecomment-6113182356).

---

## Solution

### Lecture du JSONC, consciente des chaînes

Une seule expression régulière reconnaît soit une chaîne JSON, gardée telle quelle, soit un commentaire (`//…` ou `/*…*/`), supprimé. Les chaînes étant reconnues d'abord, un `//` ou un `/*` qu'elles contiennent n'est jamais pris pour un commentaire. Le même principe retire ensuite les virgules finales avant `]` ou `}`.

```python
STRING = r'"(?:\\.|[^"\\])*"'
content = re.sub(STRING + r'|//[^\n]*|/\*.*?\*/',
                 lambda m: m.group() if m.group().startswith('"') else '',
                 content, flags=re.DOTALL)
content = re.sub('(' + STRING + r')|,(\s*[\]}])',
                 lambda m: m.group(1) or m.group(2), content)
```

### `.devcontainer/scripts/check_mounts.sh` (dépôt et squelette, identiques)

- `parse_mounts` passe de `python3 -c "…"` à un heredoc entre apostrophes (`python3 - "$1" <<'PY'`). Bash n'interprète plus rien dans le code Python : les regex contenant `"`, `\` et `$` s'écrivent sans échappement.
- Si le fichier reste invalide, le script affiche `fichier: message: line X column Y (char Z)` sur stderr au lieu d'une traceback. Le `[FAIL] … impossible de lire la section mounts` et le code retour 1 sont inchangés.

### `tests/devcontainer_utils.py`

`parse_jsonc` applique la même logique (constante `JSON_STRING`), pour que les tests lisent `devcontainer.json` comme le script.

---

## Tests

Dans `tests/test_check_mounts.py`, un dictionnaire `JSONC_SAMPLES` partagé (commentaire en fin de ligne, `//` et `/* */` dans des chaînes, virgules finales) et une classe `TestJsonc` :

- `test_script_reads_mounts[...]` : le script lit le montage de chaque échantillon (code retour 0) ;
- `test_parse_jsonc_reads_mounts[...]` : `parse_jsonc` lit les mêmes montages, ce qui garde les deux parseurs alignés ;
- `test_parse_jsonc_keeps_comment_markers_in_strings` : `http://…`, `**/*.pyc` et `*/` intacts ;
- `test_invalid_json_fails_with_location_not_traceback` : `[FAIL]`, code retour 1, `line 3` sur stderr, pas de `Traceback`.

Les 8 tests échouaient avant la correction (RED). La suite complète passe ensuite : 203 passed, 1 skipped.

---

## Validation

- Le script corrigé lit sans erreur le `devcontainer.json` de docker-lmelp (récupéré via `gh api`).
- Le projet généré avec `cookiecutter` contient un `check_mounts.sh` identique à celui du dépôt.
- L'utilisateur a confirmé que `check_mounts.sh` passe au rebuild de docker-lmelp. Le build échoue ensuite à une autre étape, sans lien avec cette issue : à traiter à part.

---

## Points d'attention

- Un `devcontainer.json` est du **JSONC** : commentaires `//` et `/* */` n'importe où, virgules finales. Tout outil qui le lit doit gérer ces trois cas, et ne pas retirer les marqueurs de commentaire contenus dans les chaînes.
- detect-secrets ajoute des `// pragma: allowlist secret` en fin de ligne : ce cas se présentera dans tous les projets générés qui l'utilisent.
- Pour du Python dans un script bash, préférer un heredoc entre apostrophes (`<<'PY'`) à `python3 -c "…"` : aucun échappement bash à gérer.
