"""Tests for the machine-readable JSON finding formatter."""

import json
from collections.abc import Iterator

import pytest

from static_analyzer.formatters import format_findings_json
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
    """Create a finding with configurable JSON formatter data."""

    return Finding(
        rule_id=rule_id,
        message=message,
        file_path=file_path,
        line_number=line_number,
        severity=severity,
        column_number=column_number,
    )


def test_empty_list_returns_expected_payload() -> None:
    """An empty list should produce the standard JSON document."""

    result = format_findings_json([])
    payload = json.loads(result)

    assert payload == {
        "findings": [],
        "summary": {
            "total": 0,
        },
    }


def test_empty_tuple_returns_expected_payload() -> None:
    """An empty tuple should produce the standard JSON document."""

    result = format_findings_json(())
    payload = json.loads(result)

    assert payload == {
        "findings": [],
        "summary": {
            "total": 0,
        },
    }


def test_result_is_valid_json_string() -> None:
    """The formatter should return valid JSON text."""

    result = format_findings_json([_finding()])

    assert isinstance(result, str)
    assert json.loads(result)


def test_top_level_findings_field_is_present() -> None:
    """The document should contain a findings list."""

    payload = json.loads(
        format_findings_json([_finding()])
    )

    assert "findings" in payload
    assert isinstance(payload["findings"], list)


def test_top_level_summary_field_is_present() -> None:
    """The document should contain a summary object."""

    payload = json.loads(
        format_findings_json([_finding()])
    )

    assert "summary" in payload
    assert isinstance(payload["summary"], dict)


def test_empty_collection_total_is_zero() -> None:
    """An empty collection should have a zero total."""

    payload = json.loads(format_findings_json([]))

    assert payload["summary"]["total"] == 0


def test_single_finding_is_serialized() -> None:
    """A single finding should produce one JSON object."""

    payload = json.loads(
        format_findings_json([_finding()])
    )

    assert len(payload["findings"]) == 1


def test_multiple_findings_are_serialized() -> None:
    """Multiple findings should produce separate JSON objects."""

    findings = [
        _finding(rule_id="SA001"),
        _finding(rule_id="SA002"),
        _finding(rule_id="SA003"),
    ]

    payload = json.loads(
        format_findings_json(findings)
    )

    assert len(payload["findings"]) == 3


def test_rule_id_field_is_serialized() -> None:
    """The public rule identifier should be included."""

    payload = json.loads(
        format_findings_json(
            [_finding(rule_id="SA004")]
        )
    )

    assert payload["findings"][0]["rule_id"] == "SA004"


def test_message_field_is_serialized() -> None:
    """The original finding message should be included."""

    message = "Custom analysis message."

    payload = json.loads(
        format_findings_json(
            [_finding(message=message)]
        )
    )

    assert payload["findings"][0]["message"] == message


def test_file_path_field_is_serialized_without_changes() -> None:
    """The original file path should be preserved."""

    file_path = "src/nested/Example.py"

    payload = json.loads(
        format_findings_json(
            [_finding(file_path=file_path)]
        )
    )

    assert payload["findings"][0]["file_path"] == file_path


def test_line_number_field_is_serialized() -> None:
    """The source line number should be included."""

    payload = json.loads(
        format_findings_json(
            [_finding(line_number=42)]
        )
    )

    assert payload["findings"][0]["line_number"] == 42


def test_column_number_field_is_serialized() -> None:
    """The source column number should be included."""

    payload = json.loads(
        format_findings_json(
            [_finding(column_number=12)]
        )
    )

    assert payload["findings"][0]["column_number"] == 12


def test_none_column_number_is_serialized_as_null() -> None:
    """A missing column should remain present as JSON null."""

    payload = json.loads(
        format_findings_json(
            [_finding(column_number=None)]
        )
    )

    finding_data = payload["findings"][0]

    assert "column_number" in finding_data
    assert finding_data["column_number"] is None


def test_info_severity_is_serialized_as_lowercase_string() -> None:
    """INFO severity should be serialized as a lowercase string."""

    payload = json.loads(
        format_findings_json(
            [_finding(severity=Severity.INFO)]
        )
    )

    assert payload["findings"][0]["severity"] == "info"


def test_warning_severity_is_serialized_as_lowercase_string() -> None:
    """WARNING severity should be serialized as a lowercase string."""

    payload = json.loads(
        format_findings_json(
            [_finding(severity=Severity.WARNING)]
        )
    )

    assert payload["findings"][0]["severity"] == "warning"


def test_error_severity_is_serialized_as_lowercase_string() -> None:
    """ERROR severity should be serialized as a lowercase string."""

    payload = json.loads(
        format_findings_json(
            [_finding(severity=Severity.ERROR)]
        )
    )

    assert payload["findings"][0]["severity"] == "error"


def test_summary_contains_real_finding_count() -> None:
    """The summary total should match the actual finding count."""

    findings = [
        _finding(rule_id="SA001"),
        _finding(rule_id="SA002"),
        _finding(rule_id="SA003"),
        _finding(rule_id="SA004"),
    ]

    payload = json.loads(
        format_findings_json(findings)
    )

    assert payload["summary"]["total"] == 4


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

    payload = json.loads(
        format_findings_json(
            [
                first_finding,
                second_finding,
            ]
        )
    )

    assert [
        finding_data["message"]
        for finding_data in payload["findings"]
    ] == [
        "First finding.",
        "Second finding.",
    ]


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

    payload = json.loads(
        format_findings_json(generate_findings())
    )

    assert [
        finding_data["message"]
        for finding_data in payload["findings"]
    ] == [
        "First generated finding.",
        "Second generated finding.",
    ]
    assert payload["summary"]["total"] == 2


def test_unicode_characters_are_preserved() -> None:
    """Unicode text should not be converted into ASCII escapes."""

    message = "Güvenlik yapılandırması kontrol edilmeli."

    result = format_findings_json(
        [_finding(message=message)]
    )
    payload = json.loads(result)

    assert payload["findings"][0]["message"] == message
    assert message in result
    assert "\\u00fc" not in result
    assert "\\u0131" not in result


def test_json_uses_two_space_indentation() -> None:
    """The JSON document should use two-space indentation."""

    result = format_findings_json([_finding()])

    assert '\n  "findings": [' in result
    assert "\n    {" in result
    assert '\n      "rule_id":' in result
    assert '\n  "summary": {' in result


def test_result_does_not_end_with_newline() -> None:
    """The formatter should not append a trailing newline."""

    result = format_findings_json([_finding()])

    assert not result.endswith("\n")


def test_finding_objects_are_not_modified() -> None:
    """JSON formatting should not mutate finding data."""

    finding = _finding(
        rule_id="SA003",
        message="TODO comment found.",
        file_path="src/example.py",
        line_number=7,
        column_number=None,
        severity=Severity.INFO,
    )
    finding_before = finding.to_dict()

    format_findings_json([finding])

    assert finding.to_dict() == finding_before


def test_formatter_does_not_write_to_terminal(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The formatter should only return JSON text."""

    result = format_findings_json([_finding()])
    captured = capsys.readouterr()

    assert result
    assert captured.out == ""
    assert captured.err == ""