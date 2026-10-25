# PyFoundry

Template Cookiecutter pour projets Data Science en Python, et les projets qui en sont issus et en reçoivent les évolutions.

## Langage

### Template et projets

**Template** :
Le dépôt PyFoundry, source des projets et de leurs mises à jour.
_À éviter_ : modèle, gabarit

**Squelette** :
Le contenu du dossier `{{ cookiecutter.project_slug }}/` du template, rendu dans chaque projet généré.
_À éviter_ : template (pour ce dossier seul)

**Projet généré** :
Un projet lié au template par son `.cruft.json`, qu'il ait été créé par `cruft create` ou rattaché par `cruft link`. PyFoundry est lui-même un projet généré de son propre template.
_À éviter_ : projet client, projet utilisateur

### Mise à jour du template

**Mise à jour du template** :
L'application à un projet généré des changements du template depuis le commit enregistré dans son `.cruft.json`, jusqu'à la tête de `main`.
_À éviter_ : synchro, cruft update (pour l'opération complète)

**Auto-mise à jour** :
La mise à jour du template appliquée à PyFoundry lui-même, dont la racine est déjà alignée sur le squelette.

**Rejet** :
Un changement du template que cruft n'a pas pu appliquer seul, laissé en fichier `.rej` ou en marqueurs de conflit dans le fichier.
_À éviter_ : conflit (pour les deux formes à la fois)

**Fichier du template** :
Un fichier du projet généré qui appartient au template : la version du template l'emporte.

**Fichier du projet** :
Un fichier du projet généré qui appartient à son équipe : la version locale l'emporte.

**Fichier mixte** :
Un fichier du projet généré où le template et l'équipe écrivent tous les deux, et dont on fusionne les deux versions.

**Verdict** :
Le sort d'un rejet lors d'une auto-mise à jour : déjà appliqué, propre au projet généré, ou trou à combler.
