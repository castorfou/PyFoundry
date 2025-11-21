"""Tests de génération du template PyFoundry."""




def test_template_generates_successfully(cookies, default_template_context):
    """Test que le template se génère sans erreur."""
    result = cookies.bake(extra_context=default_template_context)
    
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.is_dir()


def test_project_structure_created(cookies, minimal_template_context):
    """Test que la structure de projet attendue est créée."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    project_path = result.project_path
    
    # Fichiers racine attendus
    expected_files = [
        "README.md",
        "pyproject.toml", 
        ".gitignore",
        ".pre-commit-config.yaml"
    ]
    
    for file_name in expected_files:
        assert (project_path / file_name).exists(), f"Missing file: {file_name}"
    
    # Dossiers attendus
    expected_dirs = [
        "src",
        "data",
        "data/raw", 
        "data/processed",
        "notebooks",
        ".devcontainer"
    ]
    
    for dir_name in expected_dirs:
        assert (project_path / dir_name).is_dir(), f"Missing directory: {dir_name}"


def test_devcontainer_files_created(cookies, minimal_template_context):
    """Test que les fichiers devcontainer sont créés."""
    result = cookies.bake(extra_context=minimal_template_context)
    
    devcontainer_path = result.project_path / ".devcontainer"
    
    assert (devcontainer_path / "devcontainer.json").exists()
    assert (devcontainer_path / "postCreateCommand.sh").exists()


def test_template_with_different_contexts(cookies):
    """Test génération avec différents contextes."""
    contexts = [
        {"project_name": "Simple Project", "python_version": "3.11"},
        {"project_name": "Complex-Project_123", "python_version": "3.12"},
        {"project_name": "Data Science Project", "use_node": "y"},
    ]
    
    for context in contexts:
        result = cookies.bake(extra_context=context)
        assert result.exit_code == 0
        assert result.project_path.is_dir()


def test_project_slug_generation(cookies):
    """Test que le project_slug est généré correctement."""
    test_cases = [
        ("Simple Project", "simple-project"),
        ("Data Science Project", "data-science-project"),
        ("Test_Project", "test-project"),
        ("My-Cool_Project 123", "my-cool-project-123"),
    ]
    
    for project_name, expected_slug in test_cases:
        result = cookies.bake(extra_context={"project_name": project_name})
        
        # Vérifier que le dossier utilise le bon slug
        assert result.project_path.name == expected_slug
        
        # Vérifier que pyproject.toml contient le bon nom
        pyproject_content = (result.project_path / "pyproject.toml").read_text()
        assert f'name = "{expected_slug}"' in pyproject_content


def test_github_username_integration(cookies):
    """Test que github_username est bien intégré dans la config."""
    context = {
        "github_username": "testuser123",
        "project_slug": "test-project"
    }
    
    result = cookies.bake(extra_context=context)
    
    # Vérifier que pyproject.toml contient les bonnes URLs
    pyproject_content = (result.project_path / "pyproject.toml").read_text()
    assert "github.com/testuser123/test-project" in pyproject_content


def test_node_disabled_by_default(cookies, default_template_context):
    """Test que Node.js n'est pas installé par défaut."""
    result = cookies.bake(extra_context=default_template_context)
    
    # Vérifier que Node.js n'est pas dans devcontainer.json
    devcontainer_content = (result.project_path / ".devcontainer" / "devcontainer.json").read_text()
    assert "ghcr.io/devcontainers/features/node" not in devcontainer_content
    
    # Vérifier que pas de setup_node dans postCreateCommand.sh
    postcreate_content = (result.project_path / ".devcontainer" / "postCreateCommand.sh").read_text()
    assert "setup_node" not in postcreate_content
    
    # Vérifier que pas d'extensions Node.js dans .gitignore
    gitignore_content = (result.project_path / ".gitignore").read_text()
    assert "node_modules/" not in gitignore_content


def test_node_enabled_when_requested(cookies, node_template_context):
    """Test que Node.js est correctement installé quand use_node=y."""
    result = cookies.bake(extra_context=node_template_context)
    
    # Vérifier que Node.js est dans devcontainer.json
    devcontainer_content = (result.project_path / ".devcontainer" / "devcontainer.json").read_text()
    assert "ghcr.io/devcontainers/features/node:1" in devcontainer_content
    assert '"nodeGypDependencies": true' in devcontainer_content
    assert '"version": "lts"' in devcontainer_content
    
    # Vérifier que setup_node est appelé dans postCreateCommand.sh
    postcreate_content = (result.project_path / ".devcontainer" / "postCreateCommand.sh").read_text()
    assert "setup_node" in postcreate_content
    assert "Configuration Node.js..." in postcreate_content
    
    # Vérifier que les exclusions Node.js sont dans .gitignore
    gitignore_content = (result.project_path / ".gitignore").read_text()
    assert "node_modules/" in gitignore_content
    assert "npm-debug.log*" in gitignore_content
    assert "package-lock.json" in gitignore_content


def test_timezone_configuration(cookies, default_template_context):
    """Test que la timezone du host est bien héritée par le devcontainer."""
    result = cookies.bake(extra_context=default_template_context)
    
    # Vérifier que devcontainer.json contient la configuration timezone
    devcontainer_content = (result.project_path / ".devcontainer" / "devcontainer.json").read_text()
    
    # Vérifier la présence de la variable d'environnement TZ
    assert '"TZ": "${localEnv:TZ}"' in devcontainer_content or "TZ" in devcontainer_content
    
    # Vérifier les montages pour les fichiers timezone
    assert "/etc/localtime" in devcontainer_content


def test_claude_md_file_created(cookies, minimal_template_context):
    """Test que le fichier CLAUDE.md est créé avec le template."""
    result = cookies.bake(extra_context=minimal_template_context)

    claude_md_path = result.project_path / "CLAUDE.md"
    assert claude_md_path.exists(), "CLAUDE.md file should be created"


def test_claude_md_content(cookies, default_template_context):
    """Test que le fichier CLAUDE.md contient les informations attendues."""
    context = {
        "project_name": "My Data Project",
        "project_slug": "my-data-project",
        "description": "A data science project",
        "python_version": "3.11",
        "github_username": "testuser",
        "use_node": "n"
    }

    result = cookies.bake(extra_context=context)

    claude_md_path = result.project_path / "CLAUDE.md"
    content = claude_md_path.read_text()

    # Vérifier que le nom du projet est présent
    assert "My Data Project" in content

    # Vérifier que la description est présente
    assert "A data science project" in content

    # Vérifier qu'il contient des sections importantes
    assert "# Project:" in content or "## Description" in content

    # Vérifier qu'il mentionne la stack technique
    assert "python" in content.lower() or "Python" in content

    # Vérifier qu'il contient des informations sur l'environnement
    assert "uv" in content or "pyproject.toml" in content or "dependencies" in content.lower()


def test_claude_directory_structure(cookies, minimal_template_context):
    """Test que la structure .claude/ est créée avec les commandes."""
    result = cookies.bake(extra_context=minimal_template_context)

    claude_dir = result.project_path / ".claude"
    commands_dir = result.project_path / ".claude" / "commands"

    # Vérifier que le répertoire .claude existe
    assert claude_dir.exists(), ".claude directory should be created"
    assert claude_dir.is_dir(), ".claude should be a directory"

    # Vérifier que le répertoire commands existe
    assert commands_dir.exists(), ".claude/commands directory should be created"
    assert commands_dir.is_dir(), ".claude/commands should be a directory"

    # Vérifier que les commandes pré-configurées existent
    fix_issue_cmd = commands_dir / "fix-issue.md"
    stocke_memoire_cmd = commands_dir / "stocke-memoire.md"

    assert fix_issue_cmd.exists(), "/fix-issue command should be created"
    assert stocke_memoire_cmd.exists(), "/stocke-memoire command should be created"


def test_claude_code_extension_in_devcontainer(cookies, minimal_template_context):
    """Test que l'extension Claude Code est configurée dans le devcontainer."""
    result = cookies.bake(extra_context=minimal_template_context)

    devcontainer_json = result.project_path / ".devcontainer" / "devcontainer.json"
    content = devcontainer_json.read_text()

    # Vérifier que l'extension Claude Code est présente
    assert "anthropic.claude-code" in content, "Claude Code extension should be in devcontainer.json"