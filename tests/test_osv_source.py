"""Tests for the OSV vulnerability source."""

from __future__ import annotations

import dependency_scanner
import pytest

from dependency_scanner import (
    AdvisorySource,
    Dependency,
    OsvAffectedPackage,
    OsvPackage,
    OsvQueryError,
    OsvQueryResponse,
    OsvRange,
    OsvRangeEvent,
    OsvSeverity,
    OsvVulnerability,
    OsvVulnerabilitySource,
    VulnerabilitySeverity,
    VulnerabilitySource,
)


def create_dependency() -> Dependency:
    """Create a dependency used by source tests."""

    return Dependency(
        name="Sample_Package",
        version="1.0.0",
        operator="==",
        source_file="requirements.txt",
        line_number=2,
    )


def create_affected_package(
    *events: OsvRangeEvent,
    package_name: str = "sample-package",
    ecosystem: str = "PyPI",
    severity: tuple[OsvSeverity, ...] = (),
) -> OsvAffectedPackage:
    """Create affected package data with one range."""

    return OsvAffectedPackage(
        package=OsvPackage(
            ecosystem=ecosystem,
            name=package_name,
        ),
        ranges=(
            OsvRange(
                range_type="ECOSYSTEM",
                events=events,
            ),
        ),
        severity=severity,
    )


def create_vulnerability(
    advisory_id: str = "OSV-EXAMPLE-1",
    summary: str | None = "Example vulnerability",
    details: str | None = "Example details",
    aliases: tuple[str, ...] = (
        "CVE-2099-0001",
    ),
    affected: tuple[OsvAffectedPackage, ...] = (),
    severity: tuple[OsvSeverity, ...] = (),
) -> OsvVulnerability:
    """Create an OSV vulnerability used by source tests."""

    return OsvVulnerability(
        advisory_id=advisory_id,
        summary=summary,
        details=details,
        aliases=aliases,
        affected=affected,
        severity=severity,
    )


class FakeOsvQueryClient:
    """Return configured OSV pages without network access."""

    def __init__(
        self,
        *responses: OsvQueryResponse,
    ) -> None:
        """Store response pages in query order."""

        self._responses = list(responses)
        self.calls: list[
            tuple[str, str, str | None]
        ] = []

    def query_package(
        self,
        package_name: str,
        version: str,
        page_token: str | None = None,
    ) -> OsvQueryResponse:
        """Record a query and return its configured response."""

        self.calls.append(
            (
                package_name,
                version,
                page_token,
            )
        )

        if not self._responses:
            raise AssertionError(
                "Unexpected OSV query."
            )

        return self._responses.pop(0)


class FailingOsvQueryClient:
    """Raise one configured OSV query error."""

    def __init__(
        self,
        error: OsvQueryError,
    ) -> None:
        """Store the error raised by every query."""

        self._error = error

    def query_package(
        self,
        package_name: str,
        version: str,
        page_token: str | None = None,
    ) -> OsvQueryResponse:
        """Raise the configured query error."""

        raise self._error


def test_source_satisfies_vulnerability_source_protocol() -> None:
    """The OSV source implements the common source protocol."""

    source = OsvVulnerabilitySource(
        FakeOsvQueryClient()
    )

    assert isinstance(
        source,
        VulnerabilitySource,
    )


def test_source_is_available_through_package_api() -> None:
    """The OSV source is publicly exported."""

    assert (
        dependency_scanner.OsvVulnerabilitySource
        is OsvVulnerabilitySource
    )


def test_source_exposes_osv_advisory_information() -> None:
    """The source identifies OSV with its public URL."""

    source = OsvVulnerabilitySource(
        FakeOsvQueryClient()
    )

    assert source.advisory_source == AdvisorySource(
        name="OSV",
        url="https://osv.dev/",
    )


def test_empty_response_returns_empty_tuple() -> None:
    """A response without vulnerabilities creates no findings."""

    client = FakeOsvQueryClient(
        OsvQueryResponse()
    )
    source = OsvVulnerabilitySource(client)

    findings = source.find_vulnerabilities(
        create_dependency()
    )

    assert findings == ()
    assert client.calls == [
        (
            "Sample_Package",
            "1.0.0",
            None,
        ),
    ]


def test_vulnerability_is_converted_to_finding() -> None:
    """OSV fields are mapped onto one dependency finding."""

    dependency = create_dependency()
    vulnerability = create_vulnerability(
        affected=(
            create_affected_package(
                OsvRangeEvent(
                    introduced="0",
                ),
                OsvRangeEvent(
                    fixed="2.0.0",
                ),
            ),
        ),
    )
    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(
                    vulnerability,
                ),
            )
        )
    )

    findings = source.find_vulnerabilities(
        dependency
    )

    assert len(findings) == 1
    finding = findings[0]
    assert finding.dependency is dependency
    assert finding.advisory_id == "OSV-EXAMPLE-1"
    assert finding.message == "Example vulnerability"
    assert finding.source == AdvisorySource(
        name="OSV",
        url="https://osv.dev/",
    )
    assert (
        finding.severity
        is VulnerabilitySeverity.UNKNOWN
    )
    assert finding.fixed_version == "2.0.0"
    assert finding.aliases == (
        "CVE-2099-0001",
    )


def test_multiple_vulnerabilities_preserve_order() -> None:
    """Findings retain OSV vulnerability order."""

    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(
                    create_vulnerability(
                        "OSV-EXAMPLE-2"
                    ),
                    create_vulnerability(
                        "OSV-EXAMPLE-1"
                    ),
                ),
            )
        )
    )

    findings = source.find_vulnerabilities(
        create_dependency()
    )

    assert [
        finding.advisory_id
        for finding in findings
    ] == [
        "OSV-EXAMPLE-2",
        "OSV-EXAMPLE-1",
    ]


def test_summary_is_preferred_over_details() -> None:
    """A vulnerability summary is used as its message."""

    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(
                    create_vulnerability(
                        summary="Summary message",
                        details="Details message",
                    ),
                ),
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert finding.message == "Summary message"


def test_details_are_used_when_summary_is_missing() -> None:
    """Vulnerability details provide the message fallback."""

    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(
                    create_vulnerability(
                        summary=None,
                        details="Details message",
                    ),
                ),
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert finding.message == "Details message"


def test_default_message_contains_advisory_id() -> None:
    """The final message fallback identifies the advisory."""

    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(
                    create_vulnerability(
                        advisory_id="OSV-NO-MESSAGE",
                        summary=None,
                        details=None,
                    ),
                ),
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert "OSV-NO-MESSAGE" in finding.message


def test_first_fixed_range_event_is_used() -> None:
    """The first fixed event in nested OSV order wins."""

    vulnerability = create_vulnerability(
        affected=(
            create_affected_package(
                OsvRangeEvent(
                    introduced="0",
                ),
                OsvRangeEvent(
                    fixed="2.0.0",
                ),
                OsvRangeEvent(
                    fixed="3.0.0",
                ),
            ),
            create_affected_package(
                OsvRangeEvent(
                    fixed="4.0.0",
                ),
            ),
        ),
    )
    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(
                    vulnerability,
                ),
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert finding.fixed_version == "2.0.0"


def test_missing_fixed_event_returns_none() -> None:
    """A vulnerability without a fix keeps a missing version."""

    vulnerability = create_vulnerability(
        affected=(
            create_affected_package(
                OsvRangeEvent(
                    introduced="0",
                ),
                OsvRangeEvent(
                    last_affected="1.0.0",
                ),
            ),
        ),
    )
    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(
                    vulnerability,
                ),
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert finding.fixed_version is None


def test_pagination_combines_all_response_pages() -> None:
    """All paginated findings are returned in one tuple."""

    client = FakeOsvQueryClient(
        OsvQueryResponse(
            vulnerabilities=(
                create_vulnerability(
                    "OSV-PAGE-1"
                ),
            ),
            next_page_token="page-2",
        ),
        OsvQueryResponse(
            vulnerabilities=(
                create_vulnerability(
                    "OSV-PAGE-2"
                ),
            ),
        ),
    )
    source = OsvVulnerabilitySource(client)

    findings = source.find_vulnerabilities(
        create_dependency()
    )

    assert tuple(
        finding.advisory_id
        for finding in findings
    ) == (
        "OSV-PAGE-1",
        "OSV-PAGE-2",
    )
    assert client.calls == [
        (
            "Sample_Package",
            "1.0.0",
            None,
        ),
        (
            "Sample_Package",
            "1.0.0",
            "page-2",
        ),
    ]


def test_query_error_is_propagated_unchanged() -> None:
    """The source does not hide client query errors."""

    error = OsvQueryError(
        "OSV is unavailable."
    )
    source = OsvVulnerabilitySource(
        FailingOsvQueryClient(error)
    )

    with pytest.raises(OsvQueryError) as raised:
        source.find_vulnerabilities(
            create_dependency()
        )

    assert raised.value is error


def test_lookup_preserves_dependency_data() -> None:
    """Finding creation does not mutate its dependency."""

    dependency = create_dependency()
    original_data = dependency.to_dict()
    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(
                    create_vulnerability(),
                ),
            )
        )
    )

    source.find_vulnerabilities(dependency)

    assert dependency.to_dict() == original_data


def test_vulnerability_level_cvss_v3_sets_severity() -> None:
    """A top-level CVSS v3 vector determines finding severity."""

    vulnerability = create_vulnerability(
        severity=(
            OsvSeverity(
                severity_type="CVSS_V3",
                score=(
                    "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/"
                    "S:U/C:H/I:H/A:H"
                ),
            ),
        )
    )
    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(vulnerability,)
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert (
        finding.severity
        is VulnerabilitySeverity.CRITICAL
    )


def test_matching_package_severity_has_priority() -> None:
    """Package-specific severity overrides top-level data."""

    low_severity = OsvSeverity(
        severity_type="CVSS_V3",
        score=(
            "CVSS:3.1/AV:P/AC:H/PR:H/UI:R/"
            "S:U/C:L/I:N/A:N"
        ),
    )
    critical_severity = OsvSeverity(
        severity_type="CVSS_V3",
        score=(
            "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/"
            "S:U/C:H/I:H/A:H"
        ),
    )
    vulnerability = create_vulnerability(
        affected=(
            create_affected_package(
                severity=(low_severity,)
            ),
        ),
        severity=(critical_severity,),
    )
    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(vulnerability,)
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert finding.severity is VulnerabilitySeverity.LOW


@pytest.mark.parametrize(
    ("package_name", "ecosystem"),
    [
        ("another-package", "PyPI"),
        ("sample-package", "npm"),
    ],
)
def test_unrelated_package_severity_is_ignored(
    package_name: str,
    ecosystem: str,
) -> None:
    """Package-level data must match the queried PyPI package."""

    vulnerability = create_vulnerability(
        affected=(
            create_affected_package(
                package_name=package_name,
                ecosystem=ecosystem,
                severity=(
                    OsvSeverity(
                        severity_type="CVSS_V3",
                        score=(
                            "CVSS:3.1/AV:P/AC:H/PR:H/"
                            "UI:R/S:U/C:L/I:N/A:N"
                        ),
                    ),
                ),
            ),
        ),
        severity=(
            OsvSeverity(
                severity_type="CVSS_V3",
                score=(
                    "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/"
                    "S:U/C:H/I:H/A:H"
                ),
            ),
        ),
    )
    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(vulnerability,)
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert (
        finding.severity
        is VulnerabilitySeverity.CRITICAL
    )


def test_highest_valid_cvss_v3_score_is_used() -> None:
    """Multiple assessments use the most conservative score."""

    vulnerability = create_vulnerability(
        severity=(
            OsvSeverity(
                severity_type="CVSS_V3",
                score=(
                    "CVSS:3.1/AV:P/AC:H/PR:H/UI:R/"
                    "S:U/C:L/I:N/A:N"
                ),
            ),
            OsvSeverity(
                severity_type="CVSS_V3",
                score="invalid-vector",
            ),
            OsvSeverity(
                severity_type="CVSS_V3",
                score=(
                    "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/"
                    "S:U/C:H/I:N/A:N"
                ),
            ),
        )
    )
    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(vulnerability,)
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert finding.severity is VulnerabilitySeverity.HIGH


@pytest.mark.parametrize(
    "severity",
    [
        OsvSeverity(
            severity_type="CVSS_V3",
            score="invalid-vector",
        ),
        OsvSeverity(
            severity_type="CVSS_V2",
            score="AV:N/AC:L/Au:N/C:C/I:C/A:C",
        ),
        OsvSeverity(
            severity_type="CVSS_V4",
            score=(
                "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/"
                "VC:H/VI:H/VA:H/SC:N/SI:N/SA:N"
            ),
        ),
        OsvSeverity(
            severity_type="Ubuntu",
            score="high",
        ),
    ],
)
def test_unsupported_or_invalid_severity_is_unknown(
    severity: OsvSeverity,
) -> None:
    """Unsupported assessments keep the safe unknown fallback."""

    vulnerability = create_vulnerability(
        severity=(severity,)
    )
    source = OsvVulnerabilitySource(
        FakeOsvQueryClient(
            OsvQueryResponse(
                vulnerabilities=(vulnerability,)
            )
        )
    )

    finding = source.find_vulnerabilities(
        create_dependency()
    )[0]

    assert (
        finding.severity
        is VulnerabilitySeverity.UNKNOWN
    )
