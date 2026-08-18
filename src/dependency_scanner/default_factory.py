"""Create default dependency scanner components."""

from __future__ import annotations

from dependency_scanner.osv_client import OsvQueryClient
from dependency_scanner.osv_source import OsvVulnerabilitySource
from dependency_scanner.scanner import DependencyScanner


class DependencyScannerConfigurationError(ValueError):
    """Represent an unsupported scanner configuration."""


def create_default_dependency_scanner(
    *,
    source_name: str = "osv",
    timeout: float = 10.0,
) -> DependencyScanner:
    """Create a dependency scanner using configured OSV components."""

    if source_name != "osv":
        raise DependencyScannerConfigurationError(
            f"Unsupported vulnerability source: {source_name}"
        )

    client = OsvQueryClient(timeout=timeout)
    source = OsvVulnerabilitySource(client=client)

    return DependencyScanner(source=source)
