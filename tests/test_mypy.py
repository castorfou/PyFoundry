"""mypy : même environnement et même périmètre pour le hook, la CI et `mypy` (#112)."""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

from tests.devcontainer_utils import REPO_ROOT


SKELETON = REPO_ROOT / "{{ cookiecutter.project_slug }}"
PACKAGE = "mon_projet_data_science"
STUBS = ["pandas-stubs", "types-requests", "types-python-dateutil"]


@pytest.fixture(scope="module")
def generated(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Projet généré avec le contexte par défaut."""
    from cookiecutter.main import cookiecutter

    out = tmp_path_factory.mktemp("mypy")
    return Path(cookiecutter(str(REPO_ROOT), no_input=True, output_dir=str(out)))


def _roots(generated: Path) -> dict[str, Path]:
    return {"repo": REPO_ROOT, "generated": generated}


def _mypy_hook(root: Path) -> tuple[dict, dict]:
    """Dépôt et hook mypy du .pre-commit-config.yaml."""
    config = yaml.safe_load((root / ".pre-commit-config.yaml").read_text())
    found = [
        (repo, hook)
        for repo in config["repos"]
        for hook in repo["hooks"]
        if hook["id"] == "mypy"
    ]
    assert len(found) == 1, "Un seul hook mypy attendu"
    return found[0]


@pytest.mark.parametrize("source", ["repo", "generated"])
def test_mypy_hook_runs_in_project_venv(generated, source):
    """Le hook mypy tourne dans le venv du projet, sans dépendances à recopier."""
    repo, hook = _mypy_hook(_roots(generated)[source])

    assert repo["repo"] == "local"
    assert hook["entry"] == "uv run --active mypy"
    assert hook["language"] == "system"
    assert hook["types"] == ["python"]
    assert hook["pass_filenames"] is False
    assert "additional_dependencies" not in hook
    assert "files" not in hook
    assert "args" not in hook


def test_mypy_hook_identical_in_repo_and_skeleton(generated):
    """Le hook mypy est le même dans le dépôt et le projet généré (R1.5)."""
    assert _mypy_hook(REPO_ROOT) == _mypy_hook(generated)


def test_generated_mypy_checks_src_and_tests(generated):
    """`mypy` seul vérifie le code et les tests du projet généré."""
    parsed = tomllib.loads((generated / "pyproject.toml").read_text())
    assert parsed["tool"]["mypy"]["files"] == ["src", "tests"]


def test_generated_dev_extra_has_stubs(generated):
    """Les stubs de l'ancien hook isolé sont dans les extras `dev` du projet."""
    parsed = tomllib.loads((generated / "pyproject.toml").read_text())
    dev = parsed["project"]["optional-dependencies"]["dev"]
    names = {re.split(r"[<>=\[ ]", dep, maxsplit=1)[0] for dep in dev}
    for stub in STUBS:
        assert stub in names, f"{stub} manque dans les extras dev"


def test_generated_project_has_package_and_test(generated):
    """Un projet neuf a du Python dans src/ et tests/ : mypy ne sort pas en erreur."""
    assert (generated / "src" / PACKAGE / "__init__.py").is_file()
    assert (generated / "tests" / f"test_{PACKAGE}.py").is_file()
    assert not (generated / "src" / ".gitkeep").exists()


def _run_mypy(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mypy"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def test_mypy_passes_on_generated_project(generated):
    """`mypy` passe sur un projet neuf, avec la config de son pyproject.toml."""
    result = _run_mypy(generated)
    assert result.returncode == 0, result.stdout + result.stderr


def test_mypy_passes_on_repo():
    """`mypy` passe à la racine du dépôt, que le hook vérifie désormais."""
    result = _run_mypy(REPO_ROOT)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "workflow",
    [
        SKELETON / ".github" / "workflows" / "ci.yml",
        REPO_ROOT / ".github" / "workflows" / "test-template.yml",
    ],
    ids=["ci.yml", "test-template.yml"],
)
def test_ci_runs_mypy_without_path(workflow):
    """La CI lance `mypy` sans chemin : le périmètre vient de pyproject.toml."""
    lines = [
        line.strip()
        for line in workflow.read_text().splitlines()
        if re.search(r"uv run mypy\b", line)
    ]
    assert lines, "Aucune commande mypy dans le workflow"
    for line in lines:
        assert not re.search(r"uv run mypy[^|]*\bsrc/?\b", line), line
