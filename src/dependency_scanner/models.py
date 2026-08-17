"""Shared data models used by the dependency scanner."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


_SUPPORTED_OPERATORS = frozenset({"=="})


def _clean_required_text(
    value: str,
    field_name: str,
) -> str:
    """Return a stripped, non-empty string value."""

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be a string."
        )

    cleaned_value = value.strip()

    if not cleaned_value:
        raise ValueError(
            f"{field_name} must not be empty."
        )

    return cleaned_value


def _clean_optional_text(
    value: str | None,
    field_name: str,
) -> str | None:
    """Return a stripped optional string value."""

    if value is None:
        return None

    return _clean_required_text(
        value,
        field_name,
    )


def _clean_aliases(
    aliases: tuple[str, ...],
) -> tuple[str, ...]:
    """Validate and clean advisory aliases."""

    if not isinstance(aliases, tuple):
        raise ValueError(
            "aliases must be a tuple."
        )

    return tuple(
        _clean_required_text(
            alias,
            "alias",
        )
        for alias in aliases
    )


def _validate_operator(operator: str) -> None:
    """Validate a dependency version operator."""

    if operator not in _SUPPORTED_OPERATORS:
        raise ValueError(
            f"Unsupported dependency operator: "
            f"{operator}"
        )


def _validate_line_number(line_number: int) -> None:
    """Validate a dependency source line number."""

    if type(line_number) is not int or line_number <= 0:
        raise ValueError(
            "line_number must be a positive integer."
        )


def _clean_dependency_fields(
    name: str,
    version: str,
    operator: str,
    source_file: str,
    line_number: int,
) -> tuple[str, str, str, str]:
    """Validate and clean dependency fields."""

    cleaned_name = _clean_required_text(
        name,
        "name",
    )
    cleaned_version = _clean_required_text(
        version,
        "version",
    )
    cleaned_operator = _clean_required_text(
        operator,
        "operator",
    )
    cleaned_source_file = _clean_required_text(
        source_file,
        "source_file",
    )

    _validate_operator(cleaned_operator)
    _validate_line_number(line_number)

    return (
        cleaned_name,
        cleaned_version,
        cleaned_operator,
        cleaned_source_file,
    )


class VulnerabilitySeverity(str, Enum):
    """Represent supported vulnerability severity levels."""

    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class Dependency:
    """Represent one pinned Python project dependency."""

    name: str
    version: str
    operator: str
    source_file: str
    line_number: int

    def __post_init__(self) -> None:
        """Validate and normalize dependency fields."""

        (
            name,
            version,
            operator,
            source_file,
        ) = _clean_dependency_fields(
            self.name,
            self.version,
            self.operator,
            self.source_file,
            self.line_number,
        )

        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "operator", operator)
        object.__setattr__(
            self,
            "source_file",
            source_file,
        )

    def to_dict(self) -> dict[str, object]:
        """Convert the dependency into JSON-compatible data."""

        return {
            "name": self.name,
            "version": self.version,
            "operator": self.operator,
            "source_file": self.source_file,
            "line_number": self.line_number,
        }


@dataclass(frozen=True, slots=True)
class AdvisorySource:
    """Represent the source of vulnerability information."""

    name: str
    url: str | None = None

    def __post_init__(self) -> None:
        """Validate and normalize advisory source fields."""

        name = _clean_required_text(
            self.name,
            "name",
        )
        url = _clean_optional_text(
            self.url,
            "url",
        )

        object.__setattr__(self, "name", name)
        object.__setattr__(self, "url", url)

    def to_dict(self) -> dict[str, object]:
        """Convert the source into JSON-compatible data."""

        return {
            "name": self.name,
            "url": self.url,
        }


def _validate_finding_models(
    dependency: object,
    source: object,
    severity: object,
) -> None:
    """Validate nested dependency finding values."""

    if not isinstance(dependency, Dependency):
        raise ValueError(
            "dependency must be a Dependency instance."
        )

    if not isinstance(source, AdvisorySource):
        raise ValueError(
            "source must be an AdvisorySource instance."
        )

    if not isinstance(
        severity,
        VulnerabilitySeverity,
    ):
        raise ValueError(
            "severity must be a "
            "VulnerabilitySeverity value."
        )


def _clean_finding_fields(
    advisory_id: str,
    message: str,
    fixed_version: str | None,
    aliases: tuple[str, ...],
) -> tuple[
    str,
    str,
    str | None,
    tuple[str, ...],
]:
    """Validate and clean dependency finding fields."""

    return (
        _clean_required_text(
            advisory_id,
            "advisory_id",
        ),
        _clean_required_text(
            message,
            "message",
        ),
        _clean_optional_text(
            fixed_version,
            "fixed_version",
        ),
        _clean_aliases(aliases),
    )


@dataclass(frozen=True, slots=True)
class DependencyFinding:
    """Represent a vulnerability affecting one dependency."""

    dependency: Dependency
    advisory_id: str
    message: str
    source: AdvisorySource
    severity: VulnerabilitySeverity = (
        VulnerabilitySeverity.UNKNOWN
    )
    fixed_version: str | None = None
    aliases: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        """Validate and normalize finding fields."""

        _validate_finding_models(
            self.dependency,
            self.source,
            self.severity,
        )

        (
            advisory_id,
            message,
            fixed_version,
            aliases,
        ) = _clean_finding_fields(
            self.advisory_id,
            self.message,
            self.fixed_version,
            self.aliases,
        )

        object.__setattr__(
            self,
            "advisory_id",
            advisory_id,
        )
        object.__setattr__(self, "message", message)
        object.__setattr__(
            self,
            "fixed_version",
            fixed_version,
        )
        object.__setattr__(self, "aliases", aliases)

    def to_dict(self) -> dict[str, object]:
        """Convert the finding into JSON-compatible data."""

        return {
            "dependency": self.dependency.to_dict(),
            "advisory_id": self.advisory_id,
            "message": self.message,
            "source": self.source.to_dict(),
            "severity": self.severity.value,
            "fixed_version": self.fixed_version,
            "aliases": list(self.aliases),
        }