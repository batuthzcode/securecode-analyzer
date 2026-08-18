"""Tests for dependency scan orchestration."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import dependency_scanner
import pytest

from dependency_scanner import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    DependencyScanError,
    DependencyScanner,
    DependencyScanResult,
    OsvQueryError,
    RequirementsParseError,
    VulnerabilitySeverity,
    VulnerabilitySourceError,
)


def create_dependency(
    name: str = "sample-package",
    line_number: int = 1,
) -> Dependency:
    """Create a dependency used by scanner tests."""

    return Dependency(
        name=name,
        version="1.0.0",
        operator="==",
        source_file="requirements.txt",
        line_number=line_number,
    )


def create_finding(
    dependency: Dependency,
    advisory_id: str,
) -> DependencyFinding:
    """Create a finding associated with one dependency."""

    return DependencyFinding(
        dependency=dependency,
        advisory_id=advisory_id,
        message="The installed version is affected.",
        source=AdvisorySource(
            name="Fake",
            url=None,
        ),
        severity=VulnerabilitySeverity.HIGH,
    )


class FakeVulnerabilitySource:
    """Return configured findings or failures by package name."""

    def __init__(
        self,
        findings: dict[str, tuple[str, ...]] | None = None,
        failures: dict[str, Exception] | None = None,
    ) -> None:
        """Store deterministic source behavior."""

        self._findings = findings or {}
        self._failures = failures or {}
        self.received_dependencies: list[Dependency] = []

    @property
    def advisory_source(self) -> AdvisorySource:
        """Return fake advisory source information."""

        return AdvisorySource(
            name="Fake",
            url="https://example.test/",
        )

    def find_vulnerabilities(
        self,
        dependency: Dependency,
    ) -> tuple[DependencyFinding, ...]:
        """Record and process one dependency."""

        self.received_dependencies.append(dependency)

        failure = self._failures.get(dependency.name)

        if failure is not None:
            raise failure

        return tuple(
            create_finding(
                dependency,
                advisory_id,
            )
            for advisory_id in self._findings.get(
                dependency.name,
                (),
            )
        )


class InvalidSource:
    """Omit the vulnerability source protocol members."""


class InvalidFindingsSource(FakeVulnerabilitySource):
    """Return an invalid collection from the lookup method."""

    def find_vulnerabilities(
        self,
        dependency: Dependency,
    ) -> tuple[DependencyFinding, ...]:
        """Return a list disguised for protocol compatibility."""

        return []  # type: ignore[return-value]


def test_scanner_api_is_publicly_exported() -> None:
    """Orchestration values are available through package API."""

    assert (
        dependency_scanner.DependencyScanError
        is DependencyScanError
    )
    assert (
        dependency_scanner.DependencyScanner
        is DependencyScanner
    )
    assert (
        dependency_scanner.DependencyScanResult
        is DependencyScanResult
    )
    assert (
        dependency_scanner.VulnerabilitySourceError
        is VulnerabilitySourceError
    )


def test_osv_query_error_uses_common_source_error() -> None:
    """OSV lookup failures satisfy the shared error contract."""

    error = OsvQueryError("OSV is unavailable.")

    assert isinstance(error, VulnerabilitySourceError)
    assert isinstance(error, RuntimeError)


def test_scanner_exposes_configured_source() -> None:
    """The configured source is available as a read-only property."""

    source = FakeVulnerabilitySource()
    scanner = DependencyScanner(source)

    assert scanner.source is source


def test_scanner_rejects_invalid_source() -> None:
    """A source must satisfy the common source protocol."""

    with pytest.raises(
        ValueError,
        match="VulnerabilitySource",
    ):
        DependencyScanner(InvalidSource())  # type: ignore[arg-type]


def test_empty_dependencies_return_successful_result() -> None:
    """An empty dependency tuple produces an empty result."""

    source = FakeVulnerabilitySource()
    result = DependencyScanner(
        source
    ).scan_dependencies(())

    assert result == DependencyScanResult()
    assert result.succeeded
    assert source.received_dependencies == []


def test_single_dependency_finding_is_returned() -> None:
    """One dependency finding is preserved in the result."""

    dependency = create_dependency()
    source = FakeVulnerabilitySource(
        findings={
            dependency.name: ("OSV-EXAMPLE-1",),
        }
    )

    result = DependencyScanner(
        source
    ).scan_dependencies((dependency,))

    assert result.dependencies == (dependency,)
    assert tuple(
        finding.advisory_id
        for finding in result.findings
    ) == ("OSV-EXAMPLE-1",)
    assert result.errors == ()
    assert result.succeeded


def test_dependency_and_source_finding_order_is_preserved() -> None:
    """Findings retain dependency order and source order."""

    first = create_dependency("first", 1)
    second = create_dependency("second", 2)
    source = FakeVulnerabilitySource(
        findings={
            "first": (
                "OSV-FIRST-2",
                "OSV-FIRST-1",
            ),
            "second": ("OSV-SECOND-1",),
        }
    )

    result = DependencyScanner(
        source
    ).scan_dependencies((first, second))

    assert source.received_dependencies == [
        first,
        second,
    ]
    assert tuple(
        finding.advisory_id
        for finding in result.findings
    ) == (
        "OSV-FIRST-2",
        "OSV-FIRST-1",
        "OSV-SECOND-1",
    )


def test_dependency_without_findings_is_preserved() -> None:
    """A clean dependency remains part of the scan result."""

    dependency = create_dependency()
    result = DependencyScanner(
        FakeVulnerabilitySource()
    ).scan_dependencies((dependency,))

    assert result.dependencies == (dependency,)
    assert result.findings == ()
    assert result.errors == ()


def test_duplicate_dependencies_are_scanned_separately() -> None:
    """Duplicate dependency values trigger separate lookups."""

    dependency = create_dependency()
    source = FakeVulnerabilitySource()

    result = DependencyScanner(
        source
    ).scan_dependencies(
        (dependency, dependency)
    )

    assert result.dependencies == (
        dependency,
        dependency,
    )
    assert source.received_dependencies == [
        dependency,
        dependency,
    ]


def test_expected_source_error_is_recorded() -> None:
    """A source failure becomes a dependency scan error."""

    dependency = create_dependency()
    source = FakeVulnerabilitySource(
        failures={
            dependency.name: VulnerabilitySourceError(
                "Service unavailable."
            )
        }
    )

    result = DependencyScanner(
        source
    ).scan_dependencies((dependency,))

    assert result.findings == ()
    assert len(result.errors) == 1
    assert result.errors[0] == DependencyScanError(
        dependency=dependency,
        source=source.advisory_source,
        message="Service unavailable.",
    )
    assert not result.succeeded


def test_scan_continues_after_expected_source_error() -> None:
    """One failed dependency does not block the next dependency."""

    failing = create_dependency("failing", 1)
    successful = create_dependency("successful", 2)
    source = FakeVulnerabilitySource(
        findings={
            "successful": ("OSV-SUCCESS",),
        },
        failures={
            "failing": VulnerabilitySourceError(
                "Temporary failure."
            ),
        },
    )

    result = DependencyScanner(
        source
    ).scan_dependencies((failing, successful))

    assert source.received_dependencies == [
        failing,
        successful,
    ]
    assert tuple(
        finding.advisory_id
        for finding in result.findings
    ) == ("OSV-SUCCESS",)
    assert tuple(
        error.dependency
        for error in result.errors
    ) == (failing,)


def test_empty_source_error_uses_fallback_message() -> None:
    """An empty exception message receives readable fallback text."""

    dependency = create_dependency()
    source = FakeVulnerabilitySource(
        failures={
            dependency.name: VulnerabilitySourceError(),
        }
    )

    result = DependencyScanner(
        source
    ).scan_dependencies((dependency,))

    assert result.errors[0].message == (
        "Vulnerability source lookup failed."
    )


def test_unexpected_programming_error_is_propagated() -> None:
    """The scanner does not hide unexpected source defects."""

    dependency = create_dependency()
    error = TypeError("Unexpected source defect.")
    source = FakeVulnerabilitySource(
        failures={dependency.name: error}
    )

    with pytest.raises(TypeError) as raised:
        DependencyScanner(
            source
        ).scan_dependencies((dependency,))

    assert raised.value is error


@pytest.mark.parametrize(
    "dependencies",
    [
        [],
        (object(),),
    ],
)
def test_invalid_dependency_collection_is_rejected(
    dependencies: object,
) -> None:
    """Dependency scans require a typed tuple."""

    scanner = DependencyScanner(
        FakeVulnerabilitySource()
    )

    with pytest.raises(ValueError):
        scanner.scan_dependencies(
            dependencies  # type: ignore[arg-type]
        )


def test_invalid_source_findings_are_rejected() -> None:
    """A source contract violation is not silently accepted."""

    scanner = DependencyScanner(
        InvalidFindingsSource()
    )

    with pytest.raises(
        ValueError,
        match="source findings must be a tuple",
    ):
        scanner.scan_dependencies(
            (create_dependency(),)
        )


def test_requirements_file_is_parsed_and_scanned(
    tmp_path: Path,
) -> None:
    """One requirements file is scanned end to end."""

    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text(
        "first==1.0.0\nsecond==2.0.0\n",
        encoding="utf-8",
    )
    source = FakeVulnerabilitySource(
        findings={
            "first": ("OSV-FIRST",),
            "second": ("OSV-SECOND",),
        }
    )

    result = DependencyScanner(
        source
    ).scan_requirements(requirements_path)

    assert tuple(
        dependency.name
        for dependency in result.dependencies
    ) == ("first", "second")
    assert tuple(
        finding.advisory_id
        for finding in result.findings
    ) == ("OSV-FIRST", "OSV-SECOND")


def test_empty_requirements_file_returns_empty_result(
    tmp_path: Path,
) -> None:
    """An empty requirements file produces a successful result."""

    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text("", encoding="utf-8")
    source = FakeVulnerabilitySource()

    result = DependencyScanner(
        source
    ).scan_requirements(requirements_path)

    assert result == DependencyScanResult()
    assert source.received_dependencies == []


def test_requirements_parse_error_is_propagated(
    tmp_path: Path,
) -> None:
    """Invalid requirements stop before source lookups begin."""

    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text(
        "first==1.0.0\ninvalid>=2.0.0\n",
        encoding="utf-8",
    )
    source = FakeVulnerabilitySource()

    with pytest.raises(RequirementsParseError):
        DependencyScanner(
            source
        ).scan_requirements(requirements_path)

    assert source.received_dependencies == []


def test_missing_requirements_file_error_is_propagated(
    tmp_path: Path,
) -> None:
    """A missing requirements path retains its native error."""

    scanner = DependencyScanner(
        FakeVulnerabilitySource()
    )

    with pytest.raises(FileNotFoundError):
        scanner.scan_requirements(
            tmp_path / "missing.txt"
        )


def test_directory_requirements_error_is_propagated(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A directory path retains its native read error."""

    def raise_is_directory(
        self: Path,
        *,
        encoding: str,
    ) -> str:
        raise IsADirectoryError(str(self))

    monkeypatch.setattr(
        Path,
        "read_text",
        raise_is_directory,
    )

    scanner = DependencyScanner(
        FakeVulnerabilitySource()
    )

    with pytest.raises(IsADirectoryError):
        scanner.scan_requirements(tmp_path)


def test_non_utf8_requirements_error_is_propagated(
    tmp_path: Path,
) -> None:
    """Invalid UTF-8 retains its decoding error."""

    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_bytes(b"sample==1.0.0\n\xff")
    scanner = DependencyScanner(
        FakeVulnerabilitySource()
    )

    with pytest.raises(UnicodeDecodeError):
        scanner.scan_requirements(requirements_path)


def test_scan_result_is_frozen_and_uses_slots() -> None:
    """Scan result values cannot be changed or extended dynamically."""

    result = DependencyScanResult()

    with pytest.raises(FrozenInstanceError):
        result.findings = ()

    assert not hasattr(result, "__dict__")


def test_scan_error_normalizes_message_and_is_frozen() -> None:
    """Scan errors normalize text and remain immutable."""

    scan_error = DependencyScanError(
        dependency=create_dependency(),
        source=AdvisorySource(name="Fake"),
        message="  Service unavailable.  ",
    )

    assert scan_error.message == "Service unavailable."

    with pytest.raises(FrozenInstanceError):
        scan_error.message = "Changed"


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("dependencies", []),
        ("dependencies", (object(),)),
        ("findings", []),
        ("findings", (object(),)),
        ("errors", []),
        ("errors", (object(),)),
    ],
)
def test_scan_result_rejects_invalid_collections(
    field_name: str,
    invalid_value: object,
) -> None:
    """Result fields require tuples containing expected models."""

    arguments: dict[str, object] = {
        "dependencies": (),
        "findings": (),
        "errors": (),
    }
    arguments[field_name] = invalid_value

    with pytest.raises(ValueError):
        DependencyScanResult(
            **arguments  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("dependency", object()),
        ("source", object()),
        ("message", object()),
        ("message", " "),
    ],
)
def test_scan_error_rejects_invalid_values(
    field_name: str,
    invalid_value: object,
) -> None:
    """Scan error fields require valid model and text values."""

    arguments: dict[str, object] = {
        "dependency": create_dependency(),
        "source": AdvisorySource(name="Fake"),
        "message": "Service unavailable.",
    }
    arguments[field_name] = invalid_value

    with pytest.raises(ValueError):
        DependencyScanError(
            **arguments  # type: ignore[arg-type]
        )
