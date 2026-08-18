"""Generate deterministic sample-app security integration reports."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from dependency_scanner import (
    DependencyScanner,
    OsvVulnerabilitySource,
    format_dependency_scan_json,
)
from static_analyzer.default_factory import (
    create_default_analyzer,
)
from static_analyzer.formatters import (
    format_findings_json,
)
from tools.osv_fixture import FixtureOsvQueryClient


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_SAMPLE_APP_ROOT = _REPOSITORY_ROOT / "sample_app"
_VULNERABLE_REQUIREMENTS = (
    _SAMPLE_APP_ROOT / "requirements-vulnerable.txt"
)
_OSV_FIXTURE = (
    _REPOSITORY_ROOT
    / "tests"
    / "fixtures"
    / "osv"
    / "fastapi-0.109.0.json"
)
_DEFAULT_OUTPUT_DIRECTORY = (
    _REPOSITORY_ROOT / "reports" / "sample-app"
)


def build_static_analysis_report() -> str:
    """Return the portable static-analysis baseline document."""

    findings = create_default_analyzer().analyze(
        _SAMPLE_APP_ROOT
    )
    payload = json.loads(format_findings_json(findings))

    for finding in payload["findings"]:
        finding["file_path"] = _portable_path(
            finding["file_path"]
        )

    return _serialize(payload)


def build_dependency_scan_report() -> str:
    """Return the offline OSV dependency baseline document."""

    scanner = DependencyScanner(
        OsvVulnerabilitySource(
            FixtureOsvQueryClient(_OSV_FIXTURE)
        )
    )
    result = scanner.scan_requirements(
        _VULNERABLE_REQUIREMENTS
    )

    if not result.succeeded:
        raise RuntimeError(
            "The fixture-backed dependency scan failed."
        )

    payload = json.loads(
        format_dependency_scan_json(result)
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

    return _serialize(payload)


def build_reports() -> dict[str, str]:
    """Return every checked-in sample-app report by filename."""

    return {
        "static-analysis.json": (
            build_static_analysis_report()
        ),
        "dependency-scan.json": (
            build_dependency_scan_report()
        ),
    }


def write_reports(
    output_directory: Path = _DEFAULT_OUTPUT_DIRECTORY,
) -> tuple[Path, ...]:
    """Write all generated reports and return their paths."""

    output_directory.mkdir(parents=True, exist_ok=True)
    written_paths: list[Path] = []

    for filename, document in build_reports().items():
        output_path = output_directory / filename
        output_path.write_text(
            document,
            encoding="utf-8",
            newline="\n",
        )
        written_paths.append(output_path)

    return tuple(written_paths)


def find_stale_reports(
    output_directory: Path = _DEFAULT_OUTPUT_DIRECTORY,
) -> tuple[Path, ...]:
    """Return missing or outdated checked-in report paths."""

    stale_paths: list[Path] = []

    for filename, expected in build_reports().items():
        output_path = output_directory / filename

        try:
            current = output_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            stale_paths.append(output_path)
            continue

        if current != expected:
            stale_paths.append(output_path)

    return tuple(stale_paths)


def main(argv: Sequence[str] | None = None) -> int:
    """Write reports or check that committed artifacts are current."""

    arguments = _build_parser().parse_args(argv)

    if arguments.check:
        stale_paths = find_stale_reports(
            arguments.output_directory
        )

        if stale_paths:
            for stale_path in stale_paths:
                print(f"Outdated report: {stale_path}")
            return 1

        print("Sample-app reports are current.")
        return 0

    for written_path in write_reports(
        arguments.output_directory
    ):
        print(f"Wrote report: {written_path}")

    return 0


def _portable_path(value: str) -> str:
    """Return one repository-relative path using POSIX separators."""

    path = Path(value)

    if not path.is_absolute():
        path = _REPOSITORY_ROOT / path

    try:
        relative_path = path.resolve().relative_to(
            _REPOSITORY_ROOT.resolve()
        )
    except ValueError as error:
        raise ValueError(
            f"Report path is outside the repository: {value}"
        ) from error

    return relative_path.as_posix()


def _serialize(payload: object) -> str:
    """Serialize one canonical checked-in JSON document."""

    return (
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )


def _build_parser() -> argparse.ArgumentParser:
    """Create the report generator argument parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic sample-app security reports."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return exit code 1 if a committed report is stale.",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=_DEFAULT_OUTPUT_DIRECTORY,
        help="Directory where the two JSON reports are stored.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
