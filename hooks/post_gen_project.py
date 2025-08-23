#!/usr/bin/env python3
"""
Hook Cookiecutter - Information post-génération
Fournit des instructions pour configurer le devcontainer
"""
import subprocess
import sys

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

def show_setup_info(docker_available):
    """Affiche les informations de configuration."""
    print("\n" + "="*70)
    print("📋 PROCHAINES ÉTAPES")
    print("="*70)
    
    if docker_available:
        print("🐳 Devcontainer VS Code (Recommandé)")
        print("")
        print("Ce projet utilise des features devcontainer avec uv.")
        print("Si VS Code échoue à construire le devcontainer :")
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
        print("")
        print("Alternative : Installation manuelle avec uv")
        print("Consultez le README.md pour les instructions détaillées")
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
    show_setup_info(docker_available)
    
    print("📚 Documentation : https://castorfou.github.io/PyFoundry")
    print("🐛 Support : https://github.com/castorfou/PyFoundry/issues")

if __name__ == "__main__":
    main()