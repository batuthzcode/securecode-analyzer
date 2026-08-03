"""Public interface for dependency scanner components."""

from dependency_scanner.models import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    VulnerabilitySeverity,
)
from dependency_scanner.requirements_parser import (
    RequirementsParseError,
    parse_requirement_line,
    parse_requirements_file,
    parse_requirements_text,
)

__all__ = [
    "AdvisorySource",
    "Dependency",
    "DependencyFinding",
    "RequirementsParseError",
    "VulnerabilitySeverity",
    "parse_requirement_line",
    "parse_requirements_file",
    "parse_requirements_text",
]