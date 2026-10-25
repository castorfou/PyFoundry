"""Tests de scripts/clean_test_project.sh (issue #92).

Supprimer le dossier d'un projet de test n'arrête pas son devcontainer : il
continue à tourner, orphelin. Le script supprime le conteneur (retrouvé par le
label `devcontainer.local_folder`), puis le dossier, puis le HOME persistant.
`docker` est remplacé par un faux qui journalise ses appels
(`CLEAN_TEST_PROJECT_DOCKER`).
"""

import os
import subprocess
from pathlib import Path

import pytest

from tests.devcontainer_utils import REPO_ROOT


SCRIPT_PATH = REPO_ROOT / "scripts" / "clean_test_project.sh"

FAKE_DOCKER = """#!/usr/bin/env bash
if [ "$1" = rm ]; then
    if [ -e "$FAKE_DOCKER_WATCHED" ]; then state=dir-exists; else state=dir-gone; fi
    echo "$* [$state]" >> "$FAKE_DOCKER_LOG"
else
    echo "$*" >> "$FAKE_DOCKER_LOG"
fi
if [ "$1" = ps ] && [ -n "$FAKE_DOCKER_IDS" ]; then
    printf '%s\\n' $FAKE_DOCKER_IDS
fi
exit 0
"""


@pytest.fixture
def host(tmp_path: Path) -> dict[str, Path]:
    """Hôte factice : HOME, dossier de travail et faux docker."""
    home = tmp_path / "home"
    (home / ".devcontainer" / "homes").mkdir(parents=True)
    work = tmp_path / "work"
    work.mkdir()
    docker = tmp_path / "bin" / "docker"
    docker.parent.mkdir()
    docker.write_text(FAKE_DOCKER)
    docker.chmod(0o755)
    return {
        "home": home,
        "work": work,
        "docker": docker,
        "log": tmp_path / "docker.log",
    }


def run_clean(
    host: dict[str, Path], *args: str, ids: str = "", docker: str | None = None
) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(
        HOME=str(host["home"]),
        CLEAN_TEST_PROJECT_DOCKER=docker or str(host["docker"]),
        FAKE_DOCKER_LOG=str(host["log"]),
        FAKE_DOCKER_IDS=ids,
        FAKE_DOCKER_WATCHED=str(host["work"] / "projet"),
    )
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=host["work"],
        env=env,
    )


def docker_calls(host: dict[str, Path]) -> list[str]:
    log = host["log"]
    return log.read_text().splitlines() if log.exists() else []


def make_project(host: dict[str, Path], name: str = "projet") -> Path:
    project = host["work"] / name
    (project / ".devcontainer").mkdir(parents=True)
    return project


def make_home(host: dict[str, Path], name: str) -> Path:
    path = host["home"] / ".devcontainer" / "homes" / name
    (path / ".cache").mkdir(parents=True)
    return path


@pytest.mark.parametrize("arg", [None, "~", "/"])
def test_refuses_missing_or_dangerous_argument(host, arg):
    """Sans dossier, ou avec le HOME ou `/`, rien n'est supprimé."""
    args = [] if arg is None else [str(host["home"]) if arg == "~" else arg]

    result = run_clean(host, *args, ids="abc123")

    assert result.returncode != 0
    assert "Usage" in result.stderr or "refus" in result.stderr.lower()
    assert host["home"].exists()
    assert not any(call.startswith("rm") for call in docker_calls(host))


def test_removes_container_before_project_folder(host):
    """Le conteneur est supprimé pendant que le dossier existe encore, puis le dossier."""
    project = make_project(host)

    result = run_clean(host, str(project), ids="abc123 def456")

    assert result.returncode == 0, result.stderr
    assert docker_calls(host) == [
        f"ps -aq --filter label=devcontainer.local_folder={project}",
        "rm -f abc123 def456 [dir-exists]",
    ]
    assert not project.exists()


def test_no_container_means_no_docker_rm(host):
    project = make_project(host)

    result = run_clean(host, str(project))

    assert result.returncode == 0, result.stderr
    assert not any(call.startswith("rm") for call in docker_calls(host))
    assert not project.exists()


def test_relative_path_is_resolved_for_label(host):
    """Le label de VS Code contient le chemin absolu du dossier."""
    project = make_project(host)

    result = run_clean(host, "projet", ids="abc123")

    assert result.returncode == 0, result.stderr
    assert (
        docker_calls(host)[0]
        == f"ps -aq --filter label=devcontainer.local_folder={project}"
    )
    assert not project.exists()


def test_already_deleted_folder_still_cleans_container_and_home(host):
    """Le cas de l'issue : dossier supprimé à la main, conteneur toujours actif."""
    project = host["work"] / "projet"
    home = make_home(host, "projet-abc123")

    result = run_clean(host, str(project), ids="abc123")

    assert result.returncode == 0, result.stderr
    assert docker_calls(host) == [
        f"ps -aq --filter label=devcontainer.local_folder={project}",
        "rm -f abc123 [dir-gone]",
    ]
    assert not home.exists()


def test_removes_only_the_project_home(host):
    """`projet-<id>` est supprimé, pas le HOME de `projet-2` ni d'un autre projet."""
    project = make_project(host)
    own = make_home(host, "projet-abc123")
    other_id = make_home(host, "projet-def456")
    sibling = make_home(host, "projet-2-abc123")
    other = make_home(host, "autre-abc123")

    result = run_clean(host, str(project))

    assert result.returncode == 0, result.stderr
    assert not own.exists()
    assert not other_id.exists()
    assert sibling.exists()
    assert other.exists()


def test_without_docker_prints_host_command(host):
    """Dans le devcontainer PyFoundry, pas de docker : la commande pour l'hôte est donnée."""
    project = make_project(host)
    home = make_home(host, "projet-abc123")

    result = run_clean(host, str(project), docker="docker-introuvable")

    assert result.returncode == 0, result.stderr
    output = result.stdout + result.stderr
    assert "hôte" in output
    assert f'--filter "label=devcontainer.local_folder={project}"' in output
    assert "docker rm -f" in output
    assert not project.exists()
    assert not home.exists()


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignore les permissions")
def test_undeletable_home_suggests_sudo(host):
    """Un HOME avec des dossiers root : l'échec se voit, avec la commande sudo."""
    project = make_project(host)
    home = make_home(host, "projet-abc123")
    locked = home / ".cache"
    (locked / "uv").mkdir()
    locked.chmod(0o555)

    try:
        result = run_clean(host, str(project))
    finally:
        locked.chmod(0o755)

    assert result.returncode != 0
    assert f"sudo rm -rf {home}" in result.stdout + result.stderr
    assert not project.exists()
