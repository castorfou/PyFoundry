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
    export DEBIAN_FRONTEND=noninteractive
    # Empêcher tzdata de poser des questions et utiliser la timezone UTC par défaut
    export TZ="Etc/UTC"

    echo "Configuration de la source APT Yarn..."
    sudo mkdir -p /etc/apt/keyrings
    if [ ! -f /etc/apt/keyrings/yarn.gpg ]; then
        echo "Installation de la clé GPG Yarn..."
        curl -fsSL https://dl.yarnpkg.com/debian/pubkey.gpg \
            | sudo gpg --dearmor -o /etc/apt/keyrings/yarn.gpg
    fi
    echo "deb [signed-by=/etc/apt/keyrings/yarn.gpg] https://dl.yarnpkg.com/debian stable main" \
        | sudo tee /etc/apt/sources.list.d/yarn.list > /dev/null

    sudo apt-get update -qq

    # Options dpkg pour éviter les prompts de configuration
    sudo apt-get -y -qq -o Dpkg::Options::="--force-confdef" \
        -o Dpkg::Options::="--force-confnew" upgrade || {
        echo "⚠️  'apt upgrade' a échoué ; continuer sans interrompre le postCreateCommand"
        return 0
    }

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

{% if cookiecutter.use_node == "y" %}
# Configuration Node.js et npm
setup_node() {
    echo "Configuration Node.js..."
    
    # Vérification de l'installation de Node.js
    if command -v node &> /dev/null; then
        echo "✅ Node.js disponible ($(node --version))"
        echo "✅ npm disponible ($(npm --version))"
        
        # Création d'un package.json basique s'il n'existe pas
        if [ ! -f "package.json" ]; then
            echo "Création du fichier package.json..."
            cat > package.json << EOF
{
  "name": "{{ cookiecutter.project_slug }}",
  "version": "1.0.0",
  "description": "{{ cookiecutter.description }}",
  "scripts": {
    "dev": "echo 'Add your development scripts here'",
    "build": "echo 'Add your build scripts here'"
  },
  "keywords": ["data-science", "python", "node"],
  "author": "{{ cookiecutter.github_username }}",
  "license": "MIT",
  "devDependencies": {}
}
EOF
            echo "✅ package.json créé"
        fi
        
        echo "Configuration npm terminée"
    else
        echo "⚠️  Node.js non disponible - vérifiez la configuration devcontainer"
    fi
}
{% endif %}

# Configuration Git et GitHub
setup_git() {
    echo "Configuration Git..."
    
    # Initialisation du dépôt si pas encore fait
    if [ ! -d ".git" ]; then
        echo "Initialisation du dépôt Git..."
        git init --initial-branch=main
        
        # Création du commit initial
        echo "Création du commit initial..."
        git add .
        git commit -m "Initial commit: PyFoundry project setup

Project: {{ cookiecutter.project_name }}
Template: PyFoundry v0.3
Features: ruff, mypy, pre-commit hooks"
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

        # choisir le protocole: SSH si possible, sinon HTTPS
        if ssh -o BatchMode=yes -T git@github.com 2>&1 | grep -iq "successfully authenticated"; then
            remote_url="git@github.com:{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}.git"
        else
            remote_url="https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}.git"
        fi

        echo "Configuration du remote GitHub : $remote_url"
        git remote get-url origin >/dev/null 2>&1 || git remote add origin "$remote_url"
        
        # Configuration de l'upstream pour la branche main
        git branch --set-upstream-to=origin/main main 2>/dev/null || true
        
        # Configuration automatique des upstream pour futures branches (local au projet)
        git config push.autoSetupRemote true
        
        # Configuration de l'authentification GitHub avec gh CLI
        if command -v gh &> /dev/null; then
            echo "Configuration de l'authentification GitHub..."
            if ! gh auth status &>/dev/null; then
                echo "🔐 Authentification GitHub requise pour push/pull"
                echo "Lancement de l'authentification..."
                echo ""
                echo "ℹ️  Note : Vous devrez appuyer sur Entrée pour 'ouvrir' le navigateur."
                echo "   Le navigateur ne s'ouvrira pas (limitation devcontainer connue)."
                echo "   → Entrez manuellement l'URL et le code dans votre navigateur host."
                echo ""
                gh auth login --git-protocol https --web
                
                # Configuration du credential helper après authentification (local au projet)
                if gh auth status &>/dev/null; then
                    echo "Configuration du credential helper Git..."
                    git config credential.helper ""
                    git config credential."https://github.com".helper "!gh auth git-credential"
                    echo "✅ Credential helper configuré"
                fi
            else
                echo "✅ Déjà authentifié sur GitHub"
            fi
        fi
        
        echo "✅ Remote GitHub configuré"
    fi
    
    echo "Configuration Git terminée"
}

# Exécution des étapes
update_system
ensure_uv
create_python_environment
{% if cookiecutter.use_node == "y" %}setup_node
{% endif %}setup_git

echo ""
echo "=================================================================="
echo "✅ Configuration terminée !"
echo "Dépôt Git initialisé avec pre-commit hooks"
{% if cookiecutter.use_node == "y" %}echo "Node.js et npm configurés pour le développement frontend"
{% endif %}echo "Redémarrez le terminal pour activer l'environnement"