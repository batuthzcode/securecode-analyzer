"""Immutable models representing OSV query responses."""

from __future__ import annotations

from dataclasses import (
    dataclass,
    fields,
    is_dataclass,
)
from typing import Any


def _validate_required_string(
    value: object,
    field_name: str,
) -> None:
    """Validate a required non-empty string."""

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be a string."
        )

    if not value.strip():
        raise ValueError(
            f"{field_name} must not be empty."
        )


def _validate_optional_string(
    value: object,
    field_name: str,
) -> None:
    """Validate an optional non-empty string."""

    if value is None:
        return

    _validate_required_string(
        value,
        field_name,
    )


def _validate_tuple(
    value: object,
    field_name: str,
) -> None:
    """Validate that a collection is a tuple."""

    if not isinstance(value, tuple):
        raise ValueError(
            f"{field_name} must be a tuple."
        )


def _validate_model_tuple(
    value: object,
    expected_type: type[object],
    field_name: str,
) -> None:
    """Validate a tuple containing one model type."""

    _validate_tuple(
        value,
        field_name,
    )

    for item in value:
        if not isinstance(
            item,
            expected_type,
        ):
            raise ValueError(
                f"{field_name} contains an invalid item."
            )


def _validate_string_tuple(
    value: object,
    field_name: str,
) -> None:
    """Validate a tuple containing non-empty strings."""

    _validate_tuple(
        value,
        field_name,
    )

    for item in value:
        _validate_required_string(
            item,
            f"{field_name} item",
        )


def _to_serializable(
    value: object,
) -> Any:
    """Convert nested OSV models into JSON-compatible data."""

    if is_dataclass(value):
        return {
            field_info.name: _to_serializable(
                getattr(
                    value,
                    field_info.name,
                )
            )
            for field_info in fields(value)
        }

    if isinstance(value, tuple):
        return [
            _to_serializable(item)
            for item in value
        ]

    return value


class _SerializableModel:
    """Provide recursive dictionary conversion."""

    __slots__ = ()

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-compatible model data."""

        data = _to_serializable(self)

        if not isinstance(data, dict):
            raise TypeError(
                "Model data must be a dictionary."
            )

        return data


@dataclass(frozen=True, slots=True)
class OsvSeverity(_SerializableModel):
    """Represent one OSV severity record."""

    severity_type: str
    score: str

    def __post_init__(self) -> None:
        """Validate severity fields."""

        _validate_required_string(
            self.severity_type,
            "severity_type",
        )
        _validate_required_string(
            self.score,
            "score",
        )


@dataclass(frozen=True, slots=True)
class OsvRangeEvent(_SerializableModel):
    """Represent one event inside an OSV range."""

    introduced: str | None = None
    fixed: str | None = None
    last_affected: str | None = None
    limit: str | None = None

    def __post_init__(self) -> None:
        """Validate optional range-event fields."""

        _validate_optional_string(
            self.introduced,
            "introduced",
        )
        _validate_optional_string(
            self.fixed,
            "fixed",
        )
        _validate_optional_string(
            self.last_affected,
            "last_affected",
        )
        _validate_optional_string(
            self.limit,
            "limit",
        )


@dataclass(frozen=True, slots=True)
class OsvRange(_SerializableModel):
    """Represent one OSV affected-version range."""

    range_type: str
    events: tuple[OsvRangeEvent, ...]

    def __post_init__(self) -> None:
        """Validate range fields."""

        _validate_required_string(
            self.range_type,
            "range_type",
        )
        _validate_model_tuple(
            self.events,
            OsvRangeEvent,
            "events",
        )


@dataclass(frozen=True, slots=True)
class OsvPackage(_SerializableModel):
    """Represent package information from OSV."""

    ecosystem: str
    name: str

    def __post_init__(self) -> None:
        """Validate package fields."""

        _validate_required_string(
            self.ecosystem,
            "ecosystem",
        )
        _validate_required_string(
            self.name,
            "name",
        )


@dataclass(frozen=True, slots=True)
class OsvAffectedPackage(_SerializableModel):
    """Represent one affected package from OSV."""

    package: OsvPackage
    ranges: tuple[OsvRange, ...] = ()
    versions: tuple[str, ...] = ()
    severity: tuple[OsvSeverity, ...] = ()

    def __post_init__(self) -> None:
        """Validate affected-package fields."""

        if not isinstance(
            self.package,
            OsvPackage,
        ):
            raise ValueError(
                "package must be an OsvPackage."
            )

        _validate_model_tuple(
            self.ranges,
            OsvRange,
            "ranges",
        )
        _validate_string_tuple(
            self.versions,
            "versions",
        )
        _validate_model_tuple(
            self.severity,
            OsvSeverity,
            "severity",
        )


@dataclass(frozen=True, slots=True)
class OsvVulnerability(_SerializableModel):
    """Represent one vulnerability returned by OSV."""

    advisory_id: str
    summary: str | None = None
    details: str | None = None
    aliases: tuple[str, ...] = ()
    severity: tuple[OsvSeverity, ...] = ()
    affected: tuple[OsvAffectedPackage, ...] = ()

    def __post_init__(self) -> None:
        """Validate vulnerability fields."""

        _validate_required_string(
            self.advisory_id,
            "advisory_id",
        )
        _validate_optional_string(
            self.summary,
            "summary",
        )
        _validate_optional_string(
            self.details,
            "details",
        )
        _validate_string_tuple(
            self.aliases,
            "aliases",
        )
        _validate_model_tuple(
            self.severity,
            OsvSeverity,
            "severity",
        )
        _validate_model_tuple(
            self.affected,
            OsvAffectedPackage,
            "affected",
        )


@dataclass(frozen=True, slots=True)
class OsvQueryResponse(_SerializableModel):
    """Represent one OSV query response."""

    vulnerabilities: tuple[
        OsvVulnerability,
        ...
    ] = ()
    next_page_token: str | None = None

    def __post_init__(self) -> None:
        """Validate query-response fields."""

        _validate_model_tuple(
            self.vulnerabilities,
            OsvVulnerability,
            "vulnerabilities",
        )
        _validate_optional_string(
            self.next_page_token,
            "next_page_token",
        )