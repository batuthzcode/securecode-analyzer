"""Tests for the declared minimum Python syntax compatibility."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


_REPOSITORY_ROOT = Path(__file__).parents[1]
_PYTHON_SOURCE_ROOTS = (
    _REPOSITORY_ROOT / "src",
    _REPOSITORY_ROOT / "sample_app",
    _REPOSITORY_ROOT / "tools",
    _REPOSITORY_ROOT / "tests",
)
_MINIMUM_PYTHON_VERSION = (3, 11)


def test_all_python_sources_use_python_3_11_syntax() -> None:
    """Every checked-in Python file should parse with Python 3.11."""

    for source_root in _PYTHON_SOURCE_ROOTS:
        for file_path in sorted(source_root.rglob("*.py")):
            source = file_path.read_text(encoding="utf-8")

            try:
                ast.parse(
                    source,
                    filename=str(file_path),
                    feature_version=_MINIMUM_PYTHON_VERSION,
                )
            except SyntaxError as error:
                relative_path = file_path.relative_to(
                    _REPOSITORY_ROOT
                )
                pytest.fail(
                    f"{relative_path} is not compatible with "
                    "Python 3.11 syntax: "
                    f"{error.msg} at line {error.lineno}."
                )
