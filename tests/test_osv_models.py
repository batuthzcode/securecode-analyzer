"""Tests for immutable OSV response models."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import FrozenInstanceError

import dependency_scanner
import pytest

from dependency_scanner import (
    OsvAffectedPackage,
    OsvPackage,
    OsvQueryResponse,
    OsvRange,
    OsvRangeEvent,
    OsvSeverity,
    OsvVulnerability,
)


def create_package(
    name: str = "sample-package",
) -> OsvPackage:
    """Create package information for tests."""

    return OsvPackage(
        ecosystem="PyPI",
        name=name,
    )


def create_severity(
    score: str = "CVSS:3.1/AV:N/AC:L",
) -> OsvSeverity:
    """Create severity information for tests."""

    return OsvSeverity(
        severity_type="CVSS_V3",
        score=score,
    )


def create_range() -> OsvRange:
    """Create an affected range for tests."""

    return OsvRange(
        range_type="ECOSYSTEM",
        events=(
            OsvRangeEvent(
                introduced="0",
            ),
            OsvRangeEvent(
                fixed="2.0.0",
            ),
        ),
    )


def create_affected_package(
    name: str = "sample-package",
) -> OsvAffectedPackage:
    """Create affected package information for tests."""

    return OsvAffectedPackage(
        package=create_package(name),
        ranges=(
            create_range(),
        ),
        versions=(
            "1.0.0",
            "1.5.0",
        ),
        severity=(
            create_severity(),
        ),
    )


def create_vulnerability(
    advisory_id: str = "PYSEC-2026-1",
) -> OsvVulnerability:
    """Create vulnerability information for tests."""

    return OsvVulnerability(
        advisory_id=advisory_id,
        summary="Example vulnerability",
        details="Example vulnerability details.",
        aliases=(
            "CVE-2026-0001",
            "GHSA-xxxx-yyyy-zzzz",
        ),
        severity=(
            create_severity(),
        ),
        affected=(
            create_affected_package(),
        ),
    )


def create_response() -> OsvQueryResponse:
    """Create a nested OSV query response."""

    return OsvQueryResponse(
        vulnerabilities=(
            create_vulnerability(
                "PYSEC-2026-2"
            ),
            create_vulnerability(
                "PYSEC-2026-1"
            ),
        ),
        next_page_token="next-token",
    )


def test_models_are_publicly_exported() -> None:
    """All OSV models are available from the package API."""

    assert (
        dependency_scanner.OsvSeverity
        is OsvSeverity
    )
    assert (
        dependency_scanner.OsvRangeEvent
        is OsvRangeEvent
    )
    assert (
        dependency_scanner.OsvRange
        is OsvRange
    )
    assert (
        dependency_scanner.OsvPackage
        is OsvPackage
    )
    assert (
        dependency_scanner.OsvAffectedPackage
        is OsvAffectedPackage
    )
    assert (
        dependency_scanner.OsvVulnerability
        is OsvVulnerability
    )
    assert (
        dependency_scanner.OsvQueryResponse
        is OsvQueryResponse
    )


def test_severity_preserves_original_values() -> None:
    """Severity type and score are preserved."""

    severity = create_severity()

    assert severity.severity_type == "CVSS_V3"
    assert severity.score == "CVSS:3.1/AV:N/AC:L"


def test_range_event_defaults_to_none() -> None:
    """Optional event fields default to None."""

    event = OsvRangeEvent()

    assert event.introduced is None
    assert event.fixed is None
    assert event.last_affected is None
    assert event.limit is None


def test_affected_package_defaults_to_empty_tuples() -> None:
    """Optional affected collections default to tuples."""

    affected = OsvAffectedPackage(
        package=create_package(),
    )

    assert affected.ranges == ()
    assert affected.versions == ()
    assert affected.severity == ()


def test_vulnerability_defaults_to_optional_values() -> None:
    """Optional vulnerability values have safe defaults."""

    vulnerability = OsvVulnerability(
        advisory_id="PYSEC-2026-1",
    )

    assert vulnerability.summary is None
    assert vulnerability.details is None
    assert vulnerability.aliases == ()
    assert vulnerability.severity == ()
    assert vulnerability.affected == ()


def test_query_response_defaults_to_empty_result() -> None:
    """An empty OSV result can be represented."""

    response = OsvQueryResponse()

    assert response.vulnerabilities == ()
    assert response.next_page_token is None


def test_nested_response_preserves_collection_order() -> None:
    """OSV collection ordering is not changed."""

    response = create_response()

    assert [
        vulnerability.advisory_id
        for vulnerability in response.vulnerabilities
    ] == [
        "PYSEC-2026-2",
        "PYSEC-2026-1",
    ]

    vulnerability = response.vulnerabilities[0]
    affected = vulnerability.affected[0]
    osv_range = affected.ranges[0]

    assert vulnerability.aliases == (
        "CVE-2026-0001",
        "GHSA-xxxx-yyyy-zzzz",
    )
    assert affected.versions == (
        "1.0.0",
        "1.5.0",
    )
    assert [
        event.introduced
        for event in osv_range.events
    ] == [
        "0",
        None,
    ]
    assert [
        event.fixed
        for event in osv_range.events
    ] == [
        None,
        "2.0.0",
    ]


def test_to_dict_is_recursive_and_json_serializable() -> None:
    """Nested models produce JSON-compatible dictionaries."""

    response = create_response()

    data = response.to_dict()
    serialized = json.dumps(data)

    assert data["next_page_token"] == "next-token"
    assert isinstance(
        data["vulnerabilities"],
        list,
    )
    assert (
        data["vulnerabilities"][0]["advisory_id"]
        == "PYSEC-2026-2"
    )
    assert (
        data["vulnerabilities"][0]
        ["affected"][0]
        ["package"]["ecosystem"]
        == "PyPI"
    )
    assert (
        data["vulnerabilities"][0]
        ["affected"][0]
        ["ranges"][0]
        ["events"][1]["fixed"]
        == "2.0.0"
    )
    assert "PYSEC-2026-2" in serialized


@pytest.mark.parametrize(
    ("model", "field_name", "new_value"),
    [
        (
            create_severity(),
            "score",
            "changed",
        ),
        (
            OsvRangeEvent(
                introduced="0",
            ),
            "introduced",
            "1",
        ),
        (
            create_range(),
            "range_type",
            "GIT",
        ),
        (
            create_package(),
            "name",
            "changed",
        ),
        (
            create_affected_package(),
            "versions",
            (),
        ),
        (
            create_vulnerability(),
            "advisory_id",
            "changed",
        ),
        (
            create_response(),
            "next_page_token",
            None,
        ),
    ],
)
def test_models_are_immutable(
    model: object,
    field_name: str,
    new_value: object,
) -> None:
    """OSV response models cannot be modified."""

    with pytest.raises(FrozenInstanceError):
        setattr(
            model,
            field_name,
            new_value,
        )


@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(
            lambda: OsvSeverity(
                severity_type="",
                score="score",
            ),
            id="empty-severity-type",
        ),
        pytest.param(
            lambda: OsvSeverity(
                severity_type=" ",
                score="score",
            ),
            id="blank-severity-type",
        ),
        pytest.param(
            lambda: OsvSeverity(
                severity_type=None,
                score="score",
            ),
            id="non-string-severity-type",
        ),
        pytest.param(
            lambda: OsvSeverity(
                severity_type="CVSS_V3",
                score="",
            ),
            id="empty-score",
        ),
        pytest.param(
            lambda: OsvSeverity(
                severity_type="CVSS_V3",
                score=" ",
            ),
            id="blank-score",
        ),
        pytest.param(
            lambda: OsvSeverity(
                severity_type="CVSS_V3",
                score=None,
            ),
            id="non-string-score",
        ),
        pytest.param(
            lambda: OsvRange(
                range_type="",
                events=(),
            ),
            id="empty-range-type",
        ),
        pytest.param(
            lambda: OsvRange(
                range_type=" ",
                events=(),
            ),
            id="blank-range-type",
        ),
        pytest.param(
            lambda: OsvRange(
                range_type=None,
                events=(),
            ),
            id="non-string-range-type",
        ),
        pytest.param(
            lambda: OsvPackage(
                ecosystem="",
                name="package",
            ),
            id="empty-ecosystem",
        ),
        pytest.param(
            lambda: OsvPackage(
                ecosystem=" ",
                name="package",
            ),
            id="blank-ecosystem",
        ),
        pytest.param(
            lambda: OsvPackage(
                ecosystem=None,
                name="package",
            ),
            id="non-string-ecosystem",
        ),
        pytest.param(
            lambda: OsvPackage(
                ecosystem="PyPI",
                name="",
            ),
            id="empty-package-name",
        ),
        pytest.param(
            lambda: OsvPackage(
                ecosystem="PyPI",
                name=" ",
            ),
            id="blank-package-name",
        ),
        pytest.param(
            lambda: OsvPackage(
                ecosystem="PyPI",
                name=None,
            ),
            id="non-string-package-name",
        ),
        pytest.param(
            lambda: OsvVulnerability(
                advisory_id="",
            ),
            id="empty-advisory-id",
        ),
        pytest.param(
            lambda: OsvVulnerability(
                advisory_id=" ",
            ),
            id="blank-advisory-id",
        ),
        pytest.param(
            lambda: OsvVulnerability(
                advisory_id=None,
            ),
            id="non-string-advisory-id",
        ),
    ],
)
def test_required_strings_reject_invalid_values(
    factory: Callable[[], object],
) -> None:
    """Required string fields reject invalid values."""

    with pytest.raises(ValueError):
        factory()


@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(
            lambda: OsvRangeEvent(
                introduced="",
            ),
            id="empty-introduced",
        ),
        pytest.param(
            lambda: OsvRangeEvent(
                fixed=" ",
            ),
            id="blank-fixed",
        ),
        pytest.param(
            lambda: OsvRangeEvent(
                last_affected="",
            ),
            id="empty-last-affected",
        ),
        pytest.param(
            lambda: OsvRangeEvent(
                limit=" ",
            ),
            id="blank-limit",
        ),
        pytest.param(
            lambda: OsvVulnerability(
                advisory_id="PYSEC-1",
                summary="",
            ),
            id="empty-summary",
        ),
        pytest.param(
            lambda: OsvVulnerability(
                advisory_id="PYSEC-1",
                details=" ",
            ),
            id="blank-details",
        ),
        pytest.param(
            lambda: OsvQueryResponse(
                next_page_token="",
            ),
            id="empty-page-token",
        ),
        pytest.param(
            lambda: OsvQueryResponse(
                next_page_token=" ",
            ),
            id="blank-page-token",
        ),
    ],
)
def test_optional_strings_reject_empty_values(
    factory: Callable[[], object],
) -> None:
    """Optional strings allow None but reject empty strings."""

    with pytest.raises(ValueError):
        factory()


@pytest.mark.parametrize(
    "bad_collection",
    [
        pytest.param(
            [],
            id="list",
        ),
        pytest.param(
            "invalid",
            id="string",
        ),
        pytest.param(
            {},
            id="dictionary",
        ),
    ],
)
@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(
            lambda value: OsvRange(
                range_type="ECOSYSTEM",
                events=value,
            ),
            id="range-events",
        ),
        pytest.param(
            lambda value: OsvAffectedPackage(
                package=create_package(),
                ranges=value,
            ),
            id="affected-ranges",
        ),
        pytest.param(
            lambda value: OsvAffectedPackage(
                package=create_package(),
                versions=value,
            ),
            id="affected-versions",
        ),
        pytest.param(
            lambda value: OsvAffectedPackage(
                package=create_package(),
                severity=value,
            ),
            id="affected-severity",
        ),
        pytest.param(
            lambda value: OsvVulnerability(
                advisory_id="PYSEC-1",
                aliases=value,
            ),
            id="vulnerability-aliases",
        ),
        pytest.param(
            lambda value: OsvVulnerability(
                advisory_id="PYSEC-1",
                severity=value,
            ),
            id="vulnerability-severity",
        ),
        pytest.param(
            lambda value: OsvVulnerability(
                advisory_id="PYSEC-1",
                affected=value,
            ),
            id="vulnerability-affected",
        ),
        pytest.param(
            lambda value: OsvQueryResponse(
                vulnerabilities=value,
            ),
            id="response-vulnerabilities",
        ),
    ],
)
def test_collection_fields_require_tuples(
    factory: Callable[[object], object],
    bad_collection: object,
) -> None:
    """Collection fields reject invalid collection types."""

    with pytest.raises(ValueError):
        factory(bad_collection)


@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(
            lambda: OsvRange(
                range_type="ECOSYSTEM",
                events=("invalid",),
            ),
            id="invalid-range-event",
        ),
        pytest.param(
            lambda: OsvAffectedPackage(
                package=create_package(),
                ranges=("invalid",),
            ),
            id="invalid-range",
        ),
        pytest.param(
            lambda: OsvAffectedPackage(
                package=create_package(),
                versions=(1,),
            ),
            id="invalid-version",
        ),
        pytest.param(
            lambda: OsvAffectedPackage(
                package=create_package(),
                severity=("invalid",),
            ),
            id="invalid-affected-severity",
        ),
        pytest.param(
            lambda: OsvVulnerability(
                advisory_id="PYSEC-1",
                aliases=(1,),
            ),
            id="invalid-alias",
        ),
        pytest.param(
            lambda: OsvVulnerability(
                advisory_id="PYSEC-1",
                severity=("invalid",),
            ),
            id="invalid-vulnerability-severity",
        ),
        pytest.param(
            lambda: OsvVulnerability(
                advisory_id="PYSEC-1",
                affected=("invalid",),
            ),
            id="invalid-affected-package",
        ),
        pytest.param(
            lambda: OsvQueryResponse(
                vulnerabilities=("invalid",),
            ),
            id="invalid-vulnerability",
        ),
    ],
)
def test_collection_items_require_expected_types(
    factory: Callable[[], object],
) -> None:
    """Tuple elements must have the expected model type."""

    with pytest.raises(ValueError):
        factory()


def test_affected_package_requires_osv_package() -> None:
    """Affected package information requires OsvPackage."""

    with pytest.raises(
        ValueError,
        match="package must be an OsvPackage",
    ):
        OsvAffectedPackage(
            package="invalid",
        )