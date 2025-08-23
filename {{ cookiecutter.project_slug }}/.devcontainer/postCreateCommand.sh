#!/bin/bash
# =============================================================================
# PyFoundry - Configuration avancée de l'environnement de développement
# =============================================================================
set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables du projet
PROJECT_PATH=$(pwd)
USE_UV="{{ cookiecutter.use_uv }}"
USE_NODE="{{ cookiecutter.use_node }}"
SETUP_GIT="{{ cookiecutter.setup_git }}"

# Fonctions utilitaires
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Timer pour mesurer les performances
start_time=$(date +%s)

echo "🚀 Configuration de l'environnement {{ cookiecutter.project_name }}"
echo "=================================================================="

# Mise à jour du système (optimisé)
log_info "Mise à jour des paquets système..."
sudo apt-get update -qq && sudo apt-get upgrade -y -qq
log_success "Système mis à jour"

# Installation d'uv avec optimisations
{% if cookiecutter.use_uv == "y" %}
log_info "Installation de uv..."
if command -v uv &> /dev/null; then
    log_warning "uv déjà installé"
else
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    # Ajouter au profil shell de manière robuste
    for shell_config in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if [[ -f "$shell_config" ]] && ! grep -q "/.local/bin" "$shell_config"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_config"
        fi
    done
fi
log_success "uv installé et configuré"
{% endif %}

# Installation Node.js conditionnelle
{% if cookiecutter.use_node == "y" %}
log_info "Vérification de Node.js..."
if command -v node &> /dev/null; then
    log_warning "Node.js déjà installé ($(node --version))"
else
    # Utilisation du feature devcontainer au lieu d'installation manuelle
    log_info "Node.js sera installé via les features devcontainer"
fi
{% endif %}

# Création et optimisation de l'environnement virtuel
log_info "Configuration de l'environnement Python..."

{% if cookiecutter.use_uv == "y" %}
# Créer avec uv
if [[ ! -d ".venv" ]]; then
    log_info "Création de l'environnement virtuel avec uv..."
    ~/.local/bin/uv venv .venv --python {{ cookiecutter.python_version }}
else
    log_warning "Environnement virtuel .venv existe déjà"
fi

# Activation et installation des dépendances
source .venv/bin/activate
log_info "Installation des dépendances avec uv..."
~/.local/bin/uv pip install -e .

# Installation des dépendances de développement
if [[ -f "pyproject.toml" ]] && grep -q "\[project.optional-dependencies\]" pyproject.toml; then
    log_info "Installation des dépendances de développement..."
    ~/.local/bin/uv pip install -e ".[dev]"
fi

# Génération du fichier de verrouillage pour reproductibilité
log_info "Génération du fichier de verrouillage..."
~/.local/bin/uv pip freeze > requirements.lock
~/.local/bin/uv export --format requirements-txt --output-file requirements-full.lock

{% else %}
# Créer avec venv standard
if [[ ! -d ".venv" ]]; then
    log_info "Création de l'environnement virtuel avec python..."
    python -m venv .venv
else
    log_warning "Environnement virtuel .venv existe déjà"
fi

source .venv/bin/activate
log_info "Installation des dépendances avec pip..."
pip install --upgrade pip
pip install -e .

# Installation des dépendances de développement
if [[ -f "pyproject.toml" ]] && grep -q "\[project.optional-dependencies\]" pyproject.toml; then
    log_info "Installation des dépendances de développement..."
    pip install -e ".[dev]"
fi

# Génération du fichier de verrouillage
log_info "Génération du fichier de verrouillage..."
pip freeze > requirements.lock
{% endif %}

# Configuration automatique de l'activation
log_info "Configuration de l'activation automatique..."
for shell_config in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [[ -f "$shell_config" ]] && ! grep -q "source $PROJECT_PATH/.venv/bin/activate" "$shell_config"; then
        echo "source $PROJECT_PATH/.venv/bin/activate" >> "$shell_config"
    fi
done

log_success "Environnement Python configuré"

# Configuration des variables d'environnement
log_info "Configuration des variables d'environnement..."
if [[ -f ".env.template" ]] && [[ ! -f ".env" ]]; then
    cp .env.template .env
    log_success "Fichier .env créé depuis le template"
else
    log_warning "Fichier .env existe déjà ou template non trouvé"
fi

# Création des dossiers de structure de projet
log_info "Création de la structure de projet..."
mkdir -p data/{raw,processed,external} models logs reports .jupyter/{data,runtime}
mkdir -p notebooks/{exploratory,preprocessing,modeling,reporting}

# Configuration Git avancée
{% if cookiecutter.setup_git == "y" %}
log_info "Configuration Git avancée..."
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.autocrlf input
git config --global core.safecrlf true

# Créer .gitignore si inexistant
if [[ ! -f ".gitignore" ]]; then
    cat > .gitignore << 'EOF'
# Environnement
.env
.venv/
__pycache__/
*.pyc
*.pyo

# Données sensibles
data/raw/
*.csv
*.xlsx
*.parquet
!data/external/.gitkeep

# Modèles entraînés
models/*.pkl
models/*.joblib
models/*.h5

# Jupyter
.ipynb_checkpoints/
.jupyter/

# Logs
logs/
*.log

# IDE
.vscode/settings.json
.idea/

# Système
.DS_Store
Thumbs.db
EOF
    log_success ".gitignore créé"
fi

# Initialiser le dépôt si nécessaire
if [[ ! -d ".git" ]]; then
    git init
    git add .
    git commit -m "Initial commit: {{ cookiecutter.project_name }} project setup

    🚀 Project initialized with PyFoundry template
    - Python {{ cookiecutter.python_version }}
    {% if cookiecutter.use_uv == "y" %}- uv package manager{% endif %}
    - Dev containers support
    - Jupyter notebooks ready
    "
    log_success "Dépôt Git initialisé"
fi
{% endif %}

# Configuration Jupyter avancée
log_info "Configuration de Jupyter..."
if command -v jupyter &> /dev/null; then
    # Créer la configuration Jupyter personnalisée
    mkdir -p .jupyter
    cat > .jupyter/jupyter_lab_config.py << 'EOF'
# Configuration Jupyter Lab pour {{ cookiecutter.project_name }}
c = get_config()

c.ServerApp.root_dir = '/workspaces/{{ cookiecutter.project_slug }}'
c.ServerApp.notebook_dir = '/workspaces/{{ cookiecutter.project_slug }}/notebooks'
c.ServerApp.open_browser = False
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.allow_root = True
c.ServerApp.token = ''
c.ServerApp.password = ''

# Extensions et thèmes
c.LabApp.default_url = '/lab'
c.LabApp.collaborative = True
EOF
    log_success "Configuration Jupyter créée"
fi

# Vérification finale et diagnostics
log_info "Vérification de l'installation..."
errors=0

# Vérifier Python et packages
if ! python -c "import sys; print(f'Python {sys.version}')" 2>/dev/null; then
    log_error "Python non accessible"
    ((errors++))
fi

# Vérifier les packages critiques
for package in "pandas" "numpy" "jupyter"; do
    if ! python -c "import $package" 2>/dev/null; then
        log_warning "Package $package non installé"
    fi
done

# Afficher les informations de l'environnement
log_info "Informations de l'environnement:"
echo "  - Projet: {{ cookiecutter.project_name }}"
echo "  - Python: $(python --version 2>/dev/null || echo 'Non accessible')"
{% if cookiecutter.use_uv == "y" %}
echo "  - uv: $(~/.local/bin/uv --version 2>/dev/null || echo 'Non accessible')"
{% endif %}
echo "  - Packages installés: $(pip list | wc -l) packages"
echo "  - Espace disque .venv: $(du -sh .venv 2>/dev/null | cut -f1 || echo 'N/A')"

# Temps d'exécution
end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
echo "=================================================================="
if [[ $errors -eq 0 ]]; then
    log_success "Environnement configuré avec succès en ${duration}s !"
    echo ""
    echo "🎯 Prochaines étapes:"
    echo "   1. Redémarrez le terminal (Ctrl+Shift+P > 'Terminal: Create New Terminal')"
    echo "   2. Vérifiez l'activation: echo \$VIRTUAL_ENV"
    echo "   3. Lancez Jupyter: jupyter lab"
    echo "   4. Commencez à coder! 🎉"
else
    log_warning "Configuration terminée avec $errors erreurs"
    echo "   Vérifiez les logs ci-dessus"
fi

echo ""
echo "📚 Documentation: https://castorfou.github.io/PyFoundry/user/usage/"
echo "🐛 Support: https://github.com/castorfou/PyFoundry/issues"