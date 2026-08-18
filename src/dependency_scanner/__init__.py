"""Public interface for dependency scanner components."""

from dependency_scanner.models import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    VulnerabilitySeverity,
)
from dependency_scanner.osv_client import (
    OsvQueryClient,
    OsvQueryError,
)
from dependency_scanner.osv_models import (
    OsvAffectedPackage,
    OsvPackage,
    OsvQueryResponse,
    OsvRange,
    OsvRangeEvent,
    OsvSeverity,
    OsvVulnerability,
)
from dependency_scanner.osv_parser import (
    OsvResponseParseError,
    parse_osv_query_response,
)
from dependency_scanner.osv_severity import (
    CvssV3VectorError,
    calculate_cvss_v3_base_score,
    classify_cvss_score,
)
from dependency_scanner.osv_source import (
    OsvVulnerabilitySource,
)
from dependency_scanner.package_normalizer import (
    normalize_package_name,
)
from dependency_scanner.requirements_parser import (
    RequirementsParseError,
    parse_requirement_line,
    parse_requirements_file,
    parse_requirements_text,
)
from dependency_scanner.scanner import (
    DependencyScanError,
    DependencyScanner,
    DependencyScanResult,
)
from dependency_scanner.vulnerability_source import (
    VulnerabilitySource,
    VulnerabilitySourceError,
)

__all__ = [
    "AdvisorySource",
    "CvssV3VectorError",
    "Dependency",
    "DependencyFinding",
    "DependencyScanError",
    "DependencyScanner",
    "DependencyScanResult",
    "OsvAffectedPackage",
    "OsvPackage",
    "OsvQueryClient",
    "OsvQueryError",
    "OsvQueryResponse",
    "OsvRange",
    "OsvRangeEvent",
    "OsvResponseParseError",
    "OsvSeverity",
    "OsvVulnerability",
    "OsvVulnerabilitySource",
    "RequirementsParseError",
    "VulnerabilitySeverity",
    "VulnerabilitySource",
    "VulnerabilitySourceError",
    "calculate_cvss_v3_base_score",
    "classify_cvss_score",
    "normalize_package_name",
    "parse_osv_query_response",
    "parse_requirement_line",
    "parse_requirements_file",
    "parse_requirements_text",
]
