"""Coordinate the dependency scanner command-line workflow."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, TextIO

from dependency_scanner.cli import parse_arguments
from dependency_scanner.default_factory import (
    DependencyScannerConfigurationError,
    create_default_dependency_scanner,
)
from dependency_scanner.formatters import (
    format_dependency_scan_json,
    format_dependency_scan_text,
)
from dependency_scanner.models import VulnerabilitySeverity
from dependency_scanner.osv_client import OsvQueryError
from dependency_scanner.requirements_parser import (
    RequirementsParseError,
)
from dependency_scanner.scanner import (
    DependencyScanner,
    DependencyScanResult,
)


class DependencyCliError(ValueError):
    """Represent an expected dependency CLI usage error."""


class DependencyScannerFactory(Protocol):
    """Describe the scanner factory used by the runner."""

    def __call__(
        self,
        *,
        source_name: str,
        timeout: float,
    ) -> DependencyScanner:
        """Create a configured dependency scanner."""

        ...


_OPERATIONAL_ERRORS = (
    OSError,
    UnicodeDecodeError,
    RequirementsParseError,
    OsvQueryError,
    DependencyCliError,
    DependencyScannerConfigurationError,
)

_SEVERITY_RANK = {
    VulnerabilitySeverity.LOW: 1,
    VulnerabilitySeverity.MEDIUM: 2,
    VulnerabilitySeverity.HIGH: 3,
    VulnerabilitySeverity.CRITICAL: 4,
}


def run_cli(
    argv: Sequence[str] | None = None,
    *,
    scanner_factory: DependencyScannerFactory | None = None,
    stdout: TextIO | None = None,
) -> int:
    """Run one dependency scan command-line operation."""

    arguments = parse_arguments(argv)
    _validate_output_path(
        arguments.requirements_file,
        arguments.output_path,
    )

    factory = (
        scanner_factory
        if scanner_factory is not None
        else create_default_dependency_scanner
    )
    scanner = factory(
        source_name=arguments.source,
        timeout=arguments.timeout,
    )
    result = scanner.scan_requirements(
        arguments.requirements_file
    )
    output = _format_result(
        result,
        arguments.output_format,
    )

    _write_output(
        output,
        arguments.output_path,
        stdout,
    )

    return _calculate_exit_code(
        result,
        arguments.fail_on,
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    scanner_factory: DependencyScannerFactory | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Convert expected dependency CLI errors to exit code two."""

    error_stream = (
        stderr
        if stderr is not None
        else sys.stderr
    )

    try:
        return run_cli(
            argv,
            scanner_factory=scanner_factory,
            stdout=stdout,
        )
    except _OPERATIONAL_ERRORS as error:
        error_stream.write(f"Error: {error}\n")
        return 2


def _validate_output_path(
    requirements_file: Path,
    output_path: Path | None,
) -> None:
    """Prevent a report from overwriting its requirements input."""

    if output_path is None:
        return

    if output_path.resolve() == requirements_file.resolve():
        raise DependencyCliError(
            "Output path must differ from the requirements file."
        )


def _format_result(
    result: DependencyScanResult,
    output_format: str,
) -> str:
    """Apply the selected dependency scan formatter."""

    if output_format == "text":
        return format_dependency_scan_text(result)

    if output_format == "json":
        return format_dependency_scan_json(result)

    raise ValueError(
        f"Unsupported output format: {output_format}"
    )


def _write_output(
    output: str,
    output_path: Path | None,
    stdout: TextIO | None,
) -> None:
    """Write the report to exactly one selected destination."""

    document = f"{output}\n"

    if output_path is not None:
        output_path.write_text(
            document,
            encoding="utf-8",
            newline="\n",
        )
        return

    output_stream = (
        stdout
        if stdout is not None
        else sys.stdout
    )
    output_stream.write(document)


def _calculate_exit_code(
    result: DependencyScanResult,
    fail_on: str,
) -> int:
    """Return the result status using lookup-error precedence."""

    if result.errors:
        return 2

    if fail_on == "any":
        return 1 if result.findings else 0

    minimum_rank = _fail_on_rank(fail_on)

    for finding in result.findings:
        finding_rank = _SEVERITY_RANK.get(
            finding.severity
        )

        if (
            finding_rank is not None
            and finding_rank >= minimum_rank
        ):
            return 1

    return 0


def _fail_on_rank(fail_on: str) -> int:
    """Return the numeric rank for one configured threshold."""

    try:
        severity = VulnerabilitySeverity(fail_on)
        return _SEVERITY_RANK[severity]
    except (ValueError, KeyError) as error:
        raise ValueError(
            f"Unsupported fail-on severity: {fail_on}"
        ) from error
