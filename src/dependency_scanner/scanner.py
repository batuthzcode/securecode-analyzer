"""Orchestrate dependency parsing and vulnerability lookups."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from dependency_scanner.models import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
)
from dependency_scanner.requirements_parser import (
    parse_requirements_file,
)
from dependency_scanner.vulnerability_source import (
    VulnerabilitySource,
    VulnerabilitySourceError,
)


_SOURCE_ERROR_FALLBACK = (
    "Vulnerability source lookup failed."
)


def _validate_model_tuple(
    value: object,
    expected_type: type[object],
    field_name: str,
) -> None:
    """Validate a tuple containing one model type."""

    if not isinstance(value, tuple):
        raise ValueError(
            f"{field_name} must be a tuple."
        )

    for item in value:
        if not isinstance(item, expected_type):
            raise ValueError(
                f"{field_name} contains an invalid item."
            )


@dataclass(frozen=True, slots=True)
class DependencyScanError:
    """Represent one expected dependency lookup failure."""

    dependency: Dependency
    source: AdvisorySource
    message: str

    def __post_init__(self) -> None:
        """Validate and normalize error details."""

        if not isinstance(self.dependency, Dependency):
            raise ValueError(
                "dependency must be a Dependency instance."
            )

        if not isinstance(self.source, AdvisorySource):
            raise ValueError(
                "source must be an AdvisorySource instance."
            )

        if not isinstance(self.message, str):
            raise ValueError(
                "message must be a string."
            )

        cleaned_message = self.message.strip()

        if not cleaned_message:
            raise ValueError(
                "message must not be empty."
            )

        object.__setattr__(
            self,
            "message",
            cleaned_message,
        )


@dataclass(frozen=True, slots=True)
class DependencyScanResult:
    """Represent the complete outcome of one dependency scan."""

    dependencies: tuple[Dependency, ...] = field(
        default_factory=tuple
    )
    findings: tuple[DependencyFinding, ...] = field(
        default_factory=tuple
    )
    errors: tuple[DependencyScanError, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        """Validate result collections."""

        _validate_model_tuple(
            self.dependencies,
            Dependency,
            "dependencies",
        )
        _validate_model_tuple(
            self.findings,
            DependencyFinding,
            "findings",
        )
        _validate_model_tuple(
            self.errors,
            DependencyScanError,
            "errors",
        )

    @property
    def succeeded(self) -> bool:
        """Return whether every dependency lookup succeeded."""

        return not self.errors


class DependencyScanner:
    """Scan dependencies through one vulnerability source."""

    def __init__(
        self,
        source: VulnerabilitySource,
    ) -> None:
        """Create a scanner using one vulnerability source."""

        if not isinstance(source, VulnerabilitySource):
            raise ValueError(
                "source must satisfy VulnerabilitySource."
            )

        self._source = source

    @property
    def source(self) -> VulnerabilitySource:
        """Return the configured vulnerability source."""

        return self._source

    def scan_dependencies(
        self,
        dependencies: tuple[Dependency, ...],
    ) -> DependencyScanResult:
        """Scan dependencies while collecting expected source errors."""

        _validate_model_tuple(
            dependencies,
            Dependency,
            "dependencies",
        )

        findings: list[DependencyFinding] = []
        errors: list[DependencyScanError] = []

        for dependency in dependencies:
            try:
                source_findings = (
                    self._source.find_vulnerabilities(
                        dependency
                    )
                )
            except VulnerabilitySourceError as error:
                errors.append(
                    self._create_scan_error(
                        dependency,
                        error,
                    )
                )
                continue

            _validate_model_tuple(
                source_findings,
                DependencyFinding,
                "source findings",
            )
            findings.extend(source_findings)

        return DependencyScanResult(
            dependencies=dependencies,
            findings=tuple(findings),
            errors=tuple(errors),
        )

    def scan_requirements(
        self,
        file_path: str | Path,
    ) -> DependencyScanResult:
        """Parse and scan one requirements file."""

        dependencies = parse_requirements_file(
            file_path
        )

        return self.scan_dependencies(dependencies)

    def _create_scan_error(
        self,
        dependency: Dependency,
        error: VulnerabilitySourceError,
    ) -> DependencyScanError:
        """Create a serializable expected source error."""

        message = str(error).strip()

        if not message:
            message = _SOURCE_ERROR_FALLBACK

        return DependencyScanError(
            dependency=dependency,
            source=self._source.advisory_source,
            message=message,
        )
