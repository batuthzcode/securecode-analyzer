"""Tests for the command-line argument parsing foundation."""

import argparse
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from static_analyzer.cli import (
    CliArguments,
    build_parser,
    parse_arguments,
)


def test_cli_arguments_store_expected_fields() -> None:
    """CLI arguments should store validated target and format values."""

    arguments = CliArguments(
        target=Path("src"),
        output_format="json",
    )

    assert arguments.target == Path("src")
    assert arguments.output_format == "json"


def test_cli_arguments_are_immutable() -> None:
    """Validated CLI arguments should not be modified."""

    arguments = CliArguments(
        target=Path("src"),
        output_format="text",
    )

    with pytest.raises(FrozenInstanceError):
        arguments.output_format = "json"  # type: ignore[misc]


def test_cli_arguments_use_slots() -> None:
    """The CLI data model should use slots."""

    assert CliArguments.__slots__ == (
        "target",
        "output_format",
    )


def test_build_parser_returns_argument_parser() -> None:
    """The parser factory should return an ArgumentParser."""

    parser = build_parser()

    assert isinstance(parser, argparse.ArgumentParser)


def test_each_build_parser_call_returns_new_parser() -> None:
    """Parser factory calls should create independent parser objects."""

    first_parser = build_parser()
    second_parser = build_parser()

    assert first_parser is not second_parser


def test_parser_uses_expected_program_name() -> None:
    """The parser should use the public command name."""

    parser = build_parser()

    assert parser.prog == "securecode-analyzer"


def test_parser_uses_expected_description() -> None:
    """The parser should explain the command purpose."""

    parser = build_parser()

    assert parser.description == (
        "Analyze Python source code for quality and security findings."
    )


def test_string_target_is_parsed() -> None:
    """A target string should be accepted."""

    arguments = parse_arguments(["src"])

    assert isinstance(arguments, CliArguments)
    assert arguments.target == Path("src")


def test_relative_target_is_converted_to_path() -> None:
    """A relative target should become a Path object."""

    arguments = parse_arguments(
        ["src/static_analyzer"]
    )

    assert arguments.target == Path(
        "src/static_analyzer"
    )
    assert isinstance(arguments.target, Path)


def test_absolute_target_is_converted_to_path(
    tmp_path: Path,
) -> None:
    """An absolute target should become a Path object."""

    absolute_target = tmp_path.resolve()

    arguments = parse_arguments(
        [str(absolute_target)]
    )

    assert arguments.target == absolute_target
    assert isinstance(arguments.target, Path)


def test_default_output_format_is_text() -> None:
    """Text should be the default output format."""

    arguments = parse_arguments(["src"])

    assert arguments.output_format == "text"


def test_explicit_text_format_is_accepted() -> None:
    """The text output format should be accepted explicitly."""

    arguments = parse_arguments(
        [
            "src",
            "--format",
            "text",
        ]
    )

    assert arguments.output_format == "text"


def test_json_format_is_accepted() -> None:
    """The JSON output format should be accepted."""

    arguments = parse_arguments(
        [
            "src",
            "--format",
            "json",
        ]
    )

    assert arguments.output_format == "json"


def test_format_option_can_appear_before_target() -> None:
    """Optional arguments should work before the target."""

    arguments = parse_arguments(
        [
            "--format",
            "json",
            "src",
        ]
    )

    assert arguments.target == Path("src")
    assert arguments.output_format == "json"


def test_nonexistent_target_is_accepted_by_parser(
    tmp_path: Path,
) -> None:
    """Target existence should not be checked by the parser."""

    missing_target = tmp_path / "does-not-exist"

    arguments = parse_arguments(
        [str(missing_target)]
    )

    assert arguments.target == missing_target


def test_missing_target_exits_with_usage_error() -> None:
    """A missing target should preserve argparse behavior."""

    with pytest.raises(SystemExit) as error:
        parse_arguments([])

    assert error.value.code == 2


def test_invalid_output_format_exits_with_usage_error() -> None:
    """An unsupported format should be rejected."""

    with pytest.raises(SystemExit) as error:
        parse_arguments(
            [
                "src",
                "--format",
                "xml",
            ]
        )

    assert error.value.code == 2


def test_unknown_argument_exits_with_usage_error() -> None:
    """Unknown arguments should be rejected."""

    with pytest.raises(SystemExit) as error:
        parse_arguments(
            [
                "src",
                "--unknown",
            ]
        )

    assert error.value.code == 2


def test_help_option_exits_successfully() -> None:
    """The help option should preserve argparse exit behavior."""

    with pytest.raises(SystemExit) as error:
        parse_arguments(["--help"])

    assert error.value.code == 0


def test_help_output_contains_expected_information(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Help output should describe the public CLI options."""

    parser = build_parser()

    with pytest.raises(SystemExit) as error:
        parser.parse_args(["--help"])

    captured = capsys.readouterr()
    output = captured.out

    assert error.value.code == 0
    assert "securecode-analyzer" in output
    assert "target" in output
    assert "--format" in output
    assert "text" in output
    assert "json" in output
    assert (
        "Analyze Python source code for quality and security findings."
        in output
    )