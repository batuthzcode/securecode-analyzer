"""Tests for Python package name normalization."""

import dependency_scanner
import pytest

from dependency_scanner import (
    Dependency,
    normalize_package_name,
)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        (
            "Flask",
            "flask",
        ),
        (
            "requests",
            "requests",
        ),
        (
            "sample-package",
            "sample-package",
        ),
        (
            "sample_package",
            "sample-package",
        ),
        (
            "sample.package",
            "sample-package",
        ),
        (
            "Sample_Package",
            "sample-package",
        ),
        (
            "sample---package",
            "sample-package",
        ),
        (
            "sample__package",
            "sample-package",
        ),
        (
            "sample..package",
            "sample-package",
        ),
        (
            "sample-_.package",
            "sample-package",
        ),
        (
            "package2",
            "package2",
        ),
        (
            "  Package2_Name  ",
            "package2-name",
        ),
    ],
)
def test_normalize_package_name(
    name: str,
    expected: str,
) -> None:
    """Supported package names are normalized."""

    assert normalize_package_name(name) == expected


def test_different_spellings_normalize_to_same_name() -> None:
    """Equivalent package names share one normalized value."""

    names = (
        "Sample-Package",
        "sample_package",
        "sample.package",
        "sample---package",
    )

    normalized_names = {
        normalize_package_name(name)
        for name in names
    }

    assert normalized_names == {
        "sample-package",
    }


@pytest.mark.parametrize(
    "name",
    [
        "flask",
        "sample-package",
        "package2",
        "package2-name",
    ],
)
def test_normalization_is_idempotent(
    name: str,
) -> None:
    """Normalizing an already normalized name changes nothing."""

    normalized_name = normalize_package_name(
        name
    )

    assert (
        normalize_package_name(normalized_name)
        == normalized_name
    )


def test_normalization_is_deterministic() -> None:
    """Repeated calls produce the same value."""

    first_result = normalize_package_name(
        "Sample_Package"
    )
    second_result = normalize_package_name(
        "Sample_Package"
    )

    assert first_result == second_result


def test_normalization_does_not_modify_dependency() -> None:
    """The original dependency model remains unchanged."""

    dependency = Dependency(
        name="Sample_Package",
        version="1.0.0",
        operator="==",
        source_file="requirements.txt",
        line_number=1,
    )

    normalized_name = normalize_package_name(
        dependency.name
    )

    assert dependency.name == "Sample_Package"
    assert normalized_name == "sample-package"


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "\t",
        "-",
        "_",
        ".",
        "-_.",
    ],
)
def test_normalize_package_name_rejects_empty_names(
    name: str,
) -> None:
    """Names without alphanumeric characters are rejected."""

    with pytest.raises(ValueError):
        normalize_package_name(name)


@pytest.mark.parametrize(
    "name",
    [
        None,
        1,
        1.5,
        True,
        object(),
    ],
)
def test_normalize_package_name_rejects_non_strings(
    name: object,
) -> None:
    """Package names must be strings."""

    with pytest.raises(
        ValueError,
        match="name must be a string",
    ):
        normalize_package_name(
            name,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "name",
    [
        "package name",
        "package/name",
        "package@name",
        "package#name",
        "package:name",
        "paketç",
    ],
)
def test_normalize_package_name_rejects_invalid_characters(
    name: str,
) -> None:
    """Unsupported package-name characters are rejected."""

    with pytest.raises(
        ValueError,
        match="unsupported characters",
    ):
        normalize_package_name(name)


def test_package_exports_normalization_function() -> None:
    """The normalizer is available through the package API."""

    assert (
        dependency_scanner.normalize_package_name
        is normalize_package_name
    )