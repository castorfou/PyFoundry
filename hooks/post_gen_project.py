#!/usr/bin/env python3
"""
Hook Cookiecutter - Information post-génération
Fournit des instructions pour configurer le devcontainer
"""
import subprocess
import sys
import os

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

def check_ghcr_auth():
    """Teste l'authentification à ghcr.io."""
    print("🔍 Vérification de l'authentification ghcr.io...")
    
    try:
        # Tenter un login avec des credentials vides pour tester l'état
        result = subprocess.run(
            ["docker", "login", "ghcr.io", "--password-stdin", "--username", "test"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Analyser la sortie
        output = result.stderr.lower() + result.stdout.lower()
        
        if "login succeeded" in output:
            print("✅ Déjà connecté à ghcr.io")
            return True
        elif "unauthorized" in output or "authentication required" in output:
            print("❌ Non connecté à ghcr.io")
            return False
        else:
            # État incertain, assumons non connecté
            print("⚠️  État d'authentification incertain")
            return False
            
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("❌ Impossible de vérifier l'authentification")
        return False

def show_setup_info(docker_available, ghcr_auth):
    """Affiche les informations de configuration."""
    print("\n" + "="*70)
    print("📋 PROCHAINES ÉTAPES")
    print("="*70)
    
    if docker_available:
        if ghcr_auth:
            print("🚀 Tout est prêt !")
            print("")
            print("Ouvrez le projet dans VS Code :")
            print("   code .")
            print("   VS Code proposera 'Reopen in Container'")
        else:
            print("🔧 Configuration requise pour ghcr.io")
            print("")
            print("1. Créez un Personal Access Token GitHub :")
            print("   https://github.com/settings/tokens/new")
            print("   Permissions requis : read:packages")
            print("")
            print("2. Connectez-vous à ghcr.io :")
            print("   docker login ghcr.io -u VOTRE_USERNAME")
            print("   (utilisez le token comme mot de passe)")
            print("")
            print("3. Ouvrez le projet dans VS Code :")
            print("   code .")
            print("   VS Code proposera 'Reopen in Container'")
    else:
        print("🔧 Installation avec uv")
        print("")
        print("Docker non disponible - consultez le README.md")
        print("pour les instructions d'installation manuelle avec uv")
        print("")
    
    print("="*70)

def main():
    """Fonction principale du hook."""
    print(f"🚀 Projet {{ cookiecutter.project_name }} créé avec succès !")
    
    docker_available = check_docker_available()
    ghcr_auth = False
    
    if docker_available:
        ghcr_auth = check_ghcr_auth()
        
        if not ghcr_auth:
            # Vérifier si l'utilisateur veut forcer la création
            force_create = os.environ.get('PYFOUNDRY_FORCE_CREATE', '').lower() in ['1', 'true', 'yes']
            
            if not force_create:
                print("\n" + "="*70)
                print("❌ ERREUR : Authentification ghcr.io requise")
                print("="*70)
                print("Ce template utilise des features devcontainer de ghcr.io.")
                print("Vous devez être authentifié pour utiliser le devcontainer.")
                print("")
                print("SOLUTIONS :")
                print("")
                print("Option 1 - S'authentifier maintenant :")
                print("1. Créez un Personal Access Token GitHub :")
                print("   https://github.com/settings/tokens/new")
                print("   Permissions requis : read:packages")
                print("")
                print("2. Connectez-vous à ghcr.io :")
                print("   docker login ghcr.io -u VOTRE_USERNAME")
                print("   (utilisez le token comme mot de passe)")
                print("")
                print("3. Relancez la création du projet :")
                print("   cruft create https://github.com/castorfou/PyFoundry.git")
                print("")
                print("Option 2 - Forcer la création (devcontainer ne marchera pas) :")
                print("   PYFOUNDRY_FORCE_CREATE=1 cruft create https://github.com/castorfou/PyFoundry.git")
                print("="*70)
                print("")
                print("🗑️  Suppression du projet non configuré...")
                sys.exit(1)  # Interrompt cruft et supprime le projet
            else:
                print("⚠️  Création forcée - devcontainer ne fonctionnera pas sans authentification ghcr.io")
    
    show_setup_info(docker_available, ghcr_auth)
    
    print("📚 Documentation : https://castorfou.github.io/PyFoundry")
    print("🐛 Support : https://github.com/castorfou/PyFoundry/issues")

if __name__ == "__main__":
    main()