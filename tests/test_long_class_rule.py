"""Tests for the long class analysis rule."""

import ast
from typing import Any

import pytest

from static_analyzer.models import Severity
from static_analyzer.rules import LongClassRule


def _build_class_source(
    *,
    name: str = "ExampleClass",
    body_lines: int,
) -> str:
    """Build a Python class containing the requested number of body lines."""

    body = "\n".join(
        f"    value_{line_number} = {line_number}"
        for line_number in range(body_lines)
    )

    return f"class {name}:\n{body}\n"


def test_long_class_rule_uses_default_threshold() -> None:
    """The rule should use two hundred lines as its default threshold."""

    rule = LongClassRule()

    assert rule.max_lines == 200


def test_long_class_rule_uses_custom_threshold() -> None:
    """The rule should store a custom positive threshold."""

    rule = LongClassRule(max_lines=25)

    assert rule.max_lines == 25


@pytest.mark.parametrize("max_lines", [0, -1, True, 1.5])
def test_long_class_rule_rejects_invalid_thresholds(
    max_lines: Any,
) -> None:
    """The rule should reject invalid class-length thresholds."""

    with pytest.raises(ValueError, match="max_lines must be greater than zero"):
        LongClassRule(max_lines=max_lines)


def test_class_equal_to_threshold_does_not_create_finding() -> None:
    """A class equal to the configured limit should be accepted."""

    source = _build_class_source(body_lines=2)
    tree = ast.parse(source)
    rule = LongClassRule(max_lines=3)

    findings = rule.check(tree, "example.py")

    assert findings == []


def test_long_class_creates_expected_finding() -> None:
    """A class exceeding the limit should create one complete finding."""

    source = _build_class_source(
        name="DataProcessor",
        body_lines=3,
    )
    tree = ast.parse(source)
    rule = LongClassRule(max_lines=3)

    findings = rule.check(tree, "example.py")

    assert len(findings) == 1

    finding = findings[0]

    assert finding.rule_id == "SA002"
    assert finding.message == (
        "Class 'DataProcessor' has 4 lines, exceeding the limit of 3."
    )
    assert finding.file_path == "example.py"
    assert finding.line_number == 1
    assert finding.column_number == 0
    assert finding.severity is Severity.WARNING


def test_multiple_long_classes_create_separate_findings() -> None:
    """Each class exceeding the threshold should create its own finding."""

    first_class = _build_class_source(
        name="FirstClass",
        body_lines=3,
    )
    second_class = _build_class_source(
        name="SecondClass",
        body_lines=4,
    )
    tree = ast.parse(f"{first_class}\n{second_class}")
    rule = LongClassRule(max_lines=3)

    findings = rule.check(tree, "multiple.py")

    assert len(findings) == 2
    assert {finding.line_number for finding in findings} == {1, 6}
    assert all(finding.severity is Severity.WARNING for finding in findings)


def test_nested_classes_are_checked_separately() -> None:
    """Nested classes should be visited as independent AST nodes."""

    source = """\
class OuterClass:
    outer_value = 1

    class InnerClass:
        inner_value_1 = 1
        inner_value_2 = 2
        inner_value_3 = 3
"""
    tree = ast.parse(source)
    rule = LongClassRule(max_lines=3)

    findings = rule.check(tree, "nested.py")

    assert len(findings) == 2
    assert any("OuterClass" in finding.message for finding in findings)
    assert any("InnerClass" in finding.message for finding in findings)