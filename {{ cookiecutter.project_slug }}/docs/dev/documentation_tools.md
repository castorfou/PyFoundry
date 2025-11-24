# Outils de Documentation

Cette page détaille la stack technique utilisée pour la documentation du projet, ainsi que les différents packages Python impliqués.

## MkDocs

*   **Usage** : Générateur de site statique rapide et simple, orienté documentation projet. Il construit le site HTML à partir de fichiers Markdown.
*   **Exemple** : Commande `mkdocs serve` pour visualiser le site en local avec rechargement automatique.
*   **Documentation** : [https://www.mkdocs.org/](https://www.mkdocs.org/)

## MkDocs Material

*   **Usage** : Thème de référence pour MkDocs. Il offre un design moderne (Material Design), responsive, et de nombreuses fonctionnalités natives (recherche instantanée, mode sombre, etc.).
*   **Exemple** : Configuration dans `mkdocs.yml` via `theme: name: material`.
*   **Documentation** : [https://squidfunk.github.io/mkdocs-material/](https://squidfunk.github.io/mkdocs-material/)

## MkDocs Git Revision Date Localized Plugin

*   **Usage** : Plugin affichant la date de dernière modification de chaque page en se basant sur l'historique Git, avec un formatage localisé (ex: français).
*   **Exemple** : Ajoute automatiquement "Dernière mise à jour : 24 novembre 2025" au bas des pages de documentation.
*   **Documentation** : [https://github.com/timvink/mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin)

## Click

*   **Usage** : Bibliothèque Python pour créer des interfaces en ligne de commande (CLI). Elle est ici épinglée en version `8.2.1` pour contourner un problème de compatibilité connu avec MkDocs.
*   **Exemple** : Dépendance transitive technique, pas d'usage direct pour la rédaction de documentation.
*   **Documentation** : [https://click.palletsprojects.com/](https://click.palletsprojects.com/)

## MkDocstrings (Python handler)

*   **Usage** : Permet de générer automatiquement la documentation de référence du code Python à partir des docstrings, et de l'insérer directement dans les pages Markdown.
*   **Exemple** : L'instruction `::: my_package.my_module` dans un fichier Markdown générera la documentation complète du module.
*   **Documentation** : [https://mkdocstrings.github.io/](https://mkdocstrings.github.io/)

## MkDocs Include Markdown Plugin

*   **Usage** : Permet d'inclure le contenu d'un fichier Markdown dans un autre. Très utile pour réutiliser le `README.md` racine dans la documentation sans duplication.
*   **Exemple** : `{% include "../README.md" %}` pour insérer le contenu d'un fichier externe.
*   **Documentation** : [https://github.com/twardoch/mkdocs-include-markdown-plugin](https://github.com/twardoch/mkdocs-include-markdown-plugin)

## MkDocs Awesome Nav

*   **Usage** : Plugin permettant une gestion plus flexible et avancée de la navigation dans MkDocs.
*   **Exemple** : Permet de structurer le menu de navigation indépendamment de la structure des fichiers.
*   **Documentation** : (Se référer à la documentation du package spécifique utilisé, potentiellement un fork ou un nom similaire à `mkdocs-awesome-pages-plugin`)

## Pymdown Extensions

*   **Usage** : Ensemble d'extensions pour le parseur Python-Markdown, ajoutant des fonctionnalités riches à la syntaxe Markdown standard (admonitions, onglets, touches clavier, etc.).
*   **Exemple** : Utilisation de `!!! note` pour créer des encadrés d'information colorés.
*   **Documentation** : [https://facelessuser.github.io/pymdown-extensions/](https://facelessuser.github.io/pymdown-extensions/)
