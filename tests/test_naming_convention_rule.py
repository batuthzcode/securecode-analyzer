"""Tests for the Python naming convention analysis rule."""

import ast

from static_analyzer.models import Severity
from static_analyzer.rules import BaseRule, NamingConventionRule


def _parse(source: str) -> ast.AST:
    """Parse Python source code for naming rule tests."""

    return ast.parse(source)


def test_rule_uses_expected_metadata() -> None:
    """The rule should expose stable public metadata."""

    rule = NamingConventionRule()

    assert rule.rule_id == "SA006"
    assert rule.name == "Naming Convention"
    assert rule.description == (
        "Detect function and class names that violate naming conventions."
    )


def test_rule_implements_base_rule() -> None:
    """The rule should implement the AST rule contract."""

    rule = NamingConventionRule()

    assert isinstance(rule, BaseRule)


def test_empty_source_returns_no_findings() -> None:
    """An empty module should not produce findings."""

    rule = NamingConventionRule()

    findings = rule.check(
        _parse(""),
        "example.py",
    )

    assert findings == []


def test_valid_snake_case_function_is_accepted() -> None:
    """A snake_case function name should not be reported."""

    source = (
        "def calculate_total() -> int:\n"
        "    return 0\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_leading_underscore_function_is_accepted() -> None:
    """A private snake_case function should not be reported."""

    source = (
        "def _internal_helper() -> None:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_pascal_case_function_is_reported() -> None:
    """A PascalCase function name should produce a finding."""

    source = (
        "def CalculateTotal() -> int:\n"
        "    return 0\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_camel_case_function_is_reported() -> None:
    """A camelCase function name should produce a finding."""

    source = (
        "def calculateTotal() -> int:\n"
        "    return 0\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_valid_async_function_is_accepted() -> None:
    """A snake_case asynchronous function should be accepted."""

    source = (
        "async def fetch_user_data() -> None:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_invalid_async_function_is_reported() -> None:
    """An invalid asynchronous function name should be reported."""

    source = (
        "async def FetchUserData() -> None:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_dunder_methods_are_ignored() -> None:
    """Python special methods should not produce findings."""

    source = (
        "class Example:\n"
        "    def __init__(self) -> None:\n"
        "        pass\n"
        "\n"
        "    def __str__(self) -> str:\n"
        '        return "Example"\n'
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_valid_pascal_case_class_is_accepted() -> None:
    """A PascalCase class name should not be reported."""

    source = (
        "class UserService:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_private_and_acronym_class_names_are_accepted() -> None:
    """Private and acronym-based PascalCase names should be accepted."""

    source = (
        "class _InternalHandler:\n"
        "    pass\n"
        "\n"
        "class HTTPClient:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_snake_case_class_is_reported() -> None:
    """A snake_case class name should produce a finding."""

    source = (
        "class user_service:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_camel_case_class_is_reported() -> None:
    """A camelCase class name should produce a finding."""

    source = (
        "class userService:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_invalid_class_method_is_reported() -> None:
    """Methods should use the same snake_case function convention."""

    source = (
        "class UserService:\n"
        "    def FetchUser(self) -> None:\n"
        "        pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1
    assert findings[0].message == (
        "Function name should use snake_case."
    )


def test_invalid_nested_function_is_reported() -> None:
    """Nested functions should also be checked."""

    source = (
        "def outer_function() -> None:\n"
        "    def InnerFunction() -> None:\n"
        "        pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1
    assert findings[0].line_number == 2


def test_invalid_nested_class_is_reported() -> None:
    """Nested classes should also be checked."""

    source = (
        "class OuterClass:\n"
        "    class inner_class:\n"
        "        pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1
    assert findings[0].line_number == 2


def test_multiple_invalid_names_produce_multiple_findings() -> None:
    """Every invalid definition should produce a finding."""

    source = (
        "def BadFunction() -> None:\n"
        "    pass\n"
        "\n"
        "class bad_class:\n"
        "    pass\n"
        "\n"
        "async def BadAsyncFunction() -> None:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 3


def test_finding_uses_real_file_path() -> None:
    """The provided file path should be copied into the finding."""

    file_path = "src/nested/example.py"
    source = (
        "def BadFunction() -> None:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        file_path,
    )

    assert findings[0].file_path == file_path


def test_finding_uses_definition_line_and_column() -> None:
    """The finding should use the definition location."""

    source = (
        "class UserService:\n"
        "    def BadMethod(self) -> None:\n"
        "        pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings[0].line_number == 2
    assert findings[0].column_number == 5


def test_function_finding_uses_expected_payload() -> None:
    """Invalid function findings should use the expected payload."""

    source = (
        "def BadFunction() -> None:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    finding = findings[0]

    assert finding.rule_id == "SA006"
    assert finding.message == (
        "Function name should use snake_case."
    )
    assert finding.severity is Severity.INFO


def test_class_finding_uses_expected_payload() -> None:
    """Invalid class findings should use the expected payload."""

    source = (
        "class bad_class:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    finding = findings[0]

    assert finding.rule_id == "SA006"
    assert finding.message == (
        "Class name should use PascalCase."
    )
    assert finding.severity is Severity.INFO


def test_all_findings_use_info_severity() -> None:
    """Naming findings should use INFO severity."""

    source = (
        "def BadFunction() -> None:\n"
        "    pass\n"
        "\n"
        "class bad_class:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert all(
        finding.severity is Severity.INFO
        for finding in findings
    )


def test_findings_preserve_source_order() -> None:
    """Findings should follow their natural source-code order."""

    source = (
        "def BadFunction() -> None:\n"
        "    pass\n"
        "\n"
        "class bad_class:\n"
        "    pass\n"
        "\n"
        "async def BadAsyncFunction() -> None:\n"
        "    pass\n"
    )
    rule = NamingConventionRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert [finding.line_number for finding in findings] == [
        1,
        4,
        7,
    ]

    assert [finding.message for finding in findings] == [
        "Function name should use snake_case.",
        "Class name should use PascalCase.",
        "Function name should use snake_case.",
    ]


def test_rule_does_not_modify_existing_ast() -> None:
    """Analysis should not mutate the provided AST object."""

    source = (
        "def BadFunction() -> None:\n"
        "    pass\n"
        "\n"
        "class bad_class:\n"
        "    pass\n"
    )
    tree = _parse(source)
    tree_before = ast.dump(
        tree,
        include_attributes=True,
    )
    rule = NamingConventionRule()

    rule.check(tree, "example.py")

    tree_after = ast.dump(
        tree,
        include_attributes=True,
    )

    assert tree_after == tree_before