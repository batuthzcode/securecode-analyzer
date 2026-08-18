"""Tests for CVSS v3 score calculation and classification."""

from __future__ import annotations

import math

import dependency_scanner
import pytest

from dependency_scanner import (
    CvssV3VectorError,
    VulnerabilitySeverity,
    calculate_cvss_v3_base_score,
    classify_cvss_score,
)


_MAXIMUM_BASE_VECTOR = (
    "AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
)


def test_severity_api_is_publicly_exported() -> None:
    """CVSS severity helpers are available through package API."""

    assert (
        dependency_scanner.CvssV3VectorError
        is CvssV3VectorError
    )
    assert (
        dependency_scanner.calculate_cvss_v3_base_score
        is calculate_cvss_v3_base_score
    )
    assert (
        dependency_scanner.classify_cvss_score
        is classify_cvss_score
    )


@pytest.mark.parametrize(
    ("version", "expected_score"),
    [
        ("3.0", 9.8),
        ("3.1", 9.8),
    ],
)
def test_supported_versions_calculate_base_score(
    version: str,
    expected_score: float,
) -> None:
    """CVSS v3.0 and v3.1 vectors use the base formula."""

    vector = f"CVSS:{version}/{_MAXIMUM_BASE_VECTOR}"

    assert (
        calculate_cvss_v3_base_score(vector)
        == expected_score
    )


def test_scope_changed_score_is_capped_at_ten() -> None:
    """A maximum scope-changed vector cannot exceed 10.0."""

    vector = (
        "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/"
        "S:C/C:H/I:H/A:H"
    )

    assert calculate_cvss_v3_base_score(vector) == 10.0


@pytest.mark.parametrize(
    ("privileges", "scope", "expected_score"),
    [
        ("L", "U", 8.8),
        ("L", "C", 9.9),
        ("H", "U", 7.2),
        ("H", "C", 9.1),
    ],
)
def test_privilege_weight_accounts_for_scope(
    privileges: str,
    scope: str,
    expected_score: float,
) -> None:
    """Low and high privileges use their scope-specific CVSS weights."""

    vector = (
        f"CVSS:3.1/AV:N/AC:L/PR:{privileges}/UI:N/"
        f"S:{scope}/C:H/I:H/A:H"
    )

    assert calculate_cvss_v3_base_score(vector) == expected_score


def test_zero_impact_returns_zero_score() -> None:
    """A vector without any impact has a zero base score."""

    vector = (
        "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/"
        "S:U/C:N/I:N/A:N"
    )

    assert calculate_cvss_v3_base_score(vector) == 0.0


def test_metric_order_does_not_change_score() -> None:
    """Readers accept base metrics in any order."""

    vector = (
        "CVSS:3.1/A:H/I:H/C:H/S:U/UI:N/"
        "PR:N/AC:L/AV:N"
    )

    assert calculate_cvss_v3_base_score(vector) == 9.8


def test_optional_metrics_are_valid_for_base_score() -> None:
    """Valid optional metrics do not alter the base score."""

    vector = (
        f"CVSS:3.1/{_MAXIMUM_BASE_VECTOR}/"
        "E:F/RL:O/RC:C/CR:H/MAV:X"
    )

    assert calculate_cvss_v3_base_score(vector) == 9.8


@pytest.mark.parametrize(
    "vector",
    [
        "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H",
        (
            "CVSS:3.1/AV:N/AV:A/AC:L/PR:N/UI:N/"
            "S:U/C:H/I:H/A:H"
        ),
        (
            "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/"
            "C:H/I:H/A:H/XX:N"
        ),
        (
            "CVSS:3.1/AV:Z/AC:L/PR:N/UI:N/S:U/"
            "C:H/I:H/A:H"
        ),
        (
            "CVSS:4.0/AV:N/AC:L/PR:N/UI:N/S:U/"
            "C:H/I:H/A:H"
        ),
        (
            "CVSS:3.1/AV/AC:L/PR:N/UI:N/S:U/"
            "C:H/I:H/A:H"
        ),
        "",
    ],
)
def test_invalid_vector_raises_public_error(
    vector: str,
) -> None:
    """Malformed or unsupported vectors raise one public error."""

    with pytest.raises(CvssV3VectorError):
        calculate_cvss_v3_base_score(vector)


def test_non_string_vector_raises_public_error() -> None:
    """A CVSS vector must be provided as text."""

    with pytest.raises(CvssV3VectorError):
        calculate_cvss_v3_base_score(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("score", "expected_severity"),
    [
        (0.0, VulnerabilitySeverity.UNKNOWN),
        (0.1, VulnerabilitySeverity.LOW),
        (3.9, VulnerabilitySeverity.LOW),
        (4.0, VulnerabilitySeverity.MEDIUM),
        (6.9, VulnerabilitySeverity.MEDIUM),
        (7.0, VulnerabilitySeverity.HIGH),
        (8.9, VulnerabilitySeverity.HIGH),
        (9.0, VulnerabilitySeverity.CRITICAL),
        (10.0, VulnerabilitySeverity.CRITICAL),
    ],
)
def test_score_is_classified_at_first_boundaries(
    score: float,
    expected_severity: VulnerabilitySeverity,
) -> None:
    """FIRST qualitative boundaries map to shared values."""

    assert classify_cvss_score(score) is expected_severity


@pytest.mark.parametrize(
    "score",
    [
        -0.1,
        10.1,
        math.inf,
        -math.inf,
        math.nan,
        True,
        "9.8",
    ],
)
def test_invalid_score_is_rejected(
    score: object,
) -> None:
    """Classification accepts only finite in-range numbers."""

    with pytest.raises(ValueError):
        classify_cvss_score(score)  # type: ignore[arg-type]
