"""Tests de setup_pre-commit dans .devcontainer/postCreateCommand.sh (issue #68).

La fonction tourne à chaque rebuild du devcontainer : elle met à jour les hooks
pre-commit et ne doit commiter que `.pre-commit-config.yaml`, jamais le travail
en cours de l'utilisateur.
"""

import os
import re
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tests.devcontainer_utils import REPO_DEVCONTAINER


CONFIG = ".pre-commit-config.yaml"

# Faux pre-commit : `autoupdate` modifie la config seulement si FAKE_AUTOUPDATE=change
FAKE_PRE_COMMIT = """#!/usr/bin/env bash
if [ "$1" = "autoupdate" ] && [ "$FAKE_AUTOUPDATE" = "change" ]; then
    sed -i 's/rev: v1/rev: v2/' .pre-commit-config.yaml
fi
exit 0
"""


def extract_function(script: str, name: str) -> str:
    """Extrait le corps d'une fonction bash définie au niveau du script."""
    match = re.search(
        rf"^{re.escape(name)}\(\) \{{\n.*?^\}}$", script, re.DOTALL | re.MULTILINE
    )
    assert match, f"Fonction {name} introuvable"
    return match.group(0)


@pytest.fixture(params=["repo", "skeleton"])
def setup_precommit(
    request: pytest.FixtureRequest,
    cookies: Any,
    default_template_context: dict[str, str],
) -> str:
    """Code de setup_pre-commit, du dépôt PyFoundry ou du projet généré."""
    if request.param == "repo":
        script_path = REPO_DEVCONTAINER / "postCreateCommand.sh"
    else:
        result = cookies.bake(extra_context=default_template_context)
        assert result.exit_code == 0
        script_path = result.project_path / ".devcontainer" / "postCreateCommand.sh"
    return extract_function(script_path.read_text(), "setup_pre-commit")


@pytest.fixture
def workspace(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """Dépôt git avec un commit initial et du travail en cours non commité."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "pre-commit"
    fake.write_text(FAKE_PRE_COMMIT)
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)

    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=repo, env=env, check=True, capture_output=True
        )

    git("init", "-q")
    (repo / CONFIG).write_text("repos:\n  - repo: local\n    rev: v1\n    hooks: []\n")
    (repo / "travail.py").write_text("v1\n")
    (repo / "pret.py").write_text("v1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "Initial commit")

    # Travail en cours : un fichier modifié, un fichier dans l'index, un nouveau fichier
    (repo / "travail.py").write_text("v2 en cours\n")
    (repo / "pret.py").write_text("v2 prêt\n")
    git("add", "pret.py")
    (repo / "brouillon.py").write_text("brouillon\n")
    return repo, env


def git_output(repo: Path, env: dict[str, str], *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True
    ).stdout


def run_setup_precommit(
    code: str, repo: Path, env: dict[str, str], autoupdate: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", f"{code}\nsetup_pre-commit"],
        check=False,
        cwd=repo,
        env={**env, "FAKE_AUTOUPDATE": autoupdate},
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_no_hook_update_commits_nothing(setup_precommit, workspace):
    """Sans nouvelle version de hook, le rebuild ne commite rien."""
    repo, env = workspace
    head = git_output(repo, env, "rev-parse", "HEAD")
    status = git_output(repo, env, "status", "--porcelain")

    result = run_setup_precommit(setup_precommit, repo, env, autoupdate="none")

    assert result.returncode == 0, result.stderr
    assert git_output(repo, env, "rev-parse", "HEAD") == head
    assert git_output(repo, env, "status", "--porcelain") == status


def test_hook_update_commits_only_precommit_config(setup_precommit, workspace):
    """Une mise à jour des hooks commite la config seule, sans le travail en cours."""
    repo, env = workspace
    head = git_output(repo, env, "rev-parse", "HEAD").strip()
    status = git_output(repo, env, "status", "--porcelain")

    result = run_setup_precommit(setup_precommit, repo, env, autoupdate="change")

    assert result.returncode == 0, result.stderr
    assert git_output(repo, env, "rev-parse", "HEAD~1").strip() == head
    committed = git_output(repo, env, "show", "--name-only", "--format=", "HEAD")
    assert committed.split() == [CONFIG]
    assert "rev: v2" in git_output(repo, env, "show", f"HEAD:{CONFIG}")
    assert git_output(repo, env, "status", "--porcelain") == status
