"""Tests for dependency scanner command-line arguments."""

import argparse
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dependency_scanner.cli import (
    DependencyCliArguments,
    build_parser,
    parse_arguments,
)


def test_cli_arguments_store_expected_fields() -> None:
    """CLI arguments should retain every validated value."""

    arguments = DependencyCliArguments(
        requirements_file=Path("requirements.txt"),
        output_format="json",
        output_path=Path("reports/dependencies.json"),
        fail_on="high",
        source="osv",
        timeout=5.5,
    )

    assert arguments.requirements_file == Path(
        "requirements.txt"
    )
    assert arguments.output_format == "json"
    assert arguments.output_path == Path(
        "reports/dependencies.json"
    )
    assert arguments.fail_on == "high"
    assert arguments.source == "osv"
    assert arguments.timeout == 5.5


def test_cli_arguments_are_immutable() -> None:
    """Parsed dependency arguments should not be modified."""

    arguments = parse_arguments(["requirements.txt"])

    with pytest.raises(FrozenInstanceError):
        arguments.timeout = 1.0  # type: ignore[misc]


def test_cli_arguments_use_slots() -> None:
    """The argument data model should avoid a dynamic dictionary."""

    assert DependencyCliArguments.__slots__ == (
        "requirements_file",
        "output_format",
        "output_path",
        "fail_on",
        "source",
        "timeout",
    )


def test_build_parser_returns_argument_parser() -> None:
    """The parser factory should return an ArgumentParser."""

    assert isinstance(
        build_parser(),
        argparse.ArgumentParser,
    )


def test_each_build_parser_call_returns_new_parser() -> None:
    """Parser instances should not be shared between calls."""

    assert build_parser() is not build_parser()


def test_parser_uses_expected_program_name() -> None:
    """The parser should use the dependency console command."""

    assert build_parser().prog == (
        "securecode-dependency-scan"
    )


def test_parser_uses_expected_description() -> None:
    """The parser should explain the dependency scan purpose."""

    assert build_parser().description == (
        "Scan pinned Python dependencies for known vulnerabilities."
    )


def test_requirements_path_is_converted_to_path() -> None:
    """A requirements string should become a Path value."""

    arguments = parse_arguments(
        ["config/requirements.txt"]
    )

    assert arguments.requirements_file == Path(
        "config/requirements.txt"
    )
    assert isinstance(arguments.requirements_file, Path)


def test_absolute_requirements_path_is_preserved(
    tmp_path: Path,
) -> None:
    """An absolute input path should remain absolute."""

    requirements_path = (
        tmp_path / "requirements.txt"
    ).resolve()

    arguments = parse_arguments(
        [str(requirements_path)]
    )

    assert arguments.requirements_file == requirements_path


def test_default_values_are_applied() -> None:
    """A minimal invocation should use stable defaults."""

    arguments = parse_arguments(["requirements.txt"])

    assert arguments.output_format == "text"
    assert arguments.output_path is None
    assert arguments.fail_on == "any"
    assert arguments.source == "osv"
    assert arguments.timeout == 10.0


@pytest.mark.parametrize(
    "output_format",
    ["text", "json"],
)
def test_supported_output_formats_are_accepted(
    output_format: str,
) -> None:
    """Both dependency report formats should be accepted."""

    arguments = parse_arguments(
        [
            "requirements.txt",
            "--format",
            output_format,
        ]
    )

    assert arguments.output_format == output_format


def test_output_path_is_converted_to_path() -> None:
    """The optional report destination should become a Path."""

    arguments = parse_arguments(
        [
            "requirements.txt",
            "--output",
            "reports/dependencies.json",
        ]
    )

    assert arguments.output_path == Path(
        "reports/dependencies.json"
    )


@pytest.mark.parametrize(
    "fail_on",
    [
        "any",
        "low",
        "medium",
        "high",
        "critical",
    ],
)
def test_supported_fail_on_levels_are_accepted(
    fail_on: str,
) -> None:
    """Every documented finding threshold should be accepted."""

    arguments = parse_arguments(
        [
            "requirements.txt",
            "--fail-on",
            fail_on,
        ]
    )

    assert arguments.fail_on == fail_on


def test_osv_source_is_accepted_explicitly() -> None:
    """The initial OSV source should be selectable."""

    arguments = parse_arguments(
        [
            "requirements.txt",
            "--source",
            "osv",
        ]
    )

    assert arguments.source == "osv"


@pytest.mark.parametrize(
    ("timeout_text", "expected_timeout"),
    [
        ("1", 1.0),
        ("0.25", 0.25),
        ("15.5", 15.5),
    ],
)
def test_positive_timeout_is_accepted(
    timeout_text: str,
    expected_timeout: float,
) -> None:
    """Positive finite timeout values should become floats."""

    arguments = parse_arguments(
        [
            "requirements.txt",
            "--timeout",
            timeout_text,
        ]
    )

    assert arguments.timeout == expected_timeout


@pytest.mark.parametrize(
    "timeout_text",
    [
        "0",
        "-1",
        "nan",
        "inf",
        "-inf",
        "true",
    ],
)
def test_invalid_timeout_is_rejected(
    timeout_text: str,
) -> None:
    """Timeout must be a positive finite number."""

    with pytest.raises(SystemExit) as error:
        parse_arguments(
            [
                "requirements.txt",
                "--timeout",
                timeout_text,
            ]
        )

    assert error.value.code == 2


def test_options_can_appear_before_requirements_path() -> None:
    """Optional arguments should work before the positional path."""

    arguments = parse_arguments(
        [
            "--format",
            "json",
            "--fail-on",
            "high",
            "requirements.txt",
        ]
    )

    assert arguments.requirements_file == Path(
        "requirements.txt"
    )
    assert arguments.output_format == "json"
    assert arguments.fail_on == "high"


def test_missing_requirements_path_exits_with_usage_error() -> None:
    """The requirements path should remain required."""

    with pytest.raises(SystemExit) as error:
        parse_arguments([])

    assert error.value.code == 2


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--format", "xml"),
        ("--fail-on", "warning"),
        ("--source", "nvd"),
    ],
)
def test_invalid_choice_is_rejected(
    option: str,
    value: str,
) -> None:
    """Unsupported enum-like option values should fail usage."""

    with pytest.raises(SystemExit) as error:
        parse_arguments(
            [
                "requirements.txt",
                option,
                value,
            ]
        )

    assert error.value.code == 2


def test_unknown_argument_is_rejected() -> None:
    """Undocumented command-line arguments should be rejected."""

    with pytest.raises(SystemExit) as error:
        parse_arguments(
            [
                "requirements.txt",
                "--unknown",
            ]
        )

    assert error.value.code == 2


def test_help_option_exits_successfully() -> None:
    """Help should preserve argparse's success exit."""

    with pytest.raises(SystemExit) as error:
        parse_arguments(["--help"])

    assert error.value.code == 0


def test_help_output_describes_public_options(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Help text should describe every supported CLI option."""

    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])

    output = capsys.readouterr().out

    assert "securecode-dependency-scan" in output
    assert "requirements_file" in output
    assert "--format" in output
    assert "--output" in output
    assert "--fail-on" in output
    assert "--source" in output
    assert "--timeout" in output


def test_parser_does_not_require_existing_file(
    tmp_path: Path,
) -> None:
    """File-system validation should remain outside the parser."""

    missing_path = tmp_path / "missing.txt"

    arguments = parse_arguments([str(missing_path)])

    assert arguments.requirements_file == missing_path
    assert not missing_path.exists()
