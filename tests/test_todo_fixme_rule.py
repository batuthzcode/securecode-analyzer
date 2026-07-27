"""Tests for the TODO and FIXME comment analysis rule."""

from static_analyzer.models import Severity
from static_analyzer.rules import BaseTextRule, TodoFixmeRule


def test_rule_uses_expected_metadata() -> None:
    """The rule should expose stable public metadata."""

    rule = TodoFixmeRule()

    assert rule.rule_id == "SA003"
    assert rule.name == "TODO/FIXME Comment"
    assert rule.description == (
        "Detect TODO and FIXME markers in Python comments."
    )


def test_rule_implements_base_text_rule() -> None:
    """The rule should implement the text-rule contract."""

    rule = TodoFixmeRule()

    assert isinstance(rule, BaseTextRule)


def test_empty_source_returns_no_findings() -> None:
    """Empty source code should not produce findings."""

    rule = TodoFixmeRule()

    findings = rule.check("", "example.py")

    assert findings == []


def test_source_without_comments_returns_no_findings() -> None:
    """Python code without comments should not produce findings."""

    source = "value = 1\nprint(value)\n"
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert findings == []


def test_uppercase_todo_comment_is_detected() -> None:
    """An uppercase TODO marker should produce a finding."""

    source = "# TODO: add validation\n"
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert len(findings) == 1
    assert findings[0].message == "TODO comment found."


def test_lowercase_todo_comment_is_detected() -> None:
    """TODO detection should be case-insensitive."""

    source = "# todo: add validation\n"
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert len(findings) == 1
    assert findings[0].message == "TODO comment found."


def test_uppercase_fixme_comment_is_detected() -> None:
    """An uppercase FIXME marker should produce a finding."""

    source = "# FIXME: handle invalid input\n"
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert len(findings) == 1
    assert findings[0].message == "FIXME comment found."


def test_lowercase_fixme_comment_is_detected() -> None:
    """FIXME detection should be case-insensitive."""

    source = "# fixme: handle invalid input\n"
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert len(findings) == 1
    assert findings[0].message == "FIXME comment found."


def test_multiple_comments_produce_multiple_findings() -> None:
    """Every TODO and FIXME marker should produce a finding."""

    source = (
        "# TODO: add validation\n"
        "value = 1\n"
        "# FIXME: remove fallback\n"
    )
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert len(findings) == 2
    assert findings[0].message == "TODO comment found."
    assert findings[1].message == "FIXME comment found."


def test_multiple_markers_in_same_comment_are_detected() -> None:
    """Multiple markers in one comment should produce separate findings."""

    source = "# TODO: review this, FIXME: remove fallback\n"
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert len(findings) == 2
    assert findings[0].message == "TODO comment found."
    assert findings[1].message == "FIXME comment found."


def test_marker_inside_string_literal_is_ignored() -> None:
    """Markers inside strings should not produce findings."""

    source = 'message = "TODO: this is only text"\n'
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert findings == []


def test_marker_inside_variable_name_is_ignored() -> None:
    """Markers inside Python identifiers should not produce findings."""

    source = 'variable_todo = "value"\nfixme_value = 1\n'
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert findings == []


def test_non_independent_markers_are_ignored() -> None:
    """Markers should be detected only as independent words."""

    source = (
        "# TODOLIST should not match\n"
        "# PREFIXFIXME should not match\n"
        "# TODO123 should not match\n"
    )
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert findings == []


def test_finding_uses_real_file_path() -> None:
    """The provided file path should be copied into the finding."""

    file_path = "src/nested/example.py"
    rule = TodoFixmeRule()

    findings = rule.check(
        "# TODO: improve this\n",
        file_path,
    )

    assert findings[0].file_path == file_path


def test_finding_uses_correct_line_number() -> None:
    """The finding should contain the marker's source line."""

    source = (
        "value = 1\n"
        "\n"
        "# TODO: improve this\n"
    )
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert findings[0].line_number == 3


def test_finding_uses_one_based_column_number() -> None:
    """The marker column should be reported using one-based indexing."""

    source = "    # TODO: improve this\n"
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert findings[0].column_number == 7


def test_findings_preserve_source_order() -> None:
    """Findings should follow their natural order in the source."""

    source = (
        "# FIXME: first marker\n"
        "# TODO: second marker\n"
        "# FIXME: third marker\n"
    )
    rule = TodoFixmeRule()

    findings = rule.check(source, "example.py")

    assert [finding.message for finding in findings] == [
        "FIXME comment found.",
        "TODO comment found.",
        "FIXME comment found.",
    ]
    assert [finding.line_number for finding in findings] == [
        1,
        2,
        3,
    ]


def test_todo_finding_uses_info_severity() -> None:
    """TODO findings should use INFO severity."""

    rule = TodoFixmeRule()

    findings = rule.check(
        "# TODO: improve this\n",
        "example.py",
    )

    assert findings[0].severity is Severity.INFO


def test_fixme_finding_uses_warning_severity() -> None:
    """FIXME findings should use WARNING severity."""

    rule = TodoFixmeRule()

    findings = rule.check(
        "# FIXME: repair this\n",
        "example.py",
    )

    assert findings[0].severity is Severity.WARNING