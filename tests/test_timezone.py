"""Tests du fuseau horaire des devcontainers (issue #65).

Dans l'image, /etc/localtime est un lien vers zoneinfo/Etc/UTC : monter le
fichier de l'hôte sur /etc/localtime le monte en fait sur Etc/UTC. UTC devient
alors l'heure locale et la mise à jour de tzdata échoue. Le fichier de l'hôte
est donc monté sur /etc/localtime.host, puis setup_timezone de
postCreateCommand.sh fait pointer /etc/localtime vers la zone correspondante.
"""

import os
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tests.devcontainer_utils import REPO_DEVCONTAINER, mount_targets, parse_jsonc
from tests.test_post_create_command import extract_function


HOST_LOCALTIME = "/etc/localtime.host"
LOCALTIME_MOUNT = (
    f"source=/etc/localtime,target={HOST_LOCALTIME},"
    "type=bind,consistency=cached,readonly"
)

# Contenus factices des fichiers de zoneinfo
PARIS = b"TZif-paris"
UTC = b"TZif-utc"


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


def test_host_localtime_is_mounted_beside_etc_localtime(devcontainer_dir):
    mounts = mount_targets(parse_jsonc(devcontainer_dir / "devcontainer.json"))

    assert mounts[HOST_LOCALTIME] == LOCALTIME_MOUNT
    assert "/etc/localtime" not in mounts


def test_tz_is_not_forwarded_from_host(devcontainer_dir):
    """TZ non défini sur l'hôte donnerait TZ="" : glibc l'interprète comme UTC."""
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")

    assert "TZ" not in config.get("containerEnv", {})
    assert "TZ" not in config.get("remoteEnv", {})


def test_post_create_sets_timezone_after_system_update(devcontainer_dir):
    calls = (devcontainer_dir / "postCreateCommand.sh").read_text().splitlines()

    assert "setup_timezone" in calls
    assert calls.index("setup_timezone") == calls.index("update_system") + 1


@pytest.fixture
def setup_timezone(devcontainer_dir: Path) -> str:
    """Code de setup_timezone, du dépôt PyFoundry ou du projet généré."""
    script = (devcontainer_dir / "postCreateCommand.sh").read_text()
    return extract_function(script, "setup_timezone")


@pytest.fixture
def system(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """Faux système : zoneinfo, /etc pointant sur Etc/UTC, sudo transparent."""
    zoneinfo = tmp_path / "zoneinfo"
    for name, content in [
        ("Etc/UTC", UTC),
        ("posix/Europe/Paris", PARIS),
        ("Europe/Paris", PARIS),
    ]:
        (zoneinfo / name).parent.mkdir(parents=True, exist_ok=True)
        (zoneinfo / name).write_bytes(content)

    etc = tmp_path / "etc"
    etc.mkdir()
    (etc / "localtime").symlink_to(zoneinfo / "Etc/UTC")
    (etc / "timezone").write_text("Etc/UTC\n")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    sudo = bin_dir / "sudo"
    sudo.write_text('#!/usr/bin/env bash\nexec "$@"\n')
    sudo.chmod(sudo.stat().st_mode | stat.S_IEXEC)

    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "HOST_LOCALTIME": str(tmp_path / "localtime.host"),
        "ZONEINFO_DIR": str(zoneinfo),
        "ETC_DIR": str(etc),
    }
    return tmp_path, env


def run_setup_timezone(
    code: str, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", f"set -e\n{code}\nsetup_timezone"],
        check=False,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_known_host_zone_is_linked_by_name(setup_timezone, system):
    """Le fuseau de l'hôte est retrouvé par son nom, hors posix/."""
    root, env = system
    (root / "localtime.host").write_bytes(PARIS)

    result = run_setup_timezone(setup_timezone, env)

    assert result.returncode == 0, result.stderr
    assert os.readlink(root / "etc/localtime") == str(root / "zoneinfo/Europe/Paris")
    assert (root / "etc/timezone").read_text().strip() == "Europe/Paris"
    # Etc/UTC reste UTC
    assert (root / "zoneinfo/Etc/UTC").read_bytes() == UTC


def test_unknown_host_zone_links_to_host_file(setup_timezone, system):
    """Sans zone identique dans zoneinfo, /etc/localtime pointe vers l'hôte."""
    root, env = system
    (root / "localtime.host").write_bytes(b"TZif-inconnu")

    result = run_setup_timezone(setup_timezone, env)

    assert result.returncode == 0, result.stderr
    assert os.readlink(root / "etc/localtime") == str(root / "localtime.host")


@pytest.mark.parametrize("host_file", ["absent", "vide"])
def test_missing_host_zone_keeps_utc(setup_timezone, system, host_file):
    """Sans fichier de l'hôte, le conteneur reste en UTC sans erreur."""
    root, env = system
    if host_file == "vide":
        (root / "localtime.host").write_bytes(b"")

    result = run_setup_timezone(setup_timezone, env)

    assert result.returncode == 0, result.stderr
    assert os.readlink(root / "etc/localtime") == str(root / "zoneinfo/Etc/UTC")
    assert (root / "etc/timezone").read_text().strip() == "Etc/UTC"
