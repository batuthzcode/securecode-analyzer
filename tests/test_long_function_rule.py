"""Tests for the long function analysis rule."""

import ast
from typing import Any

import pytest

from static_analyzer.models import Severity
from static_analyzer.rules import LongFunctionRule


def _build_function_source(
    *,
    name: str = "example_function",
    body_lines: int,
    is_async: bool = False,
) -> str:
    """Build a Python function containing the requested number of body lines."""

    function_keyword = "async def" if is_async else "def"
    body = "\n".join(
        f"    value_{line_number} = {line_number}"
        for line_number in range(body_lines)
    )

    return f"{function_keyword} {name}():\n{body}\n"


def test_long_function_rule_uses_default_threshold() -> None:
    """The rule should use fifty lines as its default threshold."""

    rule = LongFunctionRule()

    assert rule.max_lines == 50


@pytest.mark.parametrize("max_lines", [0, -1, True, 1.5])
def test_long_function_rule_rejects_invalid_thresholds(
    max_lines: Any,
) -> None:
    """The rule should reject invalid function-length thresholds."""

    with pytest.raises(ValueError, match="max_lines must be greater than zero"):
        LongFunctionRule(max_lines=max_lines)


def test_function_equal_to_threshold_does_not_create_finding() -> None:
    """A function equal to the configured limit should be accepted."""

    source = _build_function_source(body_lines=2)
    tree = ast.parse(source)
    rule = LongFunctionRule(max_lines=3)

    findings = rule.check(tree, "example.py")

    assert findings == []


def test_long_function_creates_expected_finding() -> None:
    """A function exceeding the limit should create one complete finding."""

    source = _build_function_source(
        name="process_data",
        body_lines=3,
    )
    tree = ast.parse(source)
    rule = LongFunctionRule(max_lines=3)

    findings = rule.check(tree, "example.py")

    assert len(findings) == 1

    finding = findings[0]

    assert finding.rule_id == "SA001"
    assert finding.message == (
        "Function 'process_data' has 4 lines, exceeding the limit of 3."
    )
    assert finding.file_path == "example.py"
    assert finding.line_number == 1
    assert finding.column_number == 0
    assert finding.severity is Severity.WARNING


def test_long_async_function_creates_finding() -> None:
    """An asynchronous function should be analyzed like a normal function."""

    source = _build_function_source(
        name="fetch_data",
        body_lines=3,
        is_async=True,
    )
    tree = ast.parse(source)
    rule = LongFunctionRule(max_lines=3)

    findings = rule.check(tree, "async_example.py")

    assert len(findings) == 1
    assert "fetch_data" in findings[0].message


def test_multiple_long_functions_create_separate_findings() -> None:
    """Each function exceeding the threshold should create its own finding."""

    first_function = _build_function_source(
        name="first_function",
        body_lines=3,
    )
    second_function = _build_function_source(
        name="second_function",
        body_lines=4,
    )
    tree = ast.parse(f"{first_function}\n{second_function}")
    rule = LongFunctionRule(max_lines=3)

    findings = rule.check(tree, "multiple.py")

    assert len(findings) == 2
    assert {finding.line_number for finding in findings} == {1, 6}
    assert all(finding.severity is Severity.WARNING for finding in findings)


def test_nested_functions_are_checked_separately() -> None:
    """Nested functions should be visited as independent AST nodes."""

    source = """\
def outer_function():
    outer_value = 1

    def inner_function():
        inner_value_1 = 1
        inner_value_2 = 2
        inner_value_3 = 3
"""
    tree = ast.parse(source)
    rule = LongFunctionRule(max_lines=3)

    findings = rule.check(tree, "nested.py")

    assert len(findings) == 2
    assert any("outer_function" in finding.message for finding in findings)
    assert any("inner_function" in finding.message for finding in findings)