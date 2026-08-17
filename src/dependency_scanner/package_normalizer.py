"""Normalize Python package names for reliable comparison."""

from __future__ import annotations

import re


_SEPARATOR_PATTERN = re.compile(r"[-_.]+")
_VALID_NAME_PATTERN = re.compile(
    r"^[A-Za-z0-9._-]+$"
)
_ALPHANUMERIC_PATTERN = re.compile(
    r"[A-Za-z0-9]"
)


def normalize_package_name(name: str) -> str:
    """Return a normalized Python package name."""

    cleaned_name = _validate_package_name(name)

    normalized_name = _SEPARATOR_PATTERN.sub(
        "-",
        cleaned_name,
    ).lower()

    if (
        _ALPHANUMERIC_PATTERN.search(
            normalized_name
        )
        is None
    ):
        raise ValueError(
            "name must contain at least one "
            "alphanumeric character."
        )

    return normalized_name


def _validate_package_name(name: str) -> str:
    """Validate and clean a package name."""

    if not isinstance(name, str):
        raise ValueError(
            "name must be a string."
        )

    cleaned_name = name.strip()

    if not cleaned_name:
        raise ValueError(
            "name must not be empty."
        )

    if (
        _VALID_NAME_PATTERN.fullmatch(
            cleaned_name
        )
        is None
    ):
        raise ValueError(
            "name contains unsupported characters."
        )

    return cleaned_name