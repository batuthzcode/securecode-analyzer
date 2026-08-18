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
import tools.run_ci_dependency_scan as ci_scan_module
from tools.osv_fixture import (
    FixtureOsvQueryClient,
    OsvFixtureError,
)
from tools.run_ci_dependency_scan import (
    FixtureScannerFactory,
    _portable_path,
    main,
)


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


def _module_environment() -> dict[str, str]:
    """Return an environment without the repository root on PYTHONPATH."""

    environment = os.environ.copy()
    excluded_paths = {
        _REPOSITORY_ROOT.resolve(),
        (_REPOSITORY_ROOT / "src").resolve(),
    }
    pythonpath_entries = [str(_REPOSITORY_ROOT / "src")]

    for entry in environment.get("PYTHONPATH", "").split(os.pathsep):
        if entry and Path(entry).resolve() not in excluded_paths:
            pythonpath_entries.append(entry)

    environment["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)
    return environment


def _run_ci_scan_module(output_path: Path) -> subprocess.CompletedProcess[str]:
    """Run the documented module command in a clean subprocess."""

    return subprocess.run(
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
        env=_module_environment(),
        capture_output=True,
        text=True,
        check=False,
    )


def _fixture_payload(
    *,
    ecosystem: object = "PyPI",
    package_name: object = "demo-package",
    version: object = "1.0.0",
) -> dict[str, object]:
    """Create a minimal recorded OSV query document."""

    return {
        "_fixture": {
            "query": {
                "package": {
                    "ecosystem": ecosystem,
                    "name": package_name,
                },
                "version": version,
            },
        },
        "vulns": [],
    }


def _write_json_fixture(
    path: Path,
    payload: object,
) -> Path:
    """Write one fixture payload and return its path."""

    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_fixture_client_enforces_recorded_query() -> None:
    """Offline data should answer only its metadata query."""

    client = FixtureOsvQueryClient(_FIXTURE_PATH)

    assert client.fixture_path == _FIXTURE_PATH
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


def test_fixture_client_rejects_invalid_query_name() -> None:
    """Invalid package syntax should use the public OSV query error."""

    client = FixtureOsvQueryClient(_FIXTURE_PATH)

    with pytest.raises(OsvQueryError, match="Invalid fixture package"):
        client.query_package("invalid/package", "0.109.0")


def test_fixture_client_rejects_invalid_json(tmp_path: Path) -> None:
    """Malformed recorded data should fail before scanning."""

    fixture_path = tmp_path / "invalid.json"
    fixture_path.write_text("{", encoding="utf-8")

    with pytest.raises(OsvFixtureError, match="Invalid OSV fixture JSON"):
        FixtureOsvQueryClient(fixture_path)


def test_fixture_client_requires_object_root(tmp_path: Path) -> None:
    """OSV fixture metadata must be stored in an object."""

    fixture_path = _write_json_fixture(
        tmp_path / "array.json",
        [],
    )

    with pytest.raises(OsvFixtureError, match="root must be an object"):
        FixtureOsvQueryClient(fixture_path)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "_fixture must be an object"),
        ({"_fixture": {}}, "_fixture.query must be an object"),
        (
            {"_fixture": {"query": {}}},
            "_fixture.query.package must be an object",
        ),
        (_fixture_payload(ecosystem="npm"), "ecosystem must be PyPI"),
        (
            _fixture_payload(package_name="invalid/package"),
            "Invalid OSV fixture package name",
        ),
        (
            _fixture_payload(version=" "),
            "version must be a non-empty string",
        ),
    ],
)
def test_fixture_client_rejects_invalid_metadata(
    tmp_path: Path,
    payload: object,
    message: str,
) -> None:
    """Every required recorded-query field should fail closed."""

    fixture_path = _write_json_fixture(
        tmp_path / "metadata.json",
        payload,
    )

    with pytest.raises(OsvFixtureError, match=message):
        FixtureOsvQueryClient(fixture_path)


def test_fixture_client_translates_invalid_osv_response(
    tmp_path: Path,
) -> None:
    """A valid query envelope cannot hide malformed OSV records."""

    payload = _fixture_payload()
    payload["vulns"] = [{"summary": "missing advisory id"}]
    fixture_path = _write_json_fixture(
        tmp_path / "invalid-response.json",
        payload,
    )

    with pytest.raises(OsvFixtureError, match="Invalid OSV response"):
        FixtureOsvQueryClient(fixture_path)


@pytest.mark.parametrize(
    ("source_name", "timeout", "message"),
    [
        ("nvd", 10.0, "supports only OSV"),
        ("osv", 0.0, "timeout must be positive"),
    ],
)
def test_fixture_scanner_factory_rejects_invalid_configuration(
    source_name: str,
    timeout: float,
    message: str,
) -> None:
    """The offline scanner factory should enforce its narrow contract."""

    factory = FixtureScannerFactory(_FIXTURE_PATH)

    with pytest.raises(OsvFixtureError, match=message):
        factory(source_name=source_name, timeout=timeout)


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
    completed = _run_ci_scan_module(output_path)

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


def test_ci_scan_translates_report_normalization_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid generated JSON should produce operational exit code two."""

    output_path = tmp_path / "invalid.json"

    def write_invalid_report(
        argv: object,
        **kwargs: object,
    ) -> int:
        del argv, kwargs
        output_path.write_text("{", encoding="utf-8")
        return 0

    monkeypatch.setattr(
        ci_scan_module,
        "dependency_cli_main",
        write_invalid_report,
    )
    stderr = io.StringIO()

    exit_code = main(["--output", str(output_path)], stderr=stderr)

    assert exit_code == 2
    assert "Error:" in stderr.getvalue()


def test_ci_scan_translates_output_directory_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Output directory failures should produce operational exit code two."""

    def reject_directory(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise OSError("directory unavailable")

    monkeypatch.setattr(Path, "mkdir", reject_directory)
    stderr = io.StringIO()

    exit_code = main(
        ["--output", str(tmp_path / "report.json")],
        stderr=stderr,
    )

    assert exit_code == 2
    assert "directory unavailable" in stderr.getvalue()


def test_ci_report_path_normalization_is_repository_scoped(
    tmp_path: Path,
) -> None:
    """Portable report paths should reject files outside the repository."""

    assert _portable_path("sample_app/requirements.txt") == (
        "sample_app/requirements.txt"
    )

    with pytest.raises(OsvFixtureError, match="outside the repository"):
        _portable_path(str(tmp_path / "requirements.txt"))
