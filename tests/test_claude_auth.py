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
import shutil
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
    'DEVCONTAINER_LOCAL_FOLDER="${localWorkspaceFolder}" '
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


# Outils de l'hôte utilisés par le script. Le PATH des tests ne contient
# qu'eux : un vrai docker (runners GitHub) ne doit jamais être appelé.
HOST_TOOLS = [
    "bash", "env", "cat", "cp", "dirname", "find", "grep",
    "mkdir", "mktemp", "rm", "touch",
]  # fmt: skip


@pytest.fixture
def bin_dir(tmp_path: Path) -> Path:
    path = tmp_path / "bin"
    path.mkdir()
    for tool in HOST_TOOLS:
        found = shutil.which(tool)
        assert found, tool
        (path / tool).symlink_to(found)
    return path


def run_migration(
    host_home: Path, bin_dir: Path, **env: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(MIGRATION_SCRIPT)],
        env={
            **os.environ,
            "PATH": str(bin_dir),
            "HOME": str(host_home),
            "DEVCONTAINER_WORKSPACE_FOLDER_BASENAME": "proj",
            "DEVCONTAINER_ID": "id42",
            "DEVCONTAINER_LOCAL_FOLDER": "/host/git/proj",
            **env,
        },
        check=False,
        capture_output=True,
        text=True,
    )


def history_line(prompt: str) -> str:
    return json.dumps({"display": prompt, "project": "/workspaces/proj"}) + "\n"


def test_migration_copies_sessions_and_checkpoints(
    host_home, bin_dir, old_claude, shared
):
    write(old_claude / "projects" / "-workspaces-proj" / "s1.jsonl", "session\n")
    write(old_claude / "projects" / "-workspaces-proj" / "memory" / "MEMORY.md", "m\n")
    write(old_claude / "file-history" / "s1" / "abc@v1", "checkpoint\n")

    result = run_migration(host_home, bin_dir)

    assert result.returncode == 0, result.stdout + result.stderr
    project = shared / "projects" / "-workspaces-proj"
    assert (project / "s1.jsonl").read_text() == "session\n"
    assert (project / "memory" / "MEMORY.md").read_text() == "m\n"
    assert (shared / "file-history" / "s1" / "abc@v1").read_text() == "checkpoint\n"


def test_migration_never_overwrites_shared_files(
    host_home, bin_dir, old_claude, shared
):
    write(old_claude / "projects" / "-workspaces-proj" / "s1.jsonl", "old\n")
    write(shared / "projects" / "-workspaces-proj" / "s1.jsonl", "shared\n")

    result = run_migration(host_home, bin_dir)

    assert result.returncode == 0
    assert (shared / "projects" / "-workspaces-proj" / "s1.jsonl").read_text() == (
        "shared\n"
    )


def test_migration_appends_prompt_history(host_home, bin_dir, old_claude, shared):
    write(old_claude / "history.jsonl", history_line("old prompt"))
    write(shared / "history.jsonl", history_line("shared prompt"))

    run_migration(host_home, bin_dir)

    assert (shared / "history.jsonl").read_text() == history_line(
        "shared prompt"
    ) + history_line("old prompt")


def test_migration_runs_once_per_project(host_home, bin_dir, old_claude, shared):
    write(old_claude / "history.jsonl", history_line("old prompt"))
    run_migration(host_home, bin_dir)
    write(old_claude / "projects" / "-workspaces-proj" / "late.jsonl", "late\n")

    result = run_migration(host_home, bin_dir)

    assert result.returncode == 0
    assert not (shared / "projects" / "-workspaces-proj" / "late.jsonl").exists()
    assert (shared / "history.jsonl").read_text() == history_line("old prompt")


def test_migration_leaves_login_alone(host_home, bin_dir, old_claude, shared):
    # Connexion non migrée : on se reconnecte une fois pour tous les projets
    write(old_claude / ".credentials.json", "{}")
    write(old_claude.parent / ".claude.json", "{}")

    run_migration(host_home, bin_dir)

    assert not (shared / ".credentials.json").exists()
    assert not (shared / ".claude.json").exists()


def test_migration_succeeds_without_old_history(host_home, bin_dir, shared):
    result = run_migration(host_home, bin_dir)

    assert result.returncode == 0
    assert not (shared / "projects").exists()


def test_migration_never_blocks_the_container(host_home, bin_dir, old_claude, shared):
    write(old_claude / "projects" / "-workspaces-proj" / "s1.jsonl", "session\n")
    shared.chmod(0o500)
    try:
        result = run_migration(host_home, bin_dir)
    finally:
        shared.chmod(0o700)

    assert result.returncode == 0
    # Échec : pas de marqueur, la migration sera retentée à la prochaine ouverture
    assert not any(old_claude.glob(".migrated*"))


# --- Génération 1 : HOME dans l'ancien conteneur (issue #82) ----------------------

# Faux docker : journalise ses appels. `ps` liste FAKE_DOCKER_CONTAINERS ;
# `inspect` montre /home/vscode pour les conteneurs de FAKE_DOCKER_MOUNTED ;
# `cp` copie depuis FAKE_DOCKER_ROOT/<id>/<chemin> ; chemin absent : message de
# docker « Could not find the file » ; chemin de FAKE_DOCKER_CP_FAIL : autre erreur.
FAKE_DOCKER = """#!/usr/bin/env bash
echo "$*" >> "$FAKE_DOCKER_LOG"
case "$1" in
    ps)
        for id in $FAKE_DOCKER_CONTAINERS; do echo "$id"; done ;;
    inspect)
        id="${@: -1}"
        if [[ " $FAKE_DOCKER_MOUNTED " == *" $id "* ]]; then
            target=/home/vscode
        else
            target=/home/vscode/.cache/uv
        fi
        printf '[\\n    {\\n        "Mounts": [\\n            {\\n'
        printf '                "Destination": "%s",\\n' "$target"
        printf '                "Mode": ""\\n            }\\n        ]\\n    }\\n]\\n' ;;
    cp)
        id="${2%%:*}" path="${2#*:}"
        if [[ " $FAKE_DOCKER_CP_FAIL " == *" $path "* ]]; then
            echo "Error response from daemon: permission denied" >&2
            exit 1
        fi
        if [[ ! -e "$FAKE_DOCKER_ROOT/$id$path" ]]; then
            echo "Error response from daemon: Could not find the file $path in container $id" >&2
            exit 1
        fi
        cp -a "$FAKE_DOCKER_ROOT/$id$path" "$3" ;;
esac
exit 0
"""


@pytest.fixture
def docker(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    """Faux docker dans le PATH ; renvoie l'environnement à passer au script."""
    script = bin_dir / "docker"
    script.write_text(FAKE_DOCKER)
    script.chmod(0o755)
    return {
        "FAKE_DOCKER_LOG": str(tmp_path / "docker.log"),
        "FAKE_DOCKER_ROOT": str(tmp_path / "containers"),
        "FAKE_DOCKER_CONTAINERS": "",
        "FAKE_DOCKER_MOUNTED": "",
        "FAKE_DOCKER_CP_FAIL": "",
    }


@pytest.fixture
def persistent_home(host_home: Path) -> Path:
    return host_home / ".devcontainer" / "homes" / "proj-id42"


def container_home(docker: dict[str, str], container_id: str) -> Path:
    """HOME /home/vscode d'un faux conteneur."""
    return Path(docker["FAKE_DOCKER_ROOT"]) / container_id / "home" / "vscode"


def docker_calls(docker: dict[str, str]) -> list[str]:
    log = Path(docker["FAKE_DOCKER_LOG"])
    return log.read_text().splitlines() if log.exists() else []


def gen1_container(docker: dict[str, str], container_id: str = "c1") -> Path:
    """Conteneur de génération 1 avec un historique Claude et zsh."""
    home = container_home(docker, container_id)
    write(home / ".claude" / "projects" / "-workspaces-proj" / "s1.jsonl", "session\n")
    write(home / ".claude" / "file-history" / "s1" / "abc@v1", "checkpoint\n")
    write(home / ".claude" / "history.jsonl", history_line("container prompt"))
    write(home / ".zsh_history", ": 1:0;ls\n")
    docker["FAKE_DOCKER_CONTAINERS"] += f" {container_id}"
    return home


def test_gen1_migration_recovers_claude_and_shell_history(
    host_home, bin_dir, docker, shared, persistent_home
):
    gen1_container(docker)
    write(shared / "history.jsonl", history_line("shared prompt"))

    result = run_migration(host_home, bin_dir, **docker)

    assert result.returncode == 0, result.stdout + result.stderr
    project = shared / "projects" / "-workspaces-proj"
    assert (project / "s1.jsonl").read_text() == "session\n"
    assert (shared / "file-history" / "s1" / "abc@v1").read_text() == "checkpoint\n"
    assert (shared / "history.jsonl").read_text() == history_line(
        "shared prompt"
    ) + history_line("container prompt")
    assert (persistent_home / ".zsh_history").read_text() == ": 1:0;ls\n"
    assert (persistent_home / ".migrated-from-container").exists()
    assert "c1" in result.stdout


def test_gen1_migration_finds_container_by_project_folder(host_home, bin_dir, docker):
    run_migration(host_home, bin_dir, **docker)

    ps = [call for call in docker_calls(docker) if call.startswith("ps ")]
    assert ps == ["ps -aq --filter label=devcontainer.local_folder=/host/git/proj"]


def test_gen1_migration_never_overwrites(
    host_home, bin_dir, docker, shared, persistent_home
):
    home = gen1_container(docker)
    write(home / ".bash_history", "ls\n")
    write(shared / "projects" / "-workspaces-proj" / "s1.jsonl", "shared\n")
    write(persistent_home / ".zsh_history", ": 2:0;pwd\n")

    run_migration(host_home, bin_dir, **docker)

    project = shared / "projects" / "-workspaces-proj"
    assert (project / "s1.jsonl").read_text() == "shared\n"
    assert (persistent_home / ".zsh_history").read_text() == ": 2:0;pwd\n"
    assert (persistent_home / ".bash_history").read_text() == "ls\n"


def test_gen1_migration_leaves_logins_alone(
    host_home, bin_dir, docker, shared, persistent_home
):
    home = gen1_container(docker)
    write(home / ".claude" / ".credentials.json", "{}")
    write(home / ".claude.json", "{}")
    write(home / ".config" / "gh" / "hosts.yml", "github.com: {}\n")

    run_migration(host_home, bin_dir, **docker)

    assert not (shared / ".credentials.json").exists()
    assert not (shared / ".claude.json").exists()
    assert not (persistent_home / ".config" / "gh" / "hosts.yml").exists()
    assert not (host_home / ".config" / "gh-devcontainers").exists()
    copied = [
        call.split()[1] for call in docker_calls(docker) if call.startswith("cp ")
    ]
    assert copied and all(".config/gh" not in path for path in copied)
    assert "c1:/home/vscode" not in copied


def test_gen1_migration_skips_persistent_home_containers(
    host_home, bin_dir, docker, shared, persistent_home
):
    gen1_container(docker)
    docker["FAKE_DOCKER_MOUNTED"] = "c1"

    result = run_migration(host_home, bin_dir, **docker)

    assert result.returncode == 0
    assert not (shared / "projects").exists()
    assert not (persistent_home / ".zsh_history").exists()
    assert not (persistent_home / ".migrated-from-container").exists()


def test_gen1_migration_without_container_does_nothing(
    host_home, bin_dir, docker, shared, persistent_home
):
    result = run_migration(host_home, bin_dir, **docker)

    assert result.returncode == 0
    assert not (shared / "projects").exists()
    assert not (persistent_home / ".migrated-from-container").exists()


def test_gen1_migration_warns_on_several_old_containers(
    host_home, bin_dir, docker, shared, persistent_home
):
    gen1_container(docker, "c1")
    gen1_container(docker, "c2")

    result = run_migration(host_home, bin_dir, **docker)

    assert result.returncode == 0
    assert not (shared / "projects").exists()
    assert not (persistent_home / ".migrated-from-container").exists()
    assert "c1" in result.stdout
    assert "c2" in result.stdout
    assert "docker rm" in result.stdout
    assert not any(call.startswith("cp ") for call in docker_calls(docker))


def test_gen1_migration_ignores_new_containers_among_several(
    host_home, bin_dir, docker, shared
):
    gen1_container(docker, "old")
    gen1_container(docker, "new")
    docker["FAKE_DOCKER_MOUNTED"] = "new"
    write(
        container_home(docker, "new") / ".claude" / "projects" / "p" / "x.jsonl",
        "new\n",
    )

    run_migration(host_home, bin_dir, **docker)

    assert (shared / "projects" / "-workspaces-proj" / "s1.jsonl").exists()
    assert not (shared / "projects" / "p").exists()
    assert all(not call.startswith("cp new:") for call in docker_calls(docker))


def test_gen1_migration_runs_once(host_home, bin_dir, docker, persistent_home):
    gen1_container(docker)
    write(persistent_home / ".migrated-from-container", "")

    result = run_migration(host_home, bin_dir, **docker)

    assert result.returncode == 0
    assert docker_calls(docker) == []


def test_migration_without_docker_still_migrates_gen2(
    host_home, bin_dir, old_claude, shared
):
    write(old_claude / "projects" / "-workspaces-proj" / "s1.jsonl", "session\n")

    result = run_migration(host_home, bin_dir)

    assert result.returncode == 0, result.stdout + result.stderr
    assert (shared / "projects" / "-workspaces-proj" / "s1.jsonl").exists()


def test_gen1_migration_failure_never_blocks_the_container(
    host_home, bin_dir, docker, persistent_home
):
    gen1_container(docker)
    docker["FAKE_DOCKER_CP_FAIL"] = "/home/vscode/.claude/projects"

    result = run_migration(host_home, bin_dir, **docker)

    assert result.returncode == 0
    assert "⚠️" in result.stdout
    # Pas de marqueur : nouvel essai à la prochaine ouverture
    assert not (persistent_home / ".migrated-from-container").exists()
