"""Tests for the deterministic dependency-scan CI command."""

from __future__ import annotations

import io
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import dependency_scanner.osv_client as osv_client_module
from dependency_scanner.osv_client import OsvQueryError
from tools.osv_fixture import FixtureOsvQueryClient
from tools.run_ci_dependency_scan import main


_REPOSITORY_ROOT = Path(__file__).parents[1]
_FIXTURE_PATH = (
    _REPOSITORY_ROOT
    / "tests"
    / "fixtures"
    / "osv"
    / "fastapi-0.109.0.json"
)
_REQUIREMENTS_PATH = (
    _REPOSITORY_ROOT
    / "sample_app"
    / "requirements-vulnerable.txt"
)
_BASELINE_PATH = (
    _REPOSITORY_ROOT
    / "reports"
    / "sample-app"
    / "dependency-scan.json"
)


def test_fixture_client_enforces_recorded_query() -> None:
    """Offline data should answer only its metadata query."""

    client = FixtureOsvQueryClient(_FIXTURE_PATH)

    assert client.expected_query == (
        "fastapi",
        "0.109.0",
        None,
    )
    response = client.query_package(
        "FastAPI",
        "0.109.0",
    )
    assert response.vulnerabilities[0].advisory_id == (
        "PYSEC-2024-38"
    )

    with pytest.raises(OsvQueryError):
        client.query_package("fastapi", "0.110.0")

    with pytest.raises(OsvQueryError):
        client.query_package(
            "fastapi",
            "0.109.0",
            page_token="unexpected",
        )


def test_ci_scan_matches_baseline_without_http(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The default critical gate should write the offline baseline."""

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
    output_path = tmp_path / "dependency-scan.json"

    exit_code = main(
        [
            "--requirements",
            str(_REQUIREMENTS_PATH),
            "--fixture",
            str(_FIXTURE_PATH),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == (
        _BASELINE_PATH.read_text(encoding="utf-8")
    )


def test_ci_scan_module_entrypoint_runs_without_root_pythonpath(
    tmp_path: Path,
) -> None:
    """The workflow command should resolve the tools package on Linux."""

    output_path = tmp_path / "dependency-scan.json"
    environment = os.environ.copy()
    pythonpath_entries = [str(_REPOSITORY_ROOT / "src")]

    for entry in environment.get("PYTHONPATH", "").split(
        os.pathsep
    ):
        if not entry:
            continue

        resolved_entry = Path(entry).resolve()
        if resolved_entry in {
            _REPOSITORY_ROOT.resolve(),
            (_REPOSITORY_ROOT / "src").resolve(),
        }:
            continue

        pythonpath_entries.append(entry)

    environment["PYTHONPATH"] = os.pathsep.join(
        pythonpath_entries
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.run_ci_dependency_scan",
            "--requirements",
            str(_REQUIREMENTS_PATH),
            "--fixture",
            str(_FIXTURE_PATH),
            "--output",
            str(output_path),
            "--fail-on",
            "critical",
        ],
        cwd=_REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert output_path.read_text(encoding="utf-8") == (
        _BASELINE_PATH.read_text(encoding="utf-8")
    )


@pytest.mark.parametrize(
    ("fail_on", "expected_exit_code"),
    [
        ("high", 1),
        ("critical", 0),
    ],
)
def test_ci_scan_applies_configured_threshold(
    tmp_path: Path,
    fail_on: str,
    expected_exit_code: int,
) -> None:
    """The recorded HIGH finding should exercise the CI threshold."""

    output_path = tmp_path / f"{fail_on}.json"

    exit_code = main(
        [
            "--requirements",
            str(_REQUIREMENTS_PATH),
            "--fixture",
            str(_FIXTURE_PATH),
            "--output",
            str(output_path),
            "--fail-on",
            fail_on,
        ]
    )

    payload = json.loads(
        output_path.read_text(encoding="utf-8")
    )
    assert exit_code == expected_exit_code
    assert payload["findings"][0]["severity"] == "high"


def test_ci_scan_fails_closed_when_fixture_is_missing(
    tmp_path: Path,
) -> None:
    """Unavailable offline data should return operational exit code two."""

    output_path = tmp_path / "dependency-scan.json"
    stderr = io.StringIO()

    exit_code = main(
        [
            "--requirements",
            str(_REQUIREMENTS_PATH),
            "--fixture",
            str(tmp_path / "missing.json"),
            "--output",
            str(output_path),
        ],
        stderr=stderr,
    )

    assert exit_code == 2
    assert not output_path.exists()
    assert "Error:" in stderr.getvalue()
