#!/bin/bash
# =============================================================================
# PyFoundry - Configuration de l'environnement de développement
# =============================================================================
set -e

PYTHON_VERSION="{{ cookiecutter.python_version }}"

echo "🚀 Configuration de l'environnement {{ cookiecutter.project_name }}"
echo "=================================================================="

# Mise à jour du système
update_system() {
    echo "Mise à jour des paquets système..."
    sudo apt-get update -qq
    sudo apt-get upgrade -y -qq
    echo "Système mis à jour"
}

# Installation d'uv
install_uv() {
    echo "Installation de uv..."
    if command -v uv &> /dev/null; then
        echo "uv déjà installé"
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
    echo "uv installé"
}

# Création de l'environnement Python
create_python_environment() {
    echo "Configuration de l'environnement Python $PYTHON_VERSION ..."
    
    if [[ ! -d ".venv" ]]; then
        echo "Création de l'environnement virtuel..."
        ~/.local/bin/uv venv .venv --python $PYTHON_VERSION
    else
        echo "Environnement virtuel existe déjà"
    fi
    
    source .venv/bin/activate
    echo "Installation des dépendances..."
    ~/.local/bin/uv pip install -e .
    
    if [[ -f "pyproject.toml" ]] && grep -q "\[project.optional-dependencies\]" pyproject.toml; then
        echo "Installation des dépendances de développement..."
        ~/.local/bin/uv pip install -e ".[dev]"
    fi
    
    echo "Génération du fichier de verrouillage..."
    ~/.local/bin/uv pip freeze > requirements.lock
    
    echo "Configuration de l'activation automatique..."
    PROJECT_PATH=$(pwd)
    for shell_config in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if [[ -f "$shell_config" ]] && ! grep -q "source $PROJECT_PATH/.venv/bin/activate" "$shell_config"; then
            echo "source $PROJECT_PATH/.venv/bin/activate" >> "$shell_config"
        fi
    done
    
    echo "Environnement Python configuré"
}

# Exécution des étapes
update_system
install_uv
create_python_environment

echo ""
echo "=================================================================="
echo "✅ Configuration terminée !"
echo "Redémarrez le terminal pour activer l'environnement"