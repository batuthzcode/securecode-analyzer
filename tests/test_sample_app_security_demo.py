"""Integration tests for the isolated sample-app security demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import sample_app

from dependency_scanner import (
    DependencyScanner,
    OsvQueryResponse,
    OsvVulnerabilitySource,
    VulnerabilitySeverity,
    parse_osv_query_response,
    parse_requirements_file,
)
from static_analyzer.default_factory import (
    create_default_analyzer,
)
from static_analyzer.formatters import (
    format_findings_json,
)


_REPOSITORY_ROOT = Path(__file__).parents[1]
_SAMPLE_APP_ROOT = _REPOSITORY_ROOT / "sample_app"
_RUNTIME_REQUIREMENTS = (
    _SAMPLE_APP_ROOT / "requirements.txt"
)
_VULNERABLE_REQUIREMENTS = (
    _SAMPLE_APP_ROOT / "requirements-vulnerable.txt"
)
_OSV_FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "osv"
    / "fastapi-0.109.0.json"
)
_DEMO_LITERAL = "demo-only-not-a-real-secret"
_EXPECTED_ANALYZER_FINDINGS = [
    ("SA005", "analyzer_demo.py", 8, 1, "warning"),
    ("SA001", "analyzer_demo.py", 11, 0, "warning"),
    ("SA006", "analyzer_demo.py", 11, 1, "info"),
    ("SA003", "analyzer_demo.py", 14, 7, "info"),
    ("SA004", "analyzer_demo.py", 54, 5, "warning"),
]


class FixtureOsvClient:
    """Return the checked-in OSV response without network access."""

    def __init__(self) -> None:
        """Load the deterministic OSV fixture."""

        payload = json.loads(
            _OSV_FIXTURE.read_text(encoding="utf-8")
        )
        self.response = parse_osv_query_response(
            payload
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
        """Record and answer one expected fixture query."""

        self.calls.append(
            (package_name, version, page_token)
        )

        if page_token is not None:
            raise AssertionError(
                "The fixture has no additional page."
            )

        return self.response


def test_analyzer_demo_produces_exact_findings() -> None:
    """The sample app should produce five deliberate findings only."""

    findings = create_default_analyzer().analyze(
        _SAMPLE_APP_ROOT
    )

    assert [
        (
            finding.rule_id,
            Path(finding.file_path).name,
            finding.line_number,
            finding.column_number,
            finding.severity.value,
        )
        for finding in findings
    ] == _EXPECTED_ANALYZER_FINDINGS

    report = format_findings_json(findings)
    assert _DEMO_LITERAL not in report
    assert '"total": 5' in report


def test_demo_module_is_not_loaded_by_sample_app() -> None:
    """Importing the application package must not execute demo code."""

    sample_app.create_app({"TESTING": True})

    assert "sample_app.analyzer_demo" not in sys.modules
    assert not hasattr(sample_app, "analyzer_demo")


def test_vulnerable_dependency_is_separate_from_runtime() -> None:
    """The affected FastAPI pin must remain demo-only."""

    runtime_dependencies = parse_requirements_file(
        _RUNTIME_REQUIREMENTS
    )
    demo_dependencies = parse_requirements_file(
        _VULNERABLE_REQUIREMENTS
    )

    assert [
        (
            dependency.name,
            dependency.version,
        )
        for dependency in runtime_dependencies
    ] == [("Flask", "3.1.3")]
    assert [
        (
            dependency.name,
            dependency.version,
            dependency.line_number,
        )
        for dependency in demo_dependencies
    ] == [("fastapi", "0.109.0", 6)]


def test_vulnerable_fixture_maps_official_advisory() -> None:
    """The demo pin should map to the checked-in real OSV finding."""

    client = FixtureOsvClient()
    scanner = DependencyScanner(
        OsvVulnerabilitySource(client)
    )

    result = scanner.scan_requirements(
        _VULNERABLE_REQUIREMENTS
    )

    assert result.succeeded
    assert result.errors == ()
    assert client.calls == [
        ("fastapi", "0.109.0", None)
    ]
    assert len(result.findings) == 1

    finding = result.findings[0]
    assert finding.advisory_id == "PYSEC-2024-38"
    assert "CVE-2024-24762" in finding.aliases
    assert finding.fixed_version == "0.109.1"
    assert finding.severity is VulnerabilitySeverity.HIGH
