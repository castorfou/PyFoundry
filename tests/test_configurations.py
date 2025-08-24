"""Tests de validation des configurations générées."""

import json
import tomllib
import yaml

import pytest


def test_pyproject_toml_valid(cookies, minimal_template_context):
    """Test que pyproject.toml généré est syntaxiquement correct."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    pyproject_path = result.project_path / "pyproject.toml"
    assert pyproject_path.exists()
    
    # Vérifier que le TOML est parsable
    content = pyproject_path.read_text()
    parsed = tomllib.loads(content)
    
    # Vérifications basiques de structure
    assert "project" in parsed
    assert "name" in parsed["project"]
    assert "dependencies" in parsed["project"]
    assert "tool" in parsed
    assert "ruff" in parsed["tool"]
    assert "mypy" in parsed["tool"]


def test_precommit_config_valid(cookies, minimal_template_context):
    """Test que .pre-commit-config.yaml est valide."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    precommit_path = result.project_path / ".pre-commit-config.yaml"
    assert precommit_path.exists()
    
    # Vérifier que le YAML est parsable
    content = precommit_path.read_text()
    parsed = yaml.safe_load(content)
    
    # Vérifications de structure
    assert "repos" in parsed
    assert len(parsed["repos"]) > 0
    
    # Vérifier qu'on a les repos attendus
    repo_urls = [repo["repo"] for repo in parsed["repos"]]
    expected_repos = [
        "https://github.com/pre-commit/pre-commit-hooks",
        "https://github.com/astral-sh/ruff-pre-commit",
        "https://github.com/pre-commit/mirrors-mypy"
    ]
    
    for expected_repo in expected_repos:
        assert any(expected_repo in url for url in repo_urls)


def test_devcontainer_json_valid(cookies, minimal_template_context):
    """Test que devcontainer.json est syntaxiquement correct."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    devcontainer_path = result.project_path / ".devcontainer" / "devcontainer.json"
    assert devcontainer_path.exists()
    
    content = devcontainer_path.read_text()
    
    # Test basique : le fichier contient les éléments essentiels
    assert '"name":' in content
    assert '"image":' in content  
    assert '"features":' in content
    assert '"customizations":' in content
    
    # Test que les commentaires sont présents (format devcontainer)
    assert "// Variables d'environnement" in content
    assert "// Configuration du shell" in content


def test_gitignore_includes_ds_patterns(cookies, minimal_template_context):
    """Test que .gitignore contient les patterns Data Science essentiels."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    gitignore_path = result.project_path / ".gitignore"
    assert gitignore_path.exists()
    
    content = gitignore_path.read_text()
    
    # Patterns essentiels pour Data Science
    essential_patterns = [
        "__pycache__",
        "*.py[cod]",
        ".env",
        ".venv",
        "data/",
        ".ipynb_checkpoints"
    ]
    
    for pattern in essential_patterns:
        assert pattern in content, f"Missing pattern in .gitignore: {pattern}"


def test_ruff_configuration_valid(cookies, minimal_template_context):
    """Test que la configuration Ruff est cohérente."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    pyproject_path = result.project_path / "pyproject.toml"
    content = pyproject_path.read_text()
    parsed = tomllib.loads(content)
    
    ruff_config = parsed["tool"]["ruff"]
    
    # Vérifications configuration Ruff
    assert "extend-select" in ruff_config
    assert "ignore" in ruff_config
    assert "line-length" in ruff_config
    assert ruff_config["line-length"] == 88  # Standard
    
    # Vérifier règles Data Science
    extend_select = ruff_config["extend-select"]
    assert "PD" in extend_select  # pandas-vet
    assert "NPY" in extend_select  # numpy


def test_mypy_configuration_progressive(cookies, minimal_template_context):
    """Test que MyPy est configuré en mode progressif."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    pyproject_path = result.project_path / "pyproject.toml"
    content = pyproject_path.read_text()
    parsed = tomllib.loads(content)
    
    mypy_config = parsed["tool"]["mypy"]
    
    # Configuration progressive (pas trop stricte)
    assert mypy_config["disallow_untyped_defs"] is False
    assert mypy_config["disallow_incomplete_defs"] is True
    
    # Vérifier overrides pour Data Science
    assert "overrides" in parsed["tool"]["mypy"]
    overrides = parsed["tool"]["mypy"]["overrides"]
    
    # Chercher les modules Data Science ignorés
    ds_modules_found = False
    for override in overrides:
        if "module" in override:
            modules = override["module"]
            if any("matplotlib" in mod or "sklearn" in mod for mod in modules):
                ds_modules_found = True
                assert override.get("ignore_missing_imports") is True
    
    assert ds_modules_found, "Missing Data Science modules in mypy overrides"