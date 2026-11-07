"""Tests du package {{ cookiecutter.project_slug|replace('-', '_') }}."""

import {{ cookiecutter.project_slug|replace('-', '_') }} as package


def test_package_importable() -> None:
    """Le package s'importe depuis src/."""
    assert package.__name__ == "{{ cookiecutter.project_slug|replace('-', '_') }}"
