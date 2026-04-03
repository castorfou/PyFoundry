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
    }


@pytest.fixture
def node_template_context():
    """Contexte avec Node.js activé."""
    return {
        "project_name": "Node Test Project",
        "project_slug": "node-test-project",
        "description": "A test project with Node.js support",
        "python_version": "3.11",
        "github_username": "test-user",
        "use_node": "y",
    }


@pytest.fixture
def docker_in_docker_template_context():
    """Contexte avec Docker-in-Docker activé."""
    return {
        "project_name": "DinD Test Project",
        "project_slug": "dind-test-project",
        "description": "A test project with Docker-in-Docker support",
        "python_version": "3.11",
        "github_username": "test-user",
        "use_node": "n",
        "docker_in_docker": "yes",
    }
