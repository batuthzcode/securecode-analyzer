"""Tests for discovering Python files in a target directory."""

from pathlib import Path

import pytest

from static_analyzer.file_scanner import (
    DEFAULT_EXCLUDED_DIRECTORIES,
    FileScanner,
)


def _create_file(path: Path, content: str = "") -> Path:
    """Create a file together with any missing parent directories."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_file_scanner_uses_default_excluded_directories() -> None:
    """The scanner should exclude common generated directories by default."""

    scanner = FileScanner()

    assert scanner.excluded_directories == DEFAULT_EXCLUDED_DIRECTORIES
    assert scanner.excluded_directories == frozenset(
        {
            ".git",
            ".venv",
            "__pycache__",
        }
    )


def test_custom_excluded_directories_are_added_to_defaults() -> None:
    """Custom directory names should not remove the safe defaults."""

    scanner = FileScanner(
        excluded_directories={
            "generated",
            "vendor",
        }
    )

    assert scanner.excluded_directories == frozenset(
        {
            ".git",
            ".venv",
            "__pycache__",
            "generated",
            "vendor",
        }
    )


def test_missing_target_raises_file_not_found_error(
    tmp_path: Path,
) -> None:
    """A missing target directory should create a clear error."""

    scanner = FileScanner()
    missing_target = tmp_path / "missing"

    with pytest.raises(
        FileNotFoundError,
        match="Target path does not exist",
    ):
        scanner.scan(str(missing_target))


def test_file_target_raises_not_a_directory_error(
    tmp_path: Path,
) -> None:
    """A file cannot be used as the directory scanning target."""

    scanner = FileScanner()
    target_file = _create_file(tmp_path / "example.py")

    with pytest.raises(
        NotADirectoryError,
        match="Target path is not a directory",
    ):
        scanner.scan(target_file)


def test_empty_directory_returns_empty_list(
    tmp_path: Path,
) -> None:
    """An empty directory should be a valid scanning target."""

    scanner = FileScanner()

    results = scanner.scan(tmp_path)

    assert results == []


def test_python_file_in_target_directory_is_found(
    tmp_path: Path,
) -> None:
    """A Python file directly inside the target should be returned."""

    scanner = FileScanner()
    python_file = _create_file(tmp_path / "main.py")

    results = scanner.scan(str(tmp_path))

    assert results == [python_file]


def test_python_files_in_nested_directories_are_found(
    tmp_path: Path,
) -> None:
    """Python files should be discovered recursively."""

    scanner = FileScanner()
    first_file = _create_file(tmp_path / "package" / "first.py")
    second_file = _create_file(
        tmp_path / "package" / "nested" / "second.py"
    )

    results = scanner.scan(tmp_path)

    assert results == [
        first_file,
        second_file,
    ]


def test_non_python_files_are_ignored(
    tmp_path: Path,
) -> None:
    """Only files ending with the .py extension should be returned."""

    scanner = FileScanner()
    python_file = _create_file(tmp_path / "example.py")

    _create_file(tmp_path / "README.md")
    _create_file(tmp_path / "requirements.txt")
    _create_file(tmp_path / "config.json")
    _create_file(tmp_path / "example.pyc")

    results = scanner.scan(tmp_path)

    assert results == [python_file]


def test_default_excluded_directories_are_skipped(
    tmp_path: Path,
) -> None:
    """Files inside default excluded directories should not be found."""

    scanner = FileScanner()
    included_file = _create_file(tmp_path / "included.py")

    for directory_name in DEFAULT_EXCLUDED_DIRECTORIES:
        _create_file(
            tmp_path / directory_name / "ignored.py",
        )

    results = scanner.scan(tmp_path)

    assert results == [included_file]


def test_custom_excluded_directories_are_skipped(
    tmp_path: Path,
) -> None:
    """Files inside custom excluded directories should not be found."""

    scanner = FileScanner(
        excluded_directories={
            "generated",
            "vendor",
        }
    )
    included_file = _create_file(tmp_path / "src" / "included.py")

    _create_file(tmp_path / "generated" / "ignored.py")
    _create_file(tmp_path / "vendor" / "dependency.py")

    results = scanner.scan(tmp_path)

    assert results == [included_file]


def test_results_are_returned_in_sorted_order(
    tmp_path: Path,
) -> None:
    """The same file tree should always produce deterministic ordering."""

    scanner = FileScanner()
    second_file = _create_file(tmp_path / "b.py")
    first_file = _create_file(tmp_path / "a.py")
    third_file = _create_file(tmp_path / "nested" / "c.py")

    results = scanner.scan(tmp_path)

    assert results == [
        first_file,
        second_file,
        third_file,
    ]


def test_results_contain_path_objects(
    tmp_path: Path,
) -> None:
    """Every discovered file should be represented by pathlib.Path."""

    scanner = FileScanner()
    _create_file(tmp_path / "example.py")

    results = scanner.scan(tmp_path)

    assert results
    assert all(isinstance(result, Path) for result in results)