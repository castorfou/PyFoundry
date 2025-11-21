# Documentation Développeur

!!! info "À propos de cette section"
    Cette section contient la documentation pour les **développeurs** qui contribuent au projet {{ cookiecutter.project_name }}.

    Elle explique **comment le code fonctionne** et comment y contribuer efficacement.

## Contenu suggéré

Voici les types de documentation que vous devriez ajouter dans cette section :

### Architecture
- Vue d'ensemble de l'architecture du projet
- Diagrammes d'architecture (composants, flux de données)
- Choix de design et leurs justifications
- Structure des dossiers et organisation du code

### Configuration de l'environnement
- Installation de l'environnement de développement
- Configuration VS Code / Dev Container
- Outils et extensions recommandés
- Configuration des secrets et variables d'environnement

### Guide de contribution
- Processus de contribution (fork, branch, PR)
- Standards de code et conventions
- Comment écrire des tests
- Workflow TDD recommandé
- Comment utiliser les commandes Claude Code (`/fix-issue`, etc.)

### Référence technique
- Description des modules principaux
- APIs internes et interfaces
- Gestion des dépendances
- Configuration des outils (ruff, mypy, pytest)

### Processus de développement
- Cycle de développement (feature → tests → code → review)
- Stratégie de branches Git
- Processus de review de code
- Gestion des versions et releases

## Comment générer cette documentation

Cette documentation est générée avec l'IA (Claude Code). Pour maintenir une documentation de qualité :

### ✅ Bonnes pratiques de rédaction

**Décrire l'état actuel** du système :

- Expliquer **comment le code fonctionne maintenant**

- Documenter l'architecture et les patterns actuels

- Fournir des exemples de code et d'utilisation

**Éviter** :

- ❌ Les références historiques ("L'issue #X a amélioré...")

- ❌ Les récits d'évolution ("Nous avons d'abord implémenté X, puis Y...")

- ❌ Les marqueurs temporels ("Nouvelle fonctionnalité", "Récemment ajouté")

- ❌ Les métriques de tests dans la documentation

### Références GitHub appropriées

Les références aux issues GitHub ont leur place dans :

- ✅ Les sections dédiées "Historique" ou "Notes de développement" (en fin de document)

- ✅ Les messages de commit et pull requests

- ✅ Les commentaires de code expliquant des décisions techniques

- ❌ **Jamais** dans la documentation fonctionnelle principale

### Exemple

**❌ Mauvais** :
> "Le module d'authentification a été développé dans l'issue #42. Nous avons d'abord essayé OAuth,
> puis nous sommes passés à JWT dans l'issue #55, ce qui a beaucoup amélioré les performances."

**✅ Bon** :
> "Le module d'authentification utilise JWT (JSON Web Tokens) pour gérer les sessions utilisateur.
> Les tokens sont signés avec RS256 et ont une durée de vie de 24h. Le refresh token permet de
> renouveler la session sans redemander les credentials."

### Commandes utiles

```bash
# Prévisualiser la documentation localement
mkdocs serve

# Construire la documentation pour la production
mkdocs build --strict
```

La documentation est automatiquement déployée sur GitHub Pages à chaque push sur la branche principale.

## Ressources

- CLAUDE.md (à la racine du projet) - Instructions détaillées pour Claude Code
- [Architecture du template PyFoundry](https://castorfou.github.io/PyFoundry/) - Documentation du template utilisé
