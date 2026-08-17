"""Tests for reading and parsing Python source files."""

import ast
from pathlib import Path
from typing import Any

import pytest

from static_analyzer.source_reader import SourceFile, SourceReader


def _create_python_file(
    path: Path,
    content: str = "value = 1\n",
) -> Path:
    """Create a UTF-8 Python source file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_valid_python_file_returns_source_file(
    tmp_path: Path,
) -> None:
    """A valid Python file should create a complete SourceFile result."""

    source = "value = 42\n"
    file_path = _create_python_file(
        tmp_path / "example.py",
        source,
    )
    reader = SourceReader()

    result = reader.read(file_path)

    assert isinstance(result, SourceFile)
    assert result.file_path == file_path
    assert result.source == source
    assert isinstance(result.tree, ast.Module)


def test_reader_accepts_string_file_path(
    tmp_path: Path,
) -> None:
    """The reader should accept file paths supplied as strings."""

    file_path = _create_python_file(tmp_path / "string_target.py")
    reader = SourceReader()

    result = reader.read(str(file_path))

    assert result.file_path == file_path


def test_reader_accepts_path_object(
    tmp_path: Path,
) -> None:
    """The reader should accept pathlib.Path targets."""

    file_path = _create_python_file(tmp_path / "path_target.py")
    reader = SourceReader()

    result = reader.read(file_path)

    assert result.file_path == file_path


def test_source_code_is_preserved_exactly(
    tmp_path: Path,
) -> None:
    """The complete source text should be stored without modification."""

    source = (
        "def greet(name: str) -> str:\n"
        "    return f'Hello, {name}!'\n"
    )
    file_path = _create_python_file(
        tmp_path / "greeting.py",
        source,
    )
    reader = SourceReader()

    result = reader.read(file_path)

    assert result.source == source


def test_ast_contains_expected_python_structure(
    tmp_path: Path,
) -> None:
    """The returned AST should represent the source file contents."""

    source = "def calculate() -> int:\n    return 42\n"
    file_path = _create_python_file(
        tmp_path / "calculate.py",
        source,
    )
    reader = SourceReader()

    result = reader.read(file_path)

    functions = [
        node
        for node in ast.walk(result.tree)
        if isinstance(node, ast.FunctionDef)
    ]

    assert len(functions) == 1
    assert functions[0].name == "calculate"


def test_missing_file_raises_file_not_found_error(
    tmp_path: Path,
) -> None:
    """A missing source file should create a clear error."""

    reader = SourceReader()
    missing_file = tmp_path / "missing.py"

    with pytest.raises(
        FileNotFoundError,
        match="Source file does not exist",
    ):
        reader.read(missing_file)


def test_directory_target_raises_is_a_directory_error(
    tmp_path: Path,
) -> None:
    """A directory cannot be read as a Python source file."""

    reader = SourceReader()

    with pytest.raises(
        IsADirectoryError,
        match="Source path is a directory",
    ):
        reader.read(tmp_path)


def test_invalid_python_source_raises_syntax_error(
    tmp_path: Path,
) -> None:
    """Invalid Python syntax should not be hidden by the reader."""

    file_path = _create_python_file(
        tmp_path / "invalid.py",
        "def broken(:\n",
    )
    reader = SourceReader()

    with pytest.raises(SyntaxError):
        reader.read(file_path)


def test_syntax_error_contains_real_file_path(
    tmp_path: Path,
) -> None:
    """Syntax errors should identify the file that could not be parsed."""

    file_path = _create_python_file(
        tmp_path / "broken_source.py",
        "if True print('broken')\n",
    )
    reader = SourceReader()

    with pytest.raises(SyntaxError) as error_info:
        reader.read(file_path)

    assert error_info.value.filename == str(file_path)


def test_non_utf8_file_raises_unicode_decode_error(
    tmp_path: Path,
) -> None:
    """Files that cannot be decoded as UTF-8 should be rejected."""

    file_path = tmp_path / "non_utf8.py"
    file_path.write_bytes(b"\xff\xfe\xfa")
    reader = SourceReader()

    with pytest.raises(UnicodeDecodeError):
        reader.read(file_path)


def test_source_is_parsed_only_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A source file should create only one AST during a read operation."""

    file_path = _create_python_file(tmp_path / "single_parse.py")
    reader = SourceReader()
    original_parse = ast.parse
    parse_calls = 0

    def counting_parse(
        *args: Any,
        **kwargs: Any,
    ) -> ast.AST:
        nonlocal parse_calls
        parse_calls += 1
        return original_parse(*args, **kwargs)

    monkeypatch.setattr(ast, "parse", counting_parse)

    result = reader.read(file_path)

    assert isinstance(result.tree, ast.Module)
    assert parse_calls == 1