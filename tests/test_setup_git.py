"""Tests de setup_git dans .devcontainer/postCreateCommand.sh (issue #94).

Au premier build, le HOME est neuf : il n'y a pas encore d'identité git globale.
Le commit initial doit réussir sans écrire d'identité dans `.git/config`, sinon
elle l'emporte ensuite sur l'identité globale de l'utilisateur.
"""

import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tests.devcontainer_utils import REPO_DEVCONTAINER, REPO_ROOT
from tests.test_post_create_command import extract_function


LEGACY_NAME = "Default User"
LEGACY_EMAIL = "default@michelin" + ".com"  # assemblée, voir test_no_internal_domain


@pytest.fixture(params=["repo", "skeleton"])
def setup_git(
    request: pytest.FixtureRequest,
    cookies: Any,
    default_template_context: dict[str, str],
) -> str:
    """Code de setup_git, du dépôt PyFoundry ou du projet généré."""
    if request.param == "repo":
        script_path = REPO_DEVCONTAINER / "postCreateCommand.sh"
    else:
        result = cookies.bake(extra_context=default_template_context)
        assert result.exit_code == 0
        script_path = result.project_path / ".devcontainer" / "postCreateCommand.sh"
    return extract_function(script_path.read_text(), "setup_git")


@pytest.fixture
def workspace(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """Projet sans dépôt git, avec une config globale vide et isolée."""
    global_config = tmp_path / "gitconfig"
    global_config.touch()
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("GIT_", "GITHUB_")) and key != "EMAIL"
    }
    env.update({"GIT_CONFIG_GLOBAL": str(global_config), "GIT_CONFIG_NOSYSTEM": "1"})
    project = tmp_path / "projet"
    project.mkdir()
    (project / "README.md").write_text("# Projet\n")
    return project, env


def git(project: Path, env: dict[str, str], *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=project, env=env, check=True, capture_output=True, text=True
    ).stdout.strip()


def local_config(project: Path, env: dict[str, str], key: str) -> str:
    """Valeur de la config locale du dépôt, vide si absente."""
    return subprocess.run(
        ["git", "config", "--local", "--get", key],
        cwd=project,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    ).stdout.strip()


def run_setup_git(
    code: str, project: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", f"{code}\nsetup_git"],
        check=False,
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def set_global_identity(env: dict[str, str]) -> None:
    for key, value in (("user.name", "Alice"), ("user.email", "alice@example.com")):
        subprocess.run(["git", "config", "--global", key, value], env=env, check=True)


def test_without_identity_uses_github_noreply(setup_git, workspace):
    """Sans identité, le commit initial utilise l'adresse noreply de GITHUB_USERNAME."""
    project, env = workspace
    env["GITHUB_USERNAME"] = "octocat"

    result = run_setup_git(setup_git, project, env)

    assert result.returncode == 0, result.stderr
    assert git(project, env, "log", "-1", "--format=%an <%ae>") == (
        "octocat <octocat@users.noreply.github.com>"
    )
    assert local_config(project, env, "user.email") == ""
    assert local_config(project, env, "user.name") == ""
    assert "git config --global user.email" in result.stdout


def test_without_identity_nor_github_username(setup_git, workspace):
    """Sans GITHUB_USERNAME, le commit initial utilise une identité PyFoundry neutre."""
    project, env = workspace

    result = run_setup_git(setup_git, project, env)

    assert result.returncode == 0, result.stderr
    assert git(project, env, "log", "-1", "--format=%an <%ae>") == (
        "PyFoundry <pyfoundry@users.noreply.github.com>"
    )
    assert local_config(project, env, "user.email") == ""


def test_with_global_identity(setup_git, workspace):
    """Avec une identité globale, le commit initial l'utilise, sans avertissement."""
    project, env = workspace
    env["GITHUB_USERNAME"] = "octocat"
    set_global_identity(env)

    result = run_setup_git(setup_git, project, env)

    assert result.returncode == 0, result.stderr
    assert git(project, env, "log", "-1", "--format=%an <%ae>") == (
        "Alice <alice@example.com>"
    )
    assert local_config(project, env, "user.email") == ""
    assert "⚠️" not in result.stdout


def test_rebuild_removes_legacy_identity(setup_git, workspace):
    """Au rebuild, l'ancienne identité par défaut est retirée de .git/config."""
    project, env = workspace
    set_global_identity(env)
    git(project, env, "init", "-q")
    git(project, env, "config", "user.name", LEGACY_NAME)
    git(project, env, "config", "user.email", LEGACY_EMAIL)

    result = run_setup_git(setup_git, project, env)

    assert result.returncode == 0, result.stderr
    assert local_config(project, env, "user.email") == ""
    assert local_config(project, env, "user.name") == ""
    assert git(project, env, "config", "user.email") == "alice@example.com"


def test_rebuild_keeps_other_local_identity(setup_git, workspace):
    """Une identité locale choisie par l'utilisateur n'est pas touchée."""
    project, env = workspace
    git(project, env, "init", "-q")
    git(project, env, "config", "user.name", "Bob")
    git(project, env, "config", "user.email", "bob@example.com")

    result = run_setup_git(setup_git, project, env)

    assert result.returncode == 0, result.stderr
    assert local_config(project, env, "user.email") == "bob@example.com"
    assert local_config(project, env, "user.name") == "Bob"


def test_no_internal_domain(cookies, default_template_context):
    """Plus aucune référence au domaine d'entreprise, ni au dépôt ni au projet généré."""
    result = cookies.bake(extra_context=default_template_context)
    assert result.exit_code == 0
    # Le domaine est assemblé ici pour que ce fichier ne contienne pas la chaîne
    domain = "michelin" + ".com"
    # Seul setup_git (dépôt et squelette) peut citer l'ancienne adresse, pour la retirer
    allowed = {"postCreateCommand.sh", "CHANGELOG.md"}
    # Fichiers du dépôt suivis ou à suivre (hors .gitignore) ; le squelette est
    # couvert par le projet généré
    repo_files = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    candidates = [(REPO_ROOT, Path(name)) for name in repo_files]
    candidates += [
        (result.project_path, path.relative_to(result.project_path))
        for path in result.project_path.rglob("*")
        if path.is_file()
    ]
    offenders = [
        str(root / relative)
        for root, relative in candidates
        if relative.name not in allowed
        and (root / relative).is_file()
        and domain in (root / relative).read_text(errors="ignore")
    ]
    assert offenders == []
