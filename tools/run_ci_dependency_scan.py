"""Run the dependency CLI against a deterministic OSV fixture."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from dependency_scanner import (
    DependencyScanner,
    OsvVulnerabilitySource,
)
from dependency_scanner.runner import (
    main as dependency_cli_main,
)
from tools.osv_fixture import (
    FixtureOsvQueryClient,
    OsvFixtureError,
)


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_REQUIREMENTS = Path(
    "sample_app/requirements-vulnerable.txt"
)
_DEFAULT_FIXTURE = Path(
    "tests/fixtures/osv/fastapi-0.109.0.json"
)
_DEFAULT_OUTPUT = Path(
    "reports/ci/dependency-scan.json"
)
_FAIL_ON_LEVELS = (
    "any",
    "low",
    "medium",
    "high",
    "critical",
)


class FixtureScannerFactory:
    """Create dependency scanners backed by one local fixture."""

    def __init__(self, fixture_path: Path) -> None:
        """Store the OSV fixture used by each scanner."""

        self._fixture_path = fixture_path

    def __call__(
        self,
        *,
        source_name: str,
        timeout: float,
    ) -> DependencyScanner:
        """Create an offline scanner for the production runner."""

        if source_name != "osv":
            raise OsvFixtureError(
                "Offline CI scanning supports only OSV."
            )

        if timeout <= 0:
            raise OsvFixtureError(
                "Scanner timeout must be positive."
            )

        client = FixtureOsvQueryClient(
            self._fixture_path
        )
        return DependencyScanner(
            OsvVulnerabilitySource(client)
        )


def main(
    argv: Sequence[str] | None = None,
    *,
    stderr: TextIO | None = None,
) -> int:
    """Run one fail-closed offline dependency scan."""

    arguments = _build_parser().parse_args(argv)
    error_stream = stderr if stderr is not None else sys.stderr

    try:
        arguments.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        exit_code = dependency_cli_main(
            [
                str(arguments.requirements),
                "--format",
                "json",
                "--output",
                str(arguments.output),
                "--fail-on",
                arguments.fail_on,
            ],
            scanner_factory=FixtureScannerFactory(
                arguments.fixture
            ),
            stderr=error_stream,
        )

        if exit_code in (0, 1):
            _normalize_report_paths(
                arguments.output
            )

        return exit_code
    except (
        OSError,
        UnicodeDecodeError,
        OsvFixtureError,
        json.JSONDecodeError,
    ) as error:
        error_stream.write(f"Error: {error}\n")
        return 2


def _normalize_report_paths(output_path: Path) -> None:
    """Rewrite repository paths with portable POSIX separators."""

    payload = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    for dependency in payload["dependencies"]:
        dependency["source_file"] = _portable_path(
            dependency["source_file"]
        )

    for finding in payload["findings"]:
        dependency = finding["dependency"]
        dependency["source_file"] = _portable_path(
            dependency["source_file"]
        )

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _portable_path(value: str) -> str:
    """Return one repository-relative POSIX path."""

    path = Path(value)

    if not path.is_absolute():
        path = _REPOSITORY_ROOT / path

    try:
        relative_path = path.resolve().relative_to(
            _REPOSITORY_ROOT.resolve()
        )
    except ValueError as error:
        raise OsvFixtureError(
            f"Report path is outside the repository: {value}"
        ) from error

    return relative_path.as_posix()


def _build_parser() -> argparse.ArgumentParser:
    """Create the offline CI command parser."""

    parser = argparse.ArgumentParser(
        prog="run-ci-dependency-scan",
        description=(
            "Run the production dependency CLI with local OSV data."
        ),
    )
    parser.add_argument(
        "--requirements",
        type=Path,
        default=_DEFAULT_REQUIREMENTS,
        help="Pinned requirements file to scan.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=_DEFAULT_FIXTURE,
        help="Recorded OSV response fixture.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help="Destination JSON report path.",
    )
    parser.add_argument(
        "--fail-on",
        choices=_FAIL_ON_LEVELS,
        default="critical",
        help="Minimum vulnerability severity that fails the gate.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
