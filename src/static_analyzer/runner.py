"""Coordinate the SecureCode Analyzer command-line workflow."""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from typing import TextIO

from static_analyzer.cli import parse_arguments
from static_analyzer.default_factory import create_default_analyzer
from static_analyzer.formatters import (
    format_findings_json,
    format_findings_text,
)
from static_analyzer.project_analyzer import ProjectAnalyzer


AnalyzerFactory = Callable[[], ProjectAnalyzer]

_OPERATIONAL_ERRORS = (
    FileNotFoundError,
    NotADirectoryError,
    SyntaxError,
    UnicodeDecodeError,
)


def run_cli(
    argv: Sequence[str] | None = None,
    *,
    analyzer_factory: AnalyzerFactory | None = None,
    stdout: TextIO | None = None,
) -> int:
    """Run one static-analysis command-line operation."""

    arguments = parse_arguments(argv)

    factory = (
        analyzer_factory
        if analyzer_factory is not None
        else create_default_analyzer
    )
    analyzer = factory()

    findings = analyzer.analyze(arguments.target)

    if arguments.output_format == "text":
        output = format_findings_text(findings)
    elif arguments.output_format == "json":
        output = format_findings_json(findings)
    else:
        raise ValueError(
            f"Unsupported output format: "
            f"{arguments.output_format}"
        )

    output_stream = (
        stdout
        if stdout is not None
        else sys.stdout
    )
    output_stream.write(output)
    output_stream.write("\n")

    return 1 if findings else 0


def main(
    argv: Sequence[str] | None = None,
    *,
    analyzer_factory: AnalyzerFactory | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the CLI and convert expected operational errors to exit code 2."""

    error_stream = (
        stderr
        if stderr is not None
        else sys.stderr
    )

    try:
        return run_cli(
            argv,
            analyzer_factory=analyzer_factory,
            stdout=stdout,
        )
    except _OPERATIONAL_ERRORS as error:
        error_stream.write(f"Error: {error}\n")
        return 2