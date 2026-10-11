#!/usr/bin/env bash
# =============================================================================
# Vérification des points de montage du devcontainer
# Lancé sur l'HÔTE par initializeCommand, avant que Docker ne monte les sources.
# Usage manuel, depuis la racine du projet : bash .devcontainer/scripts/check_mounts.sh --host
# =============================================================================
set -uo pipefail

# --host est accepté pour expliciter l'usage : le script ne s'exécute que sur l'hôte
if [[ "${1:-}" != "" && "${1:-}" != "--host" ]]; then
    echo "Usage: $0 [--host]" >&2
    exit 2
fi

# Variables transmises par initializeCommand ; à défaut (lancement manuel), on les déduit
WORKSPACE_FOLDER_BASENAME="${DEVCONTAINER_WORKSPACE_FOLDER_BASENAME:-$(basename "$PWD")}"
HOMES_DIR="$HOME/.devcontainer/homes"

ERRORS=0

log_section() {
    echo ""
    echo "=== $1 ==="
    echo ""
}

log_ok() {
    echo "  [OK]   $1"
}

log_fail() {
    echo "  [FAIL] $1"
    ERRORS=$((ERRORS + 1))
}

# Extrait les montages actifs de devcontainer.json : "source<TAB>target" par ligne
parse_mounts() {
    python3 -c "
import json, re, sys

with open(sys.argv[1]) as f:
    content = f.read()

# Commentaires JSONC : blocs, et // en début de ligne seulement (pour garder les http://)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
content = re.sub(r'^[\t ]*//.*$', '', content, flags=re.MULTILINE)

for mount in json.loads(content).get('mounts', []):
    parts = dict(part.split('=', 1) for part in mount.split(',') if '=' in part)
    source, target = parts.get('source', ''), parts.get('target', '')
    if source and target:
        print(f'{source}\t{target}')
" "$1"
}

# Résout les variables Dev Containers d'un chemin source
resolve_path() {
    local path="$1"
    local -a candidates=()
    local entry

    path="${path//\$\{localEnv:HOME\}/$HOME}"
    path="${path//\$\{localWorkspaceFolderBasename\}/$WORKSPACE_FOLDER_BASENAME}"

    if [[ "$path" == *'${devcontainerId}'* && -n "${DEVCONTAINER_ID:-}" ]]; then
        path="${path//\$\{devcontainerId\}/$DEVCONTAINER_ID}"
    elif [[ "$path" == *'${devcontainerId}'* ]]; then
        # Lancement manuel : on retient le HOME persistant du projet s'il est unique
        shopt -s nullglob
        for entry in "$HOMES_DIR/$WORKSPACE_FOLDER_BASENAME-"*; do
            [[ -d "$entry" ]] && candidates+=("$entry")
        done
        shopt -u nullglob
        if [[ "${#candidates[@]}" -eq 1 ]]; then
            path="${path//\$\{devcontainerId\}/${candidates[0]#"$HOMES_DIR/$WORKSPACE_FOLDER_BASENAME-"}}"
        fi
    fi
    printf '%s\n' "$path"
}

# Vérifie qu'un dossier et ses fichiers ne sont pas plus ouverts que les modes attendus
check_permissions() {
    local path="$1" max_dir_mode="$2" max_file_mode="$3"
    local file mode max_mode

    [[ -d "$path" ]] || return 0
    mode=$(stat -c '%a' "$path" 2>/dev/null) || return 0
    [[ "$mode" -le "$max_dir_mode" ]] || return 1

    for file in "$path"/*; do
        [[ -f "$file" ]] || continue
        mode=$(stat -c '%a' "$file" 2>/dev/null) || continue
        # Les clés publiques peuvent être lisibles par tous
        if [[ "$file" == *.pub ]]; then
            max_mode=644
        else
            max_mode="$max_file_mode"
        fi
        [[ "$mode" -le "$max_mode" ]] || return 1
    done
    return 0
}

echo ""
echo "============================================================"
echo " Vérification des points de montage"
echo "============================================================"

DC_JSON=".devcontainer/devcontainer.json"
if [[ ! -f "$DC_JSON" ]]; then
    echo ""
    log_fail "devcontainer.json not found in .devcontainer/"
    echo "        Lancez ce script depuis la racine du projet."
    exit 1
fi

if ! MOUNTS=$(parse_mounts "$DC_JSON"); then
    echo ""
    log_fail "$DC_JSON: impossible de lire la section mounts"
    exit 1
fi

log_section "Montages détectés"

while IFS=$'\t' read -r source target; do
    [[ -n "$source" ]] || continue
    resolved=$(resolve_path "$source")
    echo "  Mount: $resolved -> $target"

    if [[ "$resolved" == *'${devcontainerId}'* ]]; then
        log_fail "$target: cannot resolve \${devcontainerId} for this host check"
        echo "        Le HOME persistant n'a pas encore été créé, ou plusieurs candidats existent."
        echo "        Attendu : un seul dossier correspondant à $HOMES_DIR/$WORKSPACE_FOLDER_BASENAME-*"
        continue
    fi

    if [[ ! -e "$resolved" && "$resolved" == *.sock ]]; then
        log_fail "$target: source does not exist ($resolved)"
        echo "        Ce socket est créé par le service Docker : vérifiez que Docker tourne sur l'hôte."
        continue
    fi

    if [[ ! -e "$resolved" ]]; then
        log_fail "$target: source does not exist ($resolved)"
        echo "        Corrigez source= dans $DC_JSON si le chemin est incorrect."
        echo "        Sinon, créez le chemin sur l'hôte avec le type attendu :"
        echo "          Répertoire : mkdir -p \"$resolved\""
        echo "          Fichier    : touch \"$resolved\""
        continue
    fi

    if [[ "$target" == */.ssh ]] && ! check_permissions "$resolved" 700 600; then
        log_fail "$target: SSH permissions too open"
        echo "        Corrigez sur l'hôte :"
        echo "          chmod 700 ~/.ssh"
        echo "          chmod 600 ~/.ssh/*"
        continue
    fi

    log_ok "$target"
done <<< "$MOUNTS"

log_section "Résumé"

if [[ "$ERRORS" -gt 0 ]]; then
    echo "  $ERRORS erreur(s) : corrigez-les avant de démarrer le devcontainer."
    exit 1
fi

echo "  Tous les montages sont valides."
exit 0
