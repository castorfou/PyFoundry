#!/bin/bash
set -e

echo "🚀 Configuration de l'environnement de développement..."

# Installation uv
{% if cookiecutter.use_uv == "y" %}
echo "📦 Installation de uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
{% endif %}

# Installation Node.js/npm
{% if cookiecutter.use_node == "y" %}
echo "📦 Installation de Node.js..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
{% endif %}

# Installation des dépendances Python
{% if cookiecutter.use_uv == "y" %}
echo "🐍 Installation des dépendances Python avec uv..."
~/.local/bin/uv pip install -e . --system
{% else %}
echo "🐍 Installation des dépendances Python avec pip..."
pip install -e .
{% endif %}

# Configuration Git (optionnel)
{% if cookiecutter.setup_git == "y" %}
echo "🔧 Configuration Git..."
git config --global init.defaultBranch main
git config --global pull.rebase false
{% endif %}

echo "✅ Environnement configuré avec succès !"
echo "💡 Redémarrez le terminal pour appliquer tous les changements"