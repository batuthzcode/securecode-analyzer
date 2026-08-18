"""Offline integration tests using an official OSV fixture."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

import dependency_scanner.osv_client as osv_client_module
from dependency_scanner import (
    DependencyScanResult,
    DependencyScanner,
    OsvQueryResponse,
    OsvVulnerabilitySource,
    VulnerabilitySeverity,
    format_dependency_scan_json,
    format_dependency_scan_text,
    parse_osv_query_response,
    parse_requirements_file,
)
from dependency_scanner.runner import run_cli


_FIXTURE_ROOT = Path(__file__).parent / "fixtures"
_OSV_FIXTURE_PATH = (
    _FIXTURE_ROOT / "osv" / "fastapi-0.109.0.json"
)
_REQUIREMENTS_FIXTURE_PATH = (
    _FIXTURE_ROOT
    / "requirements"
    / "fastapi-vulnerable.txt"
)
_GIT_FIXED_COMMIT = (
    "9d34ad0ee8a0dfbbcce06f76c2d5d851085024fc"
)


def _load_fixture_payload() -> dict[str, object]:
    """Load the checked-in OSV fixture as JSON data."""

    payload = json.loads(
        _OSV_FIXTURE_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(payload, dict)
    return payload


class FixtureOsvQueryClient:
    """Return one parsed OSV fixture without network access."""

    def __init__(self) -> None:
        """Load the deterministic response and initialize calls."""

        self._response = parse_osv_query_response(
            _load_fixture_payload()
        )
        self.calls: list[
            tuple[str, str, str | None]
        ] = []

    def query_package(
        self,
        package_name: str,
        version: str,
        page_token: str | None = None,
    ) -> OsvQueryResponse:
        """Record one query and return the fixture response."""

        self.calls.append(
            (package_name, version, page_token)
        )

        if page_token is not None:
            raise AssertionError(
                "The fixture does not contain another page."
            )

        return self._response


class FixtureScannerFactory:
    """Create dependency scanners backed by local OSV data."""

    def __init__(self) -> None:
        """Initialize recorded configuration and clients."""

        self.calls: list[tuple[str, float]] = []
        self.clients: list[FixtureOsvQueryClient] = []

    def __call__(
        self,
        *,
        source_name: str,
        timeout: float,
    ) -> DependencyScanner:
        """Create a fixture-backed scanner for one CLI run."""

        self.calls.append((source_name, timeout))
        client = FixtureOsvQueryClient()
        self.clients.append(client)

        return DependencyScanner(
            OsvVulnerabilitySource(client)
        )


def _scan_fixture() -> tuple[
    DependencyScanResult,
    FixtureOsvQueryClient,
]:
    """Run the requirements fixture through production layers."""

    client = FixtureOsvQueryClient()
    scanner = DependencyScanner(
        OsvVulnerabilitySource(client)
    )
    result = scanner.scan_requirements(
        _REQUIREMENTS_FIXTURE_PATH
    )

    return result, client


def test_fixture_records_official_osv_provenance() -> None:
    """Fixture metadata should identify its exact official query."""

    payload = _load_fixture_payload()
    metadata = payload["_fixture"]

    assert metadata == {
        "captured_at": "2026-08-18",
        "query_url": "https://api.osv.dev/v1/query",
        "advisory_url": (
            "https://osv.dev/vulnerability/PYSEC-2024-38"
        ),
        "query": {
            "package": {
                "name": "fastapi",
                "ecosystem": "PyPI",
            },
            "version": "0.109.0",
        },
        "projection": (
            "Only fields consumed by the parser and source are "
            "retained; their OSV security values are unchanged."
        ),
    }


def test_requirements_fixture_contains_real_query_input() -> None:
    """The pinned requirements fixture should parse as FastAPI."""

    dependencies = parse_requirements_file(
        _REQUIREMENTS_FIXTURE_PATH
    )

    assert len(dependencies) == 1
    assert dependencies[0].name == "fastapi"
    assert dependencies[0].version == "0.109.0"
    assert dependencies[0].operator == "=="
    assert dependencies[0].line_number == 1


def test_osv_fixture_parses_real_advisory_fields() -> None:
    """The official projection should use production parsing."""

    response = parse_osv_query_response(
        _load_fixture_payload()
    )

    assert len(response.vulnerabilities) == 1
    vulnerability = response.vulnerabilities[0]
    assert vulnerability.advisory_id == "PYSEC-2024-38"
    assert "CVE-2024-24762" in vulnerability.aliases
    assert vulnerability.affected[0].package.name == (
        "fastapi"
    )
    assert tuple(
        affected_range.range_type
        for affected_range in (
            vulnerability.affected[0].ranges
        )
    ) == ("GIT", "ECOSYSTEM")


def test_fixture_scan_queries_expected_package_once() -> None:
    """The orchestrator should issue one exact fixture query."""

    _, client = _scan_fixture()

    assert client.calls == [
        ("fastapi", "0.109.0", None)
    ]


def test_fixture_scan_creates_expected_real_finding() -> None:
    """All production mapping layers should preserve advisory data."""

    result, _ = _scan_fixture()

    assert result.succeeded
    assert len(result.dependencies) == 1
    assert len(result.findings) == 1
    assert result.errors == ()

    finding = result.findings[0]
    assert finding.advisory_id == "PYSEC-2024-38"
    assert "CVE-2024-24762" in finding.aliases
    assert finding.fixed_version == "0.109.1"
    assert finding.fixed_version != _GIT_FIXED_COMMIT
    assert finding.severity is VulnerabilitySeverity.HIGH
    assert "ReDoS" in finding.message


def test_fixture_text_report_contains_real_finding() -> None:
    """Text reporting should include the official advisory data."""

    result, _ = _scan_fixture()

    report = format_dependency_scan_text(result)

    assert "[HIGH] PYSEC-2024-38" in report
    assert "fastapi==0.109.0" in report
    assert "fixed=0.109.1" in report
    assert "CVE-2024-24762" in report
    assert _GIT_FIXED_COMMIT not in report


def test_fixture_json_report_contains_real_finding() -> None:
    """JSON reporting should include structured advisory data."""

    result, _ = _scan_fixture()

    payload = json.loads(
        format_dependency_scan_json(result)
    )
    finding = payload["findings"][0]

    assert finding["advisory_id"] == "PYSEC-2024-38"
    assert finding["fixed_version"] == "0.109.1"
    assert finding["severity"] == "high"
    assert "CVE-2024-24762" in finding["aliases"]
    assert payload["summary"] == {
        "dependencies": 1,
        "findings": 1,
        "errors": 0,
        "succeeded": True,
    }


@pytest.mark.parametrize(
    ("fail_on", "expected_exit_code"),
    [
        ("any", 1),
        ("high", 1),
        ("critical", 0),
    ],
)
def test_fixture_runner_applies_real_severity_threshold(
    fail_on: str,
    expected_exit_code: int,
) -> None:
    """CLI thresholds should use the fixture's CVSS severity."""

    factory = FixtureScannerFactory()
    stdout = io.StringIO()

    exit_code = run_cli(
        [
            str(_REQUIREMENTS_FIXTURE_PATH),
            "--fail-on",
            fail_on,
        ],
        scanner_factory=factory,
        stdout=stdout,
    )

    assert exit_code == expected_exit_code
    assert "PYSEC-2024-38" in stdout.getvalue()
    assert factory.calls == [("osv", 10.0)]
    assert factory.clients[0].calls == [
        ("fastapi", "0.109.0", None)
    ]


def test_fixture_runner_writes_json_output_file(
    tmp_path: Path,
) -> None:
    """The complete CLI path should write a structured report."""

    output_path = tmp_path / "fastapi-report.json"
    factory = FixtureScannerFactory()
    stdout = io.StringIO()

    exit_code = run_cli(
        [
            str(_REQUIREMENTS_FIXTURE_PATH),
            "--format",
            "json",
            "--output",
            str(output_path),
        ],
        scanner_factory=factory,
        stdout=stdout,
    )

    payload = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert payload["findings"][0][
        "advisory_id"
    ] == "PYSEC-2024-38"
    assert payload["findings"][0][
        "fixed_version"
    ] == "0.109.1"


def test_fixture_scan_does_not_modify_parsed_models() -> None:
    """The integrated scan should preserve dependency values."""

    result, _ = _scan_fixture()
    dependency = result.dependencies[0]
    before = dependency.to_dict()

    format_dependency_scan_text(result)
    format_dependency_scan_json(result)

    assert dependency.to_dict() == before


def test_fixture_integration_never_uses_live_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The integration suite must remain deterministic and offline."""

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

    result, _ = _scan_fixture()

    assert result.findings
