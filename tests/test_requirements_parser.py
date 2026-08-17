"""Tests for the requirements file parser."""

from pathlib import Path

import dependency_scanner
import pytest

from dependency_scanner import (
    Dependency,
    RequirementsParseError,
    parse_requirement_line,
    parse_requirements_file,
    parse_requirements_text,
)


def test_parse_requirement_line_accepts_exact_pin() -> None:
    """An exact-pinned dependency is parsed."""

    dependency = parse_requirement_line(
        "Flask==2.0.0",
        source_file="requirements.txt",
        line_number=1,
    )

    assert dependency == Dependency(
        name="Flask",
        version="2.0.0",
        operator="==",
        source_file="requirements.txt",
        line_number=1,
    )


def test_parse_requirement_line_accepts_spacing() -> None:
    """Whitespace around requirement fields is ignored."""

    dependency = parse_requirement_line(
        "  Flask  ==  2.0.0  ",
        source_file="requirements.txt",
        line_number=2,
    )

    assert dependency == Dependency(
        name="Flask",
        version="2.0.0",
        operator="==",
        source_file="requirements.txt",
        line_number=2,
    )


@pytest.mark.parametrize(
    "package_name",
    [
        "example-package",
        "example_package",
        "example.package",
        "package2",
    ],
)
def test_parse_requirement_line_accepts_package_names(
    package_name: str,
) -> None:
    """Supported package-name characters are accepted."""

    dependency = parse_requirement_line(
        f"{package_name}==1.0.0",
        source_file="requirements.txt",
        line_number=1,
    )

    assert dependency is not None
    assert dependency.name == package_name


@pytest.mark.parametrize(
    "line",
    [
        "",
        " ",
        "\t",
    ],
)
def test_parse_requirement_line_skips_blank_lines(
    line: str,
) -> None:
    """Blank requirements lines are ignored."""

    assert (
        parse_requirement_line(
            line,
            source_file="requirements.txt",
            line_number=1,
        )
        is None
    )


@pytest.mark.parametrize(
    "line",
    [
        "# production dependencies",
        "    # test dependencies",
    ],
)
def test_parse_requirement_line_skips_comments(
    line: str,
) -> None:
    """Full-line comments are ignored."""

    assert (
        parse_requirement_line(
            line,
            source_file="requirements.txt",
            line_number=1,
        )
        is None
    )


def test_parse_requirements_text_preserves_order_and_lines() -> None:
    """Dependency ordering and source line numbers are preserved."""

    dependencies = parse_requirements_text(
        (
            "# dependencies\n"
            "\n"
            "requests==2.25.0\n"
            "Flask==2.0.0\n"
        ),
        source_file="requirements.txt",
    )

    assert [
        dependency.name
        for dependency in dependencies
    ] == [
        "requests",
        "Flask",
    ]

    assert [
        dependency.line_number
        for dependency in dependencies
    ] == [
        3,
        4,
    ]


def test_parse_requirements_text_preserves_duplicates() -> None:
    """Duplicate package entries are not removed."""

    dependencies = parse_requirements_text(
        (
            "requests==2.25.0\n"
            "requests==2.26.0\n"
        ),
        source_file="requirements.txt",
    )

    assert [
        dependency.version
        for dependency in dependencies
    ] == [
        "2.25.0",
        "2.26.0",
    ]


def test_parse_requirements_text_accepts_empty_text() -> None:
    """Empty requirements text produces an empty tuple."""

    assert (
        parse_requirements_text(
            "",
            source_file="requirements.txt",
        )
        == ()
    )


def test_parse_requirements_text_accepts_comments_only() -> None:
    """Comment-only requirements text produces no dependencies."""

    assert (
        parse_requirements_text(
            "# first\n# second\n",
            source_file="requirements.txt",
        )
        == ()
    )


def test_parse_requirements_file_reads_utf8(
    tmp_path: Path,
) -> None:
    """A UTF-8 requirements file is read and parsed."""

    requirements_path = (
        tmp_path / "requirements.txt"
    )
    requirements_path.write_text(
        "example-package==1.2.3\n",
        encoding="utf-8",
    )

    dependencies = parse_requirements_file(
        requirements_path
    )

    assert len(dependencies) == 1
    assert dependencies[0].name == "example-package"
    assert dependencies[0].version == "1.2.3"
    assert dependencies[0].source_file == str(
        requirements_path
    )
    assert dependencies[0].line_number == 1


def test_parse_requirements_file_preserves_missing_file_error(
    tmp_path: Path,
) -> None:
    """Missing files continue to raise FileNotFoundError."""

    missing_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        parse_requirements_file(missing_path)


def test_parse_requirements_file_preserves_directory_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Directory read errors are not converted."""

    def raise_is_directory(
        self: Path,
        *,
        encoding: str,
    ) -> str:
        raise IsADirectoryError(str(self))

    monkeypatch.setattr(
        Path,
        "read_text",
        raise_is_directory,
    )

    with pytest.raises(IsADirectoryError):
        parse_requirements_file(tmp_path)


def test_parse_requirements_file_preserves_unicode_error(
    tmp_path: Path,
) -> None:
    """Invalid UTF-8 bytes continue to raise UnicodeDecodeError."""

    requirements_path = (
        tmp_path / "requirements.txt"
    )
    requirements_path.write_bytes(b"\xff")

    with pytest.raises(UnicodeDecodeError):
        parse_requirements_file(
            requirements_path
        )


@pytest.mark.parametrize(
    "line",
    [
        "==1.2.3",
        "Flask==",
        "Flask>=2.0.0",
        "Flask~=2.0.0",
        "Flask<3.0.0",
        "Flask==2.0.0 # comment",
        (
            'Flask==2.0.0; '
            'python_version >= "3.11"'
        ),
        "requests[security]==2.25.0",
        "-r base-requirements.txt",
        "-c constraints.txt",
        "--index-url https://example.com/simple",
        "Flask==2.0.0 --hash=sha256:example",
        (
            "package @ "
            "https://example.com/package.whl"
        ),
        "git+https://example.com/repository.git",
        "../local-package",
        (
            "Flask==2.0.0 "
            "requests==2.25.0"
        ),
    ],
)
def test_parse_requirement_line_rejects_unsupported_lines(
    line: str,
) -> None:
    """Unsupported active requirement forms raise an error."""

    with pytest.raises(
        RequirementsParseError,
        match="Unsupported requirement format",
    ):
        parse_requirement_line(
            line,
            source_file="requirements.txt",
            line_number=4,
        )


def test_requirements_parse_error_exposes_context() -> None:
    """Parse errors preserve source and line details."""

    original_line = "Flask>=2.0.0"

    with pytest.raises(
        RequirementsParseError
    ) as error_info:
        parse_requirement_line(
            original_line,
            source_file="requirements.txt",
            line_number=7,
        )

    error = error_info.value

    assert error.source_file == "requirements.txt"
    assert error.line_number == 7
    assert error.line == original_line
    assert (
        error.reason
        == "Unsupported requirement format."
    )


def test_requirements_parse_error_has_readable_message() -> None:
    """Parse error messages include file and line information."""

    error = RequirementsParseError(
        source_file="requirements.txt",
        line_number=4,
        line="Flask>=2.0.0",
        reason="Unsupported requirement format.",
    )

    assert str(error) == (
        "requirements.txt:4: "
        "Unsupported requirement format."
    )


def test_package_exports_parser_api() -> None:
    """Parser components are available from the package."""

    assert (
        dependency_scanner.RequirementsParseError
        is RequirementsParseError
    )
    assert (
        dependency_scanner.parse_requirement_line
        is parse_requirement_line
    )
    assert (
        dependency_scanner.parse_requirements_text
        is parse_requirements_text
    )
    assert (
        dependency_scanner.parse_requirements_file
        is parse_requirements_file
    )