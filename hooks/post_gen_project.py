#!/usr/bin/env python3
"""
Hook Cookiecutter - Vérification post-génération
Vérifie l'accès à ghcr.io pour les features devcontainer
"""
import subprocess
import sys
import os

# Image de test publique sur ghcr.io 
TEST_IMAGE = "ghcr.io/devcontainers/features/common-utils:2"

def check_docker_available():
    """Vérifie si Docker est disponible."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Docker disponible: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker n'est pas installé ou accessible")
        print("   Installez Docker Desktop pour utiliser les devcontainers")
        return False

def check_docker_auth():
    """Vérifie l'accès à ghcr.io en tentant de pull une image publique."""
    print(f"🔍 Vérification de l'accès à ghcr.io...")
    
    try:
        # Tentative de pull d'une image publique
        result = subprocess.run(
            ["docker", "pull", TEST_IMAGE],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Accès à ghcr.io confirmé")
        
        # Nettoyage de l'image de test
        subprocess.run(
            ["docker", "rmi", TEST_IMAGE], 
            capture_output=True
        )
        return True
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.lower()
        
        if "denied" in error_msg or "authentication required" in error_msg:
            print("\n" + "="*70)
            print("⚠️  ATTENTION : Authentification ghcr.io requise")
            print("="*70)
            print("Les features devcontainer nécessitent un accès à ghcr.io.")
            print("Veuillez vous connecter avant d'ouvrir le devcontainer :")
            print("")
            print("1. Créez un Personal Access Token sur GitHub :")
            print("   https://github.com/settings/tokens/new")
            print("   Permissions : read:packages")
            print("")
            print("2. Connectez-vous à ghcr.io :")
            print("   docker login ghcr.io -u VOTRE_USERNAME")
            print("   (utilisez le token comme mot de passe)")
            print("")
            print("3. Ensuite ouvrez le projet dans VS Code")
            print("="*70 + "\n")
            return False
            
        else:
            print(f"❌ Erreur Docker inattendue: {e.stderr}")
            return False

def main():
    """Fonction principale du hook."""
    print(f"🚀 Configuration du projet {{ cookiecutter.project_name }}")
    print("="*50)
    
    # Vérification Docker
    if not check_docker_available():
        print("ℹ️  Ce projet utilise des devcontainers VS Code")
        print("   Docker est requis pour cette fonctionnalité")
        return
    
    # Vérification ghcr.io
    if check_docker_auth():
        print("✅ Tout est prêt ! Vous pouvez ouvrir le projet dans VS Code")
        print("   VS Code proposera d'ouvrir dans un devcontainer")
    else:
        print("ℹ️  Vous pouvez également utiliser l'installation locale")
        print("   Exécutez: pip install -e . dans un environnement virtuel")
    
    print("")
    print("📚 Documentation : https://castorfou.github.io/PyFoundry")
    print("="*50)

if __name__ == "__main__":
    main()