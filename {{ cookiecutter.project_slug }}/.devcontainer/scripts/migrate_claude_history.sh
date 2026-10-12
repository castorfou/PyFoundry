#!/usr/bin/env bash
# =============================================================================
# Migration de l'historique vers le HOME persistant et la config Claude Code
# partagée (issues #73 et #82). Lancé sur l'HÔTE par initializeCommand, avant le
# build : l'ancien conteneur existe encore, et dans le nouveau, l'ancien ~/.claude
# du projet est masqué par ~/.config/claude-devcontainers.
#
# - Génération 1 (HOME dans le conteneur) : récupère avec `docker cp`, depuis
#   l'ancien conteneur du projet, l'historique Claude Code et celui du shell.
# - Génération 2 (HOME persistant, ~/.claude par projet) : recopie ce ~/.claude.
#
# Copie, une fois par projet et sans rien écraser, les conversations (/resume),
# la mémoire auto, les checkpoints (/rewind) et l'historique des prompts.
# Les connexions (Claude Code, gh) ne sont pas copiées : on se reconnecte une
# fois pour tous les projets.
# N'échoue jamais : l'ouverture du conteneur ne doit pas en dépendre.
# =============================================================================
set -uo pipefail

WORKSPACE_FOLDER_BASENAME="${DEVCONTAINER_WORKSPACE_FOLDER_BASENAME:-$(basename "$PWD")}"
PERSISTENT_HOME="$HOME/.devcontainer/homes/$WORKSPACE_FOLDER_BASENAME-${DEVCONTAINER_ID:-}"
OLD="$PERSISTENT_HOME/.claude"
SHARED="$HOME/.config/claude-devcontainers"
MARKER="$OLD/.migrated-to-claude-devcontainers"
CONTAINER_MARKER="$PERSISTENT_HOME/.migrated-from-container"
MIGRATION_DOC="https://castorfou.github.io/PyFoundry/user/usage/#passer-au-home-persistant"

[[ -n "${DEVCONTAINER_ID:-}" ]] || exit 0

# Copie les fichiers de $1 absents de $2. Pas de `cp -n` : selon la version de
# coreutils (9.2 à 9.4), il échoue dès qu'il saute un fichier existant.
copy_missing() {
    local src="$1" dest="$2" file
    (cd "$src" && find . -type f) | while IFS= read -r file; do
        [[ -e "$dest/$file" ]] && continue
        mkdir -p "$(dirname "$dest/$file")" && cp -p "$src/$file" "$dest/$file" || exit 1
    done
}

# Fusionne un ancien dossier ~/.claude ($1) dans la config partagée
merge_claude() {
    local src="$1" dir
    for dir in projects file-history; do
        [[ -d "$src/$dir" ]] || continue
        copy_missing "$src/$dir" "$SHARED/$dir" || return 1
    done
    if [[ -f "$src/history.jsonl" ]]; then
        cat "$src/history.jsonl" >> "$SHARED/history.jsonl" || return 1
    fi
}

# --- Génération 1 : HOME dans l'ancien conteneur ------------------------------

# Conteneurs du projet dont /home/vscode n'est pas un montage
gen1_containers() {
    local id
    docker ps -aq --filter "label=devcontainer.local_folder=$DEVCONTAINER_LOCAL_FOLDER" 2>/dev/null |
        while IFS= read -r id; do
            [[ -n "$id" ]] || continue
            docker inspect "$id" 2>/dev/null | grep -q '"Destination": *"/home/vscode"' || echo "$id"
        done
}

# Copie /home/vscode/$2 du conteneur $1 vers $3. Un chemin absent du conteneur
# n'est pas une erreur : docker répond « Could not find the file » (ou « No such
# container:path » selon la version).
copy_from_container() {
    local error
    error="$(docker cp "$1:/home/vscode/$2" "$3" 2>&1 >/dev/null)" && return 0
    [[ "$error" == *"Could not find the file"* || "$error" == *"No such container:path"* ]]
}

# Récupère depuis le conteneur $1 les éléments listés, un par un : copier tout
# /home/vscode embarquerait aussi les montages (cache uv, plusieurs Go).
# Sous-shell : le dossier temporaire est supprimé à la sortie, quelle qu'elle soit.
migrate_container() (
    id="$1"
    stage="$(mktemp -d)" || exit 1
    trap 'rm -rf "$stage"' EXIT
    mkdir -p "$stage/.claude"
    for file in .claude/projects .claude/file-history .claude/history.jsonl; do
        copy_from_container "$id" "$file" "$stage/$file" || exit 1
    done
    merge_claude "$stage/.claude" || exit 1
    for file in .zsh_history .bash_history; do
        [[ -e "$PERSISTENT_HOME/$file" ]] && continue
        copy_from_container "$id" "$file" "$PERSISTENT_HOME/$file" || exit 1
    done
)

migrate_gen1() {
    command -v docker >/dev/null 2>&1 || return 0
    [[ -n "${DEVCONTAINER_LOCAL_FOLDER:-}" && ! -e "$CONTAINER_MARKER" ]] || return 0
    local containers=() id
    # Pas de mapfile : le bash de macOS (3.2) ne l'a pas
    while IFS= read -r id; do containers+=("$id"); done < <(gen1_containers)
    case "${#containers[@]}" in
        0) return 0 ;;
        1) ;;
        *)
            echo "⚠️  Plusieurs anciens conteneurs pour $WORKSPACE_FOLDER_BASENAME : ${containers[*]}"
            echo "   Historique non récupéré. Supprimez ceux à ne pas garder (docker rm <id>) puis rouvrez le conteneur,"
            echo "   ou sauvegardez à la main : $MIGRATION_DOC"
            echo "   Pour ne plus voir ce message : touch \"$CONTAINER_MARKER\""
            return 0 ;;
    esac
    mkdir -p "$PERSISTENT_HOME"
    if migrate_container "${containers[0]}"; then
        touch "$CONTAINER_MARKER"
        echo "✅ Historique Claude Code et du shell récupérés depuis le conteneur ${containers[0]}"
    else
        echo "⚠️  Récupération de l'historique du conteneur ${containers[0]} incomplète, nouvel essai à la prochaine ouverture"
    fi
}

migrate_gen1

# --- Génération 2 : ~/.claude dans le HOME persistant du projet ---------------

[[ -d "$OLD" && ! -e "$MARKER" ]] || exit 0

if merge_claude "$OLD" 2>/dev/null; then
    touch "$MARKER"
    echo "✅ Historique Claude Code de $WORKSPACE_FOLDER_BASENAME copié dans $SHARED"
else
    echo "⚠️  Migration de l'historique Claude Code incomplète, nouvel essai à la prochaine ouverture"
fi
exit 0
