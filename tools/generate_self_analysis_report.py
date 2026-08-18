"""Generate the deterministic whole-project static-analysis report."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from static_analyzer.default_factory import create_default_analyzer
from static_analyzer.formatters import format_findings_json


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_OUTPUT_PATH = (
    _REPOSITORY_ROOT / "reports" / "project" / "static-analysis.json"
)


def build_self_analysis_report() -> str:
    """Return a portable report for every Python file in the repository."""

    findings = create_default_analyzer().analyze(_REPOSITORY_ROOT)
    payload = json.loads(format_findings_json(findings))

    for finding in payload["findings"]:
        finding["file_path"] = _portable_path(finding["file_path"])

    return _serialize(payload)


def write_self_analysis_report(
    output_path: Path = _DEFAULT_OUTPUT_PATH,
) -> Path:
    """Write the current report and return its destination."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_self_analysis_report(),
        encoding="utf-8",
        newline="\n",
    )
    return output_path


def report_is_current(
    output_path: Path = _DEFAULT_OUTPUT_PATH,
) -> bool:
    """Return whether a checked-in report matches a fresh analysis."""

    try:
        current = output_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False

    return current == build_self_analysis_report()


def main(argv: Sequence[str] | None = None) -> int:
    """Write the self-analysis report or check it for drift."""

    arguments = _build_parser().parse_args(argv)

    if arguments.check:
        if not report_is_current(arguments.output):
            print(f"Outdated report: {arguments.output}")
            return 1

        print("Whole-project self-analysis report is current.")
        return 0

    written_path = write_self_analysis_report(arguments.output)
    print(f"Wrote report: {written_path}")
    return 0


def _portable_path(value: str) -> str:
    """Return one repository-relative path using POSIX separators."""

    path = Path(value)

    if not path.is_absolute():
        path = _REPOSITORY_ROOT / path

    relative_path = path.resolve().relative_to(_REPOSITORY_ROOT.resolve())
    return relative_path.as_posix()


def _serialize(payload: object) -> str:
    """Serialize one canonical checked-in JSON document."""

    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    """Create the report generator argument parser."""

    parser = argparse.ArgumentParser(
        description="Generate the whole-project static-analysis report."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return exit code 1 when the report is missing or stale.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT_PATH,
        help="Destination for the canonical JSON report.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
