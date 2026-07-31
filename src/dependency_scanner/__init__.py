"""Public interface for dependency scanner components."""

from dependency_scanner.models import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    VulnerabilitySeverity,
)

__all__ = [
    "AdvisorySource",
    "Dependency",
    "DependencyFinding",
    "VulnerabilitySeverity",
]