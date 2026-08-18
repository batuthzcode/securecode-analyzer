"""Tests for dependency scanner data models."""

from dataclasses import FrozenInstanceError

import dependency_scanner
import pytest

from dependency_scanner import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    VulnerabilitySeverity,
)


def create_dependency() -> Dependency:
    """Create a valid dependency used by finding tests."""

    return Dependency(
        name="example-package",
        version="1.0.0",
        operator="==",
        source_file="requirements.txt",
        line_number=3,
    )


def create_source() -> AdvisorySource:
    """Create a valid advisory source used by finding tests."""

    return AdvisorySource(
        name="OSV",
        url="https://osv.dev/vulnerability/OSV-EXAMPLE",
    )


@pytest.mark.parametrize(
    ("severity", "expected_value"),
    [
        (
            VulnerabilitySeverity.UNKNOWN,
            "unknown",
        ),
        (
            VulnerabilitySeverity.LOW,
            "low",
        ),
        (
            VulnerabilitySeverity.MEDIUM,
            "medium",
        ),
        (
            VulnerabilitySeverity.HIGH,
            "high",
        ),
        (
            VulnerabilitySeverity.CRITICAL,
            "critical",
        ),
    ],
)
def test_vulnerability_severity_values(
    severity: VulnerabilitySeverity,
    expected_value: str,
) -> None:
    """Severity members expose lowercase string values."""

    assert severity.value == expected_value
    assert isinstance(severity, str)


def test_dependency_normalizes_text_fields() -> None:
    """Dependency strips surrounding whitespace."""

    dependency = Dependency(
        name="  Flask  ",
        version="  2.0.0  ",
        operator="  ==  ",
        source_file="  requirements.txt  ",
        line_number=1,
    )

    assert dependency.name == "Flask"
    assert dependency.version == "2.0.0"
    assert dependency.operator == "=="
    assert dependency.source_file == "requirements.txt"


def test_dependency_to_dict_returns_serializable_data() -> None:
    """Dependency can be converted to JSON-compatible data."""

    dependency = Dependency(
        name="Flask",
        version="2.0.0",
        operator="==",
        source_file="requirements.txt",
        line_number=1,
    )

    assert dependency.to_dict() == {
        "name": "Flask",
        "version": "2.0.0",
        "operator": "==",
        "source_file": "requirements.txt",
        "line_number": 1,
    }


def test_dependency_is_frozen() -> None:
    """Dependency instances cannot be modified."""

    dependency = create_dependency()

    with pytest.raises(FrozenInstanceError):
        dependency.version = "2.0.0"


def test_dependency_uses_slots() -> None:
    """Dependency instances do not expose a dynamic dictionary."""

    dependency = create_dependency()

    assert not hasattr(dependency, "__dict__")


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "\t",
    ],
)
def test_dependency_rejects_empty_name(
    name: str,
) -> None:
    """Dependency names must contain visible characters."""

    with pytest.raises(
        ValueError,
        match="name must not be empty",
    ):
        Dependency(
            name=name,
            version="1.0.0",
            operator="==",
            source_file="requirements.txt",
            line_number=1,
        )


def test_dependency_rejects_non_string_name() -> None:
    """Dependency text fields should fail with a controlled error."""

    with pytest.raises(ValueError, match="name must be a string"):
        Dependency(
            name=object(),  # type: ignore[arg-type]
            version="1.0.0",
            operator="==",
            source_file="requirements.txt",
            line_number=1,
        )


@pytest.mark.parametrize(
    "version",
    [
        "",
        " ",
    ],
)
def test_dependency_rejects_empty_version(
    version: str,
) -> None:
    """Dependency versions must not be empty."""

    with pytest.raises(
        ValueError,
        match="version must not be empty",
    ):
        Dependency(
            name="Flask",
            version=version,
            operator="==",
            source_file="requirements.txt",
            line_number=1,
        )


@pytest.mark.parametrize(
    "operator",
    [
        "",
        ">=",
        "~=",
    ],
)
def test_dependency_rejects_invalid_operator(
    operator: str,
) -> None:
    """Only exact version pins are supported."""

    with pytest.raises(ValueError):
        Dependency(
            name="Flask",
            version="2.0.0",
            operator=operator,
            source_file="requirements.txt",
            line_number=1,
        )


@pytest.mark.parametrize(
    "source_file",
    [
        "",
        " ",
    ],
)
def test_dependency_rejects_empty_source_file(
    source_file: str,
) -> None:
    """The source file path must not be empty."""

    with pytest.raises(
        ValueError,
        match="source_file must not be empty",
    ):
        Dependency(
            name="Flask",
            version="2.0.0",
            operator="==",
            source_file=source_file,
            line_number=1,
        )


@pytest.mark.parametrize(
    "line_number",
    [
        0,
        -1,
        True,
        1.5,
    ],
)
def test_dependency_rejects_invalid_line_number(
    line_number: object,
) -> None:
    """Dependency line numbers must be positive integers."""

    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        Dependency(
            name="Flask",
            version="2.0.0",
            operator="==",
            source_file="requirements.txt",
            line_number=line_number,  # type: ignore[arg-type]
        )


def test_advisory_source_normalizes_fields() -> None:
    """Advisory source text fields are stripped."""

    source = AdvisorySource(
        name="  OSV  ",
        url="  https://osv.dev/example  ",
    )

    assert source.name == "OSV"
    assert source.url == "https://osv.dev/example"


def test_advisory_source_accepts_missing_url() -> None:
    """An advisory source URL is optional."""

    source = AdvisorySource(
        name="OSV",
    )

    assert source.url is None


def test_advisory_source_to_dict_returns_serializable_data() -> None:
    """Advisory source can be converted to a dictionary."""

    source = AdvisorySource(
        name="OSV",
        url=None,
    )

    assert source.to_dict() == {
        "name": "OSV",
        "url": None,
    }


def test_advisory_source_rejects_empty_name() -> None:
    """Advisory source names must not be empty."""

    with pytest.raises(
        ValueError,
        match="name must not be empty",
    ):
        AdvisorySource(
            name=" ",
        )


def test_advisory_source_rejects_empty_url() -> None:
    """Present source URLs must not be empty."""

    with pytest.raises(
        ValueError,
        match="url must not be empty",
    ):
        AdvisorySource(
            name="OSV",
            url=" ",
        )


def test_dependency_finding_uses_optional_defaults() -> None:
    """Finding uses safe defaults for optional advisory data."""

    finding = DependencyFinding(
        dependency=create_dependency(),
        advisory_id="OSV-EXAMPLE",
        message="The installed version is affected.",
        source=create_source(),
    )

    assert (
        finding.severity
        is VulnerabilitySeverity.UNKNOWN
    )
    assert finding.fixed_version is None
    assert finding.aliases == ()


def test_dependency_finding_to_dict_returns_nested_data() -> None:
    """Finding returns complete JSON-compatible nested data."""

    finding = DependencyFinding(
        dependency=create_dependency(),
        advisory_id="  OSV-EXAMPLE  ",
        message="  The installed version is affected.  ",
        source=AdvisorySource(
            name="OSV",
            url=None,
        ),
        severity=VulnerabilitySeverity.HIGH,
        fixed_version="  1.0.1  ",
        aliases=(
            "  CVE-2099-0001  ",
            "GHSA-EXAMPLE",
        ),
    )

    assert finding.to_dict() == {
        "dependency": {
            "name": "example-package",
            "version": "1.0.0",
            "operator": "==",
            "source_file": "requirements.txt",
            "line_number": 3,
        },
        "advisory_id": "OSV-EXAMPLE",
        "message": "The installed version is affected.",
        "source": {
            "name": "OSV",
            "url": None,
        },
        "severity": "high",
        "fixed_version": "1.0.1",
        "aliases": [
            "CVE-2099-0001",
            "GHSA-EXAMPLE",
        ],
    }


def test_dependency_finding_is_frozen() -> None:
    """Dependency findings cannot be modified."""

    finding = DependencyFinding(
        dependency=create_dependency(),
        advisory_id="OSV-EXAMPLE",
        message="Affected dependency.",
        source=create_source(),
    )

    with pytest.raises(FrozenInstanceError):
        finding.message = "Changed"


def test_dependency_finding_rejects_empty_advisory_id() -> None:
    """Finding advisory IDs must not be empty."""

    with pytest.raises(
        ValueError,
        match="advisory_id must not be empty",
    ):
        DependencyFinding(
            dependency=create_dependency(),
            advisory_id=" ",
            message="Affected dependency.",
            source=create_source(),
        )


def test_dependency_finding_rejects_empty_message() -> None:
    """Finding messages must not be empty."""

    with pytest.raises(
        ValueError,
        match="message must not be empty",
    ):
        DependencyFinding(
            dependency=create_dependency(),
            advisory_id="OSV-EXAMPLE",
            message=" ",
            source=create_source(),
        )


def test_dependency_finding_rejects_empty_fixed_version() -> None:
    """A present fixed version must not be empty."""

    with pytest.raises(
        ValueError,
        match="fixed_version must not be empty",
    ):
        DependencyFinding(
            dependency=create_dependency(),
            advisory_id="OSV-EXAMPLE",
            message="Affected dependency.",
            source=create_source(),
            fixed_version=" ",
        )


@pytest.mark.parametrize(
    "aliases",
    [
        ("",),
        ("CVE-2099-0001", " "),
    ],
)
def test_dependency_finding_rejects_empty_alias(
    aliases: tuple[str, ...],
) -> None:
    """Advisory aliases must not contain empty values."""

    with pytest.raises(
        ValueError,
        match="alias must not be empty",
    ):
        DependencyFinding(
            dependency=create_dependency(),
            advisory_id="OSV-EXAMPLE",
            message="Affected dependency.",
            source=create_source(),
            aliases=aliases,
        )


def test_dependency_finding_rejects_non_tuple_aliases() -> None:
    """Aliases should use the immutable tuple model contract."""

    with pytest.raises(ValueError, match="aliases must be a tuple"):
        DependencyFinding(
            dependency=create_dependency(),
            advisory_id="OSV-EXAMPLE",
            message="Affected dependency.",
            source=create_source(),
            aliases=["CVE-2099-0001"],  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        (
            "dependency",
            object(),
        ),
        (
            "source",
            object(),
        ),
        (
            "severity",
            "high",
        ),
    ],
)
def test_dependency_finding_rejects_invalid_nested_values(
    field_name: str,
    invalid_value: object,
) -> None:
    """Finding requires the expected nested model types."""

    arguments: dict[str, object] = {
        "dependency": create_dependency(),
        "advisory_id": "OSV-EXAMPLE",
        "message": "Affected dependency.",
        "source": create_source(),
        "severity": VulnerabilitySeverity.UNKNOWN,
    }
    arguments[field_name] = invalid_value

    with pytest.raises(ValueError):
        DependencyFinding(
            **arguments,  # type: ignore[arg-type]
        )


def test_package_exports_public_models() -> None:
    """Models are available through the package interface."""

    assert dependency_scanner.Dependency is Dependency
    assert (
        dependency_scanner.AdvisorySource
        is AdvisorySource
    )
    assert (
        dependency_scanner.DependencyFinding
        is DependencyFinding
    )
    assert (
        dependency_scanner.VulnerabilitySeverity
        is VulnerabilitySeverity
    )
