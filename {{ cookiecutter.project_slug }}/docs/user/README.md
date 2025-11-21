# Documentation Utilisateur

!!! info "À propos de cette section"
    Cette section contient la documentation pour les **utilisateurs** du projet {{ cookiecutter.project_name }}.

    Elle explique **comment utiliser** les fonctionnalités du projet, sans nécessiter de connaissances
    approfondies du code source.

## Contenu suggéré

Voici les types de documentation que vous devriez ajouter dans cette section :

### Installation et Configuration
- Guide d'installation détaillé
- Prérequis système
- Configuration initiale
- Variables d'environnement

### Guides d'utilisation
- Tutoriels pas-à-pas
- Cas d'usage courants
- Exemples pratiques
- Captures d'écran et démonstrations

### Référence
- Liste des fonctionnalités disponibles
- Options de configuration
- Format des fichiers d'entrée/sortie
- API publique (si applicable)

### Dépannage
- Problèmes courants et solutions
- Messages d'erreur et leur signification
- FAQ (Questions fréquemment posées)

## Comment générer cette documentation

Cette documentation est générée avec l'IA (Claude Code). Pour maintenir une documentation de qualité :

### ✅ Bonnes pratiques de rédaction

**Décrire l'état actuel** du système :
- Expliquer ce que le système **fait maintenant**
- Fournir des spécifications techniques et des exemples d'utilisation
- Documenter les fonctionnalités telles qu'elles existent

**Éviter** :
- ❌ Les références historiques ("L'issue #X a amélioré...")
- ❌ Les récits d'évolution ("Nous avons d'abord implémenté X, puis Y...")
- ❌ Les marqueurs temporels ("Nouvelle fonctionnalité", "Récemment ajouté")
- ❌ Les métriques de tests dans la documentation

### Exemple

**❌ Mauvais** :
> "Nouvelle dans l'issue #75 : La Phase 0 est maintenant bien meilleure grâce à la double confirmation...
> C'est une amélioration majeure par rapport à la version précédente."

**✅ Bon** :
> "La Phase 0 utilise deux mécanismes d'enrichissement : la double confirmation quand Babelio retourne
> un score de confiance entre 0.85 et 0.99, et la correction d'auteur quand les livres ne sont pas trouvés."

### Commandes utiles

```bash
# Prévisualiser la documentation localement
mkdocs serve

# Construire la documentation pour la production
mkdocs build --strict
```

La documentation est automatiquement déployée sur GitHub Pages à chaque push sur la branche principale.
