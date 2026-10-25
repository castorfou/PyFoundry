# PyFoundry Template

> Un template Cookiecutter pour démarrer rapidement des projets de Data Science en Python.

## 🚀 Démarrage rapide

Pour créer un projet "from scratch" s'appuyant sur le template **`PyFoundry`**

(pour plus de détails ou pour des cas avancés, aller voir la doc [utilisateur](/user))

**Créer le repo local**
```bash
# se placer à la racine d'emplacement des projets (e.g. ~/git)
cruft create https://github.com/castorfou/PyFoundry.git
```
le pré-requis est d'avoir `cruft` installé dans l'environnement python actif

**Ouvrir le projet**
```bash
code <mon-nouveau-projet> # (1)
# → VS Code invite à "Reopen in Container"
```

1. à remplacer par le nom raccourci du projet (project_slug)

les pré-requis sont d'avoir *vscode*, l'extension *devcontainer*, *docker* et le package *tzdata*

**Lier à github**
```bash
gh repo create $PROJECT_SLUG --public
git push -u origin main
```

**Mettre à jour (facultatif)**

pour intégrer les dernieres fonctions de **`PyFoundry`**, demandez à Claude Code dans le projet : « mets à jour le projet depuis le template ». La skill `/cruft-update` lance `cruft update`, résume les nouveautés et les migrations, résout les rejets avec vous et vérifie le résultat. Sans Claude Code :

```bash
cruft update
```

Les nouveautés de chaque version, et les éventuelles étapes de migration, sont dans le [changelog](/changelog). Pour viser une version précise : `cruft update --checkout v1.0.0`.

## ✨ Fonctionnalités

- **Environnement reproductible** : Devcontainer VS Code avec uv & pyproject.toml, extensions vscode, zsh et ses plugins
- **Qualité de code** : Ruff + MyPy + Pre-commit hooks pré-configurés (secret, size, clean notebooks)
- **Intégration Github complète** : gh-cli, Github Actions CI/CD
- **Structure prédéfinie** : Organisation standardisée pour projets Data Science
- **Documentation moderne** : Avec MkDocs Material, config mermaid, TOC repliable, push possible depuis branches, github pages
- **Mise à jour facile** : Template évolutif avec cruft
- **Prise en compte du GPU** : [config](/user/installation/#options-de-configuration)
- **Docker in docker** : [config](/user/installation/#options-de-configuration)
- **Skills Matt Pocock pour Claude Code** : plugin activé par défaut ([cheatsheet](/cheatsheets/claude/#skills-matt-pocock))
- **Claude code local llm** : [lancement](/cheatsheets/claude/#lancement-avec-un-modele-local)
- **Excalidraw** : pour dessiner des schémas
- **Thème vscode Catpuccin**
