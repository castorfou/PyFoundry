"""Contrôles et notes de release de PyFoundry, appelés par release.yml.

La version a une seule source de vérité : `pyproject.toml`. `cookiecutter.json`
la recopie dans `_pyfoundry_version`, et `CHANGELOG.md` doit avoir sa section.
Une release part quand un merge sur `main` augmente cette version.

    python3 .github/scripts/release.py plan --base <commit avant le merge>
    python3 .github/scripts/release.py check-tag v1.2.0
    python3 .github/scripts/release.py notes v1.2.0 > release_notes.md
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path


def parse_version(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def pyproject_version(root: Path) -> str:
    return version_from_pyproject((root / "pyproject.toml").read_text())


def version_from_pyproject(text: str) -> str:
    return str(tomllib.loads(text)["project"]["version"])


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout


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


def plan(root: Path, previous: str, tags: list[str]) -> tuple[bool, list[str]]:
    """Faut-il publier `pyproject.toml` par rapport à la version `previous` ?

    Renvoie (release, erreurs). Seule une hausse sans aucune erreur publie.
    """
    current = pyproject_version(root)
    if parse_version(current) == parse_version(previous):
        return False, []
    if parse_version(current) < parse_version(previous):
        return False, [f"baisse de version : {previous} → {current}"]

    tag = f"v{current}"
    errors = check_tag(root, tag)
    if changelog_section(root, current) == "":
        errors.append(f"CHANGELOG.md : la section ## [{current}] est vide")
    released = sorted(
        (parse_version(t.removeprefix("v")), t)
        for t in tags
        if re.fullmatch(r"v\d+\.\d+\.\d+", t)
    )
    if tag in tags:
        errors.append(f"le tag {tag} existe déjà : version déjà publiée")
    elif released and parse_version(current) <= released[-1][0]:
        errors.append(
            f"{current} n'est pas supérieure à la dernière release {released[-1][1]}"
        )
    return not errors, errors


def run_plan(root: Path, base: str) -> int:
    previous = version_from_pyproject(git(root, "show", f"{base}:pyproject.toml"))
    current = pyproject_version(root)
    tags = git(root, "tag", "--list", "v*").split()
    release, errors = plan(root, previous, tags)

    for error in errors:
        print(f"[ERREUR] {error}", file=sys.stderr)
    if release:
        print(f"Hausse de version {previous} → {current} : publication de v{current}")
    elif not errors:
        print(f"Version inchangée ({current}) : pas de release")

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a") as file:
            file.write(f"release={str(release).lower()}\nversion={current}\n")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    commands = parser.add_subparsers(dest="command", required=True)
    planner = commands.add_parser(
        "plan", help="décide si la version de pyproject.toml doit être publiée"
    )
    planner.add_argument(
        "--base", required=True, help="commit de référence (avant le merge)"
    )
    check = commands.add_parser(
        "check-tag", help="vérifie qu'un tag correspond à la version"
    )
    check.add_argument("version", help="tag vX.Y.Z")
    notes = commands.add_parser(
        "notes", help="affiche la section du CHANGELOG d'une version"
    )
    notes.add_argument("version", help="tag vX.Y.Z ou version X.Y.Z")
    args = parser.parse_args()

    if args.command == "plan":
        return run_plan(args.root, args.base)

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
