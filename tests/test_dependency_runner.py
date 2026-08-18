"""Tests for the dependency scanner command-line runner."""

import io
import json
import tomllib
from pathlib import Path
from unittest.mock import Mock

import pytest

import dependency_scanner.default_factory as factory_module
import dependency_scanner.runner as runner_module
from dependency_scanner.cli import DependencyCliArguments
from dependency_scanner.default_factory import (
    DependencyScannerConfigurationError,
    create_default_dependency_scanner,
)
from dependency_scanner.models import (
    AdvisorySource,
    Dependency,
    DependencyFinding,
    VulnerabilitySeverity,
)
from dependency_scanner.osv_client import OsvQueryError
from dependency_scanner.osv_source import OsvVulnerabilitySource
from dependency_scanner.requirements_parser import (
    RequirementsParseError,
)
from dependency_scanner.runner import main, run_cli
from dependency_scanner.scanner import (
    DependencyScanner,
    DependencyScanError,
    DependencyScanResult,
)


def _dependency(
    *,
    name: str = "sample-package",
    source_file: str = "requirements.txt",
    line_number: int = 1,
) -> Dependency:
    """Create a dependency used by runner tests."""

    return Dependency(
        name=name,
        version="1.0.0",
        operator="==",
        source_file=source_file,
        line_number=line_number,
    )


def _finding(
    severity: VulnerabilitySeverity = (
        VulnerabilitySeverity.HIGH
    ),
    *,
    message: str = "Example vulnerability.",
) -> DependencyFinding:
    """Create a dependency finding used by runner tests."""

    return DependencyFinding(
        dependency=_dependency(),
        advisory_id="OSV-EXAMPLE",
        message=message,
        source=AdvisorySource(
            name="OSV",
            url="https://osv.dev/",
        ),
        severity=severity,
        fixed_version="2.0.0",
        aliases=("CVE-2099-0001",),
    )


def _error(
    message: str = "Service unavailable.",
) -> DependencyScanError:
    """Create a dependency lookup error used by runner tests."""

    return DependencyScanError(
        dependency=_dependency(),
        source=AdvisorySource(
            name="OSV",
            url="https://osv.dev/",
        ),
        message=message,
    )


def _factory_for(
    result: DependencyScanResult,
) -> tuple[Mock, Mock]:
    """Create a fake dependency scanner and its factory."""

    scanner = Mock()
    scanner.scan_requirements.return_value = result
    factory = Mock(return_value=scanner)

    return scanner, factory


def test_default_factory_creates_dependency_scanner() -> None:
    """The default factory should return the orchestrator type."""

    scanner = create_default_dependency_scanner()

    assert isinstance(scanner, DependencyScanner)
    assert isinstance(
        scanner.source,
        OsvVulnerabilitySource,
    )


def test_default_factory_wires_source_and_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Factory options should reach each constructed component."""

    client = object()
    source = object()
    scanner = object()
    client_constructor = Mock(return_value=client)
    source_constructor = Mock(return_value=source)
    scanner_constructor = Mock(return_value=scanner)

    monkeypatch.setattr(
        factory_module,
        "OsvQueryClient",
        client_constructor,
    )
    monkeypatch.setattr(
        factory_module,
        "OsvVulnerabilitySource",
        source_constructor,
    )
    monkeypatch.setattr(
        factory_module,
        "DependencyScanner",
        scanner_constructor,
    )

    result = create_default_dependency_scanner(
        source_name="osv",
        timeout=4.25,
    )

    assert result is scanner
    client_constructor.assert_called_once_with(
        timeout=4.25
    )
    source_constructor.assert_called_once_with(
        client=client
    )
    scanner_constructor.assert_called_once_with(
        source=source
    )


def test_default_factory_creates_new_components_each_time() -> None:
    """Default scanner graphs should not be shared."""

    first = create_default_dependency_scanner()
    second = create_default_dependency_scanner()

    assert first is not second
    assert first.source is not second.source


def test_default_factory_rejects_unsupported_source() -> None:
    """Only the documented OSV source should be configured."""

    with pytest.raises(
        DependencyScannerConfigurationError,
        match="Unsupported vulnerability source",
    ):
        create_default_dependency_scanner(
            source_name="nvd"
        )


def test_argv_is_forwarded_to_argument_parser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Runner argv should reach the dependency parser unchanged."""

    received: list[object] = []

    def fake_parse_arguments(
        argv: object,
    ) -> DependencyCliArguments:
        received.append(argv)
        return DependencyCliArguments(
            requirements_file=Path("parsed.txt"),
            output_format="text",
            output_path=None,
            fail_on="any",
            source="osv",
            timeout=10.0,
        )

    monkeypatch.setattr(
        runner_module,
        "parse_arguments",
        fake_parse_arguments,
    )
    _, factory = _factory_for(
        DependencyScanResult()
    )

    run_cli(
        ["custom.txt"],
        scanner_factory=factory,
        stdout=io.StringIO(),
    )

    assert received == [["custom.txt"]]


def test_factory_receives_source_and_timeout() -> None:
    """Parsed configuration should reach the scanner factory."""

    _, factory = _factory_for(
        DependencyScanResult()
    )

    run_cli(
        [
            "requirements.txt",
            "--source",
            "osv",
            "--timeout",
            "3.5",
        ],
        scanner_factory=factory,
        stdout=io.StringIO(),
    )

    factory.assert_called_once_with(
        source_name="osv",
        timeout=3.5,
    )


def test_requirements_path_is_passed_to_scanner() -> None:
    """The scanner should receive the parsed requirements path."""

    scanner, factory = _factory_for(
        DependencyScanResult()
    )

    run_cli(
        ["config/requirements.txt"],
        scanner_factory=factory,
        stdout=io.StringIO(),
    )

    scanner.scan_requirements.assert_called_once_with(
        Path("config/requirements.txt")
    )


def test_default_format_writes_text_report() -> None:
    """Text should be the default dependency report format."""

    _, factory = _factory_for(
        DependencyScanResult()
    )
    stdout = io.StringIO()

    exit_code = run_cli(
        ["requirements.txt"],
        scanner_factory=factory,
        stdout=stdout,
    )

    assert stdout.getvalue() == (
        "No dependency vulnerabilities found.\n"
        "\n"
        "0 dependencies scanned. 0 findings. "
        "0 lookup errors.\n"
    )
    assert exit_code == 0


def test_explicit_text_format_is_supported() -> None:
    """An explicit text option should use the text formatter."""

    finding = _finding()
    _, factory = _factory_for(
        DependencyScanResult(findings=(finding,))
    )
    stdout = io.StringIO()

    run_cli(
        [
            "requirements.txt",
            "--format",
            "text",
        ],
        scanner_factory=factory,
        stdout=stdout,
    )

    assert stdout.getvalue().startswith(
        "[HIGH] OSV-EXAMPLE"
    )


def test_json_format_is_supported() -> None:
    """The JSON option should emit structured scan data."""

    dependency = _dependency()
    finding = _finding()
    _, factory = _factory_for(
        DependencyScanResult(
            dependencies=(dependency,),
            findings=(finding,),
        )
    )
    stdout = io.StringIO()

    run_cli(
        [
            "requirements.txt",
            "--format",
            "json",
        ],
        scanner_factory=factory,
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())

    assert payload["summary"]["dependencies"] == 1
    assert payload["summary"]["findings"] == 1
    assert payload["findings"][0][
        "advisory_id"
    ] == "OSV-EXAMPLE"


@pytest.mark.parametrize(
    "output_format",
    ["text", "json"],
)
def test_stdout_receives_exactly_one_trailing_newline(
    output_format: str,
) -> None:
    """Runner output should end with exactly one newline."""

    _, factory = _factory_for(
        DependencyScanResult()
    )
    stdout = io.StringIO()

    run_cli(
        [
            "requirements.txt",
            "--format",
            output_format,
        ],
        scanner_factory=factory,
        stdout=stdout,
    )

    output = stdout.getvalue()

    assert output.endswith("\n")
    assert not output.endswith("\n\n")


def test_output_file_receives_utf8_json(
    tmp_path: Path,
) -> None:
    """A selected output file should contain UTF-8 report text."""

    message = "Güvenlik açığı bulundu."
    finding = _finding(message=message)
    _, factory = _factory_for(
        DependencyScanResult(findings=(finding,))
    )
    output_path = tmp_path / "dependency-report.json"
    stdout = io.StringIO()

    run_cli(
        [
            "requirements.txt",
            "--format",
            "json",
            "--output",
            str(output_path),
        ],
        scanner_factory=factory,
        stdout=stdout,
    )

    output_bytes = output_path.read_bytes()
    output_text = output_bytes.decode("utf-8")

    assert message in output_text
    assert json.loads(output_text)["findings"]
    assert output_text.endswith("\n")
    assert stdout.getvalue() == ""


def test_existing_output_file_is_replaced(
    tmp_path: Path,
) -> None:
    """An explicitly selected report file should be replaced."""

    output_path = tmp_path / "report.txt"
    output_path.write_text(
        "old report",
        encoding="utf-8",
    )
    _, factory = _factory_for(
        DependencyScanResult()
    )

    run_cli(
        [
            "requirements.txt",
            "--output",
            str(output_path),
        ],
        scanner_factory=factory,
        stdout=io.StringIO(),
    )

    output = output_path.read_text(encoding="utf-8")

    assert "old report" not in output
    assert "No dependency vulnerabilities found." in output


def test_missing_output_parent_is_operational_error(
    tmp_path: Path,
) -> None:
    """The runner should not create a missing output directory."""

    output_path = tmp_path / "missing" / "report.json"
    _, factory = _factory_for(
        DependencyScanResult()
    )
    stderr = io.StringIO()

    exit_code = main(
        [
            "requirements.txt",
            "--output",
            str(output_path),
        ],
        scanner_factory=factory,
        stdout=io.StringIO(),
        stderr=stderr,
    )

    assert exit_code == 2
    assert stderr.getvalue().startswith("Error: ")
    assert not output_path.parent.exists()


def test_requirements_file_cannot_be_output_target(
    tmp_path: Path,
) -> None:
    """The CLI should never overwrite its requirements input."""

    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text(
        "sample-package==1.0.0\n",
        encoding="utf-8",
    )
    _, factory = _factory_for(
        DependencyScanResult()
    )
    stderr = io.StringIO()

    exit_code = main(
        [
            str(requirements_path),
            "--output",
            str(requirements_path),
        ],
        scanner_factory=factory,
        stdout=io.StringIO(),
        stderr=stderr,
    )

    assert exit_code == 2
    assert "must differ" in stderr.getvalue()
    assert requirements_path.read_text(
        encoding="utf-8"
    ) == "sample-package==1.0.0\n"
    factory.assert_not_called()


def test_clean_scan_returns_exit_code_zero() -> None:
    """A complete clean scan should succeed."""

    _, factory = _factory_for(
        DependencyScanResult(
            dependencies=(_dependency(),),
        )
    )

    exit_code = run_cli(
        ["requirements.txt"],
        scanner_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == 0


@pytest.mark.parametrize(
    "severity",
    list(VulnerabilitySeverity),
)
def test_default_any_threshold_fails_for_every_finding(
    severity: VulnerabilitySeverity,
) -> None:
    """The default threshold should include unknown findings."""

    _, factory = _factory_for(
        DependencyScanResult(
            findings=(_finding(severity),),
        )
    )

    exit_code = run_cli(
        ["requirements.txt"],
        scanner_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == 1


@pytest.mark.parametrize(
    ("fail_on", "severity", "expected_exit_code"),
    [
        ("low", VulnerabilitySeverity.UNKNOWN, 0),
        ("low", VulnerabilitySeverity.LOW, 1),
        ("low", VulnerabilitySeverity.CRITICAL, 1),
        ("medium", VulnerabilitySeverity.LOW, 0),
        ("medium", VulnerabilitySeverity.MEDIUM, 1),
        ("medium", VulnerabilitySeverity.HIGH, 1),
        ("high", VulnerabilitySeverity.MEDIUM, 0),
        ("high", VulnerabilitySeverity.HIGH, 1),
        ("high", VulnerabilitySeverity.CRITICAL, 1),
        ("critical", VulnerabilitySeverity.HIGH, 0),
        ("critical", VulnerabilitySeverity.CRITICAL, 1),
    ],
)
def test_fail_on_threshold_uses_severity_order(
    fail_on: str,
    severity: VulnerabilitySeverity,
    expected_exit_code: int,
) -> None:
    """Configured thresholds should use qualitative severity order."""

    _, factory = _factory_for(
        DependencyScanResult(
            findings=(_finding(severity),),
        )
    )

    exit_code = run_cli(
        [
            "requirements.txt",
            "--fail-on",
            fail_on,
        ],
        scanner_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == expected_exit_code


def test_lookup_error_returns_exit_code_two() -> None:
    """A partial source failure should take precedence."""

    _, factory = _factory_for(
        DependencyScanResult(errors=(_error(),))
    )

    exit_code = run_cli(
        ["requirements.txt"],
        scanner_factory=factory,
        stdout=io.StringIO(),
    )

    assert exit_code == 2


def test_partial_result_is_reported_before_error_exit() -> None:
    """Findings and lookup errors should both remain visible."""

    result = DependencyScanResult(
        findings=(_finding(),),
        errors=(_error(),),
    )
    _, factory = _factory_for(result)
    stdout = io.StringIO()

    exit_code = run_cli(
        ["requirements.txt"],
        scanner_factory=factory,
        stdout=stdout,
    )

    assert exit_code == 2
    assert "[HIGH] OSV-EXAMPLE" in stdout.getvalue()
    assert "[LOOKUP ERROR] OSV" in stdout.getvalue()


@pytest.mark.parametrize(
    "operational_error",
    [
        FileNotFoundError("Requirements file not found."),
        IsADirectoryError("Requirements path is a directory."),
        UnicodeDecodeError(
            "utf-8",
            b"\xff",
            0,
            1,
            "invalid start byte",
        ),
        RequirementsParseError(
            source_file="requirements.txt",
            line_number=2,
            line="sample>=1.0.0",
            reason="Unsupported requirement format.",
        ),
        OsvQueryError("OSV configuration failed."),
    ],
)
def test_main_converts_operational_errors_to_exit_code_two(
    operational_error: Exception,
) -> None:
    """Expected fatal failures should be reported consistently."""

    scanner = Mock()
    scanner.scan_requirements.side_effect = operational_error
    factory = Mock(return_value=scanner)
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = main(
        ["requirements.txt"],
        scanner_factory=factory,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue().startswith("Error: ")
    assert stderr.getvalue().endswith("\n")


def test_factory_configuration_error_is_operational() -> None:
    """Expected factory configuration errors should use exit two."""

    factory = Mock(
        side_effect=DependencyScannerConfigurationError(
            "Unsupported vulnerability source: custom"
        )
    )
    stderr = io.StringIO()

    exit_code = main(
        ["requirements.txt"],
        scanner_factory=factory,
        stdout=io.StringIO(),
        stderr=stderr,
    )

    assert exit_code == 2
    assert "Unsupported vulnerability source" in (
        stderr.getvalue()
    )


def test_unexpected_programming_error_is_propagated() -> None:
    """Unexpected defects should remain visible to callers."""

    scanner = Mock()
    scanner.scan_requirements.side_effect = TypeError(
        "Unexpected scanner defect."
    )
    factory = Mock(return_value=scanner)

    with pytest.raises(
        TypeError,
        match="Unexpected scanner defect",
    ):
        main(
            ["requirements.txt"],
            scanner_factory=factory,
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )


def test_missing_arguments_preserve_argparse_exit() -> None:
    """Argparse usage failures should not be converted by main."""

    factory = Mock()

    with pytest.raises(SystemExit) as error:
        main(
            [],
            scanner_factory=factory,
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )

    assert error.value.code == 2
    factory.assert_not_called()


def test_help_preserves_argparse_success_exit() -> None:
    """Help requests should retain argparse's zero exit."""

    factory = Mock()

    with pytest.raises(SystemExit) as error:
        main(
            ["--help"],
            scanner_factory=factory,
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )

    assert error.value.code == 0
    factory.assert_not_called()


def test_runner_does_not_modify_scan_models() -> None:
    """CLI reporting should preserve the immutable scan result."""

    dependency = _dependency()
    finding = _finding()
    error = _error()
    result = DependencyScanResult(
        dependencies=(dependency,),
        findings=(finding,),
        errors=(error,),
    )
    before = (
        dependency.to_dict(),
        finding.to_dict(),
        error.message,
        result,
    )
    _, factory = _factory_for(result)

    run_cli(
        ["requirements.txt"],
        scanner_factory=factory,
        stdout=io.StringIO(),
    )

    assert dependency.to_dict() == before[0]
    assert finding.to_dict() == before[1]
    assert error.message == before[2]
    assert result == before[3]


def test_console_script_points_to_dependency_runner() -> None:
    """The project should expose the dependency scan command."""

    project_data = tomllib.loads(
        Path("pyproject.toml").read_text(
            encoding="utf-8"
        )
    )

    assert project_data["project"]["scripts"][
        "securecode-dependency-scan"
    ] == "dependency_scanner.runner:main"


def test_static_analyzer_console_script_is_unchanged() -> None:
    """Adding dependency scanning should preserve the static CLI."""

    project_data = tomllib.loads(
        Path("pyproject.toml").read_text(
            encoding="utf-8"
        )
    )

    assert project_data["project"]["scripts"][
        "securecode-analyzer"
    ] == "static_analyzer.runner:main"
