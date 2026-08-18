"""Tests for the checked-in whole-project self-analysis report."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.generate_self_analysis_report import (
    build_self_analysis_report,
    main,
    report_is_current,
    write_self_analysis_report,
)


_REPOSITORY_ROOT = Path(__file__).parents[1]
_REPORT_PATH = (
    _REPOSITORY_ROOT / "reports" / "project" / "static-analysis.json"
)
_EXPECTED_FINDINGS = [
    ("SA005", "sample_app/analyzer_demo.py", 8, "warning"),
    ("SA001", "sample_app/analyzer_demo.py", 11, "warning"),
    ("SA006", "sample_app/analyzer_demo.py", 11, "info"),
    ("SA003", "sample_app/analyzer_demo.py", 14, "info"),
    ("SA004", "sample_app/analyzer_demo.py", 54, "warning"),
]


def test_checked_in_self_analysis_report_is_current() -> None:
    """The committed artifact should match a fresh production analysis."""

    assert report_is_current(_REPORT_PATH)
    assert _REPORT_PATH.read_text(encoding="utf-8") == (
        build_self_analysis_report()
    )


def test_self_analysis_contains_only_controlled_demo_findings() -> None:
    """All remaining project findings should be intentional true positives."""

    payload = json.loads(build_self_analysis_report())

    assert payload["summary"] == {"total": 5}
    assert [
        (
            finding["rule_id"],
            finding["file_path"],
            finding["line_number"],
            finding["severity"],
        )
        for finding in payload["findings"]
    ] == _EXPECTED_FINDINGS


def test_self_analysis_report_can_be_written_from_any_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Generation should not depend on the process working directory."""

    output_path = tmp_path / "reports" / "self-analysis.json"
    monkeypatch.chdir(tmp_path)

    assert write_self_analysis_report(output_path) == output_path
    assert output_path.read_text(encoding="utf-8") == (
        build_self_analysis_report()
    )


def test_self_analysis_check_rejects_missing_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Check mode should fail closed when the artifact is absent."""

    output_path = tmp_path / "missing.json"

    assert main(["--check", "--output", str(output_path)]) == 1
    assert str(output_path) in capsys.readouterr().out


def test_self_analysis_check_rejects_stale_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Check mode should report drift without replacing the artifact."""

    output_path = tmp_path / "stale.json"
    output_path.write_text("{}\n", encoding="utf-8")

    assert main(["--check", "--output", str(output_path)]) == 1
    assert str(output_path) in capsys.readouterr().out
    assert output_path.read_text(encoding="utf-8") == "{}\n"


def test_self_analysis_check_accepts_current_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Check mode should accept an exact generated artifact."""

    output_path = write_self_analysis_report(tmp_path / "current.json")

    assert main(["--check", "--output", str(output_path)]) == 0
    assert "is current" in capsys.readouterr().out


def test_self_analysis_main_writes_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Write mode should create the selected artifact."""

    output_path = tmp_path / "generated" / "report.json"

    assert main(["--output", str(output_path)]) == 0
    assert output_path.exists()
    assert str(output_path) in capsys.readouterr().out
