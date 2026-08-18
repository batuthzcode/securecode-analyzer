"""Tests for decoded OSV response payload parsing."""

import re
from collections.abc import Callable

import pytest

import dependency_scanner.osv_parser as osv_parser
from dependency_scanner import (
    OsvQueryResponse,
    OsvResponseParseError,
    parse_osv_query_response,
)


PayloadFactory = Callable[[object], object]

_FULL_NESTED_PAYLOAD = {
    "vulns": [
        {
            "id": "OSV-2026-1",
            "summary": "Summary",
            "details": "Details",
            "aliases": [
                "CVE-2026-0001",
                "GHSA-aaaa-bbbb-cccc",
            ],
            "severity": [
                {
                    "type": "CVSS_V3",
                    "score": "9.8",
                },
            ],
            "affected": [
                {
                    "package": {
                        "ecosystem": "PyPI",
                        "name": "demo-package",
                    },
                    "ranges": [
                        {
                            "type": "ECOSYSTEM",
                            "events": [
                                {"introduced": "0"},
                                {
                                    "fixed": "2.0.0",
                                    "last_affected": "1.9.9",
                                    "limit": "3.0.0",
                                },
                            ],
                        },
                    ],
                    "versions": ["1.0.0", "1.5.0"],
                    "severity": [
                        {
                            "type": "CVSS_V3",
                            "score": "7.5",
                        },
                    ],
                },
            ],
        },
    ],
    "next_page_token": "page-2",
}

_ORDERED_DUPLICATE_PAYLOAD = {
    "vulns": [
        {
            "id": "OSV-B",
            "aliases": ["CVE-Z", "CVE-Z", "CVE-A"],
            "affected": [
                {
                    "package": {
                        "ecosystem": "PyPI",
                        "name": "demo-package",
                    },
                    "versions": ["2.0", "2.0", "1.0"],
                },
            ],
        },
        {"id": "OSV-A"},
    ],
}


def _vulnerability(
    **values: object,
) -> dict[str, object]:
    """Create a minimal vulnerability payload."""

    payload: dict[str, object] = {
        "id": "OSV-TEST-1",
    }
    payload.update(values)
    return payload


def _package(
    **values: object,
) -> dict[str, object]:
    """Create a minimal package payload."""

    payload: dict[str, object] = {
        "ecosystem": "PyPI",
        "name": "demo-package",
    }
    payload.update(values)
    return payload


def _affected(
    **values: object,
) -> dict[str, object]:
    """Create a minimal affected-package payload."""

    payload: dict[str, object] = {
        "package": _package(),
    }
    payload.update(values)
    return payload


def _response(
    vulnerability: object,
) -> dict[str, object]:
    """Create a response containing one vulnerability."""

    return {
        "vulns": [
            vulnerability,
        ],
    }


def _assert_parse_error(
    payload: object,
    expected_path: str,
) -> None:
    """Assert that parsing fails at a payload path."""

    with pytest.raises(
        OsvResponseParseError,
        match=re.escape(expected_path),
    ):
        parse_osv_query_response(payload)


def test_public_parser_returns_query_response() -> None:
    """Expose the parser and response model through the public API."""

    result = parse_osv_query_response({})

    assert isinstance(
        result,
        OsvQueryResponse,
    )


def test_parse_empty_response() -> None:
    """Parse a response without vulnerabilities."""

    result = parse_osv_query_response({})

    assert result.vulnerabilities == ()
    assert result.next_page_token is None


def test_parse_full_nested_response() -> None:
    """Parse all supported nested OSV response fields."""

    result = parse_osv_query_response(_FULL_NESTED_PAYLOAD)

    vulnerability = result.vulnerabilities[0]
    affected = vulnerability.affected[0]
    affected_range = affected.ranges[0]

    assert result.next_page_token == "page-2"
    assert vulnerability.advisory_id == "OSV-2026-1"
    assert vulnerability.summary == "Summary"
    assert vulnerability.details == "Details"
    assert vulnerability.aliases == (
        "CVE-2026-0001",
        "GHSA-aaaa-bbbb-cccc",
    )
    assert vulnerability.severity[0].severity_type == "CVSS_V3"
    assert vulnerability.severity[0].score == "9.8"
    assert affected.package.ecosystem == "PyPI"
    assert affected.package.name == "demo-package"
    assert affected.versions == (
        "1.0.0",
        "1.5.0",
    )
    assert affected.severity[0].score == "7.5"
    assert affected_range.range_type == "ECOSYSTEM"
    assert affected_range.events[0].introduced == "0"
    assert affected_range.events[1].fixed == "2.0.0"
    assert affected_range.events[1].last_affected == "1.9.9"
    assert affected_range.events[1].limit == "3.0.0"


def test_ignore_unknown_fields() -> None:
    """Ignore unsupported fields at every response level."""

    result = parse_osv_query_response(
        {
            "future_response_field": True,
            "vulns": [
                {
                    "id": "OSV-1",
                    "future_vulnerability_field": True,
                    "affected": [
                        {
                            "package": {
                                "ecosystem": "PyPI",
                                "name": "demo",
                                "future_package_field": True,
                            },
                            "future_affected_field": True,
                        },
                    ],
                },
            ],
        }
    )

    assert result.vulnerabilities[0].advisory_id == "OSV-1"
    assert result.vulnerabilities[0].affected[0].package.name == "demo"


def test_preserve_order_and_duplicates() -> None:
    """Preserve source order and duplicate values."""

    result = parse_osv_query_response(_ORDERED_DUPLICATE_PAYLOAD)

    assert tuple(
        item.advisory_id
        for item in result.vulnerabilities
    ) == (
        "OSV-B",
        "OSV-A",
    )

    first = result.vulnerabilities[0]

    assert first.aliases == (
        "CVE-Z",
        "CVE-Z",
        "CVE-A",
    )
    assert first.affected[0].versions == (
        "2.0",
        "2.0",
        "1.0",
    )


def test_preserve_missing_and_null_optional_fields() -> None:
    """Convert missing collections and preserve optional nulls."""

    result = parse_osv_query_response(
        {
            "vulns": [
                {
                    "id": "OSV-1",
                    "summary": None,
                    "details": None,
                    "affected": [
                        {
                            "package": _package(),
                            "ranges": [
                                {
                                    "type": "ECOSYSTEM",
                                    "events": [
                                        {
                                            "introduced": None,
                                            "fixed": None,
                                            "last_affected": None,
                                            "limit": None,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
            "next_page_token": None,
        }
    )

    vulnerability = result.vulnerabilities[0]
    affected = vulnerability.affected[0]
    event = affected.ranges[0].events[0]

    assert vulnerability.summary is None
    assert vulnerability.details is None
    assert vulnerability.aliases == ()
    assert vulnerability.severity == ()
    assert affected.versions == ()
    assert affected.severity == ()
    assert event.introduced is None
    assert event.fixed is None
    assert event.last_affected is None
    assert event.limit is None
    assert result.next_page_token is None


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        "invalid",
        1,
    ],
)
def test_reject_invalid_top_level_payload(
    payload: object,
) -> None:
    """Require the top-level payload to be a dictionary."""

    _assert_parse_error(
        payload,
        "payload",
    )


@pytest.mark.parametrize(
    ("payload", "expected_path"),
    [
        (
            {
                "vulns": {},
            },
            "payload.vulns",
        ),
        (
            _response(
                _vulnerability(
                    aliases={},
                )
            ),
            "payload.vulns[0].aliases",
        ),
        (
            _response(
                _vulnerability(
                    severity={},
                )
            ),
            "payload.vulns[0].severity",
        ),
        (
            _response(
                _vulnerability(
                    affected={},
                )
            ),
            "payload.vulns[0].affected",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges={},
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges=[
                                {
                                    "type": "ECOSYSTEM",
                                    "events": {},
                                },
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges[0].events",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        _affected(
                            versions={},
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].versions",
        ),
    ],
)
def test_reject_non_list_collections(
    payload: object,
    expected_path: str,
) -> None:
    """Require collection fields to use lists."""

    _assert_parse_error(
        payload,
        expected_path,
    )


@pytest.mark.parametrize(
    ("payload", "expected_path"),
    [
        (
            {
                "vulns": [
                    1,
                ],
            },
            "payload.vulns[0]",
        ),
        (
            _response(
                _vulnerability(
                    severity=[
                        1,
                    ],
                )
            ),
            "payload.vulns[0].severity[0]",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        1,
                    ],
                )
            ),
            "payload.vulns[0].affected[0]",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges=[
                                1,
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges[0]",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges=[
                                {
                                    "type": "ECOSYSTEM",
                                    "events": [
                                        1,
                                    ],
                                },
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges[0].events[0]",
        ),
    ],
)
def test_reject_non_dictionary_collection_items(
    payload: object,
    expected_path: str,
) -> None:
    """Require nested records to use dictionaries."""

    _assert_parse_error(
        payload,
        expected_path,
    )


@pytest.mark.parametrize(
    ("payload", "expected_path"),
    [
        (
            _response({}),
            "payload.vulns[0].id",
        ),
        (
            _response(
                _vulnerability(
                    severity=[
                        {
                            "score": "9.8",
                        },
                    ],
                )
            ),
            "payload.vulns[0].severity[0].type",
        ),
        (
            _response(
                _vulnerability(
                    severity=[
                        {
                            "type": "CVSS_V3",
                        },
                    ],
                )
            ),
            "payload.vulns[0].severity[0].score",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        {},
                    ],
                )
            ),
            "payload.vulns[0].affected[0].package",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        {
                            "package": {
                                "name": "demo",
                            },
                        },
                    ],
                )
            ),
            "payload.vulns[0].affected[0].package.ecosystem",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        {
                            "package": {
                                "ecosystem": "PyPI",
                            },
                        },
                    ],
                )
            ),
            "payload.vulns[0].affected[0].package.name",
        ),
        (
            _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges=[
                                {},
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges[0].type",
        ),
    ],
)
def test_reject_missing_required_fields(
    payload: object,
    expected_path: str,
) -> None:
    """Reject missing required fields."""

    _assert_parse_error(
        payload,
        expected_path,
    )


@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        "",
        "   ",
        1,
    ],
)
@pytest.mark.parametrize(
    ("payload_factory", "expected_path"),
    [
        (
            lambda value: _response(
                _vulnerability(
                    id=value,
                )
            ),
            "payload.vulns[0].id",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    severity=[
                        {
                            "type": value,
                            "score": "9.8",
                        },
                    ],
                )
            ),
            "payload.vulns[0].severity[0].type",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    severity=[
                        {
                            "type": "CVSS_V3",
                            "score": value,
                        },
                    ],
                )
            ),
            "payload.vulns[0].severity[0].score",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    affected=[
                        {
                            "package": {
                                "ecosystem": value,
                                "name": "demo",
                            },
                        },
                    ],
                )
            ),
            "payload.vulns[0].affected[0].package.ecosystem",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    affected=[
                        {
                            "package": {
                                "ecosystem": "PyPI",
                                "name": value,
                            },
                        },
                    ],
                )
            ),
            "payload.vulns[0].affected[0].package.name",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges=[
                                {
                                    "type": value,
                                },
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges[0].type",
        ),
    ],
)
def test_reject_invalid_required_strings(
    payload_factory: PayloadFactory,
    expected_path: str,
    invalid_value: object,
) -> None:
    """Reject invalid required string values."""

    _assert_parse_error(
        payload_factory(invalid_value),
        expected_path,
    )


@pytest.mark.parametrize(
    "invalid_value",
    [
        1,
        "   ",
    ],
)
@pytest.mark.parametrize(
    ("payload_factory", "expected_path"),
    [
        (
            lambda value: {
                "next_page_token": value,
            },
            "payload.next_page_token",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    summary=value,
                )
            ),
            "payload.vulns[0].summary",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    details=value,
                )
            ),
            "payload.vulns[0].details",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges=[
                                {
                                    "type": "ECOSYSTEM",
                                    "events": [
                                        {
                                            "introduced": value,
                                        },
                                    ],
                                },
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges[0].events[0].introduced",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges=[
                                {
                                    "type": "ECOSYSTEM",
                                    "events": [
                                        {
                                            "fixed": value,
                                        },
                                    ],
                                },
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges[0].events[0].fixed",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges=[
                                {
                                    "type": "ECOSYSTEM",
                                    "events": [
                                        {
                                            "last_affected": value,
                                        },
                                    ],
                                },
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges[0].events[0].last_affected",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    affected=[
                        _affected(
                            ranges=[
                                {
                                    "type": "ECOSYSTEM",
                                    "events": [
                                        {
                                            "limit": value,
                                        },
                                    ],
                                },
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].ranges[0].events[0].limit",
        ),
    ],
)
def test_reject_invalid_optional_strings(
    payload_factory: PayloadFactory,
    expected_path: str,
    invalid_value: object,
) -> None:
    """Reject invalid non-null optional strings."""

    _assert_parse_error(
        payload_factory(invalid_value),
        expected_path,
    )


@pytest.mark.parametrize(
    "invalid_value",
    [
        1,
        "",
    ],
)
@pytest.mark.parametrize(
    ("payload_factory", "expected_path"),
    [
        (
            lambda value: _response(
                _vulnerability(
                    aliases=[
                        value,
                    ],
                )
            ),
            "payload.vulns[0].aliases[0]",
        ),
        (
            lambda value: _response(
                _vulnerability(
                    affected=[
                        _affected(
                            versions=[
                                value,
                            ],
                        ),
                    ],
                )
            ),
            "payload.vulns[0].affected[0].versions[0]",
        ),
    ],
)
def test_reject_invalid_string_collection_items(
    payload_factory: PayloadFactory,
    expected_path: str,
    invalid_value: object,
) -> None:
    """Reject invalid alias and version values."""

    _assert_parse_error(
        payload_factory(invalid_value),
        expected_path,
    )


@pytest.mark.parametrize(
    "package_value",
    [
        None,
        [],
        "invalid",
        1,
    ],
)
def test_require_package_dictionary(
    package_value: object,
) -> None:
    """Require package values to be dictionaries."""

    _assert_parse_error(
        _response(
            _vulnerability(
                affected=[
                    {
                        "package": package_value,
                    },
                ],
            )
        ),
        "payload.vulns[0].affected[0].package",
    )


def test_translate_model_validation_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Translate model validation failures into parser errors."""

    def reject_model(
        **values: object,
    ) -> object:
        del values
        raise ValueError(
            "model rejected the values"
        )

    monkeypatch.setattr(
        osv_parser,
        "OsvQueryResponse",
        reject_model,
    )

    with pytest.raises(
        OsvResponseParseError,
        match=re.escape(
            "payload: model rejected the values"
        ),
    ):
        osv_parser.parse_osv_query_response({})
