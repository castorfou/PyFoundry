"""Tests de la recréation du venv au démarrage du conteneur (issue #86).

Avec docker-in-docker, `/tmp` est un tmpfs remonté à chaque démarrage : un
redémarrage sans rebuild efface `/tmp/venv`. `postStartCommand` lance
`.devcontainer/scripts/ensure_venv.sh`, qui le recrée s'il manque.
"""

import os
import re
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tests.devcontainer_utils import REPO_DEVCONTAINER, parse_jsonc


SCRIPT = REPO_DEVCONTAINER / "scripts" / "ensure_venv.sh"
GUARDED_ACTIVATE = "[[ ! -f /tmp/venv/bin/activate ]] || source /tmp/venv/bin/activate"
OLD_ACTIVATE = "source /tmp/venv/bin/activate"

# Faux uv : journalise ses appels (avec VIRTUAL_ENV) ; `uv venv DIR` crée DIR/bin/python.
# FAKE_UV_FAIL=1 le fait échouer.
FAKE_UV = """#!/usr/bin/env bash
echo "$*|VIRTUAL_ENV=${VIRTUAL_ENV:-}" >> "$FAKE_UV_LOG"
[ "${FAKE_UV_FAIL:-}" = "1" ] && exit 1
if [ "$1" = "venv" ]; then
    mkdir -p "$2/bin"
    printf '#!/bin/sh\\n' > "$2/bin/python"
    chmod +x "$2/bin/python"
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


def extract_function(script: str, name: str) -> str:
    """Extrait le corps d'une fonction bash définie au niveau du script."""
    match = re.search(
        rf"^{re.escape(name)}\(\) \{{\n.*?^\}}$", script, re.DOTALL | re.MULTILINE
    )
    assert match, f"Fonction {name} introuvable"
    return match.group(0)


# --- Câblage dans le devcontainer --------------------------------------------------


def test_post_start_ensures_venv(devcontainer_dir):
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")

    assert "bash .devcontainer/scripts/ensure_venv.sh" in config["postStartCommand"]


def test_ensure_venv_script_is_identical_in_repo_and_project(devcontainer_dir):
    assert (
        devcontainer_dir / "scripts" / "ensure_venv.sh"
    ).read_text() == SCRIPT.read_text()


def test_post_create_delegates_venv_creation(devcontainer_dir):
    script = (devcontainer_dir / "postCreateCommand.sh").read_text()
    function = extract_function(script, "create_python_environment")

    assert "bash .devcontainer/scripts/ensure_venv.sh --sync" in function
    assert "uv venv" not in function


# --- ensure_venv.sh ----------------------------------------------------------------


@pytest.fixture
def fake_uv(tmp_path: Path) -> dict[str, str]:
    """Environnement où `uv` est un faux et le venv vit dans tmp_path."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text(FAKE_UV)
    uv.chmod(uv.stat().st_mode | stat.S_IEXEC)
    env = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
    return {
        **env,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "FAKE_UV_LOG": str(tmp_path / "uv.log"),
        "VENV_HOME": str(tmp_path / "venv"),
        "PYTHON_VERSION": "3.11",
    }


def run_ensure_venv(
    env: dict[str, str], *args: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def uv_calls(env: dict[str, str]) -> list[str]:
    log = Path(env["FAKE_UV_LOG"])
    return log.read_text().splitlines() if log.exists() else []


def make_venv(env: dict[str, str]) -> None:
    python = Path(env["VENV_HOME"]) / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.write_text("#!/bin/sh\n")
    python.chmod(0o755)


def test_missing_venv_is_created_then_synced(fake_uv):
    venv = fake_uv["VENV_HOME"]

    result = run_ensure_venv(fake_uv)

    assert result.returncode == 0, result.stderr
    assert uv_calls(fake_uv) == [
        f"venv {venv} --python 3.11|VIRTUAL_ENV=",
        f"sync --active --all-extras|VIRTUAL_ENV={venv}",
    ]


def test_existing_venv_is_left_alone(fake_uv):
    make_venv(fake_uv)

    result = run_ensure_venv(fake_uv)

    assert result.returncode == 0, result.stderr
    assert uv_calls(fake_uv) == []


def test_sync_option_resyncs_existing_venv(fake_uv):
    make_venv(fake_uv)

    result = run_ensure_venv(fake_uv, "--sync")

    assert result.returncode == 0, result.stderr
    assert uv_calls(fake_uv) == [
        f"sync --active --all-extras|VIRTUAL_ENV={fake_uv['VENV_HOME']}"
    ]


def test_venv_without_python_is_recreated(fake_uv):
    """Un venv à moitié créé (dossier sans interpréteur) est refait."""
    Path(fake_uv["VENV_HOME"], "bin").mkdir(parents=True)

    result = run_ensure_venv(fake_uv)

    assert result.returncode == 0, result.stderr
    assert [call.split()[0] for call in uv_calls(fake_uv)] == ["venv", "sync"]


def test_uv_failure_is_reported_with_workaround(fake_uv):
    result = run_ensure_venv({**fake_uv, "FAKE_UV_FAIL": "1"})

    assert result.returncode != 0
    assert "uv sync --active --all-extras" in result.stdout + result.stderr


# --- Activation du venv dans .zshrc ----------------------------------------------


@pytest.fixture
def setup_venv_activation(devcontainer_dir: Path) -> str:
    script = (devcontainer_dir / "postCreateCommand.sh").read_text()
    return "\n".join(
        extract_function(script, name)
        for name in ("ensure_zshrc_line", "setup_venv_activation")
    )


def run_setup_venv_activation(code: str, home: Path) -> str:
    subprocess.run(
        ["bash", "-c", f"{code}\nsetup_venv_activation"],
        env={**os.environ, "HOME": str(home)},
        check=True,
        capture_output=True,
        text=True,
    )
    return (home / ".zshrc").read_text()


def test_zshrc_activates_venv_only_if_present(setup_venv_activation, tmp_path):
    zshrc = run_setup_venv_activation(setup_venv_activation, tmp_path)

    assert zshrc.splitlines() == [GUARDED_ACTIVATE]


def test_zshrc_unguarded_activation_is_replaced(setup_venv_activation, tmp_path):
    """Le HOME est persistant : la ligne d'avant #86 est retirée au rebuild."""
    (tmp_path / ".zshrc").write_text(f"export FOO=1\n{OLD_ACTIVATE}\nexport BAR=2\n")

    zshrc = run_setup_venv_activation(setup_venv_activation, tmp_path)

    assert zshrc.splitlines() == ["export FOO=1", "export BAR=2", GUARDED_ACTIVATE]


def test_zshrc_activation_is_added_once(setup_venv_activation, tmp_path):
    run_setup_venv_activation(setup_venv_activation, tmp_path)

    zshrc = run_setup_venv_activation(setup_venv_activation, tmp_path)

    assert zshrc.splitlines() == [GUARDED_ACTIVATE]
