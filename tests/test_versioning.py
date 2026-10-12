"""Tests de la gestion des versions et du processus de release (issue #62).

La version a une seule source de vérité : `pyproject.toml`. Elle est recopiée
dans `cookiecutter.json` (`_pyfoundry_version`) pour que chaque projet généré
connaisse, dans son `.cruft.json`, la version du template dont il vient : cruft
relit les variables privées dans le nouveau template à chaque `cruft update`.
`.github/scripts/release.py` vérifie qu'un tag correspond à cette version et
extrait du CHANGELOG les notes de la release.
"""

import json
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

from tests.devcontainer_utils import REPO_ROOT


RELEASE_SCRIPT = REPO_ROOT / ".github" / "scripts" / "release.py"
RELEASE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
FIX_ISSUE = Path(".claude") / "commands" / "fix-issue.md"
SKELETON = REPO_ROOT / "{{ cookiecutter.project_slug }}"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def pyproject_version(root: Path = REPO_ROOT) -> str:
    return str(
        tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    )


def run_release(*args: str, root: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RELEASE_SCRIPT), "--root", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


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


def _workflow_steps() -> list[dict]:
    workflow = yaml.safe_load(RELEASE_WORKFLOW.read_text())
    return [step for job in workflow["jobs"].values() for step in job.get("steps", [])]


def _run_scripts() -> str:
    return "\n".join(step.get("run", "") for step in _workflow_steps())


def test_release_workflow_checks_tag_against_version():
    assert ".github/scripts/release.py check-tag" in _run_scripts()


def test_release_workflow_takes_notes_from_changelog():
    scripts = _run_scripts()
    assert ".github/scripts/release.py notes" in scripts
    assert "git log" not in scripts


@pytest.mark.parametrize("root", [REPO_ROOT, SKELETON], ids=["depot", "projet-genere"])
def test_fix_issue_has_changelog_step(root):
    assert "CHANGELOG.md" in (root / FIX_ISSUE).read_text()


def test_fix_issue_is_identical_in_repo_and_skeleton():
    assert (REPO_ROOT / FIX_ISSUE).read_text() == (SKELETON / FIX_ISSUE).read_text()
