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
    try:
        # Tenter un login avec des credentials vides pour tester l'état
        result = subprocess.run(
            ["docker", "login", "ghcr.io", "--password-stdin", "--username", "test"],
            input="",
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Analyser la sortie
        output = result.stderr.lower() + result.stdout.lower()
        
        if "login succeeded" in output:
            return True
        else:
            return False
            
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

def handle_auth_failure():
    """Gère l'échec d'authentification - interrompt ou continue selon FORCE_CREATE."""
    force_create = os.environ.get('PYFOUNDRY_FORCE_CREATE', '').lower() in ['1', 'true', 'yes']
    
    if not force_create:
        print("\n❌ Authentification ghcr.io requise pour les devcontainers")
        print("\n1. Connectez-vous : docker login ghcr.io -u USERNAME")
        print("2. Relancez : cruft create ...")
        print("\nOu forcez : PYFOUNDRY_FORCE_CREATE=1 cruft create ...")
        sys.exit(1)
    else:
        print("⚠️  Création forcée - devcontainer ne fonctionnera pas")
        return True


def main():
    """Fonction principale du hook."""
    docker_available = check_docker_available()
    ghcr_auth = False
    
    if docker_available:
        ghcr_auth = check_ghcr_auth()
        
        if not ghcr_auth:
            handle_auth_failure()
        else:
            print("✅ Prêt pour devcontainer VS Code")
    else:
        print("ℹ️  Consultez le README.md pour l'installation locale")
    
    print("\n📚 Documentation : https://castorfou.github.io/PyFoundry")

if __name__ == "__main__":
    main()