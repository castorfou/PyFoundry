"""Tests du HOME persistant des devcontainers (issue #59).

Le HOME `/home/vscode` est un dossier de l'hôte propre à chaque projet, pour
survivre aux rebuilds. Le venv vit dans `/tmp/venv`, hors du HOME : il est
recréé à chaque rebuild.
"""

from pathlib import Path
from typing import Any

import pytest

from tests.devcontainer_utils import (
    REPO_DEVCONTAINER,
    mount_targets,
    nested_mountpoints,
    parse_jsonc,
)


HOME_MOUNT = (
    "source=${localEnv:HOME}/.devcontainer/homes/"
    "${localWorkspaceFolderBasename}-${devcontainerId},"
    "target=/home/vscode,type=bind"
)
PRE_COMMIT_MOUNT = (
    "source=${localEnv:HOME}/.cache/pre-commit-devcontainers,"
    "target=/home/vscode/.cache/pre-commit,type=bind"
)
VENV = "/tmp/venv"


@pytest.fixture(params=["repo", "default", "docker_in_docker"])
def devcontainer_dir(
    request: pytest.FixtureRequest,
    cookies: Any,
    minimal_template_context: dict[str, str],
) -> Path:
    """Dossier .devcontainer du dépôt PyFoundry ou d'un projet généré."""
    if request.param == "repo":
        return REPO_DEVCONTAINER
    context = dict(minimal_template_context)
    if request.param == "docker_in_docker":
        context["docker_in_docker"] = "y"
    result = cookies.bake(extra_context=context)
    assert result.exit_code == 0
    return Path(result.project_path) / ".devcontainer"


def test_home_is_mounted_from_a_per_project_host_directory(devcontainer_dir):
    mounts = mount_targets(parse_jsonc(devcontainer_dir / "devcontainer.json"))

    assert mounts["/home/vscode"] == HOME_MOUNT


def test_pre_commit_cache_is_shared_between_devcontainers(devcontainer_dir):
    mounts = mount_targets(parse_jsonc(devcontainer_dir / "devcontainer.json"))

    assert mounts["/home/vscode/.cache/pre-commit"] == PRE_COMMIT_MOUNT


def test_gitconfig_is_not_mounted(devcontainer_dir):
    """VS Code copie lui-même le ~/.gitconfig de l'hôte (cf. issue #61)."""
    mounts = mount_targets(parse_jsonc(devcontainer_dir / "devcontainer.json"))

    assert "/home/vscode/.gitconfig" not in mounts


def test_ssh_stays_readonly(devcontainer_dir):
    mounts = mount_targets(parse_jsonc(devcontainer_dir / "devcontainer.json"))

    assert mounts["/home/vscode/.ssh"].endswith(",readonly")


def test_initialize_command_creates_mount_sources_then_checks_them(devcontainer_dir):
    """Les sources sont créées sur l'hôte avant que Docker ne les crée en root."""
    command = parse_jsonc(devcontainer_dir / "devcontainer.json")["initializeCommand"]

    assert '"${localEnv:HOME}/.cache/pre-commit-devcontainers"' in command
    assert '"${localEnv:HOME}/.cache/uv"' in command
    assert 'mkdir -p -m 700 "${localEnv:HOME}/.ssh"' in command
    assert command.endswith(
        '(cd "${localWorkspaceFolder}" && '
        'DEVCONTAINER_WORKSPACE_FOLDER_BASENAME="${localWorkspaceFolderBasename}" '
        'DEVCONTAINER_ID="${devcontainerId}" '
        "bash .devcontainer/scripts/check_mounts.sh --host)"
    )


def test_initialize_command_creates_nested_mountpoints(devcontainer_dir):
    """Un montage imbriqué dans un autre (ex. ~/.ssh dans le HOME) a besoin d'un
    point de montage dans la source du parent : sinon Docker le crée en root."""
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")
    mountpoints = nested_mountpoints(config)

    assert "/home/vscode/.ssh" in mountpoints
    for target, mountpoint in mountpoints.items():
        assert f'"{mountpoint}"' in config["initializeCommand"], target


def test_python_tooling_points_to_tmp_venv(devcontainer_dir):
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")
    settings = config["customizations"]["vscode"]["settings"]
    terminal_env = settings["terminal.integrated.env.linux"]

    assert config["containerEnv"]["UV_PYTHON"] == f"{VENV}/bin/python"
    assert settings["python.defaultInterpreterPath"] == f"{VENV}/bin/python"
    assert settings["python.venvPath"] == "/tmp"
    assert terminal_env["VIRTUAL_ENV"] == VENV
    assert terminal_env["PATH"].startswith(f"{VENV}/bin:")


def test_uv_project_environment_points_to_tmp_venv(devcontainer_dir):
    """Un `uv sync` sans `--active` ne doit pas créer de `.venv` à la racine (#70)."""
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")

    assert config["containerEnv"]["UV_PROJECT_ENVIRONMENT"] == VENV


def test_post_create_builds_venv_in_tmp(devcontainer_dir):
    script = (devcontainer_dir / "postCreateCommand.sh").read_text()

    assert f'VENV_HOME="{VENV}"' in script
    assert f"ensure_zshrc_line 'source {VENV}/bin/activate'" in script


def test_post_create_seeds_home_from_skel(devcontainer_dir):
    """Le bind mount masque le HOME de l'image : on recopie /etc/skel sans écraser."""
    script = (devcontainer_dir / "postCreateCommand.sh").read_text()

    assert 'cp -rn /etc/skel/. "$HOME"' in script
    assert "\nseed_home\n" in script


def test_no_reference_to_old_home_venv(devcontainer_dir):
    for path in devcontainer_dir.rglob("*"):
        if path.is_file():
            assert "/home/vscode/.venv" not in path.read_text(), path
