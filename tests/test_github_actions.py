"""Versions des actions GitHub utilisées par les workflows (#120).

Node.js 20 est retiré des runners GitHub : chaque action externe doit être
épinglée sur une majeure qui tourne sous Node 24. Le squelette reprend les
versions des workflows du dépôt, que Dependabot tient à jour.
"""

import re
from pathlib import Path

import pytest
import yaml

from tests.devcontainer_utils import REPO_ROOT


# Première majeure de chaque action qui tourne sous Node 24 (notes de version).
# Avant d'ajouter une action, vérifier le `runs.using` de son action.yml.
MIN_MAJOR = {
    "actions/checkout": 5,
    "astral-sh/setup-uv": 7,
    "actions/configure-pages": 6,
    "actions/upload-pages-artifact": 5,  # composite, utilise upload-artifact v7
    "actions/deploy-pages": 5,
    "actions/upload-artifact": 6,  # v5 tournait encore sous Node 20 par défaut
}

# Actions qui ne publient plus de tag flottant (`@v10` n'existe pas).
EXACT_TAG_ONLY = {"astral-sh/setup-uv"}

USES_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)


def action_refs(workflows_dir: Path) -> list[tuple[str, str, str]]:
    """(fichier, action, référence) de chaque action externe des workflows."""
    refs = []
    for path in sorted(workflows_dir.glob("*.yml")):
        for uses in USES_RE.findall(path.read_text()):
            if uses.startswith("./"):
                continue  # workflow réutilisable local
            action, _, ref = uses.partition("@")
            refs.append((path.name, action, ref))
    return refs


@pytest.fixture(scope="module")
def generated_workflows(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from cookiecutter.main import cookiecutter

    out = tmp_path_factory.mktemp("generated")
    project = cookiecutter(
        str(REPO_ROOT),
        no_input=True,
        output_dir=str(out),
        extra_context={"project_slug": "test-project"},
    )
    return Path(project) / ".github" / "workflows"


@pytest.fixture(params=["depot", "projet-genere"])
def workflow_refs(
    request: pytest.FixtureRequest, generated_workflows: Path
) -> list[tuple[str, str, str]]:
    if request.param == "depot":
        return action_refs(REPO_ROOT / ".github" / "workflows")
    return action_refs(generated_workflows)


def major(ref: str) -> int:
    match = re.fullmatch(r"v(\d+)(\.\d+){0,2}", ref)
    assert match, f"référence {ref!r} : attendu vN, vN.M ou vN.M.P"
    return int(match.group(1))


def test_workflows_reference_actions(workflow_refs):
    assert workflow_refs, "aucune action trouvée : la collecte des `uses:` est cassée"


def test_every_action_has_a_known_minimum(workflow_refs):
    unknown = sorted({a for _, a, _ in workflow_refs if a not in MIN_MAJOR})
    assert not unknown, (
        f"actions sans version minimale : {unknown}. Vérifier leur version de "
        "Node (runs.using) puis les ajouter à MIN_MAJOR"
    )


def test_no_action_targets_node20(workflow_refs):
    too_old = [
        f"{f}: {a}@{r} (minimum v{MIN_MAJOR[a]})"
        for f, a, r in workflow_refs
        if a in MIN_MAJOR and major(r) < MIN_MAJOR[a]
    ]
    assert not too_old, "majeures sous Node 20 :\n" + "\n".join(too_old)


def test_exact_tag_for_actions_without_floating_tags(workflow_refs):
    floating = [
        f"{f}: {a}@{r}"
        for f, a, r in workflow_refs
        if a in EXACT_TAG_ONLY and not re.fullmatch(r"v\d+\.\d+\.\d+", r)
    ]
    assert not floating, "tag exact vX.Y.Z attendu :\n" + "\n".join(floating)


def test_generated_project_uses_repo_versions(generated_workflows):
    repo = {a: r for _, a, r in action_refs(REPO_ROOT / ".github" / "workflows")}
    diverging = [
        f"{f}: {a}@{r} (dépôt : @{repo[a]})"
        for f, a, r in action_refs(generated_workflows)
        if a in repo and r != repo[a]
    ]
    assert not diverging, (
        "le squelette doit reprendre les versions des workflows du dépôt "
        "(mises à jour par Dependabot) :\n" + "\n".join(diverging)
    )


def test_repo_versions_are_consistent():
    refs: dict[str, set[str]] = {}
    for _, a, r in action_refs(REPO_ROOT / ".github" / "workflows"):
        refs.setdefault(a, set()).add(r)
    mixed = {a: sorted(r) for a, r in refs.items() if len(r) > 1}
    assert not mixed, f"une même action sous plusieurs versions : {mixed}"


def test_dependabot_updates_repo_actions():
    config = yaml.safe_load((REPO_ROOT / ".github" / "dependabot.yml").read_text())
    assert config["version"] == 2
    entries = [
        u for u in config["updates"] if u["package-ecosystem"] == "github-actions"
    ]
    assert len(entries) == 1
    assert entries[0]["directory"] == "/"


def test_generated_project_has_no_dependabot(generated_workflows):
    # Une PR Dependabot dans un projet généré créerait des rejets au cruft update.
    github_dir = generated_workflows.parent
    assert not (github_dir / "dependabot.yml").exists()
    assert not (github_dir / "dependabot.yaml").exists()
