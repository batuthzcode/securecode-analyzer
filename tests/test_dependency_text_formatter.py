"""Tests for the dependency scan text formatter."""

import dependency_scanner
import pytest

from dependency_scanner import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    DependencyScanError,
    DependencyScanResult,
    VulnerabilitySeverity,
    format_dependency_scan_text,
)


def _dependency(
    *,
    name: str = "sample-package",
    version: str = "1.0.0",
    source_file: str = "requirements.txt",
    line_number: int = 2,
) -> Dependency:
    """Create a dependency with configurable output fields."""

    return Dependency(
        name=name,
        version=version,
        operator="==",
        source_file=source_file,
        line_number=line_number,
    )


def _source(name: str = "OSV") -> AdvisorySource:
    """Create an advisory source used by formatter tests."""

    return AdvisorySource(
        name=name,
        url="https://osv.dev/",
    )


def _finding(
    dependency: Dependency | None = None,
    *,
    advisory_id: str = "OSV-EXAMPLE",
    message: str = "Example vulnerability.",
    severity: VulnerabilitySeverity = (
        VulnerabilitySeverity.HIGH
    ),
    fixed_version: str | None = "2.0.0",
    aliases: tuple[str, ...] = ("CVE-2099-0001",),
) -> DependencyFinding:
    """Create a finding with configurable output fields."""

    return DependencyFinding(
        dependency=dependency or _dependency(),
        advisory_id=advisory_id,
        message=message,
        source=_source(),
        severity=severity,
        fixed_version=fixed_version,
        aliases=aliases,
    )


def _error(
    dependency: Dependency | None = None,
    *,
    source_name: str = "OSV",
    message: str = "Service unavailable.",
) -> DependencyScanError:
    """Create a lookup error with configurable output fields."""

    return DependencyScanError(
        dependency=dependency or _dependency(),
        source=_source(source_name),
        message=message,
    )


def test_text_formatter_is_publicly_exported() -> None:
    """The package API should expose the text formatter."""

    assert (
        dependency_scanner.format_dependency_scan_text
        is format_dependency_scan_text
    )


def test_empty_successful_result_uses_expected_text() -> None:
    """An empty successful scan should include a clean message."""

    result = format_dependency_scan_text(
        DependencyScanResult()
    )

    assert result == (
        "No dependency vulnerabilities found.\n"
        "\n"
        "0 dependencies scanned. 0 findings. "
        "0 lookup errors."
    )


def test_clean_dependency_is_counted() -> None:
    """A scanned clean dependency should appear in the summary."""

    dependency = _dependency()
    result = format_dependency_scan_text(
        DependencyScanResult(
            dependencies=(dependency,),
        )
    )

    assert result == (
        "No dependency vulnerabilities found.\n"
        "\n"
        "1 dependency scanned. 0 findings. "
        "0 lookup errors."
    )


def test_finding_uses_complete_expected_format() -> None:
    """A finding should include every available public field."""

    dependency = _dependency()
    finding = _finding(dependency)

    result = format_dependency_scan_text(
        DependencyScanResult(
            dependencies=(dependency,),
            findings=(finding,),
        )
    )

    assert result == (
        "[HIGH] OSV-EXAMPLE sample-package==1.0.0 "
        "requirements.txt:2 - Example vulnerability. "
        "| source=OSV | fixed=2.0.0 "
        "| aliases=CVE-2099-0001\n"
        "\n"
        "1 dependency scanned. 1 finding. "
        "0 lookup errors."
    )


def test_missing_optional_finding_fields_are_omitted() -> None:
    """Missing fixes and aliases should not produce placeholders."""

    finding = _finding(
        fixed_version=None,
        aliases=(),
    )

    result = format_dependency_scan_text(
        DependencyScanResult(findings=(finding,))
    )

    assert " | fixed=" not in result
    assert " | aliases=" not in result
    assert "| source=OSV\n" in result


@pytest.mark.parametrize(
    "severity",
    list(VulnerabilitySeverity),
)
def test_severity_is_uppercase(
    severity: VulnerabilitySeverity,
) -> None:
    """Every supported severity should use uppercase text."""

    finding = _finding(severity=severity)

    result = format_dependency_scan_text(
        DependencyScanResult(findings=(finding,))
    )

    assert result.startswith(
        f"[{severity.value.upper()}]"
    )


def test_finding_order_is_preserved() -> None:
    """Findings should remain in result order."""

    first = _finding(
        advisory_id="OSV-SECOND-NUMBER",
        message="First result item.",
    )
    second = _finding(
        advisory_id="OSV-FIRST-NUMBER",
        message="Second result item.",
    )

    result = format_dependency_scan_text(
        DependencyScanResult(
            findings=(first, second),
        )
    )

    assert result.index("First result item.") < result.index(
        "Second result item."
    )


def test_lookup_error_uses_expected_format() -> None:
    """A lookup error should include its dependency and source."""

    dependency = _dependency()
    error = _error(dependency)

    result = format_dependency_scan_text(
        DependencyScanResult(
            dependencies=(dependency,),
            errors=(error,),
        )
    )

    assert result == (
        "[LOOKUP ERROR] OSV sample-package==1.0.0 "
        "requirements.txt:2 - Service unavailable.\n"
        "\n"
        "1 dependency scanned. 0 findings. "
        "1 lookup error."
    )


def test_multiple_lookup_errors_preserve_order() -> None:
    """Lookup errors should remain in result order."""

    first = _error(
        _dependency(name="first", line_number=1),
        message="First lookup failed.",
    )
    second = _error(
        _dependency(name="second", line_number=2),
        message="Second lookup failed.",
    )

    result = format_dependency_scan_text(
        DependencyScanResult(errors=(first, second))
    )

    assert result.index("First lookup failed.") < result.index(
        "Second lookup failed."
    )
    assert result.endswith("2 lookup errors.")


def test_findings_appear_before_errors() -> None:
    """Finding records should precede lookup error records."""

    finding = _finding(message="Finding record.")
    error = _error(message="Error record.")

    result = format_dependency_scan_text(
        DependencyScanResult(
            findings=(finding,),
            errors=(error,),
        )
    )

    assert result.index("Finding record.") < result.index(
        "Error record."
    )


@pytest.mark.parametrize(
    (
        "dependencies",
        "findings",
        "errors",
        "expected_summary",
    ),
    [
        (
            (_dependency(),),
            (_finding(),),
            (_error(),),
            "1 dependency scanned. 1 finding. "
            "1 lookup error.",
        ),
        (
            (_dependency(), _dependency()),
            (_finding(), _finding()),
            (_error(), _error()),
            "2 dependencies scanned. 2 findings. "
            "2 lookup errors.",
        ),
    ],
)
def test_summary_uses_correct_singular_and_plural_words(
    dependencies: tuple[Dependency, ...],
    findings: tuple[DependencyFinding, ...],
    errors: tuple[DependencyScanError, ...],
    expected_summary: str,
) -> None:
    """Summary words should match their actual counts."""

    result = format_dependency_scan_text(
        DependencyScanResult(
            dependencies=dependencies,
            findings=findings,
            errors=errors,
        )
    )

    assert result.endswith(expected_summary)


def test_result_does_not_end_with_newline() -> None:
    """The text document should not append a trailing newline."""

    result = format_dependency_scan_text(
        DependencyScanResult()
    )

    assert not result.endswith("\n")


def test_formatting_does_not_modify_models() -> None:
    """Text formatting should leave every model unchanged."""

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

    format_dependency_scan_text(result_model)

    assert dependency.to_dict() == before[0]
    assert finding.to_dict() == before[1]
    assert error.message == before[2]
    assert result_model == before[3]


def test_formatter_does_not_write_to_terminal(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The formatter should only return text."""

    result = format_dependency_scan_text(
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
    """Text formatting should require a scan result model."""

    with pytest.raises(
        ValueError,
        match="DependencyScanResult",
    ):
        format_dependency_scan_text(
            invalid_result  # type: ignore[arg-type]
        )
