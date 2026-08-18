"""Calculate and classify CVSS v3 base scores from OSV data."""

from __future__ import annotations

from decimal import Decimal, ROUND_CEILING

from dependency_scanner.models import (
    VulnerabilitySeverity,
)


_BASE_METRICS = frozenset(
    {
        "AV",
        "AC",
        "PR",
        "UI",
        "S",
        "C",
        "I",
        "A",
    }
)

_METRIC_VALUES = {
    "AV": frozenset({"N", "A", "L", "P"}),
    "AC": frozenset({"L", "H"}),
    "PR": frozenset({"N", "L", "H"}),
    "UI": frozenset({"N", "R"}),
    "S": frozenset({"U", "C"}),
    "C": frozenset({"H", "L", "N"}),
    "I": frozenset({"H", "L", "N"}),
    "A": frozenset({"H", "L", "N"}),
    "E": frozenset({"X", "H", "F", "P", "U"}),
    "RL": frozenset({"X", "U", "W", "T", "O"}),
    "RC": frozenset({"X", "C", "R", "U"}),
    "CR": frozenset({"X", "H", "M", "L"}),
    "IR": frozenset({"X", "H", "M", "L"}),
    "AR": frozenset({"X", "H", "M", "L"}),
    "MAV": frozenset({"X", "N", "A", "L", "P"}),
    "MAC": frozenset({"X", "L", "H"}),
    "MPR": frozenset({"X", "N", "L", "H"}),
    "MUI": frozenset({"X", "N", "R"}),
    "MS": frozenset({"X", "U", "C"}),
    "MC": frozenset({"X", "N", "L", "H"}),
    "MI": frozenset({"X", "N", "L", "H"}),
    "MA": frozenset({"X", "N", "L", "H"}),
}

_ATTACK_VECTOR_WEIGHTS = {
    "N": Decimal("0.85"),
    "A": Decimal("0.62"),
    "L": Decimal("0.55"),
    "P": Decimal("0.2"),
}

_ATTACK_COMPLEXITY_WEIGHTS = {
    "L": Decimal("0.77"),
    "H": Decimal("0.44"),
}

_USER_INTERACTION_WEIGHTS = {
    "N": Decimal("0.85"),
    "R": Decimal("0.62"),
}

_IMPACT_WEIGHTS = {
    "H": Decimal("0.56"),
    "L": Decimal("0.22"),
    "N": Decimal("0"),
}


class CvssV3VectorError(ValueError):
    """Indicate that a CVSS v3 vector is invalid or unsupported."""


def _split_vector(vector: str) -> list[str]:
    """Validate vector text and return its metric sections."""

    if not isinstance(vector, str):
        raise CvssV3VectorError(
            "CVSS v3 vector must be a string."
        )

    cleaned_vector = vector.strip()

    if not cleaned_vector:
        raise CvssV3VectorError(
            "CVSS v3 vector must not be empty."
        )

    sections = cleaned_vector.split("/")

    if sections[0] not in {
        "CVSS:3.0",
        "CVSS:3.1",
    }:
        raise CvssV3VectorError(
            "Unsupported CVSS v3 vector version."
        )

    return sections[1:]


def _add_metric(
    metrics: dict[str, str],
    section: str,
) -> None:
    """Validate and add one CVSS v3 metric section."""

    if section.count(":") != 1:
        raise CvssV3VectorError(
            "Invalid CVSS v3 metric syntax."
        )

    metric_name, metric_value = section.split(":")

    if metric_name in metrics:
        raise CvssV3VectorError(
            "CVSS v3 vector contains a duplicate metric."
        )

    allowed_values = _METRIC_VALUES.get(metric_name)

    if allowed_values is None:
        raise CvssV3VectorError(
            "CVSS v3 vector contains an unknown metric."
        )

    if metric_value not in allowed_values:
        raise CvssV3VectorError(
            "CVSS v3 vector contains an invalid metric value."
        )

    metrics[metric_name] = metric_value


def _parse_vector(vector: str) -> dict[str, str]:
    """Validate a CVSS v3 vector and return its metrics."""

    metrics: dict[str, str] = {}

    for section in _split_vector(vector):
        _add_metric(metrics, section)

    if not _BASE_METRICS.issubset(metrics):
        raise CvssV3VectorError(
            "CVSS v3 vector is missing a base metric."
        )

    return metrics


def _privileges_required_weight(
    metric_value: str,
    scope: str,
) -> Decimal:
    """Return the scope-aware privileges-required weight."""

    if metric_value == "N":
        return Decimal("0.85")

    if metric_value == "L":
        if scope == "C":
            return Decimal("0.68")

        return Decimal("0.62")

    if scope == "C":
        return Decimal("0.5")

    return Decimal("0.27")


def _calculate_impact(
    metrics: dict[str, str],
) -> Decimal:
    """Calculate the CVSS v3 impact sub-score."""

    impact_sub_score = Decimal("1") - (
        (
            Decimal("1")
            - _IMPACT_WEIGHTS[metrics["C"]]
        )
        * (
            Decimal("1")
            - _IMPACT_WEIGHTS[metrics["I"]]
        )
        * (
            Decimal("1")
            - _IMPACT_WEIGHTS[metrics["A"]]
        )
    )

    if metrics["S"] == "U":
        return Decimal("6.42") * impact_sub_score

    return (
        Decimal("7.52")
        * (impact_sub_score - Decimal("0.029"))
        - Decimal("3.25")
        * (
            impact_sub_score - Decimal("0.02")
        )
        ** 15
    )


def _calculate_exploitability(
    metrics: dict[str, str],
) -> Decimal:
    """Calculate the CVSS v3 exploitability sub-score."""

    return (
        Decimal("8.22")
        * _ATTACK_VECTOR_WEIGHTS[metrics["AV"]]
        * _ATTACK_COMPLEXITY_WEIGHTS[metrics["AC"]]
        * _privileges_required_weight(
            metrics["PR"],
            metrics["S"],
        )
        * _USER_INTERACTION_WEIGHTS[metrics["UI"]]
    )


def _round_up(value: Decimal) -> Decimal:
    """Round a positive CVSS value up to one decimal place."""

    return (
        value * Decimal("10")
    ).to_integral_value(
        rounding=ROUND_CEILING
    ) / Decimal("10")


def calculate_cvss_v3_base_score(
    vector: str,
) -> float:
    """Return the CVSS v3.0 or v3.1 base score for a vector."""

    metrics = _parse_vector(vector)
    impact = _calculate_impact(metrics)

    if impact <= 0:
        return 0.0

    base_score = impact + _calculate_exploitability(
        metrics
    )

    if metrics["S"] == "C":
        base_score *= Decimal("1.08")

    rounded_score = _round_up(
        min(
            base_score,
            Decimal("10"),
        )
    )

    return float(rounded_score)


def classify_cvss_score(
    score: float,
) -> VulnerabilitySeverity:
    """Map a numeric CVSS score to a supported severity value."""

    if isinstance(score, bool) or not isinstance(
        score,
        (int, float),
    ):
        raise ValueError(
            "CVSS score must be a number."
        )

    decimal_score = Decimal(str(score))

    if (
        not decimal_score.is_finite()
        or decimal_score < Decimal("0")
        or decimal_score > Decimal("10")
    ):
        raise ValueError(
            "CVSS score must be between 0.0 and 10.0."
        )

    if decimal_score == Decimal("0"):
        return VulnerabilitySeverity.UNKNOWN

    if decimal_score < Decimal("4"):
        return VulnerabilitySeverity.LOW

    if decimal_score < Decimal("7"):
        return VulnerabilitySeverity.MEDIUM

    if decimal_score < Decimal("9"):
        return VulnerabilitySeverity.HIGH

    return VulnerabilitySeverity.CRITICAL
