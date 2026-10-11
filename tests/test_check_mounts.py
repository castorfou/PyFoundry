"""Tests de .devcontainer/scripts/check_mounts.sh (issue #59).

Le script est lancé sur l'hôte par `initializeCommand`, avant le montage :
il vérifie que chaque source de `mounts` existe et explique comment corriger.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

from tests.devcontainer_utils import (
    REPO_DEVCONTAINER,
    REPO_ROOT,
    SKELETON_DEVCONTAINER,
)


SCRIPT_PATH = REPO_DEVCONTAINER / "scripts" / "check_mounts.sh"
SKELETON_SCRIPT_PATH = SKELETON_DEVCONTAINER / "scripts" / "check_mounts.sh"
HOME_MOUNT = (
    "source=${localEnv:HOME}/.devcontainer/homes/"
    "${localWorkspaceFolderBasename}-${devcontainerId},"
    "target=/home/vscode,type=bind"
)


def host_env(home: Path, **extra: str) -> dict[str, str]:
    """Environnement d'un hôte dont le HOME est `home`, sans variables devcontainer."""
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"DEVCONTAINER_WORKSPACE_FOLDER_BASENAME", "DEVCONTAINER_ID"}
    }
    env["HOME"] = str(home)
    env.update(extra)
    return env


def write_devcontainer(workspace: Path, content: str | list[str]) -> None:
    """Écrit un devcontainer.json factice (liste de montages ou contenu brut)."""
    if isinstance(content, list):
        content = json.dumps({"name": "test", "image": "python", "mounts": content})
    path = workspace / ".devcontainer" / "devcontainer.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def run_check(workspace: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), "--host"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=workspace,
        env=env,
    )


@pytest.fixture
def host_home(tmp_path: Path) -> Path:
    home = tmp_path / "host-home"
    home.mkdir()
    return home


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "mon-projet"
    workspace.mkdir()
    return workspace


class TestScriptFiles:
    def test_script_is_executable_bash(self):
        assert os.access(SCRIPT_PATH, os.X_OK)
        assert SCRIPT_PATH.read_text().startswith("#!/usr/bin/env bash\n")

    def test_repo_and_skeleton_scripts_are_identical(self):
        assert SKELETON_SCRIPT_PATH.read_text() == SCRIPT_PATH.read_text()
        assert os.access(SKELETON_SCRIPT_PATH, os.X_OK)

    def test_generated_project_ships_the_script(
        self, cookies, minimal_template_context
    ):
        result = cookies.bake(extra_context=minimal_template_context)
        generated = (
            result.project_path / ".devcontainer" / "scripts" / "check_mounts.sh"
        )

        assert generated.read_text() == SCRIPT_PATH.read_text()


class TestHostCheck:
    def test_existing_sources_pass(self, workspace, host_home):
        (host_home / ".cache" / "uv").mkdir(parents=True)
        write_devcontainer(
            workspace,
            [
                "source=${localEnv:HOME}/.cache/uv,target=/home/vscode/.cache/uv,type=bind"
            ],
        )

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 0, result.stdout
        assert "[OK]   /home/vscode/.cache/uv" in result.stdout
        assert "[FAIL]" not in result.stdout

    def test_missing_source_fails_and_explains_fix(self, workspace, host_home):
        write_devcontainer(
            workspace, ["source=/nonexistent/host/path,target=/data,type=bind"]
        )

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 1
        assert "[FAIL] /data: source does not exist (/nonexistent/host/path)" in (
            result.stdout
        )
        assert 'mkdir -p "/nonexistent/host/path"' in result.stdout
        assert 'touch "/nonexistent/host/path"' in result.stdout
        assert "source=" in result.stdout

    def test_missing_socket_suggests_starting_docker(self, workspace, host_home):
        """Un socket ne se crée pas avec mkdir/touch : il faut démarrer le service."""
        socket = host_home / "docker.sock"
        write_devcontainer(
            workspace, [f"source={socket},target=/var/run/docker-host.sock,type=bind"]
        )

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 1
        assert "Docker" in result.stdout
        assert "mkdir -p" not in result.stdout
        assert "touch" not in result.stdout

    def test_commented_mounts_are_ignored(self, workspace, host_home):
        write_devcontainer(
            workspace,
            """{
    // Montages
    "mounts": [
        // "source=/nonexistent/commented,target=/data,type=bind",
        "source=/etc/localtime,target=/etc/localtime,type=bind,readonly"
    ]
}""",
        )

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 0, result.stdout
        assert "/nonexistent/commented" not in result.stdout

    def test_devcontainer_variables_resolved_from_env(self, workspace, host_home):
        home_dir = host_home / ".devcontainer" / "homes" / "projet-abc123"
        home_dir.mkdir(parents=True)
        write_devcontainer(workspace, [HOME_MOUNT])

        result = run_check(
            workspace,
            host_env(
                host_home,
                DEVCONTAINER_WORKSPACE_FOLDER_BASENAME="projet",
                DEVCONTAINER_ID="abc123",
            ),
        )

        assert result.returncode == 0, result.stdout
        assert f"Mount: {home_dir} -> /home/vscode" in result.stdout

    def test_devcontainer_id_resolved_from_single_home_candidate(
        self, workspace, host_home
    ):
        """Lancé à la main, sans variables : le seul HOME du projet est retenu."""
        home_dir = host_home / ".devcontainer" / "homes" / f"{workspace.name}-xyz789"
        home_dir.mkdir(parents=True)
        write_devcontainer(workspace, [HOME_MOUNT])

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 0, result.stdout
        assert f"Mount: {home_dir} -> /home/vscode" in result.stdout
        assert "${" not in result.stdout

    def test_unresolved_devcontainer_id_is_explained(self, workspace, host_home):
        write_devcontainer(workspace, [HOME_MOUNT])

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 1
        assert "cannot resolve ${devcontainerId}" in result.stdout
        assert f"{workspace.name}-*" in result.stdout

    @staticmethod
    def _ssh_dir(host_home: Path, files: dict[str, int], dir_mode: int = 0o700) -> Path:
        ssh = host_home / ".ssh"
        ssh.mkdir()
        for name, mode in files.items():
            (ssh / name).write_text("x")
            (ssh / name).chmod(mode)
        ssh.chmod(dir_mode)
        return ssh

    @staticmethod
    def _ssh_mount() -> list[str]:
        return [
            "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,readonly"
        ]

    def test_ssh_public_files_permissions_are_not_checked(self, workspace, host_home):
        """ssh ne vérifie ni les clés publiques ni known_hosts (cas réel : .pub en 664)."""
        self._ssh_dir(
            host_home,
            {
                "id_rsa": 0o600,
                "id_rsa.pub": 0o664,
                "known_hosts": 0o644,
                "config": 0o644,
            },
            dir_mode=0o755,
        )
        write_devcontainer(workspace, self._ssh_mount())

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 0, result.stdout
        assert "[OK]   /home/vscode/.ssh" in result.stdout

    def test_ssh_private_key_readable_by_others_fails(self, workspace, host_home):
        ssh = self._ssh_dir(host_home, {"id_ed25519": 0o644})
        write_devcontainer(workspace, self._ssh_mount())

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 1
        assert "[FAIL] /home/vscode/.ssh: SSH permissions too open" in result.stdout
        assert f'chmod 600 "{ssh}/id_ed25519"' in result.stdout

    def test_ssh_config_writable_by_others_fails(self, workspace, host_home):
        ssh = self._ssh_dir(host_home, {"config": 0o664})
        write_devcontainer(workspace, self._ssh_mount())

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 1
        assert f'chmod 600 "{ssh}/config"' in result.stdout

    def test_ssh_dir_writable_by_others_fails(self, workspace, host_home):
        ssh = self._ssh_dir(host_home, {}, dir_mode=0o775)
        write_devcontainer(workspace, self._ssh_mount())

        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 1
        assert f'chmod 700 "{ssh}"' in result.stdout

    def test_missing_devcontainer_json_fails(self, workspace, host_home):
        result = run_check(workspace, host_env(host_home))

        assert result.returncode == 1
        assert "devcontainer.json not found" in result.stdout


def test_repo_configuration_passes_once_sources_exist(tmp_path, host_home):
    """La vraie config du dépôt passe après les mkdir de initializeCommand."""
    workspace = tmp_path / "PyFoundry"
    (workspace / ".devcontainer").mkdir(parents=True)
    (workspace / ".devcontainer" / "devcontainer.json").write_text(
        (REPO_ROOT / ".devcontainer" / "devcontainer.json").read_text()
    )
    for directory in [
        ".devcontainer/homes/PyFoundry-id42/.cache",
        ".devcontainer/homes/PyFoundry-id42/.config",
        ".cache/pre-commit-devcontainers",
        ".cache/uv",
    ]:
        (host_home / directory).mkdir(parents=True)
    (host_home / ".ssh").mkdir(mode=0o700)
    (host_home / ".config" / "gh-devcontainers").mkdir(parents=True, mode=0o700)

    result = run_check(
        workspace,
        host_env(
            host_home,
            DEVCONTAINER_WORKSPACE_FOLDER_BASENAME="PyFoundry",
            DEVCONTAINER_ID="id42",
        ),
    )

    assert result.returncode == 0, result.stdout
