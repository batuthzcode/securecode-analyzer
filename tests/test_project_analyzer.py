"""Tests for the project-level static analysis coordinator."""

import ast
from pathlib import Path
from unittest.mock import Mock, call

import pytest

from static_analyzer.models import Finding, Severity
from static_analyzer.project_analyzer import ProjectAnalyzer
from static_analyzer.source_reader import SourceFile


def _source_file(file_path: str | Path) -> SourceFile:
    """Create a minimal parsed source file for coordinator tests."""

    path = Path(file_path)
    source = ""

    return SourceFile(
        file_path=path,
        source=source,
        tree=ast.parse(
            source,
            filename=str(path),
        ),
    )


def _finding(
    file_path: str,
    line_number: int = 1,
    column_number: int | None = 1,
    rule_id: str = "SA001",
) -> Finding:
    """Create a finding with configurable sorting information."""

    return Finding(
        rule_id=rule_id,
        message="Example finding.",
        file_path=file_path,
        line_number=line_number,
        severity=Severity.WARNING,
        column_number=column_number,
    )


def test_constructor_stores_dependencies() -> None:
    """The analyzer should retain its injected dependencies."""

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    assert analyzer.scanner is scanner
    assert analyzer.reader is reader
    assert analyzer.engine is engine


def test_analyze_accepts_string_target() -> None:
    """A string target should be passed directly to the scanner."""

    scanner = Mock()
    scanner.scan.return_value = []
    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=Mock(),
        engine=Mock(),
    )

    findings = analyzer.analyze("src")

    assert findings == []
    scanner.scan.assert_called_once_with("src")


def test_analyze_accepts_path_target() -> None:
    """A Path target should be passed directly to the scanner."""

    target = Path("src")
    scanner = Mock()
    scanner.scan.return_value = []
    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=Mock(),
        engine=Mock(),
    )

    findings = analyzer.analyze(target)

    assert findings == []
    scanner.scan.assert_called_once_with(target)


def test_empty_project_returns_no_findings() -> None:
    """A project without Python files should return an empty list."""

    scanner = Mock()
    reader = Mock()
    engine = Mock()
    scanner.scan.return_value = []

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    findings = analyzer.analyze("empty-project")

    assert findings == []
    reader.read.assert_not_called()
    engine.analyze.assert_not_called()


def test_single_python_file_is_analyzed() -> None:
    """A discovered Python file should be read and analyzed."""

    file_path = Path("src/example.py")
    source_file = _source_file(file_path)
    finding = _finding(str(file_path))

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [file_path]
    reader.read.return_value = source_file
    engine.analyze.return_value = [finding]

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    findings = analyzer.analyze("src")

    assert findings == [finding]
    reader.read.assert_called_once_with(file_path)
    engine.analyze.assert_called_once_with(source_file)


def test_multiple_python_files_are_processed() -> None:
    """Every file returned by the scanner should be processed."""

    first_path = Path("src/first.py")
    second_path = Path("src/second.py")
    first_source = _source_file(first_path)
    second_source = _source_file(second_path)

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [
        first_path,
        second_path,
    ]
    reader.read.side_effect = [
        first_source,
        second_source,
    ]
    engine.analyze.side_effect = [
        [],
        [],
    ]

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    analyzer.analyze("src")

    assert reader.read.call_args_list == [
        call(first_path),
        call(second_path),
    ]


def test_each_file_is_read_exactly_once() -> None:
    """Every discovered file should be read exactly once."""

    first_path = Path("src/first.py")
    second_path = Path("src/second.py")

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [
        first_path,
        second_path,
    ]
    reader.read.side_effect = [
        _source_file(first_path),
        _source_file(second_path),
    ]
    engine.analyze.return_value = []

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    analyzer.analyze("src")

    assert reader.read.call_count == 2
    reader.read.assert_has_calls(
        [
            call(first_path),
            call(second_path),
        ]
    )


def test_each_source_file_is_analyzed_exactly_once() -> None:
    """Every parsed source file should be analyzed exactly once."""

    first_source = _source_file("src/first.py")
    second_source = _source_file("src/second.py")

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [
        first_source.file_path,
        second_source.file_path,
    ]
    reader.read.side_effect = [
        first_source,
        second_source,
    ]
    engine.analyze.return_value = []

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    analyzer.analyze("src")

    assert engine.analyze.call_count == 2
    engine.analyze.assert_has_calls(
        [
            call(first_source),
            call(second_source),
        ]
    )


def test_findings_from_different_files_are_combined() -> None:
    """Findings produced for all files should be combined."""

    first_source = _source_file("src/first.py")
    second_source = _source_file("src/second.py")
    first_finding = _finding("src/first.py")
    second_finding = _finding("src/second.py")

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [
        first_source.file_path,
        second_source.file_path,
    ]
    reader.read.side_effect = [
        first_source,
        second_source,
    ]
    engine.analyze.side_effect = [
        [first_finding],
        [second_finding],
    ]

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    findings = analyzer.analyze("src")

    assert findings == [
        first_finding,
        second_finding,
    ]


def test_findings_are_sorted_by_file_path() -> None:
    """File paths should be the primary sorting criterion."""

    later_finding = _finding("src/Zeta.py")
    earlier_finding = _finding("src/alpha.py")

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [Path("src/example.py")]
    reader.read.return_value = _source_file("src/example.py")
    engine.analyze.return_value = [
        later_finding,
        earlier_finding,
    ]

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    findings = analyzer.analyze("src")

    assert findings == [
        earlier_finding,
        later_finding,
    ]


def test_findings_are_sorted_by_line_number() -> None:
    """Line numbers should order findings in the same file."""

    later_finding = _finding(
        "src/example.py",
        line_number=20,
    )
    earlier_finding = _finding(
        "src/example.py",
        line_number=4,
    )

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [Path("src/example.py")]
    reader.read.return_value = _source_file("src/example.py")
    engine.analyze.return_value = [
        later_finding,
        earlier_finding,
    ]

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    findings = analyzer.analyze("src")

    assert findings == [
        earlier_finding,
        later_finding,
    ]


def test_findings_are_sorted_by_column_number() -> None:
    """Column numbers should order findings on the same line."""

    later_finding = _finding(
        "src/example.py",
        line_number=4,
        column_number=15,
    )
    earlier_finding = _finding(
        "src/example.py",
        line_number=4,
        column_number=3,
    )

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [Path("src/example.py")]
    reader.read.return_value = _source_file("src/example.py")
    engine.analyze.return_value = [
        later_finding,
        earlier_finding,
    ]

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    findings = analyzer.analyze("src")

    assert findings == [
        earlier_finding,
        later_finding,
    ]


def test_none_column_number_is_sorted_as_zero() -> None:
    """A missing column number should sort as column zero."""

    column_finding = _finding(
        "src/example.py",
        line_number=4,
        column_number=1,
    )
    no_column_finding = _finding(
        "src/example.py",
        line_number=4,
        column_number=None,
    )

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [Path("src/example.py")]
    reader.read.return_value = _source_file("src/example.py")
    engine.analyze.return_value = [
        column_finding,
        no_column_finding,
    ]

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    findings = analyzer.analyze("src")

    assert findings == [
        no_column_finding,
        column_finding,
    ]


def test_same_location_findings_are_sorted_by_rule_id() -> None:
    """Rule IDs should break ties at the same source location."""

    later_rule = _finding(
        "src/example.py",
        rule_id="SA010",
    )
    earlier_rule = _finding(
        "src/example.py",
        rule_id="SA002",
    )

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [Path("src/example.py")]
    reader.read.return_value = _source_file("src/example.py")
    engine.analyze.return_value = [
        later_rule,
        earlier_rule,
    ]

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    findings = analyzer.analyze("src")

    assert findings == [
        earlier_rule,
        later_rule,
    ]


def test_scanner_file_not_found_error_is_propagated() -> None:
    """Scanner FileNotFoundError exceptions should not be hidden."""

    scanner = Mock()
    scanner.scan.side_effect = FileNotFoundError(
        "Target path does not exist."
    )

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=Mock(),
        engine=Mock(),
    )

    with pytest.raises(
        FileNotFoundError,
        match="Target path does not exist",
    ):
        analyzer.analyze("missing")


def test_scanner_not_a_directory_error_is_propagated() -> None:
    """Scanner NotADirectoryError exceptions should not be hidden."""

    scanner = Mock()
    scanner.scan.side_effect = NotADirectoryError(
        "Target path is not a directory."
    )

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=Mock(),
        engine=Mock(),
    )

    with pytest.raises(
        NotADirectoryError,
        match="Target path is not a directory",
    ):
        analyzer.analyze("example.py")


def test_reader_syntax_error_is_propagated() -> None:
    """Reader SyntaxError exceptions should not be hidden."""

    scanner = Mock()
    reader = Mock()

    scanner.scan.return_value = [Path("src/broken.py")]
    reader.read.side_effect = SyntaxError("invalid syntax")

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=Mock(),
    )

    with pytest.raises(
        SyntaxError,
        match="invalid syntax",
    ):
        analyzer.analyze("src")


def test_reader_unicode_decode_error_is_propagated() -> None:
    """Reader UnicodeDecodeError exceptions should not be hidden."""

    scanner = Mock()
    reader = Mock()

    scanner.scan.return_value = [Path("src/broken.py")]
    reader.read.side_effect = UnicodeDecodeError(
        "utf-8",
        b"\xff",
        0,
        1,
        "invalid start byte",
    )

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=Mock(),
    )

    with pytest.raises(UnicodeDecodeError):
        analyzer.analyze("src")


def test_engine_error_is_propagated() -> None:
    """Analysis-engine exceptions should not be hidden."""

    source_file = _source_file("src/example.py")
    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [source_file.file_path]
    reader.read.return_value = source_file
    engine.analyze.side_effect = RuntimeError(
        "Analysis engine failed."
    )

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    with pytest.raises(
        RuntimeError,
        match="Analysis engine failed",
    ):
        analyzer.analyze("src")


def test_finding_objects_are_not_modified() -> None:
    """The analyzer should return the original finding objects unchanged."""

    finding = _finding(
        "src/example.py",
        line_number=8,
        column_number=None,
        rule_id="SA004",
    )
    finding_before = finding.to_dict()

    scanner = Mock()
    reader = Mock()
    engine = Mock()

    scanner.scan.return_value = [Path("src/example.py")]
    reader.read.return_value = _source_file("src/example.py")
    engine.analyze.return_value = [finding]

    analyzer = ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )

    findings = analyzer.analyze("src")

    assert findings[0] is finding
    assert finding.to_dict() == finding_before