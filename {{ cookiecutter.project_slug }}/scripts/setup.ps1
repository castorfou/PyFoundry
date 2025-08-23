# =============================================================================
# PyFoundry - Script de Setup Automatisé Windows PowerShell
# =============================================================================

param(
    [switch]$Force = $false
)

# Configuration
$ProjectName = "{{ cookiecutter.project_name }}"
$PythonVersion = "{{ cookiecutter.python_version }}"
$UseNode = "{{ cookiecutter.use_node }}"
$SetupGit = "{{ cookiecutter.setup_git }}"

# Couleurs pour les logs
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
}

# Fonctions utilitaires
function Write-Info($Message) {
    Write-Host "ℹ️  $Message" -ForegroundColor $Colors.Blue
}

function Write-Success($Message) {
    Write-Host "✅ $Message" -ForegroundColor $Colors.Green
}

function Write-Warning($Message) {
    Write-Host "⚠️  $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error($Message) {
    Write-Host "❌ $Message" -ForegroundColor $Colors.Red
}

# Vérification des prérequis
function Test-Prerequisites {
    Write-Info "Vérification des prérequis..."
    
    # Vérifier Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Python n'est pas installé ou accessible"
            exit 1
        }
        
        $currentVersion = ($pythonVersion -replace "Python ", "").Split('.')[0..1] -join '.'
        $requiredVersion = $PythonVersion.Split('.')[0..1] -join '.'
        
        if ([version]$currentVersion -lt [version]$requiredVersion) {
            Write-Error "Python $PythonVersion+ requis, $currentVersion trouvé"
            exit 1
        }
        
        Write-Success "Python $currentVersion OK"
    }
    catch {
        Write-Error "Erreur lors de la vérification Python: $_"
        exit 1
    }
}

# Installation d'uv
function Install-Uv {
    Write-Info "Installation de uv..."
    
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Warning "uv déjà installé"
    }
    else {
        try {
            # Installation via PowerShell
            irm https://astral.sh/uv/install.ps1 | iex
            
            # Ajouter au PATH pour la session courante
            $uvPath = "$env:USERPROFILE\.local\bin"
            $env:PATH = "$uvPath;$env:PATH"
            
            Write-Success "uv installé"
        }
        catch {
            Write-Error "Erreur lors de l'installation d'uv: $_"
            exit 1
            }
        }
    }
}

# Installation de Node.js
function Install-Node {
    if ($UseNode -eq "y") {
        Write-Info "Installation de Node.js..."
        
        if (Get-Command node -ErrorAction SilentlyContinue) {
            Write-Warning "Node.js déjà installé"
        }
        else {
            Write-Warning "Veuillez installer Node.js manuellement depuis https://nodejs.org"
            Write-Warning "Ou utilisez Chocolatey: choco install nodejs"
            Write-Warning "Ou utilisez Scoop: scoop install nodejs"
        }
    }
}

# Création de l'environnement virtuel
function New-VirtualEnv {
    Write-Info "Création de l'environnement virtuel..."
    
    if (Test-Path ".venv") {
        if ($Force) {
            Write-Warning "Suppression de l'environnement existant..."
            Remove-Item -Recurse -Force .venv
        }
        else {
            Write-Warning "Environnement virtuel .venv existe déjà"
            $response = Read-Host "Voulez-vous le recréer ? (y/N)"
            if ($response -match "^[Yy]$") {
                Remove-Item -Recurse -Force .venv
            }
            else {
                Write-Info "Réutilisation de l'environnement existant"
                return
            }
        }
    }
    
    try {
        & "$env:USERPROFILE\.local\bin\uv" venv .venv --python $PythonVersion
        Write-Success "Environnement virtuel créé"
    }
    catch {
        Write-Error "Erreur lors de la création de l'environnement virtuel: $_"
        exit 1
    }
}

# Installation des dépendances
function Install-Dependencies {
    Write-Info "Installation des dépendances..."
    
    try {
        # Activation de l'environnement virtuel
        & .\.venv\Scripts\Activate.ps1
        
        & "$env:USERPROFILE\.local\bin\uv" pip install -e .
        # Générer requirements.lock pour reproductibilité
        & "$env:USERPROFILE\.local\bin\uv" pip freeze | Out-File -FilePath "requirements.lock" -Encoding UTF8
        
        Write-Success "Dépendances installées"
    }
    catch {
        Write-Error "Erreur lors de l'installation des dépendances: $_"
        exit 1
    }
}

# Configuration Git
function Set-GitConfig {
    if ($SetupGit -eq "y") {
        Write-Info "Configuration Git..."
        
        try {
            git config --global init.defaultBranch main
            git config --global pull.rebase false
            
            if (-not (Test-Path ".git")) {
                git init
                git add .
                git commit -m "Initial commit: $ProjectName project setup"
            }
            
            Write-Success "Git configuré"
        }
        catch {
            Write-Warning "Erreur lors de la configuration Git: $_"
        }
    }
}

# Configuration des variables d'environnement
function Set-EnvVars {
    Write-Info "Configuration des variables d'environnement..."
    
    if (-not (Test-Path ".env")) {
        $envContent = @"
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
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "Fichier .env créé"
    }
    else {
        Write-Warning "Fichier .env existe déjà"
    }
}

# Script principal
function Main {
    Write-Host "🚀 Configuration de $ProjectName" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    
    Test-Prerequisites
    Install-Uv
    Install-Node
    New-VirtualEnv
    Install-Dependencies
    Set-GitConfig
    Set-EnvVars
    
    Write-Host ""
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Success "Setup terminé avec succès !"
    Write-Host ""
    Write-Host "📝 Prochaines étapes:" -ForegroundColor Cyan
    Write-Host "   1. Activez l'environnement: .\.venv\Scripts\Activate.ps1"
    Write-Host "   2. Ouvrez dans VS Code: code ."
    Write-Host "   3. Commencez à développer! 🎉"
    Write-Host ""
    Write-Host "📚 Documentation: https://castorfou.github.io/PyFoundry" -ForegroundColor Cyan
}

# Exécution si appelé directement
if ($MyInvocation.InvocationName -ne '.') {
    Main
}