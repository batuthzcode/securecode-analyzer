"""Integration tests for checked-in sample-app security reports."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import dependency_scanner.osv_client as osv_client_module
from tools.generate_sample_app_reports import (
    build_dependency_scan_report,
    build_reports,
    find_stale_reports,
    main,
    write_reports,
)


_REPOSITORY_ROOT = Path(__file__).parents[1]
_REPORT_DIRECTORY = (
    _REPOSITORY_ROOT / "reports" / "sample-app"
)
_DEMO_LITERAL = "demo-only-not-a-real-secret"


def _load_report(filename: str) -> dict[str, object]:
    """Load one committed report as structured JSON."""

    return json.loads(
        (_REPORT_DIRECTORY / filename).read_text(
            encoding="utf-8"
        )
    )


def test_checked_in_reports_match_generator() -> None:
    """Committed artifacts should be exact generated baselines."""

    for filename, expected in build_reports().items():
        assert (
            _REPORT_DIRECTORY / filename
        ).read_text(encoding="utf-8") == expected


def test_static_analysis_report_has_exact_findings() -> None:
    """The report should capture only five deliberate findings."""

    payload = _load_report("static-analysis.json")

    assert payload["summary"] == {"total": 5}
    assert [
        (
            finding["rule_id"],
            finding["file_path"],
            finding["line_number"],
            finding["severity"],
        )
        for finding in payload["findings"]
    ] == [
        (
            "SA005",
            "sample_app/analyzer_demo.py",
            8,
            "warning",
        ),
        (
            "SA001",
            "sample_app/analyzer_demo.py",
            11,
            "warning",
        ),
        (
            "SA006",
            "sample_app/analyzer_demo.py",
            11,
            "info",
        ),
        (
            "SA003",
            "sample_app/analyzer_demo.py",
            14,
            "info",
        ),
        (
            "SA004",
            "sample_app/analyzer_demo.py",
            54,
            "warning",
        ),
    ]
    assert _DEMO_LITERAL not in json.dumps(payload)


def test_dependency_report_has_official_finding() -> None:
    """The report should retain real OSV source and fix data."""

    payload = _load_report("dependency-scan.json")
    finding = payload["findings"][0]

    assert payload["summary"] == {
        "dependencies": 1,
        "findings": 1,
        "errors": 0,
        "succeeded": True,
    }
    assert finding["dependency"]["source_file"] == (
        "sample_app/requirements-vulnerable.txt"
    )
    assert finding["advisory_id"] == "PYSEC-2024-38"
    assert "CVE-2024-24762" in finding["aliases"]
    assert finding["severity"] == "high"
    assert finding["fixed_version"] == "0.109.1"
    assert finding["source"] == {
        "name": "OSV",
        "url": "https://osv.dev/",
    }


def test_dependency_report_generation_never_uses_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Baseline generation should stay deterministic and offline."""

    def fail_network_call(
        *args: object,
        **kwargs: object,
    ) -> None:
        pytest.fail("Unexpected live OSV HTTP request.")

    monkeypatch.setattr(
        osv_client_module,
        "urlopen",
        fail_network_call,
    )

    assert "PYSEC-2024-38" in (
        build_dependency_scan_report()
    )


def test_reports_can_be_written_from_any_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Absolute repository inputs should make generation portable."""

    output_directory = tmp_path / "generated"
    monkeypatch.chdir(tmp_path)

    written_paths = write_reports(output_directory)

    assert written_paths == (
        output_directory / "static-analysis.json",
        output_directory / "dependency-scan.json",
    )
    assert find_stale_reports(output_directory) == ()


def test_check_mode_reports_stale_artifact(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Check mode should fail without replacing an outdated file."""

    write_reports(tmp_path)
    stale_path = tmp_path / "static-analysis.json"
    stale_path.write_text("{}\n", encoding="utf-8")

    exit_code = main(
        [
            "--check",
            "--output-directory",
            str(tmp_path),
        ]
    )

    assert exit_code == 1
    assert str(stale_path) in capsys.readouterr().out
    assert stale_path.read_text(encoding="utf-8") == "{}\n"
