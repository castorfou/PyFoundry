"""Tests de la gestion des versions et du processus de release (issue #62).

La version a une seule source de vérité : `pyproject.toml`. Elle est recopiée
dans `cookiecutter.json` (`_pyfoundry_version`) pour que chaque projet généré
connaisse, dans son `.cruft.json`, la version du template dont il vient : cruft
relit les variables privées dans le nouveau template à chaque `cruft update`.
`.github/scripts/release.py` vérifie qu'un tag correspond à cette version et
extrait du CHANGELOG les notes de la release.

Depuis l'issue #90, `release.py plan` décide après chaque merge sur `main` s'il
faut publier : seule une hausse de version cohérente publie, et `release.yml`
crée le tag et la release en une seule commande. Le projet généré expose la
version du template dans `TEMPLATE_VERSION`.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.devcontainer_utils import REPO_ROOT


RELEASE_SCRIPT = REPO_ROOT / ".github" / "scripts" / "release.py"
RELEASE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"
TEST_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "test-template.yml"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
FIX_ISSUE = Path(".claude") / "commands" / "fix-issue.md"
SKELETON = REPO_ROOT / "{{ cookiecutter.project_slug }}"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def pyproject_version(root: Path = REPO_ROOT) -> str:
    return str(
        tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    )


def run_release(
    *args: str, root: Path = REPO_ROOT, github_output: Path | None = None
) -> subprocess.CompletedProcess:
    # En CI, GITHUB_OUTPUT pointe vers les sorties du vrai job : jamais hérité.
    env = {k: v for k, v in GIT_ENV.items() if k != "GITHUB_OUTPUT"}
    if github_output is not None:
        env["GITHUB_OUTPUT"] = str(github_output)
    return subprocess.run(
        [sys.executable, str(RELEASE_SCRIPT), "--root", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        env=GIT_ENV,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


@pytest.fixture
def release_root(tmp_path: Path) -> Path:
    """Copie des fichiers lus par release.py, modifiable par le test."""
    for name in ("pyproject.toml", "cookiecutter.json", "CHANGELOG.md"):
        shutil.copy(REPO_ROOT / name, tmp_path / name)
    return tmp_path


def test_pyproject_version_is_strict_semver():
    """Pas de suffixe -dev : la version est celle de la dernière release."""
    assert SEMVER.match(pyproject_version())


def test_cookiecutter_version_matches_pyproject():
    context = json.loads((REPO_ROOT / "cookiecutter.json").read_text())
    assert context["_pyfoundry_version"] == pyproject_version()


def test_generated_project_records_template_version(cookies, minimal_template_context):
    result = cookies.bake(extra_context=minimal_template_context)
    assert result.exit_code == 0
    assert result.context["_pyfoundry_version"] == pyproject_version()


def test_changelog_starts_with_unreleased_section():
    sections = re.findall(r"^## (.+)$", CHANGELOG.read_text(), re.MULTILINE)
    assert sections[0] == "[Non publié]"


def test_changelog_has_dated_section_for_current_version():
    version = re.escape(pyproject_version())
    pattern = rf"^## \[{version}\] - \d{{4}}-\d{{2}}-\d{{2}}$"
    assert re.search(pattern, CHANGELOG.read_text(), re.MULTILINE)


@pytest.mark.parametrize("version", ["1.0.0", "0.5.0", "0.4.0"])
def test_changelog_covers_history_since_v0_5_0(version):
    assert f"## [{version}]" in CHANGELOG.read_text()


def test_check_tag_accepts_current_version():
    result = run_release("check-tag", f"v{pyproject_version()}")
    assert result.returncode == 0, result.stderr


def test_check_tag_rejects_other_version():
    result = run_release("check-tag", "v99.0.0")
    assert result.returncode == 1
    assert "pyproject.toml" in result.stderr


def test_check_tag_rejects_tag_without_v_prefix():
    result = run_release("check-tag", pyproject_version())
    assert result.returncode == 1


def test_check_tag_rejects_cookiecutter_out_of_sync(release_root):
    path = release_root / "cookiecutter.json"
    context = json.loads(path.read_text())
    context["_pyfoundry_version"] = "0.0.1"
    path.write_text(json.dumps(context))

    result = run_release("check-tag", f"v{pyproject_version()}", root=release_root)

    assert result.returncode == 1
    assert "cookiecutter.json" in result.stderr


def test_check_tag_rejects_version_missing_from_changelog(release_root):
    changelog = release_root / "CHANGELOG.md"
    version = pyproject_version()
    changelog.write_text(changelog.read_text().replace(f"## [{version}]", "## [0.0.0]"))

    result = run_release("check-tag", f"v{version}", root=release_root)

    assert result.returncode == 1
    assert "CHANGELOG.md" in result.stderr


def test_notes_prints_changelog_section_body(release_root):
    (release_root / "CHANGELOG.md").write_text(
        "# Changelog\n\n"
        "## [Non publié]\n\n"
        "## [2.0.0] - 2026-01-02\n\n"
        "### Ajouté\n\n- Nouveauté\n\n"
        "## [1.0.0] - 2026-01-01\n\n- Ancien\n\n"
        "[2.0.0]: https://example.com\n"
    )

    result = run_release("notes", "2.0.0", root=release_root)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "### Ajouté\n\n- Nouveauté"


def test_notes_accepts_tag_with_v_prefix(release_root):
    result = run_release("notes", f"v{pyproject_version()}", root=release_root)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()


def test_notes_fails_for_unknown_version():
    result = run_release("notes", "99.0.0")
    assert result.returncode == 1


@pytest.fixture
def release_repo(release_root: Path) -> Path:
    """Dépôt git à la version courante, taguée comme sur le vrai dépôt."""
    git(release_root, "init", "-q")
    git(release_root, "add", "-A")
    git(release_root, "commit", "-q", "-m", "release")
    git(release_root, "tag", f"v{pyproject_version()}")
    return release_root


def bump(
    root: Path,
    version: str,
    notes: str | None = "### Ajouté\n\n- Nouveauté (#90).",
    cookiecutter: bool = True,
) -> None:
    """Prépare une PR de release ; `notes=None` omet la section du CHANGELOG."""
    current = pyproject_version(root)
    pyproject = root / "pyproject.toml"
    pyproject.write_text(
        re.sub(
            r'^version = ".*"$',
            f'version = "{version}"',
            pyproject.read_text(),
            count=1,
            flags=re.MULTILINE,
        )
    )
    if cookiecutter:
        path = root / "cookiecutter.json"
        context = json.loads(path.read_text())
        context["_pyfoundry_version"] = version
        path.write_text(json.dumps(context))
    if notes is not None:
        changelog = root / "CHANGELOG.md"
        changelog.write_text(
            changelog.read_text().replace(
                f"## [{current}]",
                f"## [{version}] - 2026-10-25\n\n{notes}\n\n## [{current}]",
                1,
            )
        )


# Versions de la PR de release simulée, relatives à la version courante :
# les tests passent aussi sur une branche de release déjà montée de version.
_MAJOR, _MINOR, _ = (int(part) for part in pyproject_version().split("."))
NEXT = f"{_MAJOR}.{_MINOR + 1}.0"
NEXT_MAJOR = f"{_MAJOR + 1}.0.0"


def run_plan(root: Path, tmp_path: Path) -> tuple[subprocess.CompletedProcess, str]:
    output = tmp_path / "github_output"
    output.write_text("")
    result = run_release("plan", "--base", "HEAD", root=root, github_output=output)
    return result, output.read_text()


def test_plan_skips_release_when_version_unchanged(release_repo, tmp_path):
    result, output = run_plan(release_repo, tmp_path)

    assert result.returncode == 0, result.stderr
    assert "release=false" in output.splitlines()
    assert "inchangée" in result.stdout


def test_plan_releases_on_version_bump(release_repo, tmp_path):
    bump(release_repo, NEXT)

    result, output = run_plan(release_repo, tmp_path)

    assert result.returncode == 0, result.stderr
    assert "release=true" in output.splitlines()
    assert f"version={NEXT}" in output.splitlines()


def test_plan_without_github_output_prints_decision(release_repo):
    bump(release_repo, NEXT)

    result = run_release("plan", "--base", "HEAD", root=release_repo)

    assert result.returncode == 0, result.stderr
    assert f"v{NEXT}" in result.stdout


def test_plan_rejects_version_decrease(release_repo, tmp_path):
    bump(release_repo, "0.0.0")

    result, output = run_plan(release_repo, tmp_path)

    assert result.returncode == 1
    assert "baisse" in result.stderr
    assert "release=true" not in output


def test_plan_rejects_existing_tag(release_repo, tmp_path):
    bump(release_repo, NEXT)
    git(release_repo, "tag", f"v{NEXT}")

    result, output = run_plan(release_repo, tmp_path)

    assert result.returncode == 1
    assert f"v{NEXT} existe déjà" in result.stderr
    assert "release=true" not in output


def test_plan_rejects_version_not_above_latest_tag(release_repo, tmp_path):
    git(release_repo, "tag", f"v{NEXT_MAJOR}")
    bump(release_repo, NEXT)

    result, _ = run_plan(release_repo, tmp_path)

    assert result.returncode == 1
    assert f"v{NEXT_MAJOR}" in result.stderr


def test_plan_rejects_cookiecutter_out_of_sync(release_repo, tmp_path):
    bump(release_repo, NEXT, cookiecutter=False)

    result, _ = run_plan(release_repo, tmp_path)

    assert result.returncode == 1
    assert "cookiecutter.json" in result.stderr


def test_plan_rejects_missing_changelog_section(release_repo, tmp_path):
    bump(release_repo, NEXT, notes=None)

    result, _ = run_plan(release_repo, tmp_path)

    assert result.returncode == 1
    assert "CHANGELOG.md" in result.stderr


def test_plan_rejects_empty_changelog_section(release_repo, tmp_path):
    bump(release_repo, NEXT, notes="")

    result, _ = run_plan(release_repo, tmp_path)

    assert result.returncode == 1
    assert "CHANGELOG.md" in result.stderr
    assert "vide" in result.stderr


def test_plan_reports_every_error(release_repo, tmp_path):
    bump(release_repo, NEXT, notes=None, cookiecutter=False)

    result, _ = run_plan(release_repo, tmp_path)

    assert result.stderr.count("[ERREUR]") == 2


def _workflow(path: Path = RELEASE_WORKFLOW) -> Any:
    return yaml.safe_load(path.read_text())


def _triggers(workflow: dict) -> Any:
    # PyYAML lit la clé `on` comme le booléen True.
    return workflow.get("on", workflow.get(True))


def _steps(job: dict) -> Any:
    return job.get("steps", [])


def _job_runs(job: dict) -> str:
    return "\n".join(step.get("run", "") for step in _steps(job))


def _workflow_steps() -> list[dict]:
    return [step for job in _workflow()["jobs"].values() for step in _steps(job)]


def _run_scripts() -> str:
    return "\n".join(step.get("run", "") for step in _workflow_steps())


def _fetches_full_history(job: dict) -> bool:
    return any(
        step.get("uses", "").startswith("actions/checkout")
        and step.get("with", {}).get("fetch-depth") == 0
        for step in _steps(job)
    )


def test_release_workflow_runs_on_push_to_main_only():
    """Plus de tag poussé à la main : le merge de la PR de release publie."""
    assert _triggers(_workflow()) == {"push": {"branches": ["main"]}}


def test_release_workflow_plans_against_previous_commit():
    plan = _workflow()["jobs"]["plan"]
    assert ".github/scripts/release.py plan --base" in _job_runs(plan)
    assert "github.event.before" in str(plan)
    assert _fetches_full_history(plan)


@pytest.mark.parametrize("job", ["run-tests", "publish"])
def test_release_workflow_publishes_only_on_planned_release(job):
    jobs = _workflow()["jobs"]
    assert "plan" in jobs[job]["needs"]
    assert "needs.plan.outputs.release == 'true'" in jobs[job]["if"]


def test_release_workflow_tests_before_publishing():
    jobs = _workflow()["jobs"]
    assert jobs["run-tests"]["uses"] == "./.github/workflows/test-template.yml"
    assert "run-tests" in jobs["publish"]["needs"]


def test_release_workflow_creates_tag_and_release_in_one_command():
    """Ni publication partielle (tag sans release), ni second workflow attendu."""
    runs = _job_runs(_workflow()["jobs"]["publish"])
    assert 'gh release create "v$VERSION"' in runs
    assert '--target "$GITHUB_SHA"' in runs
    assert "git tag" not in runs
    assert "git push" not in runs


def test_release_workflow_has_minimal_permissions():
    workflow = _workflow()
    assert workflow["permissions"] == {"contents": "read"}
    write_jobs = {
        name: job["permissions"]
        for name, job in workflow["jobs"].items()
        if "permissions" in job
    }
    assert write_jobs == {"publish": {"contents": "write"}}


def test_release_workflow_never_runs_twice_at_once():
    concurrency = _workflow()["concurrency"]
    assert concurrency["group"]
    assert concurrency["cancel-in-progress"] is False


def test_release_workflow_takes_notes_from_changelog():
    scripts = _run_scripts()
    assert ".github/scripts/release.py notes" in scripts
    assert "git log" not in scripts


def test_pull_request_ci_runs_release_plan():
    """Une PR de release incohérente échoue avant le merge."""
    jobs = _workflow(TEST_WORKFLOW)["jobs"]
    planned = [
        job
        for job in jobs.values()
        if ".github/scripts/release.py plan --base" in _job_runs(job)
    ]
    assert len(planned) == 1
    job = planned[0]
    assert "github.base_ref" in str(job)
    assert "github.event_name == 'pull_request'" in job["if"]
    assert _fetches_full_history(job)


def test_generated_project_has_template_version_file(cookies, minimal_template_context):
    result = cookies.bake(extra_context=minimal_template_context)

    assert result.exit_code == 0
    path = Path(result.project_path) / "TEMPLATE_VERSION"
    assert path.read_text() == f"{pyproject_version()}\n"


def cruft(*args: str, cwd: Path) -> None:
    subprocess.run(
        [sys.executable, "-m", "cruft", *args],
        cwd=cwd,
        env=GIT_ENV,
        check=True,
        capture_output=True,
        text=True,
    )


def test_template_version_follows_cruft_update(tmp_path):
    """cruft relit `_pyfoundry_version` dans le nouveau template, pas dans .cruft.json."""
    template = tmp_path / "template"
    skeleton = template / "{{ cookiecutter.project_slug }}"
    skeleton.mkdir(parents=True)
    shutil.copy(SKELETON / "TEMPLATE_VERSION", skeleton / "TEMPLATE_VERSION")
    context = {"project_slug": "demo", "_pyfoundry_version": "1.0.0"}
    (template / "cookiecutter.json").write_text(json.dumps(context))
    git(template, "init", "-q")
    git(template, "add", "-A")
    git(template, "commit", "-q", "-m", "1.0.0")

    cruft("create", str(template), "--no-input", cwd=tmp_path)
    project = tmp_path / "demo"
    git(project, "init", "-q")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "init")

    context["_pyfoundry_version"] = "1.1.0"
    (template / "cookiecutter.json").write_text(json.dumps(context))
    git(template, "commit", "-q", "-am", "1.1.0")
    cruft("update", "--skip-apply-ask", cwd=project)

    assert (project / "TEMPLATE_VERSION").read_text() == "1.1.0\n"


@pytest.mark.parametrize("root", [REPO_ROOT, SKELETON], ids=["depot", "projet-genere"])
def test_fix_issue_has_changelog_step(root):
    assert "CHANGELOG.md" in (root / FIX_ISSUE).read_text()


def test_fix_issue_is_identical_in_repo_and_skeleton():
    assert (REPO_ROOT / FIX_ISSUE).read_text() == (SKELETON / FIX_ISSUE).read_text()
