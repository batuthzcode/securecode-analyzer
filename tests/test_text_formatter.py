"""Tests for the human-readable text finding formatter."""

from collections.abc import Iterator

import pytest

from static_analyzer.formatters.text import format_findings_text
from static_analyzer.models import Finding, Severity


def _finding(
    *,
    rule_id: str = "SA005",
    message: str = "Possible hardcoded secret found.",
    file_path: str = "src/example.py",
    line_number: int = 1,
    column_number: int | None = 1,
    severity: Severity = Severity.WARNING,
) -> Finding:
    """Create a finding with configurable formatter data."""

    return Finding(
        rule_id=rule_id,
        message=message,
        file_path=file_path,
        line_number=line_number,
        severity=severity,
        column_number=column_number,
    )


def test_empty_list_returns_no_findings_message() -> None:
    """An empty list should produce the standard empty message."""

    result = format_findings_text([])

    assert result == "No findings found."


def test_empty_tuple_returns_no_findings_message() -> None:
    """An empty tuple should produce the standard empty message."""

    result = format_findings_text(())

    assert result == "No findings found."


def test_single_finding_uses_expected_format() -> None:
    """A single finding should use the complete text format."""

    finding = _finding()

    result = format_findings_text([finding])

    assert result == (
        "[WARNING] SA005 src/example.py:1:1"
        " - Possible hardcoded secret found.\n"
        "\n"
        "1 finding found."
    )


def test_multiple_findings_use_expected_format() -> None:
    """Multiple findings should appear on separate lines."""

    first_finding = _finding(
        file_path="src/config.py",
        line_number=1,
        column_number=1,
    )
    second_finding = _finding(
        rule_id="SA006",
        message="Function name should use snake_case.",
        file_path="src/config.py",
        line_number=3,
        column_number=1,
        severity=Severity.INFO,
    )

    result = format_findings_text(
        [
            first_finding,
            second_finding,
        ]
    )

    assert result == (
        "[WARNING] SA005 src/config.py:1:1"
        " - Possible hardcoded secret found.\n"
        "[INFO] SA006 src/config.py:3:1"
        " - Function name should use snake_case.\n"
        "\n"
        "2 findings found."
    )


def test_info_severity_is_uppercase() -> None:
    """INFO severity should be displayed in uppercase."""

    finding = _finding(severity=Severity.INFO)

    result = format_findings_text([finding])

    assert result.startswith("[INFO]")


def test_warning_severity_is_uppercase() -> None:
    """WARNING severity should be displayed in uppercase."""

    finding = _finding(severity=Severity.WARNING)

    result = format_findings_text([finding])

    assert result.startswith("[WARNING]")


def test_error_severity_is_uppercase() -> None:
    """ERROR severity should be displayed in uppercase."""

    finding = _finding(severity=Severity.ERROR)

    result = format_findings_text([finding])

    assert result.startswith("[ERROR]")


def test_rule_id_is_included() -> None:
    """The finding rule identifier should be displayed."""

    finding = _finding(rule_id="SA004")

    result = format_findings_text([finding])

    assert "SA004" in result


def test_file_path_is_included_without_normalization() -> None:
    """The original finding file path should be displayed."""

    file_path = "src/nested/Example.py"
    finding = _finding(file_path=file_path)

    result = format_findings_text([finding])

    assert file_path in result


def test_line_number_is_included() -> None:
    """The source line number should be displayed."""

    finding = _finding(
        file_path="src/example.py",
        line_number=42,
        column_number=None,
    )

    result = format_findings_text([finding])

    assert "src/example.py:42" in result


def test_column_number_is_included_when_available() -> None:
    """The source column number should be displayed when present."""

    finding = _finding(
        file_path="src/example.py",
        line_number=8,
        column_number=12,
    )

    result = format_findings_text([finding])

    assert "src/example.py:8:12" in result


def test_none_column_number_is_omitted() -> None:
    """A missing column number should not appear in the output."""

    finding = _finding(
        rule_id="SA003",
        message="TODO comment found.",
        file_path="src/example.py",
        line_number=8,
        column_number=None,
        severity=Severity.INFO,
    )

    result = format_findings_text([finding])

    assert result == (
        "[INFO] SA003 src/example.py:8"
        " - TODO comment found.\n"
        "\n"
        "1 finding found."
    )
    assert ":None" not in result


def test_finding_message_is_included_without_changes() -> None:
    """The original finding message should be displayed."""

    message = "Custom analysis message."
    finding = _finding(message=message)

    result = format_findings_text([finding])

    assert message in result


def test_single_finding_uses_singular_summary() -> None:
    """One finding should use the singular summary form."""

    result = format_findings_text([_finding()])

    assert result.endswith("1 finding found.")


def test_multiple_findings_use_plural_summary() -> None:
    """Multiple findings should use the plural summary form."""

    result = format_findings_text(
        [
            _finding(rule_id="SA001"),
            _finding(rule_id="SA002"),
            _finding(rule_id="SA003"),
        ]
    )

    assert result.endswith("3 findings found.")


def test_findings_are_separated_by_newline() -> None:
    """Finding records should be written on separate lines."""

    first_finding = _finding(
        rule_id="SA001",
        message="First finding.",
    )
    second_finding = _finding(
        rule_id="SA002",
        message="Second finding.",
    )

    result = format_findings_text(
        [
            first_finding,
            second_finding,
        ]
    )

    assert "First finding.\n[WARNING] SA002" in result


def test_blank_line_appears_before_summary() -> None:
    """A blank line should separate findings from the summary."""

    result = format_findings_text(
        [
            _finding(rule_id="SA001"),
            _finding(rule_id="SA002"),
        ]
    )

    assert "\n\n2 findings found." in result


def test_input_order_is_preserved() -> None:
    """The formatter should not reorder findings."""

    first_finding = _finding(
        rule_id="SA006",
        message="First finding.",
        line_number=30,
    )
    second_finding = _finding(
        rule_id="SA001",
        message="Second finding.",
        line_number=1,
    )

    result = format_findings_text(
        [
            first_finding,
            second_finding,
        ]
    )

    assert result.index("First finding.") < result.index(
        "Second finding."
    )


def test_generator_input_is_supported() -> None:
    """A single-use finding generator should be supported."""

    def generate_findings() -> Iterator[Finding]:
        yield _finding(
            rule_id="SA001",
            message="First generated finding.",
        )
        yield _finding(
            rule_id="SA002",
            message="Second generated finding.",
        )

    result = format_findings_text(generate_findings())

    assert "First generated finding." in result
    assert "Second generated finding." in result
    assert result.endswith("2 findings found.")


def test_result_does_not_end_with_newline() -> None:
    """The formatter should not append a trailing newline."""

    result = format_findings_text([_finding()])

    assert not result.endswith("\n")


def test_finding_objects_are_not_modified() -> None:
    """Formatting should not mutate finding data."""

    finding = _finding(
        rule_id="SA003",
        message="TODO comment found.",
        file_path="src/example.py",
        line_number=7,
        column_number=None,
        severity=Severity.INFO,
    )
    finding_before = finding.to_dict()

    format_findings_text([finding])

    assert finding.to_dict() == finding_before


def test_formatter_does_not_write_to_terminal(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The formatter should only return text."""

    result = format_findings_text([_finding()])
    captured = capsys.readouterr()

    assert result
    assert captured.out == ""
    assert captured.err == ""