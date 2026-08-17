"""Parse decoded OSV payloads into response models."""

from collections.abc import Callable
from typing import NoReturn, TypeVar

from dependency_scanner.osv_models import (
    OsvAffectedPackage,
    OsvPackage,
    OsvQueryResponse,
    OsvRange,
    OsvRangeEvent,
    OsvSeverity,
    OsvVulnerability,
)


ParsedItem = TypeVar("ParsedItem")


class OsvResponseParseError(ValueError):
    """Represent invalid data in an OSV response payload."""


def _fail(
    path: str,
    message: str,
) -> NoReturn:
    """Raise a parse error containing the invalid field path."""

    raise OsvResponseParseError(
        f"{path}: {message}"
    )


def _expect_dictionary(
    value: object,
    path: str,
) -> dict[str, object]:
    """Require a dictionary value."""

    if not isinstance(value, dict):
        _fail(
            path,
            "must be a dictionary.",
        )

    return value


def _expect_list(
    value: object,
    path: str,
) -> list[object]:
    """Require a list value."""

    if not isinstance(value, list):
        _fail(
            path,
            "must be a list.",
        )

    return value


def _required_value(
    data: dict[str, object],
    field_name: str,
    path: str,
) -> object:
    """Return a required dictionary value."""

    field_path = f"{path}.{field_name}"

    if field_name not in data:
        _fail(
            field_path,
            "required field is missing.",
        )

    return data[field_name]


def _required_string_value(
    value: object,
    path: str,
) -> str:
    """Require a non-empty string value."""

    if not isinstance(value, str):
        _fail(
            path,
            "must be a string.",
        )

    if not value.strip():
        _fail(
            path,
            "must not be empty.",
        )

    return value


def _required_string_field(
    data: dict[str, object],
    field_name: str,
    path: str,
) -> str:
    """Return a required non-empty string field."""

    value = _required_value(
        data,
        field_name,
        path,
    )

    return _required_string_value(
        value,
        f"{path}.{field_name}",
    )


def _optional_string_field(
    data: dict[str, object],
    field_name: str,
    path: str,
) -> str | None:
    """Return an optional string field."""

    if field_name not in data:
        return None

    value = data[field_name]

    if value is None:
        return None

    return _required_string_value(
        value,
        f"{path}.{field_name}",
    )


def _create_model(
    constructor: Callable[..., ParsedItem],
    path: str,
    **values: object,
) -> ParsedItem:
    """Create a model and translate validation errors."""

    try:
        return constructor(**values)
    except ValueError as error:
        raise OsvResponseParseError(
            f"{path}: {error}"
        ) from error


def _parse_object_collection(
    data: dict[str, object],
    field_name: str,
    path: str,
    parser: Callable[
        [object, str],
        ParsedItem,
    ],
) -> tuple[ParsedItem, ...]:
    """Parse an optional list of nested records."""

    collection_path = f"{path}.{field_name}"

    if field_name not in data:
        return ()

    items = _expect_list(
        data[field_name],
        collection_path,
    )

    return tuple(
        parser(
            item,
            f"{collection_path}[{index}]",
        )
        for index, item in enumerate(items)
    )


def _parse_string_collection(
    data: dict[str, object],
    field_name: str,
    path: str,
) -> tuple[str, ...]:
    """Parse an optional list of non-empty strings."""

    collection_path = f"{path}.{field_name}"

    if field_name not in data:
        return ()

    items = _expect_list(
        data[field_name],
        collection_path,
    )

    return tuple(
        _required_string_value(
            item,
            f"{collection_path}[{index}]",
        )
        for index, item in enumerate(items)
    )


def _parse_severity(
    value: object,
    path: str,
) -> OsvSeverity:
    """Parse one OSV severity record."""

    data = _expect_dictionary(
        value,
        path,
    )

    return _create_model(
        OsvSeverity,
        path,
        severity_type=_required_string_field(
            data,
            "type",
            path,
        ),
        score=_required_string_field(
            data,
            "score",
            path,
        ),
    )


def _parse_range_event(
    value: object,
    path: str,
) -> OsvRangeEvent:
    """Parse one OSV range event."""

    data = _expect_dictionary(
        value,
        path,
    )

    return _create_model(
        OsvRangeEvent,
        path,
        introduced=_optional_string_field(
            data,
            "introduced",
            path,
        ),
        fixed=_optional_string_field(
            data,
            "fixed",
            path,
        ),
        last_affected=_optional_string_field(
            data,
            "last_affected",
            path,
        ),
        limit=_optional_string_field(
            data,
            "limit",
            path,
        ),
    )


def _parse_range(
    value: object,
    path: str,
) -> OsvRange:
    """Parse one OSV affected-version range."""

    data = _expect_dictionary(
        value,
        path,
    )

    return _create_model(
        OsvRange,
        path,
        range_type=_required_string_field(
            data,
            "type",
            path,
        ),
        events=_parse_object_collection(
            data,
            "events",
            path,
            _parse_range_event,
        ),
    )


def _parse_package(
    value: object,
    path: str,
) -> OsvPackage:
    """Parse one OSV package record."""

    data = _expect_dictionary(
        value,
        path,
    )

    return _create_model(
        OsvPackage,
        path,
        ecosystem=_required_string_field(
            data,
            "ecosystem",
            path,
        ),
        name=_required_string_field(
            data,
            "name",
            path,
        ),
    )


def _parse_affected_package(
    value: object,
    path: str,
) -> OsvAffectedPackage:
    """Parse one affected package record."""

    data = _expect_dictionary(
        value,
        path,
    )

    package_value = _required_value(
        data,
        "package",
        path,
    )

    return _create_model(
        OsvAffectedPackage,
        path,
        package=_parse_package(
            package_value,
            f"{path}.package",
        ),
        ranges=_parse_object_collection(
            data,
            "ranges",
            path,
            _parse_range,
        ),
        versions=_parse_string_collection(
            data,
            "versions",
            path,
        ),
        severity=_parse_object_collection(
            data,
            "severity",
            path,
            _parse_severity,
        ),
    )


def _parse_vulnerability(
    value: object,
    path: str,
) -> OsvVulnerability:
    """Parse one vulnerability record."""

    data = _expect_dictionary(
        value,
        path,
    )

    return _create_model(
        OsvVulnerability,
        path,
        advisory_id=_required_string_field(
            data,
            "id",
            path,
        ),
        summary=_optional_string_field(
            data,
            "summary",
            path,
        ),
        details=_optional_string_field(
            data,
            "details",
            path,
        ),
        aliases=_parse_string_collection(
            data,
            "aliases",
            path,
        ),
        severity=_parse_object_collection(
            data,
            "severity",
            path,
            _parse_severity,
        ),
        affected=_parse_object_collection(
            data,
            "affected",
            path,
            _parse_affected_package,
        ),
    )


def parse_osv_query_response(
    payload: object,
) -> OsvQueryResponse:
    """Parse a decoded OSV query response payload."""

    data = _expect_dictionary(
        payload,
        "payload",
    )

    return _create_model(
        OsvQueryResponse,
        "payload",
        vulnerabilities=_parse_object_collection(
            data,
            "vulns",
            "payload",
            _parse_vulnerability,
        ),
        next_page_token=_optional_string_field(
            data,
            "next_page_token",
            "payload",
        ),
    )