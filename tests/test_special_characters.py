"""Saisies avec caractères spéciaux : fichiers structurés du projet généré valides (#110).

Le nom et la description saisis à la génération sont écrits dans des fichiers
YAML, TOML et JSON. Un « : », un « " » ou un « \\ » ne doit casser aucun d'eux.
"""

import json
import os
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.devcontainer_utils import parse_jsonc


PROJECT_NAME = 'Projet : "Spécial" d\'été \\ test'
DESCRIPTION = (
    'Outils de transcription : brute, "citée", d\'été, C:\\data, $HOME et `ls`'
)


class _MkdocsLoader(yaml.SafeLoader):
    """Lit mkdocs.yml en ignorant les balises !!python/name."""


_MkdocsLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/name:", lambda loader, suffix, node: suffix
)


@pytest.fixture
def special_project(cookies: Any) -> Path:
    """Projet généré avec un nom et une description pleins de caractères spéciaux."""
    result = cookies.bake(
        extra_context={
            "project_name": PROJECT_NAME,
            "project_slug": "projet-special",
            "description": DESCRIPTION,
            "python_version": "3.11",
            "github_username": "test-user",
            "use_node": "y",
        }
    )
    assert result.exit_code == 0, result.exception
    return Path(result.project_path)


def _mkdocs_config(project: Path) -> dict[str, Any]:
    text = (project / "mkdocs.yml").read_text(encoding="utf-8")
    config: dict[str, Any] = yaml.load(text, Loader=_MkdocsLoader)
    return config


def test_mkdocs_yml_keeps_name_and_description(special_project):
    config = _mkdocs_config(special_project)

    assert config["site_name"] == PROJECT_NAME
    assert config["site_description"] == DESCRIPTION


def test_mkdocs_yml_keeps_accents_readable(special_project):
    text = (special_project / "mkdocs.yml").read_text(encoding="utf-8")

    assert "été" in text
    assert "\\u00e9" not in text


def test_pyproject_keeps_description(special_project):
    with (special_project / "pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    assert pyproject["project"]["description"] == DESCRIPTION


def test_devcontainer_json_keeps_project_name(special_project):
    config = parse_jsonc(special_project / ".devcontainer" / "devcontainer.json")

    assert config["name"] == f"{PROJECT_NAME} - Dev Environment"
    assert config["containerEnv"]["PROJECT_NAME"] == PROJECT_NAME


def test_post_start_command_reads_project_name_from_env(special_project):
    config = parse_jsonc(special_project / ".devcontainer" / "devcontainer.json")
    command = config["postStartCommand"]
    assert PROJECT_NAME not in command

    # Seule la partie echo est rejouée : ensure_venv.sh demande un vrai conteneur
    echo = command.split("&&", 1)[1]
    result = subprocess.run(
        ["bash", "-c", echo],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PROJECT_NAME": PROJECT_NAME},
    )

    assert result.stdout == f"🚀 {PROJECT_NAME} - Environnement prêt!\n"


def test_package_json_keeps_description(special_project, tmp_path):
    script = (special_project / ".devcontainer" / "postCreateCommand.sh").read_text(
        encoding="utf-8"
    )
    heredoc = re.search(
        r"^\s*cat > package\.json <<.*?^EOF$", script, re.MULTILINE | re.DOTALL
    )
    assert heredoc, "heredoc du package.json introuvable dans postCreateCommand.sh"

    subprocess.run(["bash", "-c", heredoc.group(0)], check=True, cwd=tmp_path)
    package = json.loads((tmp_path / "package.json").read_text(encoding="utf-8"))

    assert package["description"] == DESCRIPTION


def test_mkdocs_build_strict(special_project):
    try:
        result = subprocess.run(
            ["mkdocs", "build", "--strict"],
            check=False,
            cwd=special_project,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        pytest.skip("mkdocs absent de l'environnement de test")
    if "is not installed" in result.stderr:
        pytest.skip("plugins mkdocs absents de l'environnement de test")

    assert result.returncode == 0, result.stderr
