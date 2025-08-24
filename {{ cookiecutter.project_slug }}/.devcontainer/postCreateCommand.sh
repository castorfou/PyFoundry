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

# Vérification et installation d'uv (priorité: devcontainer feature, fallback: installation manuelle)
ensure_uv() {
    echo "Vérification de uv..."
    if command -v uv &> /dev/null; then
        echo "✅ uv disponible ($(uv --version))"
        return 0
    fi
    
    echo "❌ Échec d'installation d'uv"
    echo "   Vérifiez votre connexion Docker/ghcr.io (docker login ghcr.io)"
    exit 1
}

# Création de l'environnement Python
create_python_environment() {
    echo "Configuration de l'environnement Python $PYTHON_VERSION ..."

    echo "Création de l'environnement virtuel..."
    uv venv .venv --python $PYTHON_VERSION
    
    source .venv/bin/activate
    echo "Installation des dépendances..."
    uv pip install -e .
    
    if [[ -f "pyproject.toml" ]] && grep -q "\[project.optional-dependencies\]" pyproject.toml; then
        echo "Installation des dépendances de développement..."
        uv pip install -e ".[dev]"
    fi
    
    echo "Génération du fichier de verrouillage..."
    uv pip freeze > requirements.lock
    
    echo "Configuration de l'activation automatique..."
    PROJECT_PATH=$(pwd)
    for shell_config in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if [[ -f "$shell_config" ]] && ! grep -q "source $PROJECT_PATH/.venv/bin/activate" "$shell_config"; then
            echo "source $PROJECT_PATH/.venv/bin/activate" >> "$shell_config"
        fi
    done
    
    echo "Environnement Python configuré"
}

# Configuration Git et GitHub
setup_git() {
    echo "Configuration Git..."
    
    # Initialisation du dépôt si pas encore fait
    if [ ! -d ".git" ]; then
        echo "Initialisation du dépôt Git..."
        git init --initial-branch=main
        
        # Création du commit initial si applicable
        if [ "{{ cookiecutter.setup_git }}" = "y" ]; then
            echo "Création du commit initial..."
            git add .
            git commit -m "Initial commit: PyFoundry project setup

Project: {{ cookiecutter.project_name }}
Template: PyFoundry v0.3
Features: ruff, mypy, pre-commit hooks"
        fi
    fi
    
    # Configuration pre-commit si disponible
    if [ -f ".pre-commit-config.yaml" ]; then
        echo "Configuration des hooks pre-commit..."
        if command -v pre-commit &> /dev/null; then
            echo "Mise à jour des hooks vers les dernières versions..."
            pre-commit autoupdate
            pre-commit install
            
            echo "Pré-installation des environnements pre-commit..."
            # Force l'installation des environnements maintenant pour éviter les délais futurs
            pre-commit install-hooks
            
            # Commiter les changements de pre-commit autoupdate + corrections formatage
            if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
                echo "Commit des mises à jour et corrections pre-commit..."
                git add .pre-commit-config.yaml
                
                # Correction du formatage par les hooks peut générer des changements
                if ! git commit -m "chore: update pre-commit hooks to latest versions" 2>/dev/null; then
                    # Si le commit échoue à cause des hooks, ajouter les corrections
                    echo "Ajout des corrections de formatage..."
                    git add .
                    git commit -m "chore: update pre-commit hooks and fix formatting" || true
                fi
            fi
            
            echo "✅ Pre-commit hooks installés et mis à jour"
        else
            echo "⚠️  pre-commit non installé, ignoré"
        fi
    fi
    
    # Configuration du remote GitHub si username fourni
    if [ "{{ cookiecutter.github_username }}" != "votre-username" ]; then
        echo "Configuration du remote GitHub..."
        git remote add origin "https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}.git"
        
        # Configuration de l'authentification GitHub avec gh CLI
        if command -v gh &> /dev/null; then
            echo "Configuration de l'authentification GitHub..."
            echo "Utilisez 'gh auth login' pour vous authentifier"
        fi
        
        echo "✅ Remote GitHub configuré"
    fi
    
    echo "Configuration Git terminée"
}

# Exécution des étapes
update_system
ensure_uv
create_python_environment
setup_git

echo ""
echo "=================================================================="
echo "✅ Configuration terminée !"
echo "Dépôt Git initialisé avec pre-commit hooks"
echo "Redémarrez le terminal pour activer l'environnement"