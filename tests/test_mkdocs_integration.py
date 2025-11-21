"""Tests pour l'intégration de MkDocs dans le projet généré."""

import subprocess

import pytest


def test_mkdocs_yml_created(cookies, minimal_template_context):
    """Test que le fichier mkdocs.yml est créé."""
    result = cookies.bake(extra_context=minimal_template_context)

    mkdocs_yml = result.project_path / "mkdocs.yml"
    assert mkdocs_yml.exists(), "mkdocs.yml should be created"


def test_mkdocs_yml_has_material_theme(cookies, minimal_template_context):
    """Test que mkdocs.yml utilise le thème Material."""
    result = cookies.bake(extra_context=minimal_template_context)

    mkdocs_yml = result.project_path / "mkdocs.yml"
    content = mkdocs_yml.read_text()

    assert "theme:" in content
    assert "name: material" in content


def test_mkdocs_dependencies_in_pyproject(cookies, minimal_template_context):
    """Test que MkDocs est dans les dépendances optionnelles."""
    result = cookies.bake(extra_context=minimal_template_context)

    pyproject = result.project_path / "pyproject.toml"
    content = pyproject.read_text()

    # Vérifier la présence d'un groupe de dépendances docs
    assert "docs" in content
    assert "mkdocs" in content.lower()
    assert "mkdocs-material" in content.lower()


def test_docs_structure_created(cookies, minimal_template_context):
    """Test que la structure docs/ user/dev est créée."""
    result = cookies.bake(extra_context=minimal_template_context)

    docs_dir = result.project_path / "docs"
    user_dir = result.project_path / "docs" / "user"
    dev_dir = result.project_path / "docs" / "dev"

    assert docs_dir.exists(), "docs/ directory should be created"
    assert user_dir.exists(), "docs/user/ directory should be created"
    assert dev_dir.exists(), "docs/dev/ directory should be created"


def test_docs_index_created(cookies, minimal_template_context):
    """Test que docs/index.md est créé."""
    result = cookies.bake(extra_context=minimal_template_context)

    index_md = result.project_path / "docs" / "index.md"
    assert index_md.exists(), "docs/index.md should be created"


def test_docs_user_readme_created(cookies, minimal_template_context):
    """Test que docs/user/README.md est créé avec des instructions."""
    result = cookies.bake(extra_context=minimal_template_context)

    user_readme = result.project_path / "docs" / "user" / "README.md"
    assert user_readme.exists(), "docs/user/README.md should be created"

    content = user_readme.read_text()
    assert len(content) > 0, "docs/user/README.md should not be empty"


def test_docs_dev_readme_created(cookies, minimal_template_context):
    """Test que docs/dev/README.md est créé avec des instructions."""
    result = cookies.bake(extra_context=minimal_template_context)

    dev_readme = result.project_path / "docs" / "dev" / "README.md"
    assert dev_readme.exists(), "docs/dev/README.md should be created"

    content = dev_readme.read_text()
    assert len(content) > 0, "docs/dev/README.md should not be empty"


def test_mkdocs_navigation_structure(cookies, minimal_template_context):
    """Test que mkdocs.yml a une navigation user/dev."""
    result = cookies.bake(extra_context=minimal_template_context)

    mkdocs_yml = result.project_path / "mkdocs.yml"
    content = mkdocs_yml.read_text()

    # Vérifier la présence de sections navigation
    assert "nav:" in content
    # La navigation devrait avoir une structure basique
    assert "user" in content.lower() or "dev" in content.lower()


def test_github_workflows_docs_created(cookies, minimal_template_context):
    """Test que .github/workflows/docs.yml est créé."""
    result = cookies.bake(extra_context=minimal_template_context)

    docs_workflow = result.project_path / ".github" / "workflows" / "docs.yml"
    assert docs_workflow.exists(), "docs.yml workflow should be created"


def test_docs_workflow_builds_mkdocs(cookies, minimal_template_context):
    """Test que la workflow docs.yml build MkDocs."""
    result = cookies.bake(extra_context=minimal_template_context)

    docs_workflow = result.project_path / ".github" / "workflows" / "docs.yml"
    content = docs_workflow.read_text()

    assert "mkdocs" in content.lower()
    assert "build" in content.lower()


def test_docs_workflow_deploys_to_pages(cookies, minimal_template_context):
    """Test que la workflow docs.yml déploie sur GitHub Pages."""
    result = cookies.bake(extra_context=minimal_template_context)

    docs_workflow = result.project_path / ".github" / "workflows" / "docs.yml"
    content = docs_workflow.read_text()

    assert "github-pages" in content.lower() or "pages" in content.lower()
    assert "deploy" in content.lower()


def test_claude_md_mentions_mkdocs(cookies, minimal_template_context):
    """Test que CLAUDE.md mentionne MkDocs et les commandes."""
    result = cookies.bake(extra_context=minimal_template_context)

    claude_md = result.project_path / "CLAUDE.md"
    content = claude_md.read_text()

    assert "mkdocs" in content.lower()
    assert "mkdocs serve" in content.lower() or "documentation" in content.lower()


def test_claude_md_has_documentation_guidelines(cookies, minimal_template_context):
    """Test que CLAUDE.md contient des bonnes pratiques de documentation."""
    result = cookies.bake(extra_context=minimal_template_context)

    claude_md = result.project_path / "CLAUDE.md"
    content = claude_md.read_text()

    # Vérifier la présence de guidelines
    assert "documentation" in content.lower()
    # Devrait mentionner la distinction user/dev
    assert "user" in content.lower() or "utilisateur" in content.lower()
    assert "dev" in content.lower() or "développeur" in content.lower()


def test_readme_mentions_documentation(cookies, minimal_template_context):
    """Test que README.md mentionne où trouver la documentation."""
    result = cookies.bake(extra_context=minimal_template_context)

    readme = result.project_path / "README.md"
    content = readme.read_text()

    assert "documentation" in content.lower() or "docs" in content.lower()


def test_mkdocs_can_build(cookies, minimal_template_context):
    """Test que mkdocs peut builder la documentation du projet généré."""
    result = cookies.bake(extra_context=minimal_template_context)

    # Essayer de builder avec mkdocs (si disponible)
    try:
        build_result = subprocess.run(
            ["mkdocs", "build", "--strict"],
            cwd=result.project_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Si mkdocs ou les plugins ne sont pas installés, on skip
        if "is not installed" in build_result.stderr:
            pytest.skip("mkdocs plugins not installed in test environment")

        # Si mkdocs est installé, le build doit réussir
        assert build_result.returncode == 0, f"mkdocs build failed: {build_result.stderr}"

        # Vérifier que le site est généré
        site_dir = result.project_path / "site"
        assert site_dir.exists(), "site/ directory should be created by mkdocs build"

    except FileNotFoundError:
        # mkdocs n'est pas installé dans l'environnement de test, on skip
        pytest.skip("mkdocs not installed in test environment")


def test_project_name_in_mkdocs_yml(cookies):
    """Test que le nom du projet est utilisé dans mkdocs.yml."""
    context = {
        "project_name": "My Awesome Project",
        "project_slug": "my-awesome-project",
        "description": "An awesome data science project",
        "python_version": "3.11",
        "github_username": "testuser",
        "use_node": "n"
    }

    result = cookies.bake(extra_context=context)

    mkdocs_yml = result.project_path / "mkdocs.yml"
    content = mkdocs_yml.read_text()

    # Le nom du projet devrait apparaître dans site_name
    assert "My Awesome Project" in content or "my-awesome-project" in content
