"""Tests de l'authentification GitHub des devcontainers (issue #64).

`gh auth login --web` ne peut pas ouvrir le navigateur depuis postCreateCommand :
seuls les terminaux VS Code reçoivent `$BROWSER`, qui ouvre l'URL sur l'hôte.
L'authentification est donc proposée au premier terminal zsh, par
`.devcontainer/scripts/gh_login.sh`. La config gh est un dossier de l'hôte
partagé entre devcontainers : on s'authentifie une fois pour tous les projets.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tests.devcontainer_utils import REPO_DEVCONTAINER, mount_targets, parse_jsonc
from tests.test_post_create_command import extract_function


GH_CONFIG_MOUNT = (
    "source=${localEnv:HOME}/.config/gh-devcontainers,"
    "target=/home/vscode/.config/gh,type=bind"
)
LOGIN_HOOK = 'bash "$WORKSPACE_FOLDER/.devcontainer/scripts/gh_login.sh"'

# Faux gh : journalise ses appels ; authentifié si FAKE_GH_TOKEN est défini,
# `auth login` échoue si FAKE_GH_LOGIN=fail
FAKE_GH = """#!/usr/bin/env bash
echo "$*" >> "$FAKE_GH_LOG"
if [ "$1 $2" = "auth token" ]; then
    [ -n "$FAKE_GH_TOKEN" ] && echo "$FAKE_GH_TOKEN" && exit 0
    exit 1
fi
if [ "$1 $2" = "auth login" ] && [ "$FAKE_GH_LOGIN" = "fail" ]; then
    exit 1
fi
exit 0
"""


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


def test_gh_config_is_shared_between_devcontainers(devcontainer_dir):
    mounts = mount_targets(parse_jsonc(devcontainer_dir / "devcontainer.json"))

    assert mounts["/home/vscode/.config/gh"] == GH_CONFIG_MOUNT


def test_initialize_command_creates_private_gh_config(devcontainer_dir):
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")
    private_dirs = [
        command
        for command in config["initializeCommand"].split("&&")
        if command.strip().startswith("mkdir -p -m 700 ")
    ]

    # Le dossier contient le token gh
    assert any(
        '"${localEnv:HOME}/.config/gh-devcontainers"' in command
        for command in private_dirs
    )


def test_initialize_command_creates_config_dir_in_persistent_home(devcontainer_dir):
    # Sinon Docker crée /home/vscode/.config en root pour y monter .config/gh
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")

    assert (
        '"${localEnv:HOME}/.devcontainer/homes/'
        '${localWorkspaceFolderBasename}-${devcontainerId}/.config"'
        in config["initializeCommand"]
    )


def test_post_create_never_runs_gh_auth_login(devcontainer_dir):
    script = (devcontainer_dir / "postCreateCommand.sh").read_text()

    assert "gh auth login" not in script


def test_zshrc_runs_gh_login_hook(devcontainer_dir):
    script = (devcontainer_dir / "postCreateCommand.sh").read_text()

    assert f"ensure_zshrc_line '{LOGIN_HOOK}'" in extract_function(script, "config_zsh")


def test_gh_login_script_is_identical_in_repo_and_project(devcontainer_dir):
    script = devcontainer_dir / "scripts" / "gh_login.sh"

    assert (
        script.read_text()
        == (REPO_DEVCONTAINER / "scripts" / "gh_login.sh").read_text()
    )


@pytest.fixture
def fake_gh(tmp_path: Path) -> dict[str, str]:
    """Environnement où `gh` est un faux qui journalise ses appels."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    return {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "FAKE_GH_LOG": str(tmp_path / "gh.log"),
        "FAKE_GH_TOKEN": "",
        "GH_LOGIN_MARKER": str(tmp_path / "gh-login-attempted"),
    }


def gh_calls(env: dict[str, str]) -> list[str]:
    log = Path(env["FAKE_GH_LOG"])
    return log.read_text().splitlines() if log.exists() else []


# --- setup_gh_credential_helper -------------------------------------------------


@pytest.fixture
def setup_gh_credential_helper(devcontainer_dir: Path) -> str:
    script = (devcontainer_dir / "postCreateCommand.sh").read_text()
    return extract_function(script, "setup_gh_credential_helper")


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def local_config(repo: Path, key: str) -> list[str]:
    result = subprocess.run(
        ["git", "config", "--local", "--get-all", key],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def test_credential_helper_delegates_github_to_gh(
    setup_gh_credential_helper, git_repo, fake_gh
):
    subprocess.run(
        [
            "bash",
            "-c",
            f"set -e\n{setup_gh_credential_helper}\nsetup_gh_credential_helper",
        ],
        cwd=git_repo,
        env=fake_gh,
        check=True,
        capture_output=True,
    )

    assert local_config(git_repo, "credential.helper") == [""]
    assert local_config(git_repo, "credential.https://github.com.helper") == [
        "!gh auth git-credential"
    ]


def test_credential_helper_untouched_without_gh(
    setup_gh_credential_helper, git_repo, tmp_path
):
    # PATH sans gh : seulement git
    bin_dir = tmp_path / "nogh"
    bin_dir.mkdir()
    git = shutil.which("git")
    assert git
    (bin_dir / "git").symlink_to(git)
    env = {**os.environ, "PATH": str(bin_dir)}

    subprocess.run(
        [
            "/bin/bash",
            "-c",
            f"set -e\n{setup_gh_credential_helper}\nsetup_gh_credential_helper",
        ],
        cwd=git_repo,
        env=env,
        check=True,
        capture_output=True,
    )

    assert local_config(git_repo, "credential.https://github.com.helper") == []


# --- gh_login.sh -----------------------------------------------------------------


def run_gh_login(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(REPO_DEVCONTAINER / "scripts" / "gh_login.sh")],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def logins(env: dict[str, str]) -> list[str]:
    return [call for call in gh_calls(env) if call.startswith("auth login")]


def test_gh_login_does_nothing_when_authenticated(fake_gh):
    fake_gh["FAKE_GH_TOKEN"] = "gho_xxx"

    result = run_gh_login(fake_gh)

    assert result.returncode == 0
    assert result.stdout == ""
    assert logins(fake_gh) == []


def test_gh_login_checks_auth_offline(fake_gh):
    fake_gh["FAKE_GH_TOKEN"] = "gho_xxx"

    run_gh_login(fake_gh)

    # `gh auth status` interroge l'API : trop lent à chaque ouverture de terminal
    assert not any(call.startswith("auth status") for call in gh_calls(fake_gh))


def test_gh_login_runs_web_login_when_not_authenticated(fake_gh):
    result = run_gh_login(fake_gh)

    assert result.returncode == 0
    assert logins(fake_gh) == [
        "auth login --hostname github.com --git-protocol https --web --skip-ssh-key"
    ]
    assert Path(fake_gh["GH_LOGIN_MARKER"]).exists()


def test_gh_login_is_attempted_once_per_container(fake_gh):
    run_gh_login(fake_gh)

    result = run_gh_login(fake_gh)

    assert result.returncode == 0
    assert len(logins(fake_gh)) == 1
    assert "gh auth login --web" in result.stdout


def test_gh_login_failure_never_breaks_the_shell(fake_gh):
    fake_gh["FAKE_GH_LOGIN"] = "fail"

    result = run_gh_login(fake_gh)

    assert result.returncode == 0


def test_gh_login_is_silent_without_gh(tmp_path):
    env = {**os.environ, "PATH": str(tmp_path), "GH_LOGIN_MARKER": str(tmp_path / "m")}

    result = subprocess.run(
        ["/bin/bash", str(REPO_DEVCONTAINER / "scripts" / "gh_login.sh")],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout == ""
