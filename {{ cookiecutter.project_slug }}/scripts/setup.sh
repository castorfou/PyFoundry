#!/bin/bash
# =============================================================================
# PyFoundry - Script de Setup Automatisé Linux/macOS
# =============================================================================
set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="{{ cookiecutter.project_name }}"
PYTHON_VERSION="{{ cookiecutter.python_version }}"
USE_NODE="{{ cookiecutter.use_node }}"
SETUP_GIT="{{ cookiecutter.setup_git }}"

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Détection du système d'exploitation
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    log_info "Système détecté: $OS"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier Python
    if ! command -v python &> /dev/null; then
        log_error "Python n'est pas installé"
        exit 1
    fi
    
    PYTHON_CURRENT=$(python --version | grep -oE '[0-9]+\.[0-9]+')
    PYTHON_REQUIRED=$(echo "$PYTHON_VERSION" | grep -oE '[0-9]+\.[0-9]+')
    
    if [[ "$(printf '%s\n' "$PYTHON_REQUIRED" "$PYTHON_CURRENT" | sort -V | head -n1)" != "$PYTHON_REQUIRED" ]]; then
        log_error "Python $PYTHON_VERSION+ requis, $PYTHON_CURRENT trouvé"
        exit 1
    fi
    
    log_success "Python $PYTHON_CURRENT OK"
}

# Installation d'uv
install_uv() {
    log_info "Installation de uv..."
    if command -v uv &> /dev/null; then
        log_warning "uv déjà installé"
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        # Ajouter au profil shell
        if [[ -f "$HOME/.bashrc" ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        fi
        if [[ -f "$HOME/.zshrc" ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        fi
    fi
    log_success "uv installé"
}

# Installation de Node.js
install_node() {
    if [[ "$USE_NODE" == "y" ]]; then
        log_info "Installation de Node.js..."
        if command -v node &> /dev/null; then
            log_warning "Node.js déjà installé"
        else
            if [[ "$OS" == "linux" ]]; then
                curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                sudo apt-get install -y nodejs
            elif [[ "$OS" == "macos" ]]; then
                if command -v brew &> /dev/null; then
                    brew install node
                else
                    log_error "Homebrew requis pour installer Node.js sur macOS"
                    exit 1
                fi
            fi
        fi
        log_success "Node.js installé"
    fi
}

# Création de l'environnement virtuel
create_venv() {
    log_info "Création de l'environnement virtuel..."
    
    if [[ -d ".venv" ]]; then
        log_warning "Environnement virtuel .venv existe déjà"
        read -p "Voulez-vous le recréer ? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf .venv
        else
            log_info "Réutilisation de l'environnement existant"
            return
        fi
    fi
    
    ~/.local/bin/uv venv .venv --python $PYTHON_VERSION
    
    log_success "Environnement virtuel créé"
}

# Installation des dépendances
install_dependencies() {
    log_info "Installation des dépendances..."
    
    # Activation de l'environnement virtuel
    source .venv/bin/activate
    
    ~/.local/bin/uv pip install -e .
    # Générer requirements.lock pour reproductibilité
    ~/.local/bin/uv pip freeze > requirements.lock
    
    log_success "Dépendances installées"
}

# Configuration Git
setup_git() {
    if [[ "$SETUP_GIT" == "y" ]]; then
        log_info "Configuration Git..."
        git config --global init.defaultBranch main
        git config --global pull.rebase false
        
        if [[ ! -d ".git" ]]; then
            git init
            git add .
            git commit -m "Initial commit: $PROJECT_NAME project setup"
        fi
        
        log_success "Git configuré"
    fi
}

# Configuration des variables d'environnement
setup_env_vars() {
    log_info "Configuration des variables d'environnement..."
    
    if [[ ! -f ".env" ]]; then
        cat > .env << EOF
# Configuration du projet {{ cookiecutter.project_name }}
PROJECT_NAME="{{ cookiecutter.project_name }}"
PROJECT_SLUG="{{ cookiecutter.project_slug }}"
PYTHON_VERSION="{{ cookiecutter.python_version }}"

# Dossiers de données
DATA_DIR=./data
NOTEBOOKS_DIR=./notebooks
SRC_DIR=./src

# Configuration Jupyter
JUPYTER_CONFIG_DIR=./.jupyter
JUPYTER_DATA_DIR=./.jupyter/data

# Variables d'environnement personnalisées
# Ajoutez vos variables ici...
EOF
        log_success "Fichier .env créé"
    else
        log_warning "Fichier .env existe déjà"
    fi
}

# Script principal
main() {
    echo "🚀 Configuration de $PROJECT_NAME"
    echo "================================="
    
    detect_os
    check_prerequisites
    install_uv
    install_node
    create_venv
    install_dependencies
    setup_git
    setup_env_vars
    
    echo ""
    echo "================================="
    log_success "Setup terminé avec succès !"
    echo ""
    echo "📝 Prochaines étapes:"
    echo "   1. Activez l'environnement: source .venv/bin/activate"
    echo "   2. Ouvrez dans VS Code: code ."
    echo "   3. Commencez à développer! 🎉"
    echo ""
    echo "📚 Documentation: https://castorfou.github.io/PyFoundry"
}

# Exécution si appelé directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi