"""Tests de la config Claude Code partagée entre devcontainers (issue #73).

La connexion Claude Code (`.credentials.json`, compte dans `.claude.json`) vivait
dans le HOME persistant propre à chaque projet : il fallait se connecter une fois
par projet. Le dossier de config est désormais un dossier de l'hôte partagé par
tous les devcontainers, monté sur `~/.claude`, et `CLAUDE_CONFIG_DIR` y place
aussi `.claude.json`. On monte un dossier et pas des fichiers : Claude Code les
réécrit par renommage atomique, ce qui casse un bind mount de fichier.

Les verrous `~/.claude/ide/*.lock` (PID et port de l'IDE) restent propres au
projet. `migrate_claude_history.sh`, lancé sur l'hôte, recopie l'historique de
l'ancien HOME du projet, masqué dans le conteneur par le montage.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tests.devcontainer_utils import REPO_DEVCONTAINER, mount_targets, parse_jsonc


PERSISTENT_HOME = (
    "${localEnv:HOME}/.devcontainer/homes/"
    "${localWorkspaceFolderBasename}-${devcontainerId}"
)
CLAUDE_CONFIG_MOUNT = (
    "source=${localEnv:HOME}/.config/claude-devcontainers,"
    "target=/home/vscode/.claude,type=bind"
)
IDE_LOCKS_MOUNT = (
    f"source={PERSISTENT_HOME}/.claude-ide,target=/home/vscode/.claude/ide,type=bind"
)
MIGRATION_CALL = (
    'DEVCONTAINER_WORKSPACE_FOLDER_BASENAME="${localWorkspaceFolderBasename}" '
    'DEVCONTAINER_ID="${devcontainerId}" '
    'bash "${localWorkspaceFolder}/.devcontainer/scripts/migrate_claude_history.sh"'
)
MIGRATION_SCRIPT = REPO_DEVCONTAINER / "scripts" / "migrate_claude_history.sh"


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


def private_dirs(config: dict[str, Any]) -> list[str]:
    """Commandes `mkdir -p -m 700` de initializeCommand."""
    return [
        command.strip()
        for command in config["initializeCommand"].split("&&")
        if command.strip().startswith("mkdir -p -m 700 ")
    ]


def test_claude_config_is_shared_between_devcontainers(devcontainer_dir):
    mounts = mount_targets(parse_jsonc(devcontainer_dir / "devcontainer.json"))

    assert mounts["/home/vscode/.claude"] == CLAUDE_CONFIG_MOUNT


def test_claude_config_dir_points_to_shared_mount(devcontainer_dir):
    # Sans elle, .claude.json (le compte) resterait dans le HOME du projet
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")

    assert config["containerEnv"]["CLAUDE_CONFIG_DIR"] == "/home/vscode/.claude"


def test_ide_locks_are_isolated_per_project(devcontainer_dir):
    # Un verrou ne contient qu'un PID : invisible, donc « périmé », d'un autre conteneur
    mounts = mount_targets(parse_jsonc(devcontainer_dir / "devcontainer.json"))

    assert mounts["/home/vscode/.claude/ide"] == IDE_LOCKS_MOUNT


def test_initialize_command_creates_private_claude_dirs(devcontainer_dir):
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")
    commands = " ".join(private_dirs(config))

    # Tokens OAuth et tokens IDE ; ide/ est le point de montage imbriqué
    assert '"${localEnv:HOME}/.config/claude-devcontainers"' in commands
    assert '"${localEnv:HOME}/.config/claude-devcontainers/ide"' in commands
    assert f'"{PERSISTENT_HOME}/.claude-ide"' in commands


def test_initialize_command_creates_claude_mountpoint_in_persistent_home(
    devcontainer_dir,
):
    # Sinon Docker crée le point de montage .claude en root dans le HOME persistant
    config = parse_jsonc(devcontainer_dir / "devcontainer.json")

    assert f'"{PERSISTENT_HOME}/.claude"' in config["initializeCommand"]


def test_initialize_command_migrates_history_before_checking_mounts(
    devcontainer_dir,
):
    command = parse_jsonc(devcontainer_dir / "devcontainer.json")["initializeCommand"]

    assert MIGRATION_CALL in command
    assert command.index(MIGRATION_CALL) < command.index("check_mounts.sh")


def test_migration_script_is_identical_in_repo_and_project(devcontainer_dir):
    script = devcontainer_dir / "scripts" / "migrate_claude_history.sh"

    assert script.read_text() == MIGRATION_SCRIPT.read_text()


# --- migrate_claude_history.sh ----------------------------------------------------


@pytest.fixture
def host_home(tmp_path: Path) -> Path:
    """HOME de l'hôte, avec les dossiers créés par initializeCommand."""
    home = tmp_path / "host"
    (home / ".devcontainer" / "homes" / "proj-id42" / ".claude").mkdir(parents=True)
    (home / ".config" / "claude-devcontainers" / "ide").mkdir(parents=True)
    return home


@pytest.fixture
def old_claude(host_home: Path) -> Path:
    """Ancien ~/.claude du projet, dans son HOME persistant."""
    return host_home / ".devcontainer" / "homes" / "proj-id42" / ".claude"


@pytest.fixture
def shared(host_home: Path) -> Path:
    return host_home / ".config" / "claude-devcontainers"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def run_migration(host_home: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(MIGRATION_SCRIPT)],
        env={
            **os.environ,
            "HOME": str(host_home),
            "DEVCONTAINER_WORKSPACE_FOLDER_BASENAME": "proj",
            "DEVCONTAINER_ID": "id42",
        },
        check=False,
        capture_output=True,
        text=True,
    )


def history_line(prompt: str) -> str:
    return json.dumps({"display": prompt, "project": "/workspaces/proj"}) + "\n"


def test_migration_copies_sessions_and_checkpoints(host_home, old_claude, shared):
    write(old_claude / "projects" / "-workspaces-proj" / "s1.jsonl", "session\n")
    write(old_claude / "projects" / "-workspaces-proj" / "memory" / "MEMORY.md", "m\n")
    write(old_claude / "file-history" / "s1" / "abc@v1", "checkpoint\n")

    result = run_migration(host_home)

    assert result.returncode == 0, result.stdout + result.stderr
    project = shared / "projects" / "-workspaces-proj"
    assert (project / "s1.jsonl").read_text() == "session\n"
    assert (project / "memory" / "MEMORY.md").read_text() == "m\n"
    assert (shared / "file-history" / "s1" / "abc@v1").read_text() == "checkpoint\n"


def test_migration_never_overwrites_shared_files(host_home, old_claude, shared):
    write(old_claude / "projects" / "-workspaces-proj" / "s1.jsonl", "old\n")
    write(shared / "projects" / "-workspaces-proj" / "s1.jsonl", "shared\n")

    result = run_migration(host_home)

    assert result.returncode == 0
    assert (shared / "projects" / "-workspaces-proj" / "s1.jsonl").read_text() == (
        "shared\n"
    )


def test_migration_appends_prompt_history(host_home, old_claude, shared):
    write(old_claude / "history.jsonl", history_line("old prompt"))
    write(shared / "history.jsonl", history_line("shared prompt"))

    run_migration(host_home)

    assert (shared / "history.jsonl").read_text() == history_line(
        "shared prompt"
    ) + history_line("old prompt")


def test_migration_runs_once_per_project(host_home, old_claude, shared):
    write(old_claude / "history.jsonl", history_line("old prompt"))
    run_migration(host_home)
    write(old_claude / "projects" / "-workspaces-proj" / "late.jsonl", "late\n")

    result = run_migration(host_home)

    assert result.returncode == 0
    assert not (shared / "projects" / "-workspaces-proj" / "late.jsonl").exists()
    assert (shared / "history.jsonl").read_text() == history_line("old prompt")


def test_migration_leaves_login_alone(host_home, old_claude, shared):
    # Connexion non migrée : on se reconnecte une fois pour tous les projets
    write(old_claude / ".credentials.json", "{}")
    write(old_claude.parent / ".claude.json", "{}")

    run_migration(host_home)

    assert not (shared / ".credentials.json").exists()
    assert not (shared / ".claude.json").exists()


def test_migration_succeeds_without_old_history(host_home, shared):
    result = run_migration(host_home)

    assert result.returncode == 0
    assert not (shared / "projects").exists()


def test_migration_never_blocks_the_container(host_home, old_claude, shared):
    write(old_claude / "projects" / "-workspaces-proj" / "s1.jsonl", "session\n")
    shared.chmod(0o500)
    try:
        result = run_migration(host_home)
    finally:
        shared.chmod(0o700)

    assert result.returncode == 0
    # Échec : pas de marqueur, la migration sera retentée à la prochaine ouverture
    assert not any(old_claude.glob(".migrated*"))
