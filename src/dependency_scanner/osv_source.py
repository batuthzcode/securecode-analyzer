"""Map OSV query responses to dependency vulnerability findings."""

from __future__ import annotations

from typing import Protocol

from dependency_scanner.models import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    VulnerabilitySeverity,
)
from dependency_scanner.osv_client import OsvQueryClient
from dependency_scanner.osv_models import (
    OsvAffectedPackage,
    OsvQueryResponse,
    OsvSeverity,
    OsvVulnerability,
)
from dependency_scanner.osv_severity import (
    CvssV3VectorError,
    calculate_cvss_v3_base_score,
    classify_cvss_score,
)
from dependency_scanner.package_normalizer import (
    normalize_package_name,
)


_OSV_ADVISORY_SOURCE = AdvisorySource(
    name="OSV",
    url="https://osv.dev/",
)


class _QueryClient(Protocol):
    """Describe the OSV query behavior used by the source."""

    def query_package(
        self,
        package_name: str,
        version: str,
        page_token: str | None = None,
    ) -> OsvQueryResponse:
        """Return one OSV result page."""

        ...


class OsvVulnerabilitySource:
    """Create dependency findings from OSV query results."""

    def __init__(
        self,
        client: _QueryClient | None = None,
    ) -> None:
        """Create a source backed by an OSV query client."""

        if client is None:
            client = OsvQueryClient()

        self._client = client

    @property
    def advisory_source(self) -> AdvisorySource:
        """Return identifying information for OSV."""

        return _OSV_ADVISORY_SOURCE

    def find_vulnerabilities(
        self,
        dependency: Dependency,
    ) -> tuple[DependencyFinding, ...]:
        """Return all OSV findings for one dependency."""

        findings: list[DependencyFinding] = []
        page_token: str | None = None

        while True:
            response = self._client.query_package(
                dependency.name,
                dependency.version,
                page_token=page_token,
            )

            findings.extend(
                _create_finding(
                    dependency,
                    vulnerability,
                )
                for vulnerability in (
                    response.vulnerabilities
                )
            )

            page_token = response.next_page_token

            if page_token is None:
                return tuple(findings)


def _create_finding(
    dependency: Dependency,
    vulnerability: OsvVulnerability,
) -> DependencyFinding:
    """Convert one OSV vulnerability into a finding."""

    return DependencyFinding(
        dependency=dependency,
        advisory_id=vulnerability.advisory_id,
        message=_select_message(vulnerability),
        source=_OSV_ADVISORY_SOURCE,
        severity=_find_severity(
            dependency,
            vulnerability,
        ),
        fixed_version=_find_fixed_version(
            dependency,
            vulnerability
        ),
        aliases=vulnerability.aliases,
    )


def _select_message(
    vulnerability: OsvVulnerability,
) -> str:
    """Select the best available vulnerability message."""

    if vulnerability.summary is not None:
        return vulnerability.summary

    if vulnerability.details is not None:
        return vulnerability.details

    return (
        "Dependency is affected by OSV advisory "
        f"{vulnerability.advisory_id}."
    )


def _find_fixed_version(
    dependency: Dependency,
    vulnerability: OsvVulnerability,
) -> str | None:
    """Return the first matching PyPI ecosystem fix."""

    for affected_package in vulnerability.affected:
        if not _is_matching_pypi_package(
            dependency,
            affected_package,
        ):
            continue

        for affected_range in affected_package.ranges:
            if affected_range.range_type != "ECOSYSTEM":
                continue

            for event in affected_range.events:
                if event.fixed is not None:
                    return event.fixed

    return None


def _find_severity(
    dependency: Dependency,
    vulnerability: OsvVulnerability,
) -> VulnerabilitySeverity:
    """Return the highest valid relevant CVSS v3 severity."""

    scores: list[float] = []

    for severity in _select_severity_records(
        dependency,
        vulnerability,
    ):
        if severity.severity_type != "CVSS_V3":
            continue

        try:
            score = calculate_cvss_v3_base_score(
                severity.score
            )
        except CvssV3VectorError:
            continue

        scores.append(score)

    if not scores:
        return VulnerabilitySeverity.UNKNOWN

    return classify_cvss_score(max(scores))


def _select_severity_records(
    dependency: Dependency,
    vulnerability: OsvVulnerability,
) -> tuple[OsvSeverity, ...]:
    """Select package-specific or vulnerability-wide severity data."""

    dependency_name = normalize_package_name(
        dependency.name
    )
    package_severity: list[OsvSeverity] = []

    for affected_package in vulnerability.affected:
        if not _is_matching_pypi_package(
            dependency,
            affected_package,
            normalized_dependency_name=(
                dependency_name
            ),
        ):
            continue

        package_severity.extend(
            affected_package.severity
        )

    if package_severity:
        return tuple(package_severity)

    return vulnerability.severity


def _is_matching_pypi_package(
    dependency: Dependency,
    affected_package: OsvAffectedPackage,
    *,
    normalized_dependency_name: str | None = None,
) -> bool:
    """Return whether affected data matches the scanned PyPI package."""

    package = affected_package.package

    if package.ecosystem != "PyPI":
        return False

    if normalized_dependency_name is None:
        normalized_dependency_name = (
            normalize_package_name(dependency.name)
        )

    return (
        normalize_package_name(package.name)
        == normalized_dependency_name
    )
