# Guide de déploiement

Ce guide détaille comment publier PyFoundry sur GitHub avec documentation automatique.

## Pré-requis

- [GitHub CLI](https://cli.github.com/) installé et configuré
- Droits de création de repository sur GitHub
- Branch principale commitée et prête


## Configuration initiale

### Authentification
```bash
# Lancer le processus d'authentification
gh auth login

# Suivre les instructions :
# 1. Choisir "GitHub.com"
# 2. Protocole : "HTTPS" (recommandé)
# 3. Authentification : "Login with a web browser" (plus simple)
# 4. Copier le code et suivre le lien
# 5. Upload SSH key (optionnel mais recommandé)
```

### Vérification
```bash
# Vérifier l'authentification
gh auth status

# Tester l'accès
gh api user
```

## Publication du projet

### Depuis le dossier PyFoundry
```bash
# Se placer dans le dossier du template
cd /path/to/PyFoundry

# Vérifier l'état Git
git status
git log --oneline -5

# Créer le repository avec toutes les options
gh repo create PyFoundry \
  --description "Template Cookiecutter de qualité industrielle pour projets Data Science Python" \
  --homepage "https://VOTRE_USERNAME.github.io/PyFoundry" \
  --public \
  --source=. \
  --remote=origin \
  --push
```

### Paramètres du repository

La commande ci-dessus va :
- ✅ Créer le repository `PyFoundry` sur GitHub
- ✅ Le configurer comme public
- ✅ Ajouter la description et homepage
- ✅ Ajouter le remote `origin` local
- ✅ Pousser la branch `main`

## Configuration GitHub Pages

### Méthode automatique (recommandée)
```bash
# Attendre que le premier workflow tourne
sleep 30

# Activer GitHub Pages avec GitHub Actions
gh api repos/:owner/PyFoundry/pages \
  --method POST \
  --field source[branch]=main \
  --field source[path]="/" \
  --field build_type="workflow"
```

### Méthode manuelle
1. Aller sur `https://github.com/VOTRE_USERNAME/PyFoundry`
2. Settings → Pages
3. Source : "GitHub Actions"
4. Sauvegarder

## Vérification du déploiement

### Status des workflows
```bash
# Voir les actions en cours
gh run list

# Détail d'un workflow
gh run view RUN_ID

# Logs d'un workflow
gh run view RUN_ID --log
```

### URL de la documentation
```bash
# Vérifier le statut GitHub Pages
gh api repos/:owner/PyFoundry/pages

# La documentation sera disponible sur :
# https://VOTRE_USERNAME.github.io/PyFoundry
```

## Post-déploiement

### Mettre à jour les liens
```bash
# Mettre à jour README.md avec le bon username
sed -i 's/guillaume/VOTRE_USERNAME/g' README.md
git add README.md
git commit -m "docs: update username in links"
git push
```

### Configurer les topics GitHub
```bash
# Ajouter des topics pour la découverte
gh api repos/:owner/PyFoundry \
  --method PATCH \
  --field topics='["cookiecutter", "template", "data-science", "python", "devcontainer"]'
```

## Gestion des releases

### Créer une release v0.1
```bash
# Créer un tag
git tag -a v0.1.0 -m "Release v0.1.0 - Squelette avec environnement reproductible"
git push origin v0.1.0

# Créer la release sur GitHub
gh release create v0.1.0 \
  --title "v0.1.0 - Squelette fonctionnel" \
  --notes "## 🚀 Fonctionnalités

- ✅ Structure de projet standardisée
- ✅ Configuration devcontainer VS Code avec .venv
- ✅ Installation conditionnelle d'outils (uv, Node.js, Git)
- ✅ Documentation complète avec MkDocs Material
- ✅ CI/CD GitHub Actions

## 📦 Utilisation

\`\`\`bash
cruft create https://github.com/VOTRE_USERNAME/PyFoundry.git
\`\`\`"
```

## Troubleshooting

### Erreur d'authentification
```bash
# Renouveler l'authentification
gh auth logout
gh auth login
```

### Repository existe déjà
```bash
# Supprimer et recréer
gh repo delete PyFoundry --confirm
gh repo create PyFoundry --public --source=. --remote=origin --push
```

### GitHub Pages ne se déploie pas
```bash
# Vérifier les permissions du workflow
gh api repos/:owner/PyFoundry \
  --method PATCH \
  --field allow_auto_merge=false \
  --field delete_branch_on_merge=true
```

### Forcer un nouveau déploiement de documentation
```bash
# Re-trigger le workflow docs
gh workflow run docs.yml
```

## Ressources

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
