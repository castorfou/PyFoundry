"""Tests de génération du template PyFoundry."""

import os
from pathlib import Path

import pytest


def test_template_generates_successfully(cookies, default_template_context):
    """Test que le template se génère sans erreur."""
    result = cookies.bake(extra_context=default_template_context)
    
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.is_dir()


def test_project_structure_created(cookies, minimal_template_context):
    """Test que la structure de projet attendue est créée."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    project_path = result.project_path
    
    # Fichiers racine attendus
    expected_files = [
        "README.md",
        "pyproject.toml", 
        ".gitignore",
        ".pre-commit-config.yaml"
    ]
    
    for file_name in expected_files:
        assert (project_path / file_name).exists(), f"Missing file: {file_name}"
    
    # Dossiers attendus
    expected_dirs = [
        "src",
        "data",
        "data/raw", 
        "data/processed",
        "notebooks",
        ".devcontainer"
    ]
    
    for dir_name in expected_dirs:
        assert (project_path / dir_name).is_dir(), f"Missing directory: {dir_name}"


def test_devcontainer_files_created(cookies, minimal_template_context):
    """Test que les fichiers devcontainer sont créés."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    devcontainer_path = result.project_path / ".devcontainer"
    
    assert (devcontainer_path / "devcontainer.json").exists()
    assert (devcontainer_path / "postCreateCommand.sh").exists()


def test_template_with_different_contexts(cookies):
    """Test génération avec différents contextes."""
    contexts = [
        {"project_name": "Simple Project", "python_version": "3.11"},
        {"project_name": "Complex-Project_123", "python_version": "3.12"},
        {"project_name": "Data Science Project", "use_node": "y"},
    ]
    
    for context in contexts:
        result = cookies.bake(extra_context=context)
        assert result.exit_code == 0
        assert result.project_path.is_dir()


def test_project_slug_generation(cookies):
    """Test que le project_slug est généré correctement."""
    test_cases = [
        ("Simple Project", "simple-project"),
        ("Data Science Project", "data-science-project"),
        ("Test_Project", "test-project"),
        ("My-Cool_Project 123", "my-cool-project-123"),
    ]
    
    for project_name, expected_slug in test_cases:
        result = cookies.bake(extra_context={"project_name": project_name})
        
        # Vérifier que le dossier utilise le bon slug
        assert result.project_path.name == expected_slug
        
        # Vérifier que pyproject.toml contient le bon nom
        pyproject_content = (result.project_path / "pyproject.toml").read_text()
        assert f'name = "{expected_slug}"' in pyproject_content


def test_github_username_integration(cookies):
    """Test que github_username est bien intégré dans la config."""
    context = {
        "github_username": "testuser123",
        "project_slug": "test-project"
    }
    
    result = cookies.bake(extra_context=context)
    
    # Vérifier que pyproject.toml contient les bonnes URLs
    pyproject_content = (result.project_path / "pyproject.toml").read_text()
    assert "github.com/testuser123/test-project" in pyproject_content