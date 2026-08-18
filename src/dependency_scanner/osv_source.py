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
    OsvQueryResponse,
    OsvVulnerability,
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
        severity=VulnerabilitySeverity.UNKNOWN,
        fixed_version=_find_fixed_version(
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
    vulnerability: OsvVulnerability,
) -> str | None:
    """Return the first fixed version in OSV range order."""

    for affected_package in vulnerability.affected:
        for affected_range in affected_package.ranges:
            for event in affected_range.events:
                if event.fixed is not None:
                    return event.fixed

    return None
