#!/usr/bin/env bash
# =============================================================================
# Nettoyage complet d'un projet de test du template (issue #92)
# Usage : bash scripts/clean_test_project.sh <dossier du projet>
#
# Supprimer le dossier n'arrête pas son devcontainer : il continue à tourner,
# orphelin. Ce script supprime, dans cet ordre :
#   1. le conteneur, retrouvé par le label devcontainer.local_folder ;
#   2. le dossier du projet ;
#   3. son HOME persistant, ~/.devcontainer/homes/<dossier>-<devcontainerId>.
# À lancer sur l'hôte : dans le devcontainer PyFoundry, docker est absent et le
# script donne la commande à lancer sur l'hôte.
# =============================================================================

DOCKER="${CLEAN_TEST_PROJECT_DOCKER:-docker}"

if [ $# -ne 1 ] || [ -z "$1" ]; then
    echo "Usage : $0 <dossier du projet de test>" >&2
    exit 1
fi

# Chemin absolu, tel que VS Code l'enregistre dans le label (même si le dossier
# a déjà été supprimé)
if [ -d "$1" ]; then
    PROJECT="$(cd "$1" && pwd)"
elif [[ "$1" = /* ]]; then
    PROJECT="${1%/}"
else
    PROJECT="$PWD/${1%/}"
fi

if [ -z "$PROJECT" ] || [ "$PROJECT" = "/" ] || [ "$PROJECT" = "$(cd "$HOME" && pwd)" ]; then
    echo "❌ Refusé : '$1' n'est pas un dossier de projet de test" >&2
    exit 1
fi

NAME="$(basename "$PROJECT")"
LABEL="label=devcontainer.local_folder=$PROJECT"
status=0
removed=0

# 1. Conteneur, avant le dossier
if command -v "$DOCKER" > /dev/null 2>&1; then
    containers="$("$DOCKER" ps -aq --filter "$LABEL")"
    if [ -n "$containers" ]; then
        # shellcheck disable=SC2086 # un ID par mot
        if "$DOCKER" rm -f $containers > /dev/null; then
            echo "🐳 Conteneur supprimé : $(echo $containers)"
            removed=1
        else
            echo "❌ Échec de docker rm -f $(echo $containers)" >&2
            status=1
        fi
    fi
else
    echo "⚠️  docker introuvable : le conteneur n'est pas arrêté. Sur l'hôte, lancez :" >&2
    echo "    docker rm -f \$(docker ps -aq --filter \"$LABEL\")" >&2
fi

remove() {
    if rm -rf "$1" 2> /dev/null; then
        echo "🗑️  Supprimé : $1"
        removed=1
    else
        echo "❌ Suppression incomplète (dossiers root) : sudo rm -rf $1" >&2
        status=1
    fi
}

# 2. Dossier du projet
[ -e "$PROJECT" ] && remove "$PROJECT"

# 3. HOME persistant : <dossier>-<devcontainerId>, l'identifiant (base 32) n'a pas
# de tiret, ce qui exclut le HOME de <dossier>-2
for home in "$HOME/.devcontainer/homes/$NAME"-*; do
    [ -d "$home" ] || continue
    suffix="${home##*/"$NAME"-}"
    [[ "$suffix" == *-* ]] && continue
    remove "$home"
done

[ "$removed" -eq 0 ] && [ "$status" -eq 0 ] && echo "ℹ️  Rien à supprimer pour $PROJECT"
exit "$status"
