"""Tests for the dependency scan JSON formatter."""

import json

import dependency_scanner
import pytest

from dependency_scanner import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    DependencyScanError,
    DependencyScanResult,
    VulnerabilitySeverity,
    format_dependency_scan_json,
)


def _dependency(
    *,
    name: str = "sample-package",
    version: str = "1.0.0",
    source_file: str = "requirements.txt",
    line_number: int = 2,
) -> Dependency:
    """Create a dependency with configurable JSON fields."""

    return Dependency(
        name=name,
        version=version,
        operator="==",
        source_file=source_file,
        line_number=line_number,
    )


def _source(name: str = "OSV") -> AdvisorySource:
    """Create an advisory source used by JSON tests."""

    return AdvisorySource(
        name=name,
        url="https://osv.dev/",
    )


def _finding(
    dependency: Dependency | None = None,
    *,
    advisory_id: str = "OSV-EXAMPLE",
    message: str = "Example vulnerability.",
) -> DependencyFinding:
    """Create a finding with representative JSON data."""

    return DependencyFinding(
        dependency=dependency or _dependency(),
        advisory_id=advisory_id,
        message=message,
        source=_source(),
        severity=VulnerabilitySeverity.HIGH,
        fixed_version="2.0.0",
        aliases=("CVE-2099-0001",),
    )


def _error(
    dependency: Dependency | None = None,
    *,
    message: str = "Service unavailable.",
) -> DependencyScanError:
    """Create a lookup error with representative JSON data."""

    return DependencyScanError(
        dependency=dependency or _dependency(),
        source=_source(),
        message=message,
    )


def test_json_formatter_is_publicly_exported() -> None:
    """The package API should expose the JSON formatter."""

    assert (
        dependency_scanner.format_dependency_scan_json
        is format_dependency_scan_json
    )


def test_empty_successful_result_uses_expected_payload() -> None:
    """An empty result should serialize all document sections."""

    result = format_dependency_scan_json(
        DependencyScanResult()
    )

    assert json.loads(result) == {
        "dependencies": [],
        "findings": [],
        "errors": [],
        "summary": {
            "dependencies": 0,
            "findings": 0,
            "errors": 0,
            "succeeded": True,
        },
    }


def test_result_is_valid_json_string() -> None:
    """The formatter should return parseable JSON text."""

    result = format_dependency_scan_json(
        DependencyScanResult()
    )

    assert isinstance(result, str)
    assert isinstance(json.loads(result), dict)


def test_dependency_is_serialized_with_existing_contract() -> None:
    """Dependency data should use its public dictionary shape."""

    dependency = _dependency(
        name="example",
        version="3.4.5",
        source_file="config/requirements.txt",
        line_number=8,
    )

    payload = json.loads(
        format_dependency_scan_json(
            DependencyScanResult(
                dependencies=(dependency,),
            )
        )
    )

    assert payload["dependencies"] == [
        dependency.to_dict()
    ]


def test_finding_nested_fields_are_serialized() -> None:
    """Finding data should retain nested models and optionals."""

    dependency = _dependency()
    finding = _finding(dependency)

    payload = json.loads(
        format_dependency_scan_json(
            DependencyScanResult(
                dependencies=(dependency,),
                findings=(finding,),
            )
        )
    )

    assert payload["findings"] == [finding.to_dict()]
    assert payload["findings"][0] == {
        "dependency": dependency.to_dict(),
        "advisory_id": "OSV-EXAMPLE",
        "message": "Example vulnerability.",
        "source": _source().to_dict(),
        "severity": "high",
        "fixed_version": "2.0.0",
        "aliases": ["CVE-2099-0001"],
    }


def test_error_nested_fields_are_serialized() -> None:
    """Lookup errors should retain dependency and source data."""

    dependency = _dependency()
    error = _error(dependency)

    payload = json.loads(
        format_dependency_scan_json(
            DependencyScanResult(
                dependencies=(dependency,),
                errors=(error,),
            )
        )
    )

    assert payload["errors"] == [
        {
            "dependency": dependency.to_dict(),
            "source": _source().to_dict(),
            "message": "Service unavailable.",
        }
    ]


def test_summary_contains_real_counts_and_success() -> None:
    """Summary values should reflect the complete result."""

    first = _dependency(name="first", line_number=1)
    second = _dependency(name="second", line_number=2)
    finding = _finding(first)
    error = _error(second)

    payload = json.loads(
        format_dependency_scan_json(
            DependencyScanResult(
                dependencies=(first, second),
                findings=(finding,),
                errors=(error,),
            )
        )
    )

    assert payload["summary"] == {
        "dependencies": 2,
        "findings": 1,
        "errors": 1,
        "succeeded": False,
    }


def test_finding_and_error_order_is_preserved() -> None:
    """Both result collections should retain their input order."""

    first_finding = _finding(
        advisory_id="OSV-SECOND-NUMBER",
        message="First finding.",
    )
    second_finding = _finding(
        advisory_id="OSV-FIRST-NUMBER",
        message="Second finding.",
    )
    first_error = _error(message="First error.")
    second_error = _error(message="Second error.")

    payload = json.loads(
        format_dependency_scan_json(
            DependencyScanResult(
                findings=(
                    first_finding,
                    second_finding,
                ),
                errors=(first_error, second_error),
            )
        )
    )

    assert [
        finding["message"]
        for finding in payload["findings"]
    ] == ["First finding.", "Second finding."]
    assert [
        error["message"]
        for error in payload["errors"]
    ] == ["First error.", "Second error."]


def test_unicode_characters_are_preserved() -> None:
    """Unicode text should not be converted into ASCII escapes."""

    message = "Güvenlik kaynağına erişilemedi."

    result = format_dependency_scan_json(
        DependencyScanResult(
            errors=(_error(message=message),),
        )
    )
    payload = json.loads(result)

    assert payload["errors"][0]["message"] == message
    assert message in result
    assert "\\u00fc" not in result
    assert "\\u0131" not in result


def test_json_uses_two_space_indentation() -> None:
    """The JSON document should use two-space indentation."""

    result = format_dependency_scan_json(
        DependencyScanResult(
            dependencies=(_dependency(),),
        )
    )

    assert '\n  "dependencies": [' in result
    assert "\n    {" in result
    assert '\n      "name":' in result
    assert '\n  "summary": {' in result


def test_result_does_not_end_with_newline() -> None:
    """The JSON document should not append a trailing newline."""

    result = format_dependency_scan_json(
        DependencyScanResult()
    )

    assert not result.endswith("\n")


def test_formatting_does_not_modify_models() -> None:
    """JSON formatting should leave every model unchanged."""

    dependency = _dependency()
    finding = _finding(dependency)
    error = _error(dependency)
    result_model = DependencyScanResult(
        dependencies=(dependency,),
        findings=(finding,),
        errors=(error,),
    )
    before = (
        dependency.to_dict(),
        finding.to_dict(),
        error.message,
        result_model,
    )

    format_dependency_scan_json(result_model)

    assert dependency.to_dict() == before[0]
    assert finding.to_dict() == before[1]
    assert error.message == before[2]
    assert result_model == before[3]


def test_formatter_does_not_write_to_terminal(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The formatter should only return JSON text."""

    result = format_dependency_scan_json(
        DependencyScanResult(findings=(_finding(),))
    )
    captured = capsys.readouterr()

    assert result
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize(
    "invalid_result",
    [
        None,
        (),
        object(),
    ],
)
def test_invalid_result_is_rejected(
    invalid_result: object,
) -> None:
    """JSON formatting should require a scan result model."""

    with pytest.raises(
        ValueError,
        match="DependencyScanResult",
    ):
        format_dependency_scan_json(
            invalid_result  # type: ignore[arg-type]
        )
