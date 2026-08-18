"""Define command-line arguments for dependency scanning."""

from __future__ import annotations

import argparse
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


_DEFAULT_TIMEOUT = 10.0
_OUTPUT_FORMATS = ("text", "json")
_FAIL_ON_LEVELS = (
    "any",
    "low",
    "medium",
    "high",
    "critical",
)
_SOURCES = ("osv",)


@dataclass(frozen=True, slots=True)
class DependencyCliArguments:
    """Represent validated dependency scan arguments."""

    requirements_file: Path
    output_format: str
    output_path: Path | None
    fail_on: str
    source: str
    timeout: float


def build_parser() -> argparse.ArgumentParser:
    """Create the dependency scan argument parser."""

    parser = argparse.ArgumentParser(
        prog="securecode-dependency-scan",
        description=(
            "Scan pinned Python dependencies for known vulnerabilities."
        ),
    )

    parser.add_argument(
        "requirements_file",
        type=Path,
        help="Path to the requirements file to scan.",
    )

    _add_report_arguments(parser)
    _add_scan_arguments(parser)

    return parser


def _add_report_arguments(
    parser: argparse.ArgumentParser,
) -> None:
    """Add report formatting and destination options."""

    parser.add_argument(
        "--format",
        dest="output_format",
        choices=_OUTPUT_FORMATS,
        default="text",
        help="Output format to use. Available formats: text, json.",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        type=Path,
        default=None,
        help="Write the report to this path instead of stdout.",
    )


def _add_scan_arguments(
    parser: argparse.ArgumentParser,
) -> None:
    """Add scan policy and vulnerability source options."""

    parser.add_argument(
        "--fail-on",
        choices=_FAIL_ON_LEVELS,
        default="any",
        help=(
            "Return exit code 1 for findings at or above this severity."
        ),
    )
    parser.add_argument(
        "--source",
        choices=_SOURCES,
        default="osv",
        help="Vulnerability source to query. Available sources: osv.",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_finite_float,
        default=_DEFAULT_TIMEOUT,
        metavar="SECONDS",
        help="Positive OSV request timeout in seconds.",
    )


def parse_arguments(
    argv: Sequence[str] | None = None,
) -> DependencyCliArguments:
    """Parse command-line values into immutable arguments."""

    namespace = build_parser().parse_args(argv)

    return DependencyCliArguments(
        requirements_file=namespace.requirements_file,
        output_format=namespace.output_format,
        output_path=namespace.output_path,
        fail_on=namespace.fail_on,
        source=namespace.source,
        timeout=namespace.timeout,
    )


def _positive_finite_float(value: str) -> float:
    """Parse a positive finite floating-point argument."""

    try:
        parsed_value = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "must be a positive finite number"
        ) from error

    if (
        not math.isfinite(parsed_value)
        or parsed_value <= 0
    ):
        raise argparse.ArgumentTypeError(
            "must be a positive finite number"
        )

    return parsed_value
