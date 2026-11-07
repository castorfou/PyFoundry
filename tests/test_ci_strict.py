"""La CI échoue quand ruff, mypy ou pre-commit échouent (#111).

Un `|| echo` après ces commandes masquait leurs échecs : option ruff retirée,
pre-commit hors d'un dépôt git, hook `no-venv-at-root` face au `.venv` de `uv sync`.
"""

import os
import re
import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.devcontainer_utils import REPO_ROOT


CHECKERS = re.compile(r"\b(ruff|mypy|pre-commit)\b")
SWALLOW = re.compile(r"\|\|\s*(echo|true|:)\b")


@pytest.fixture(scope="module")
def generated(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Projet généré avec le contexte par défaut."""
    from cookiecutter.main import cookiecutter

    out = tmp_path_factory.mktemp("ci_strict")
    return Path(cookiecutter(str(REPO_ROOT), no_input=True, output_dir=str(out)))


@pytest.fixture(params=["ci.yml", "test-template.yml"])
def workflow(request: pytest.FixtureRequest, generated: Path) -> dict[str, Any]:
    """Workflow rendu : CI du projet généré ou CI du template."""
    path = {
        "ci.yml": generated / ".github" / "workflows" / "ci.yml",
        "test-template.yml": REPO_ROOT / ".github" / "workflows" / "test-template.yml",
    }[request.param]
    loaded: dict[str, Any] = yaml.safe_load(path.read_text())
    return loaded


def _steps(workflow: dict[str, Any]) -> Iterator[tuple[dict[str, Any], dict[str, Any]]]:
    """(job, step) pour chaque étape `run:` du workflow."""
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            if "run" in step:
                yield job, step


def _validity_script() -> str:
    workflow = yaml.safe_load(
        (REPO_ROOT / ".github" / "workflows" / "test-template.yml").read_text()
    )
    script: str = next(
        step["run"]
        for step in workflow["jobs"]["test-template"]["steps"]
        if step.get("name", "").endswith("Test generated project validity")
    )
    return script


def test_checkers_failures_are_not_swallowed(workflow):
    """Aucune commande ruff, mypy ou pre-commit n'est suivie d'un `|| echo`."""
    for _, step in _steps(workflow):
        for line in step["run"].splitlines():
            if CHECKERS.search(line):
                assert not SWALLOW.search(line), line


def test_no_removed_ruff_option(workflow):
    """`--show-source` a été retiré de ruff : la commande échouerait."""
    for _, step in _steps(workflow):
        assert "--show-source" not in step["run"], step["run"]


def test_pre_commit_venv_outside_repo(workflow):
    """Le venv vit hors du dépôt, sinon le hook `no-venv-at-root` échoue."""
    found = False
    for job, step in _steps(workflow):
        if "pre-commit run" not in step["run"]:
            continue
        found = True
        env = {**job.get("env", {}), **step.get("env", {})}
        venv = env.get("UV_PROJECT_ENVIRONMENT", "")
        assert venv.startswith("/tmp/"), f"{step.get('name')}: {venv!r}"
    assert found, "Aucune étape pre-commit dans le workflow"


def test_validity_step_commits_before_pre_commit():
    """Le projet généré est un dépôt git avec un commit avant pre-commit."""
    script = _validity_script()
    pre_commit = script.index("pre-commit run")
    init = script.find("git init")
    add = script.find("git add -A")
    commit = re.search(r"git -c user\.name=\S+ -c user\.email=\S+ commit", script)
    assert 0 <= init < add < pre_commit, script
    assert commit and add < commit.start() < pre_commit, script


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv absent")
def test_validity_step_passes_on_generated_project(tmp_path):
    """L'étape de validité du projet généré passe, rejouée en local.

    `cruft create` est remplacé par cookiecutter, qui voit les fichiers non commités.
    """
    script = _validity_script()
    lines = script.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip().startswith("cd "))
    from cookiecutter.main import cookiecutter

    project = Path(
        cookiecutter(str(REPO_ROOT), no_input=True, output_dir=str(tmp_path))
    )
    env = {k: v for k, v in os.environ.items() if k not in {"VIRTUAL_ENV", "GIT_DIR"}}
    env["UV_PROJECT_ENVIRONMENT"] = str(tmp_path / "venv")
    result = subprocess.run(
        ["bash", "-e", "-c", "\n".join(lines[start + 1 :])],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode and "Could not resolve host" in result.stdout + result.stderr:
        pytest.skip("réseau indisponible pour installer les hooks")
    assert result.returncode == 0, result.stdout + result.stderr


def test_no_codecov_upload(workflow):
    """Pas d'upload Codecov : il échouait en silence, sans secret (#126)."""
    text = yaml.safe_dump(workflow)
    assert "codecov" not in text.lower(), "étape Codecov encore présente"
    assert "CODECOV_TOKEN" not in text


def test_no_silenced_step_errors(workflow):
    """Aucune étape ne masque son échec par `fail_ci_if_error: false` (#126)."""
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            assert step.get("with", {}).get("fail_ci_if_error") is not False, step


def test_generated_ci_coverage_in_log_only(generated):
    """La couverture reste dans le log pytest, sans `coverage.xml` inutilisé."""
    ci = yaml.safe_load((generated / ".github" / "workflows" / "ci.yml").read_text())
    run = next(
        step["run"]
        for step in ci["jobs"]["tests"]["steps"]
        if "pytest" in step.get("run", "")
    )
    assert "--cov=src" in run
    assert "--cov-report=term-missing" in run
    assert "--cov-report=xml" not in run


def _generated_ci(generated: Path) -> dict[str, Any]:
    loaded: dict[str, Any] = yaml.safe_load(
        (generated / ".github" / "workflows" / "ci.yml").read_text()
    )
    return loaded


def test_generated_ci_never_swallows_failures(generated):
    """Aucune étape de la CI générée ne masque un échec par `|| echo` (#125)."""
    for _, step in _steps(_generated_ci(generated)):
        for line in step["run"].splitlines():
            assert not SWALLOW.search(line), f"{step.get('name')}: {line}"


def test_generated_ci_has_no_verify_package_step(generated):
    """L'étape « Verify package » ne vérifiait rien : elle est retirée (#125)."""
    build = _generated_ci(generated)["jobs"]["build"]
    names = [step.get("name", "") for step in build["steps"]]
    assert not any("Verify package" in name for name in names), names
    assert all("pip show" not in step.get("run", "") for step in build["steps"])
    assert any(step.get("run") == "uv build" for step in build["steps"])


def test_generated_entry_points_resolve(generated):
    """Chaque console script du projet généré pointe vers un module de `src/`."""
    import tomllib

    pyproject = tomllib.loads((generated / "pyproject.toml").read_text())
    scripts = pyproject["project"].get("scripts", {})
    for name, target in scripts.items():
        module = target.split(":")[0].replace(".", "/")
        candidates = [
            generated / "src" / f"{module}.py",
            generated / "src" / module / "__init__.py",
        ]
        assert any(path.exists() for path in candidates), f"{name} = {target}"


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv absent")
def test_generated_wheel_imports(generated, tmp_path):
    """Le wheel construit s'installe dans un venv jetable et son package s'importe."""
    env = {k: v for k, v in os.environ.items() if k not in {"VIRTUAL_ENV"}}
    dist = tmp_path / "dist"
    build = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(dist)],
        cwd=generated,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    output = build.stdout + build.stderr
    if build.returncode and "Could not resolve host" in output:
        pytest.skip("réseau indisponible pour construire le wheel")
    assert build.returncode == 0, output
    wheel = next(dist.glob("*.whl"))

    package = generated.name.replace("-", "_")
    run = subprocess.run(
        [
            "uv",
            "run",
            "--isolated",
            "--no-project",
            "--with",
            str(wheel),
            "python",
            "-c",
            f"import {package}",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    output = run.stdout + run.stderr
    if run.returncode and "Could not resolve host" in output:
        pytest.skip("réseau indisponible pour installer le wheel")
    assert run.returncode == 0, output
