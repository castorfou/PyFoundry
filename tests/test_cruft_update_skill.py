"""Tests de la skill /cruft-update (issue #89).

La skill guide la mise à jour du template dans un projet généré : `cruft update`,
CHANGELOG, résolution des rejets (`.rej` et marqueurs de conflit) selon le
propriétaire de chaque fichier (ADR 0003). Son script fournit les faits ; le
cycle complet, avec un vrai `cruft update`, reste un test manuel.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.devcontainer_utils import REPO_ROOT


SKILL = Path(".claude") / "skills" / "cruft-update"
SKILL_FILES = ["SKILL.md", "AUTO-MISE-A-JOUR.md", "scripts/template_update.py"]
SCRIPT = REPO_ROOT / SKILL / "scripts" / "template_update.py"

GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


@pytest.fixture(params=["repo", "generated"])
def project_root(
    request: pytest.FixtureRequest,
    cookies: Any,
    minimal_template_context: dict[str, str],
) -> Path:
    """Racine du dépôt PyFoundry ou d'un projet généré."""
    if request.param == "repo":
        return REPO_ROOT
    result = cookies.bake(extra_context=minimal_template_context)
    assert result.exit_code == 0
    return Path(result.project_path)


def frontmatter(skill_md: Path) -> dict[str, Any]:
    _, header, _ = skill_md.read_text().split("---\n", 2)
    data = yaml.safe_load(header)
    assert isinstance(data, dict)
    return data


# --- La skill ----------------------------------------------------------------------


@pytest.mark.parametrize("name", SKILL_FILES)
def test_skill_is_identical_in_repo_and_generated_project(project_root, name):
    """Aussi la preuve que cookiecutter ne rend pas `{{ cookiecutter.project_slug }}`."""
    assert (project_root / SKILL / name).read_text() == (
        REPO_ROOT / SKILL / name
    ).read_text()


def test_skill_is_model_invoked_on_template_update_and_rejects():
    meta = frontmatter(REPO_ROOT / SKILL / "SKILL.md")

    assert meta["name"] == "cruft-update"
    assert "disable-model-invocation" not in meta
    description = meta["description"].lower()
    assert "template" in description
    assert "rejet" in description


def test_skill_points_to_its_script_and_self_update_reference():
    skill = (REPO_ROOT / SKILL / "SKILL.md").read_text()

    for command in ("rejets", "categorie", "changelog"):
        assert f"template_update.py {command}" in skill
    assert "AUTO-MISE-A-JOUR.md" in skill
    assert "{{ cookiecutter.project_slug }}" in skill


# --- Le script ---------------------------------------------------------------------


def run_script(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        env=GIT_ENV,
        check=False,
        capture_output=True,
        text=True,
    )


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        env=GIT_ENV,
        check=check,
        capture_output=True,
        text=True,
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Dépôt git propre avec un commit initial."""
    root = tmp_path / "projet"
    root.mkdir()
    git(root, "init", "-q")
    write(root / "pyproject.toml", "[project]\nname = 'x'\n")
    write(root / ".devcontainer" / "x.sh", "base\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "init")
    return root


@pytest.mark.parametrize(
    ("path", "category"),
    [
        (".devcontainer/postCreateCommand.sh", "template"),
        (".github/workflows/ci.yml", "template"),
        (".claude/commands/fix-issue.md", "template"),
        (".claude/skills/cruft-update/SKILL.md", "template"),
        (".pre-commit-config.yaml", "template"),
        ("docs/cheatsheets/uv.md", "template"),
        ("TEMPLATE_VERSION", "template"),
        ("src/pkg/module.py", "projet"),
        ("tests/test_x.py", "projet"),
        ("notebooks/explo.ipynb", "projet"),
        ("README.md", "projet"),
        ("docs/user/README.md", "projet"),
        ("docs/claude/memory/note.md", "projet"),
        ("pyproject.toml", "mixte"),
        ("uv.lock", "mixte"),
        ("mkdocs.yml", "mixte"),
        ("CLAUDE.md", "mixte"),
        ("docs/agents/domain.md", "mixte"),
        (".claude/settings.json", "mixte"),
        ("CLAUDE.md.rej", "mixte"),
        (".devcontainer/devcontainer.json.rej", "template"),
        ("divers.txt", "inconnu"),
    ],
)
def test_categorie(path, category, tmp_path):
    result = run_script("categorie", path, cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == category


def test_rejets_on_clean_repo_is_empty(repo):
    result = run_script("rejets", cwd=repo)

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def test_rejets_lists_rej_files_with_category(repo):
    write(repo / "pyproject.toml.rej", "@@ -1 +1 @@\n")

    result = run_script("rejets", cwd=repo)

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["mixte\trej\tpyproject.toml.rej"]


def test_rejets_lists_three_way_conflicts(repo):
    """Conflit laissé par `git apply -3`, comme le fait cruft."""
    script = repo / ".devcontainer" / "x.sh"
    script.write_text("template\n")
    patch = git(repo, "diff").stdout
    git(repo, "checkout", "--", ".devcontainer/x.sh")
    script.write_text("local\n")
    git(repo, "commit", "-q", "-am", "personnalisation")
    applied = subprocess.run(
        ["git", "apply", "-3"],
        cwd=repo,
        env=GIT_ENV,
        input=patch,
        check=False,
        capture_output=True,
        text=True,
    )
    assert applied.returncode != 0
    assert "<<<<<<<" in script.read_text()

    result = run_script("rejets", cwd=repo)

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["template\tconflit\t.devcontainer/x.sh"]


@pytest.fixture
def template_repo(tmp_path: Path) -> tuple[Path, str, str]:
    """Faux dépôt du template : deux commits qui modifient le CHANGELOG."""
    root = tmp_path / "template"
    root.mkdir()
    git(root, "init", "-q")
    write(root / "CHANGELOG.md", "# Changelog\n\n## [Non publié]\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "v1")
    before = git(root, "rev-parse", "HEAD").stdout.strip()
    write(
        root / "CHANGELOG.md",
        "# Changelog\n\n## [Non publié]\n\n### Migration\n\n- Faire X (#2).\n",
    )
    git(root, "commit", "-q", "-am", "v2")
    after = git(root, "rev-parse", "HEAD").stdout.strip()
    return root, before, after


ADDED = ["", "### Migration", "", "- Faire X (#2)."]


def test_changelog_from_local_template(template_repo, tmp_path):
    root, before, after = template_repo

    result = run_script(
        "changelog", before, after, "--template-path", str(root), cwd=tmp_path
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ADDED


def test_changelog_clones_template_from_cruft_json(template_repo, repo):
    root, before, after = template_repo
    (repo / ".cruft.json").write_text(json.dumps({"template": root.as_uri()}))

    result = run_script("changelog", before, after, cwd=repo)

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ADDED
