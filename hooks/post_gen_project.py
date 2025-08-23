#!/usr/bin/env python3
"""
Hook Cookiecutter - Vérifications post-génération pour le Dev Container.
"""
import subprocess
import sys
import os
import shutil # <- Import nécessaire pour la suppression de dossier

TEST_IMAGE = "ghcr.io/devcontainers/features/hello:1"
PROJECT_DIR = os.path.realpath(os.path.curdir)

def check_docker_available():
    """Vérifie si Docker est installé et en cours d'exécution."""
    print("INFO: Vérification de la disponibilité de Docker...")
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
        print("❌ Docker n'est pas installé ou n'est pas accessible dans le PATH.")
        return False

def check_ghcr_auth():
    """Teste l'authentification à ghcr.io en téléchargeant une image de test."""
    print(f"INFO: Vérification de l'authentification à ghcr.io en téléchargeant '{TEST_IMAGE}'...")
    try:
        subprocess.run(
            ["docker", "pull", TEST_IMAGE],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Authentification à ghcr.io réussie.")
        subprocess.run(["docker", "rmi", TEST_IMAGE], capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.lower()
        if "denied" in error_message or "authentication required" in error_message:
            print("❌ Échec de l'authentification à ghcr.io.")
        else:
            print(f"❌ Échec du téléchargement. Erreur Docker:\n{e.stderr}")
        return False

def handle_auth_failure():
    """Affiche les instructions, nettoie le projet généré et quitte proprement."""
    print("\n" + "="*80)
    print("🛑 ACTION REQUISE : Authentification au GitHub Container Registry (ghcr.io)")
    print("   Le Dev Container de ce projet a besoin de télécharger des outils depuis GitHub.")
    print("\n   Veuillez suivre ces étapes dans votre terminal :")
    print("   1. Créez un Personal Access Token (classic) avec la permission 'read:packages'.")
    print("      Lien direct : https://github.com/settings/tokens/new")
    print("   2. Exécutez la commande suivante en remplaçant USERNAME et en utilisant")
    print("      votre token comme mot de passe :")
    print("      docker login ghcr.io -u VOTRE_USERNAME_GITHUB")
    print("="*80)
    
    # Suppression du projet qui vient d'être généré
    try:
        print(f"\nINFO: La création du projet est annulée. Suppression de '{PROJECT_DIR}'...")
        # On se déplace dans le répertoire parent pour pouvoir supprimer le dossier actuel
        parent_dir = os.path.dirname(PROJECT_DIR)
        os.chdir(parent_dir)
        shutil.rmtree(PROJECT_DIR)
        print("INFO: Nettoyage terminé.")
    except Exception as e:
        print(f"⚠️  Erreur lors du nettoyage du dossier du projet : {e}")

    # On quitte avec un code de succès pour ne pas afficher le traceback de cruft
    sys.exit(0)

def main():
    """Fonction principale du hook."""
    if not check_docker_available():
        print("\n⚠️  Le projet a été créé, mais le Dev Container ne pourra pas être construit.")
        print("   Installez Docker, puis suivez les instructions du README.md.")
        sys.exit(0)

    if not check_ghcr_auth():
        handle_auth_failure()

    print("\n✅ Configuration validée ! Le projet a été créé avec succès.")
    print(f"   Votre projet se trouve ici : {PROJECT_DIR}")
    print("   Ouvrez ce dossier dans VS Code pour démarrer le Dev Container.")

if __name__ == "__main__":
    main()