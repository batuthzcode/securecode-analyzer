"""Tests for the empty except block analysis rule."""

import ast

from static_analyzer.models import Severity
from static_analyzer.rules import BaseRule, EmptyExceptRule


def _parse(source: str) -> ast.AST:
    """Parse Python source code for rule tests."""

    return ast.parse(source)


def test_rule_uses_expected_metadata() -> None:
    """The rule should expose stable public metadata."""

    rule = EmptyExceptRule()

    assert rule.rule_id == "SA004"
    assert rule.name == "Empty Except Block"
    assert rule.description == (
        "Detect except blocks that contain only pass statements."
    )


def test_rule_implements_base_rule() -> None:
    """The rule should implement the AST rule contract."""

    rule = EmptyExceptRule()

    assert isinstance(rule, BaseRule)


def test_empty_source_returns_no_findings() -> None:
    """An empty module should not produce findings."""

    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(""),
        "example.py",
    )

    assert findings == []


def test_synthetic_handler_without_body_is_ignored() -> None:
    """Incomplete AST handlers should fail safely without a finding."""

    handler = ast.ExceptHandler(type=None, name=None, body=[])
    handler.lineno = 1
    handler.col_offset = 0
    tree = ast.Module(body=[handler], type_ignores=[])

    assert EmptyExceptRule().check(tree, "example.py") == []


def test_typed_except_with_only_pass_is_detected() -> None:
    """A typed except containing only pass should be reported."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except Exception:\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_bare_except_with_only_pass_is_detected() -> None:
    """A bare except containing only pass should be reported."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except:\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_handler_with_multiple_pass_statements_is_detected() -> None:
    """Multiple pass statements should still represent an empty handler."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except Exception:\n"
        "    pass\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_comment_and_pass_handler_is_detected() -> None:
    """Comments should not make a pass-only handler non-empty."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except Exception:\n"
        "    # The error is temporarily ignored.\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_handler_with_logging_is_ignored() -> None:
    """A handler containing a logging call should not be reported."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except Exception as error:\n"
        "    logger.exception(error)\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_handler_with_raise_is_ignored() -> None:
    """A handler that re-raises an exception should not be reported."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except Exception:\n"
        "    raise\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_handler_with_operation_and_pass_is_ignored() -> None:
    """A real operation should make the handler non-empty."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except Exception:\n"
        "    recover()\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_multiple_empty_handlers_produce_multiple_findings() -> None:
    """Every empty exception handler should produce a finding."""

    source = (
        "try:\n"
        "    first_operation()\n"
        "except ValueError:\n"
        "    pass\n"
        "\n"
        "try:\n"
        "    second_operation()\n"
        "except RuntimeError:\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 2


def test_nested_empty_handlers_are_detected() -> None:
    """Empty handlers inside nested structures should be reported."""

    source = (
        "def process() -> None:\n"
        "    try:\n"
        "        first_operation()\n"
        "    except ValueError:\n"
        "        pass\n"
        "\n"
        "    class Handler:\n"
        "        def run(self) -> None:\n"
        "            try:\n"
        "                second_operation()\n"
        "            except RuntimeError:\n"
        "                pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 2


def test_empty_except_star_handler_is_detected() -> None:
    """A pass-only except-star handler should be reported."""

    source = (
        "try:\n"
        "    raise ExceptionGroup('errors', [ValueError()])\n"
        "except* ValueError:\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert len(findings) == 1


def test_finding_uses_real_file_path() -> None:
    """The provided file path should be copied into the finding."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except Exception:\n"
        "    pass\n"
    )
    file_path = "src/nested/example.py"
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        file_path,
    )

    assert findings[0].file_path == file_path


def test_finding_uses_except_line_number() -> None:
    """The finding should point to the except statement."""

    source = (
        "value = 1\n"
        "\n"
        "try:\n"
        "    risky_operation()\n"
        "except Exception:\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings[0].line_number == 5


def test_finding_uses_one_based_column_number() -> None:
    """The except column should use one-based indexing."""

    source = (
        "def process() -> None:\n"
        "    try:\n"
        "        risky_operation()\n"
        "    except Exception:\n"
        "        pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings[0].column_number == 5


def test_finding_uses_expected_payload() -> None:
    """The finding should use the expected ID, message, and severity."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except Exception:\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    finding = findings[0]

    assert finding.rule_id == "SA004"
    assert finding.message == "Empty except block found."
    assert finding.severity is Severity.WARNING


def test_findings_preserve_source_order() -> None:
    """Findings should follow their natural order in the source."""

    source = (
        "try:\n"
        "    first_operation()\n"
        "except ValueError:\n"
        "    pass\n"
        "\n"
        "try:\n"
        "    second_operation()\n"
        "except RuntimeError:\n"
        "    pass\n"
        "\n"
        "try:\n"
        "    third_operation()\n"
        "except KeyError:\n"
        "    pass\n"
    )
    rule = EmptyExceptRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert [finding.line_number for finding in findings] == [
        3,
        8,
        13,
    ]


def test_rule_does_not_modify_existing_ast() -> None:
    """Analysis should not mutate the provided AST object."""

    source = (
        "try:\n"
        "    risky_operation()\n"
        "except Exception:\n"
        "    pass\n"
    )
    tree = _parse(source)
    tree_before = ast.dump(
        tree,
        include_attributes=True,
    )
    rule = EmptyExceptRule()

    rule.check(tree, "example.py")

    tree_after = ast.dump(
        tree,
        include_attributes=True,
    )

    assert tree_after == tree_before
