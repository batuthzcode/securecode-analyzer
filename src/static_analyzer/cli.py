"""Define command-line arguments for the static analyzer."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CliArguments:
    """Represent validated command-line arguments."""

    target: Path
    output_format: str
    fail_on: str = "any"


def build_parser() -> argparse.ArgumentParser:
    """Create and configure a new command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="securecode-analyzer",
        description=(
            "Analyze Python source code for quality and security findings."
        ),
    )

    parser.add_argument(
        "target",
        type=Path,
        help="Directory containing Python source code to analyze.",
    )

    parser.add_argument(
        "--format",
        dest="output_format",
        choices=("text", "json"),
        default="text",
        help="Output format to use. Available formats: text, json.",
    )

    parser.add_argument(
        "--fail-on",
        choices=("any", "info", "warning", "error"),
        default="any",
        help=(
            "Return exit code 1 for findings at or above this severity."
        ),
    )

    return parser


def parse_arguments(
    argv: Sequence[str] | None = None,
) -> CliArguments:
    """Parse command-line arguments into validated CLI data."""

    parser = build_parser()
    namespace = parser.parse_args(argv)

    return CliArguments(
        target=namespace.target,
        output_format=namespace.output_format,
        fail_on=namespace.fail_on,
    )
