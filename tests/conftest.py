"""Configuration pytest et fixtures pour les tests PyFoundry."""

import pytest


@pytest.fixture
def default_template_context():
    """Contexte par défaut pour la génération du template."""
    return {
        "project_name": "Test Project",
        "project_slug": "test-project", 
        "description": "A test project for PyFoundry template",
        "python_version": "3.11",
        "github_username": "test-user",
        "use_node": "n",
        "setup_git": "y"
    }


@pytest.fixture
def minimal_template_context():
    """Contexte minimal pour les tests rapides."""
    return {
        "project_name": "Minimal Test",
        "project_slug": "minimal-test",
        "description": "Minimal test project",
        "python_version": "3.11",
        "github_username": "test-user",
        "use_node": "n", 
        "setup_git": "n"  # Pas de setup git pour tests rapides
    }