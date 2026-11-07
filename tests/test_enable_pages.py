"""Tests de l'activation automatique de GitHub Pages (issue #116).

`docs.yml` publie la doc avec GitHub Actions, mais ne peut pas activer Pages :
le `GITHUB_TOKEN` n'a pas les droits admin (#85). `enable_pages.sh` l'active au
terminal zsh, juste après `gh_login.sh`, avec le compte `gh` de l'utilisateur.
Seulement sur un dépôt public ; la source « Deploy from a branch » n'est jamais
modifiée. Un marqueur dans `.git/` évite tout appel réseau une fois le dépôt réglé.
"""

import os
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tests.devcontainer_utils import REPO_DEVCONTAINER
from tests.test_post_create_command import extract_function


REPO_ROOT = REPO_DEVCONTAINER.parent
SCRIPT = REPO_DEVCONTAINER / "scripts" / "enable_pages.sh"
LOGIN_HOOK = 'bash "$WORKSPACE_FOLDER/.devcontainer/scripts/gh_login.sh"'
PAGES_HOOK = 'bash "$WORKSPACE_FOLDER/.devcontainer/scripts/enable_pages.sh"'
POST = "api -X POST repos/castorfou/demo/pages -f build_type=workflow"

# Faux gh : journalise ses appels et répond selon l'environnement.
# FAKE_REPO : réponse de `gh api repos/...` (visibility, admin, has_pages), ou `fail`
FAKE_GH = """#!/usr/bin/env bash
echo "$*" >> "$FAKE_GH_LOG"
case "$*" in
    "auth token")
        [ -n "$FAKE_GH_TOKEN" ] && echo "$FAKE_GH_TOKEN" && exit 0
        exit 1 ;;
    "api -X POST "*)
        [ "$FAKE_POST" = "fail" ] && echo "HTTP 403" >&2 && exit 1
        exit 0 ;;
    "api -X PUT "*)
        exit 0 ;;
    "api repos/"*"/pages --jq .build_type")
        echo "$FAKE_BUILD_TYPE" ;;
    "api repos/"*)
        [ "$FAKE_REPO" = "fail" ] && echo "HTTP 404: Not Found" >&2 && exit 1
        printf '%b\\n' "$FAKE_REPO" ;;
esac
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


def test_enable_pages_script_is_identical_in_repo_and_project(devcontainer_dir):
    script = devcontainer_dir / "scripts" / "enable_pages.sh"

    assert script.read_text() == SCRIPT.read_text()


def test_zshrc_runs_enable_pages_after_gh_login(devcontainer_dir):
    script = (devcontainer_dir / "postCreateCommand.sh").read_text()
    config_zsh = extract_function(script, "config_zsh")

    login = config_zsh.index(f"ensure_zshrc_line '{LOGIN_HOOK}'")
    pages = config_zsh.index(f"ensure_zshrc_line '{PAGES_HOOK}'")
    assert login < pages


# --- enable_pages.sh --------------------------------------------------------------


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Dépôt git dont `origin` pointe sur castorfou/demo."""
    path = tmp_path / "demo"
    path.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    set_origin(path, "https://github.com/castorfou/demo.git")
    return path


def set_origin(repo: Path, url: str) -> None:
    subprocess.run(
        ["git", "remote", "remove", "origin"],
        cwd=repo,
        check=False,
        capture_output=True,
    )
    subprocess.run(["git", "remote", "add", "origin", url], cwd=repo, check=True)


@pytest.fixture
def env(tmp_path: Path, repo: Path) -> dict[str, str]:
    """Faux gh authentifié ; dépôt public, admin, Pages désactivé."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    return {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "WORKSPACE_FOLDER": str(repo),
        "FAKE_GH_LOG": str(tmp_path / "gh.log"),
        "FAKE_GH_TOKEN": "gho_xxx",
        "FAKE_REPO": "public\\ntrue\\nfalse",
        "FAKE_BUILD_TYPE": "workflow",
        "FAKE_POST": "",
        "PAGES_MARKER": str(tmp_path / "pages-marker"),
    }


def run_script(env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        env=env,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    # Lancé à chaque ouverture de terminal : jamais d'échec, jamais de bruit sur stderr
    assert result.returncode == 0
    assert result.stderr == ""
    assert len(result.stdout.splitlines()) <= 1
    return result


def api_calls(env: dict[str, str]) -> list[str]:
    log = Path(env["FAKE_GH_LOG"])
    calls = log.read_text().splitlines() if log.exists() else []
    return [call for call in calls if call.startswith("api ")]


def marker(env: dict[str, str]) -> Path:
    return Path(env["PAGES_MARKER"])


def test_enables_pages_with_github_actions_source(env, repo):
    result = run_script(env, repo)

    assert POST in api_calls(env)
    assert "GitHub Pages activé" in result.stdout
    assert marker(env).exists()


def test_does_nothing_when_pages_already_uses_github_actions(env, repo):
    env["FAKE_REPO"] = "public\\ntrue\\ntrue"

    result = run_script(env, repo)

    assert result.stdout == ""
    assert not [call for call in api_calls(env) if " -X " in call]
    assert marker(env).exists()


def test_never_changes_deploy_from_a_branch_source(env, repo):
    env["FAKE_REPO"] = "public\\ntrue\\ntrue"
    env["FAKE_BUILD_TYPE"] = "legacy"

    result = run_script(env, repo)

    assert not [call for call in api_calls(env) if " -X " in call]
    assert "docs/cheatsheets/mkdocs.md" in result.stdout
    assert marker(env).exists()


@pytest.mark.parametrize("visibility", ["private", "internal"])
def test_never_enables_pages_on_non_public_repo(env, repo, visibility):
    env["FAKE_REPO"] = f"{visibility}\\ntrue\\nfalse"

    result = run_script(env, repo)

    assert POST not in api_calls(env)
    assert "docs/cheatsheets/mkdocs.md" in result.stdout
    assert marker(env).exists()


def test_never_enables_pages_without_admin_rights(env, repo):
    env["FAKE_REPO"] = "public\\nfalse\\nfalse"

    result = run_script(env, repo)

    assert POST not in api_calls(env)
    assert result.stdout != ""
    assert marker(env).exists()


def test_retries_later_when_repo_is_not_reachable(env, repo):
    # Dépôt GitHub pas encore créé, réseau coupé, timeout
    env["FAKE_REPO"] = "fail"

    result = run_script(env, repo)

    assert result.stdout == ""
    assert not marker(env).exists()

    env["FAKE_REPO"] = "public\\ntrue\\nfalse"
    run_script(env, repo)

    assert POST in api_calls(env)


def test_failed_activation_is_reported_and_retried(env, repo):
    env["FAKE_POST"] = "fail"

    result = run_script(env, repo)

    assert "gh api -X POST" in result.stdout
    assert not marker(env).exists()


def test_no_network_call_once_repo_is_settled(env, repo):
    run_script(env, repo)
    calls = len(api_calls(env))

    result = run_script(env, repo)

    assert result.stdout == ""
    assert len(api_calls(env)) == calls


def test_checks_again_when_origin_changes(env, repo):
    run_script(env, repo)
    set_origin(repo, "git@github.com:castorfou/autre.git")

    run_script(env, repo)

    assert (
        api_calls(env)[-1]
        == "api -X POST repos/castorfou/autre/pages -f build_type=workflow"
    )


def test_default_marker_lives_in_git_dir(env, repo):
    del env["PAGES_MARKER"]

    run_script(env, repo)

    assert (repo / ".git" / "pyfoundry-pages").read_text().strip() == "castorfou/demo"


def test_reads_repo_of_workspace_folder(env, repo, tmp_path):
    # Un terminal peut s'ouvrir hors du dossier du projet
    run_script(env, tmp_path)

    assert POST in api_calls(env)


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/castorfou/demo.git",
        "https://github.com/castorfou/demo",
        "git@github.com:castorfou/demo.git",
        "ssh://git@github.com/castorfou/demo.git",
    ],
)
def test_reads_owner_and_repo_from_origin(env, repo, url):
    set_origin(repo, url)

    run_script(env, repo)

    assert api_calls(env)[0].startswith("api repos/castorfou/demo ")


def test_silent_when_not_authenticated(env, repo):
    env["FAKE_GH_TOKEN"] = ""

    result = run_script(env, repo)

    assert result.stdout == ""
    assert api_calls(env) == []


def test_silent_when_origin_is_not_github(env, repo):
    set_origin(repo, "https://gitlab.com/castorfou/demo.git")

    result = run_script(env, repo)

    assert result.stdout == ""
    assert api_calls(env) == []


def test_silent_without_origin(env, repo):
    subprocess.run(["git", "remote", "remove", "origin"], cwd=repo, check=True)

    result = run_script(env, repo)

    assert result.stdout == ""
    assert api_calls(env) == []


def test_silent_outside_git_repo(env, tmp_path):
    folder = tmp_path / "pas-un-depot"
    folder.mkdir()
    env["WORKSPACE_FOLDER"] = str(folder)

    result = run_script(env, folder)

    assert result.stdout == ""
    assert api_calls(env) == []


def test_silent_without_gh(env, repo, tmp_path):
    empty = tmp_path / "vide"
    empty.mkdir()
    env["PATH"] = str(empty)

    result = subprocess.run(
        ["/bin/bash", str(SCRIPT)],
        env=env,
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout == result.stderr == ""


# --- Documentation -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("root", "doc"),
    [
        ("repo", "docs/user/usage.md"),
        ("repo", "docs/cheatsheets/mkdocs.md"),
        ("repo", "docs/user/troubleshooting.md"),
        ("generated", "docs/cheatsheets/mkdocs.md"),
        ("generated", "CLAUDE.md"),
    ],
)
def test_automatic_activation_documented(root, doc, cookies, minimal_template_context):
    if root == "repo":
        base = REPO_ROOT
    else:
        result = cookies.bake(extra_context=minimal_template_context)
        assert result.exit_code == 0
        base = Path(result.project_path)

    assert "enable_pages.sh" in (base / doc).read_text()


def test_troubleshooting_explains_missing_pages_site():
    content = (REPO_ROOT / "docs" / "user" / "troubleshooting.md").read_text()

    assert "Get Pages site failed" in content
