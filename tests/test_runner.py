"""Tests for the SecureCode Analyzer CLI runner."""

import io
import json
import tomllib
from pathlib import Path
from unittest.mock import Mock

import pytest

import static_analyzer.runner as runner_module
from static_analyzer.cli import CliArguments
from static_analyzer.models import Finding, Severity
from static_analyzer.runner import main, run_cli


def _finding(
    *,
    rule_id: str = "SA005",
    message: str = "Possible hardcoded secret found.",
    file_path: str = "src/example.py",
    line_number: int = 1,
    column_number: int | None = 1,
    severity: Severity = Severity.WARNING,
) -> Finding:
    """Create a finding with configurable runner test data."""

    return Finding(
        rule_id=rule_id,
        message=message,
        file_path=file_path,
        line_number=line_number,
        severity=severity,
        column_number=column_number,
    )


def _factory_for(
    findings: list[Finding],
) -> tuple[Mock, Mock]:
    """Create a mock analyzer and its factory."""

    analyzer = Mock()
    analyzer.analyze.return_value = findings

    factory = Mock(return_value=analyzer)

    return analyzer, factory


def test_default_format_uses_text_output() -> None:
    """The default format should produce human-readable text."""

    _, factory = _factory_for([])
    stdout = io.StringIO()

    exit_code = run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=stdout,
    )

    assert stdout.getvalue() == "No findings found.\n"
    assert exit_code == 0


def test_explicit_text_format_is_supported() -> None:
    """An explicit text format should use the text formatter."""

    finding = _finding()
    _, factory = _factory_for([finding])
    stdout = io.StringIO()

    run_cli(
        [
            "src",
            "--format",
            "text",
        ],
        analyzer_factory=factory,
        stdout=stdout,
    )

    assert stdout.getvalue() == (
        "[WARNING] SA005 src/example.py:1:1"
        " - Possible hardcoded secret found.\n"
        "\n"
        "1 finding found.\n"
    )


def test_json_format_is_supported() -> None:
    """The JSON option should produce machine-readable output."""

    finding = _finding()
    _, factory = _factory_for([finding])
    stdout = io.StringIO()

    run_cli(
        [
            "src",
            "--format",
            "json",
        ],
        analyzer_factory=factory,
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())

    assert payload["summary"]["total"] == 1
    assert payload["findings"][0]["rule_id"] == "SA005"


def test_argv_is_forwarded_to_argument_parser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The provided argument sequence should reach the parser."""

    captured_arguments: list[object] = []

    def fake_parse_arguments(
        argv: object,
    ) -> CliArguments:
        captured_arguments.append(argv)

        return CliArguments(
            target=Path("parsed-target"),
            output_format="text",
        )

    monkeypatch.setattr(
        runner_module,
        "parse_arguments",
        fake_parse_arguments,
    )

    _, factory = _factory_for([])

    run_cli(
        ["custom-target"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert captured_arguments == [
        ["custom-target"],
    ]


def test_default_analyzer_factory_is_called_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The default analyzer factory should be used when none is injected."""

    analyzer = Mock()
    analyzer.analyze.return_value = []
    factory = Mock(return_value=analyzer)

    monkeypatch.setattr(
        runner_module,
        "create_default_analyzer",
        factory,
    )

    run_cli(
        ["src"],
        stdout=io.StringIO(),
    )

    factory.assert_called_once_with()


def test_injected_analyzer_factory_is_called_once() -> None:
    """An injected analyzer factory should be called exactly once."""

    _, factory = _factory_for([])

    run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    factory.assert_called_once_with()


def test_target_path_is_passed_to_analyzer() -> None:
    """The parsed Path target should be passed to the analyzer."""

    analyzer, factory = _factory_for([])

    run_cli(
        ["src/nested"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    analyzer.analyze.assert_called_once_with(
        Path("src/nested")
    )


def test_analyzer_is_called_once() -> None:
    """One CLI execution should perform one project analysis."""

    analyzer, factory = _factory_for([])

    run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert analyzer.analyze.call_count == 1


def test_finding_text_output_is_written_to_stdout() -> None:
    """Text findings should be written to the supplied output stream."""

    finding = _finding(
        rule_id="SA003",
        message="TODO comment found.",
        line_number=8,
        column_number=None,
        severity=Severity.INFO,
    )
    _, factory = _factory_for([finding])
    stdout = io.StringIO()

    run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=stdout,
    )

    assert stdout.getvalue() == (
        "[INFO] SA003 src/example.py:8"
        " - TODO comment found.\n"
        "\n"
        "1 finding found.\n"
    )


def test_empty_json_output_contains_zero_total() -> None:
    """An empty JSON report should contain a zero summary total."""

    _, factory = _factory_for([])
    stdout = io.StringIO()

    run_cli(
        [
            "src",
            "--format",
            "json",
        ],
        analyzer_factory=factory,
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())

    assert payload == {
        "findings": [],
        "summary": {
            "total": 0,
        },
    }


def test_finding_json_output_contains_serialized_data() -> None:
    """JSON output should preserve formatter finding data."""

    finding = _finding(
        rule_id="SA006",
        message="Function name should use snake_case.",
        severity=Severity.INFO,
    )
    _, factory = _factory_for([finding])
    stdout = io.StringIO()

    run_cli(
        [
            "src",
            "--format",
            "json",
        ],
        analyzer_factory=factory,
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())

    assert payload["findings"][0] == finding.to_dict()


def test_stdout_receives_exactly_one_trailing_newline() -> None:
    """The runner should append exactly one final newline."""

    _, factory = _factory_for([_finding()])
    stdout = io.StringIO()

    run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=stdout,
    )

    output = stdout.getvalue()

    assert output.endswith("\n")
    assert not output.endswith("\n\n")


def test_no_findings_return_exit_code_zero() -> None:
    """A clean analysis should return success."""

    _, factory = _factory_for([])

    exit_code = run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == 0


def test_findings_return_exit_code_one() -> None:
    """Any finding should return the findings exit code."""

    _, factory = _factory_for([_finding()])

    exit_code = run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == 1


def test_info_finding_returns_exit_code_one() -> None:
    """INFO findings should still produce exit code one."""

    finding = _finding(severity=Severity.INFO)
    _, factory = _factory_for([finding])

    exit_code = run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == 1


def test_warning_finding_returns_exit_code_one() -> None:
    """WARNING findings should produce exit code one."""

    finding = _finding(severity=Severity.WARNING)
    _, factory = _factory_for([finding])

    exit_code = run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == 1


def test_error_finding_returns_exit_code_one() -> None:
    """ERROR findings should produce exit code one."""

    finding = _finding(severity=Severity.ERROR)
    _, factory = _factory_for([finding])

    exit_code = run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == 1


@pytest.mark.parametrize(
    ("fail_on", "severity", "expected_exit_code"),
    [
        ("info", Severity.INFO, 1),
        ("info", Severity.WARNING, 1),
        ("warning", Severity.INFO, 0),
        ("warning", Severity.WARNING, 1),
        ("warning", Severity.ERROR, 1),
        ("error", Severity.WARNING, 0),
        ("error", Severity.ERROR, 1),
    ],
)
def test_fail_on_threshold_uses_severity_order(
    fail_on: str,
    severity: Severity,
    expected_exit_code: int,
) -> None:
    """Static findings should use the configured severity floor."""

    _, factory = _factory_for([_finding(severity=severity)])

    exit_code = run_cli(
        ["src", "--fail-on", fail_on],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == expected_exit_code


def test_fail_on_threshold_considers_every_finding() -> None:
    """A later finding at the threshold should still fail analysis."""

    findings = [
        _finding(severity=Severity.INFO),
        _finding(severity=Severity.ERROR),
    ]
    _, factory = _factory_for(findings)

    exit_code = run_cli(
        ["src", "--fail-on", "error"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == 1


def test_main_handles_file_not_found_error() -> None:
    """Missing targets should be presented as operational errors."""

    analyzer = Mock()
    analyzer.analyze.side_effect = FileNotFoundError(
        "Target path does not exist."
    )
    factory = Mock(return_value=analyzer)
    stderr = io.StringIO()

    exit_code = main(
        ["missing"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
        stderr=stderr,
    )

    assert exit_code == 2
    assert stderr.getvalue() == (
        "Error: Target path does not exist.\n"
    )


def test_main_handles_not_a_directory_error() -> None:
    """File targets should be presented as operational errors."""

    analyzer = Mock()
    analyzer.analyze.side_effect = NotADirectoryError(
        "Target path is not a directory."
    )
    factory = Mock(return_value=analyzer)
    stderr = io.StringIO()

    exit_code = main(
        ["example.py"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
        stderr=stderr,
    )

    assert exit_code == 2
    assert stderr.getvalue() == (
        "Error: Target path is not a directory.\n"
    )


def test_main_handles_syntax_error() -> None:
    """Invalid Python syntax should produce an operational error."""

    analyzer = Mock()
    analyzer.analyze.side_effect = SyntaxError(
        "invalid syntax"
    )
    factory = Mock(return_value=analyzer)
    stderr = io.StringIO()

    exit_code = main(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
        stderr=stderr,
    )

    assert exit_code == 2
    assert stderr.getvalue() == "Error: invalid syntax\n"


def test_main_handles_unicode_decode_error() -> None:
    """Invalid UTF-8 input should produce an operational error."""

    analyzer = Mock()
    analyzer.analyze.side_effect = UnicodeDecodeError(
        "utf-8",
        b"\xff",
        0,
        1,
        "invalid start byte",
    )
    factory = Mock(return_value=analyzer)
    stderr = io.StringIO()

    exit_code = main(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
        stderr=stderr,
    )

    assert exit_code == 2
    assert "Error: " in stderr.getvalue()
    assert "invalid start byte" in stderr.getvalue()


def test_operational_error_keeps_stdout_empty() -> None:
    """An operational failure should not produce an analysis report."""

    analyzer = Mock()
    analyzer.analyze.side_effect = FileNotFoundError(
        "Missing target."
    )
    factory = Mock(return_value=analyzer)
    stdout = io.StringIO()

    main(
        ["missing"],
        analyzer_factory=factory,
        stdout=stdout,
        stderr=io.StringIO(),
    )

    assert stdout.getvalue() == ""


def test_operational_error_is_written_to_stderr() -> None:
    """Operational error messages should use standard error."""

    analyzer = Mock()
    analyzer.analyze.side_effect = FileNotFoundError(
        "Missing target."
    )
    factory = Mock(return_value=analyzer)
    stderr = io.StringIO()

    main(
        ["missing"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
        stderr=stderr,
    )

    assert stderr.getvalue() == "Error: Missing target.\n"


def test_operational_error_returns_exit_code_two() -> None:
    """Expected operational failures should return exit code two."""

    analyzer = Mock()
    analyzer.analyze.side_effect = NotADirectoryError(
        "Not a directory."
    )
    factory = Mock(return_value=analyzer)

    exit_code = main(
        ["example.py"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    )

    assert exit_code == 2


def test_unexpected_runtime_error_is_propagated() -> None:
    """Unexpected exceptions should remain visible to callers."""

    analyzer = Mock()
    analyzer.analyze.side_effect = RuntimeError(
        "Unexpected analysis failure."
    )
    factory = Mock(return_value=analyzer)

    with pytest.raises(
        RuntimeError,
        match="Unexpected analysis failure",
    ):
        main(
            ["src"],
            analyzer_factory=factory,
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )


def test_missing_target_preserves_argparse_system_exit() -> None:
    """Missing arguments should preserve argparse usage behavior."""

    factory = Mock()

    with pytest.raises(SystemExit) as error:
        run_cli(
            [],
            analyzer_factory=factory,
            stdout=io.StringIO(),
        )

    assert error.value.code == 2
    factory.assert_not_called()


def test_help_preserves_argparse_system_exit() -> None:
    """Help requests should preserve argparse success behavior."""

    factory = Mock()

    with pytest.raises(SystemExit) as error:
        run_cli(
            ["--help"],
            analyzer_factory=factory,
            stdout=io.StringIO(),
        )

    assert error.value.code == 0
    factory.assert_not_called()


def test_runner_does_not_modify_findings() -> None:
    """The runner should preserve analyzer finding objects."""

    finding = _finding(
        rule_id="SA003",
        message="TODO comment found.",
        column_number=None,
        severity=Severity.INFO,
    )
    finding_before = finding.to_dict()
    _, factory = _factory_for([finding])

    run_cli(
        ["src"],
        analyzer_factory=factory,
        stdout=io.StringIO(),
    )

    assert finding.to_dict() == finding_before


def test_console_script_points_to_runner_main() -> None:
    """The project should expose the public console command."""

    project_data = tomllib.loads(
        Path("pyproject.toml").read_text(
            encoding="utf-8"
        )
    )

    assert project_data["project"]["scripts"][
        "securecode-analyzer"
    ] == "static_analyzer.runner:main"
