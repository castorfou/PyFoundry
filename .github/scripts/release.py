"""Contrôles et notes de release de PyFoundry, appelés par release.yml.

La version a une seule source de vérité : `pyproject.toml`. `cookiecutter.json`
la recopie dans `_pyfoundry_version`, et `CHANGELOG.md` doit avoir sa section.

    python3 .github/scripts/release.py check-tag v1.2.0
    python3 .github/scripts/release.py notes v1.2.0 > release_notes.md
"""

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path


def pyproject_version(root: Path) -> str:
    return str(
        tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    )


def changelog_section(root: Path, version: str) -> str | None:
    """Corps de la section `## [version]` du CHANGELOG, sans son titre."""
    text = (root / "CHANGELOG.md").read_text()
    match = re.search(
        rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## |^\[[^\]]+\]: |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else None


def check_tag(root: Path, tag: str) -> list[str]:
    """Écarts entre le tag et la version des fichiers ; vide si tout concorde."""
    version = pyproject_version(root)
    errors = []
    if tag != f"v{version}":
        errors.append(
            f"le tag {tag} ne correspond pas à pyproject.toml (version {version})"
        )
    context = json.loads((root / "cookiecutter.json").read_text())
    if context.get("_pyfoundry_version") != version:
        errors.append(
            f"cookiecutter.json : _pyfoundry_version vaut "
            f"{context.get('_pyfoundry_version')}, attendu {version}"
        )
    if changelog_section(root, version) is None:
        errors.append(f"CHANGELOG.md : pas de section ## [{version}]")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser(
        "check-tag", help="vérifie qu'un tag correspond à la version"
    )
    check.add_argument("version", help="tag vX.Y.Z")
    notes = commands.add_parser(
        "notes", help="affiche la section du CHANGELOG d'une version"
    )
    notes.add_argument("version", help="tag vX.Y.Z ou version X.Y.Z")
    args = parser.parse_args()

    if args.command == "check-tag":
        errors = check_tag(args.root, args.version)
        for error in errors:
            print(f"[ERREUR] {error}", file=sys.stderr)
        return 1 if errors else 0

    section = changelog_section(args.root, args.version.removeprefix("v"))
    if section is None:
        print(
            f"[ERREUR] CHANGELOG.md : pas de section pour {args.version}",
            file=sys.stderr,
        )
        return 1
    print(section)
    return 0


if __name__ == "__main__":
    sys.exit(main())
