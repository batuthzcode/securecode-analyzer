"""Format dependency scan results as human-readable text."""

from __future__ import annotations

from dependency_scanner.models import DependencyFinding
from dependency_scanner.scanner import (
    DependencyScanError,
    DependencyScanResult,
)


def format_dependency_scan_text(
    result: DependencyScanResult,
) -> str:
    """Return one dependency scan result as readable text."""

    _validate_result(result)

    detail_lines = [
        *(
            _format_finding(finding)
            for finding in result.findings
        ),
        *(
            _format_error(error)
            for error in result.errors
        ),
    ]

    if not detail_lines:
        detail_lines.append(
            "No dependency vulnerabilities found."
        )

    return "\n".join(
        [
            *detail_lines,
            "",
            _format_summary(result),
        ]
    )


def _validate_result(result: object) -> None:
    """Require a complete dependency scan result."""

    if not isinstance(result, DependencyScanResult):
        raise ValueError(
            "result must be a DependencyScanResult instance."
        )


def _format_finding(finding: DependencyFinding) -> str:
    """Format one dependency vulnerability finding."""

    dependency = finding.dependency
    location = (
        f"{dependency.source_file}:"
        f"{dependency.line_number}"
    )
    line = (
        f"[{finding.severity.value.upper()}] "
        f"{finding.advisory_id} "
        f"{dependency.name}{dependency.operator}"
        f"{dependency.version} "
        f"{location} - "
        f"{finding.message} | "
        f"source={finding.source.name}"
    )

    if finding.fixed_version is not None:
        line += f" | fixed={finding.fixed_version}"

    if finding.aliases:
        line += f" | aliases={', '.join(finding.aliases)}"

    return line


def _format_error(error: DependencyScanError) -> str:
    """Format one dependency lookup failure."""

    dependency = error.dependency
    location = (
        f"{dependency.source_file}:"
        f"{dependency.line_number}"
    )

    return (
        f"[LOOKUP ERROR] {error.source.name} "
        f"{dependency.name}{dependency.operator}"
        f"{dependency.version} "
        f"{location} - {error.message}"
    )


def _format_summary(result: DependencyScanResult) -> str:
    """Format scan counters with correct singular forms."""

    dependency_count = len(result.dependencies)
    finding_count = len(result.findings)
    error_count = len(result.errors)

    dependency_word = (
        "dependency"
        if dependency_count == 1
        else "dependencies"
    )
    finding_word = (
        "finding"
        if finding_count == 1
        else "findings"
    )
    error_word = (
        "lookup error"
        if error_count == 1
        else "lookup errors"
    )

    return (
        f"{dependency_count} {dependency_word} scanned. "
        f"{finding_count} {finding_word}. "
        f"{error_count} {error_word}."
    )
