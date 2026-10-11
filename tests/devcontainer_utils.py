"""Utilitaires de lecture des fichiers devcontainer.json (JSONC)."""

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).parent.parent
REPO_DEVCONTAINER = REPO_ROOT / ".devcontainer"
SKELETON_DEVCONTAINER = REPO_ROOT / "{{ cookiecutter.project_slug }}" / ".devcontainer"


def parse_jsonc(path: Path) -> dict[str, Any]:
    """Parse un devcontainer.json en retirant les commentaires.

    Même logique que check_mounts.sh : seuls les commentaires `//` en début de
    ligne sont retirés, pour ne pas casser les URLs (`http://`).
    """
    content = path.read_text()
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    content = re.sub(r"^[\t ]*//.*$", "", content, flags=re.MULTILINE)
    config: dict[str, Any] = json.loads(content)
    return config


def mount_targets(config: dict[str, Any]) -> dict[str, str]:
    """Indexe les montages par leur cible : {target: chaîne de montage complète}."""
    targets = {}
    for mount in config.get("mounts", []):
        parts = dict(part.split("=", 1) for part in mount.split(",") if "=" in part)
        targets[parts["target"]] = mount
    return targets


def nested_mountpoints(config: dict[str, Any]) -> dict[str, str]:
    """Points de montage à créer dans la source d'un autre montage.

    Pour chaque cible imbriquée dans la cible d'un autre montage (le plus
    profond), renvoie {cible: source du parent + chemin relatif}. Si ce dossier
    n'existe pas sur l'hôte, Docker le crée en root.
    """
    sources = {
        target: mount.split("source=", 1)[1].split(",", 1)[0]
        for target, mount in mount_targets(config).items()
    }
    mountpoints = {}
    for target in sources:
        parents = [p for p in sources if target.startswith(p.rstrip("/") + "/")]
        if parents:
            parent = max(parents, key=len)
            mountpoints[target] = sources[parent] + target[len(parent) :]
    return mountpoints
