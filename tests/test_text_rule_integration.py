"""Tests for text rule integration with the analysis engine."""

import ast
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from static_analyzer.analysis_engine import AnalysisEngine
from static_analyzer.models import Finding
from static_analyzer.rules import BaseRule, BaseTextRule
from static_analyzer.source_reader import SourceFile


class RecordingAstRule(BaseRule):
    """Record AST rule calls and return configured findings."""

    rule_id = "AST-TEST"
    name = "Recording AST Rule"
    description = "Record AST rule calls for tests."

    def __init__(
        self,
        findings: Sequence[Finding] = (),
        events: list[str] | None = None,
        event_name: str = "ast",
    ) -> None:
        """Initialize the test AST rule."""

        self.findings = list(findings)
        self.events = events
        self.event_name = event_name
        self.calls: list[tuple[ast.AST, str]] = []

    def check(
        self,
        tree: ast.AST,
        file_path: str,
    ) -> list[Finding]:
        """Record the AST call and return configured findings."""

        self.calls.append((tree, file_path))

        if self.events is not None:
            self.events.append(self.event_name)

        return list(self.findings)


class RecordingTextRule(BaseTextRule):
    """Record text rule calls and return configured findings."""

    rule_id = "TEXT-TEST"
    name = "Recording Text Rule"
    description = "Record text rule calls for tests."

    def __init__(
        self,
        findings: Sequence[Finding] = (),
        events: list[str] | None = None,
        event_name: str = "text",
        error: Exception | None = None,
    ) -> None:
        """Initialize the test text rule."""

        self.findings = list(findings)
        self.events = events
        self.event_name = event_name
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def check(
        self,
        source: str,
        file_path: str,
    ) -> list[Finding]:
        """Record the text call and return configured findings."""

        self.calls.append((source, file_path))

        if self.events is not None:
            self.events.append(self.event_name)

        if self.error is not None:
            raise self.error

        return list(self.findings)


def _create_source_file(
    file_path: Path,
    source: str = "value = 1\n",
) -> SourceFile:
    """Create a parsed source file for integration tests."""

    return SourceFile(
        file_path=file_path,
        source=source,
        tree=ast.parse(
            source,
            filename=str(file_path),
        ),
    )


def _create_finding(
    rule_id: str,
    line_number: int,
) -> Finding:
    """Create a finding for integration tests."""

    return Finding(
        rule_id=rule_id,
        message=f"Finding from {rule_id}",
        file_path="example.py",
        line_number=line_number,
    )


def test_text_rule_runs_once(
    tmp_path: Path,
) -> None:
    """A registered text rule should run exactly once."""

    source_file = _create_source_file(tmp_path / "example.py")
    rule = RecordingTextRule()
    engine = AnalysisEngine([rule])

    engine.analyze(source_file)

    assert len(rule.calls) == 1


def test_text_rule_receives_existing_source(
    tmp_path: Path,
) -> None:
    """A text rule should receive the source stored in SourceFile."""

    source = "# TODO: improve this\nvalue = 1\n"
    source_file = _create_source_file(
        tmp_path / "example.py",
        source,
    )
    rule = RecordingTextRule()
    engine = AnalysisEngine([rule])

    engine.analyze(source_file)

    assert rule.calls[0][0] is source_file.source
    assert rule.calls[0][0] == source


def test_text_rule_receives_real_file_path(
    tmp_path: Path,
) -> None:
    """A text rule should receive the real path as a string."""

    file_path = tmp_path / "nested" / "example.py"
    source_file = _create_source_file(file_path)
    rule = RecordingTextRule()
    engine = AnalysisEngine([rule])

    engine.analyze(source_file)

    assert rule.calls[0][1] == str(file_path)


def test_ast_rule_still_receives_existing_tree(
    tmp_path: Path,
) -> None:
    """AST rule behavior should remain unchanged."""

    source_file = _create_source_file(tmp_path / "example.py")
    rule = RecordingAstRule()
    engine = AnalysisEngine([rule])

    engine.analyze(source_file)

    assert rule.calls[0][0] is source_file.tree


def test_ast_and_text_rules_run_in_registration_order(
    tmp_path: Path,
) -> None:
    """Mixed rule types should run in registration order."""

    source_file = _create_source_file(tmp_path / "example.py")
    events: list[str] = []

    first_rule = RecordingTextRule(
        events=events,
        event_name="first-text",
    )
    second_rule = RecordingAstRule(
        events=events,
        event_name="second-ast",
    )
    third_rule = RecordingTextRule(
        events=events,
        event_name="third-text",
    )

    engine = AnalysisEngine(
        [
            first_rule,
            second_rule,
            third_rule,
        ]
    )

    engine.analyze(source_file)

    assert events == [
        "first-text",
        "second-ast",
        "third-text",
    ]


def test_ast_and_text_findings_are_combined_in_order(
    tmp_path: Path,
) -> None:
    """Findings from mixed rule types should keep their order."""

    source_file = _create_source_file(tmp_path / "example.py")
    first_finding = _create_finding("TEXT001", 1)
    second_finding = _create_finding("AST001", 2)
    third_finding = _create_finding("AST001", 3)

    text_rule = RecordingTextRule([first_finding])
    ast_rule = RecordingAstRule(
        [
            second_finding,
            third_finding,
        ]
    )
    engine = AnalysisEngine([text_rule, ast_rule])

    findings = engine.analyze(source_file)

    assert findings == [
        first_finding,
        second_finding,
        third_finding,
    ]


def test_source_file_is_not_read_again(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The engine should reuse the source stored in SourceFile."""

    source_file = _create_source_file(tmp_path / "example.py")
    rule = RecordingTextRule()
    engine = AnalysisEngine([rule])

    def unexpected_read_text(
        *args: Any,
        **kwargs: Any,
    ) -> str:
        raise AssertionError(
            "AnalysisEngine must not read the source file again."
        )

    monkeypatch.setattr(Path, "read_text", unexpected_read_text)

    engine.analyze(source_file)

    assert len(rule.calls) == 1


def test_source_is_not_parsed_again(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mixed rule execution should reuse the existing AST."""

    source_file = _create_source_file(tmp_path / "example.py")
    ast_rule = RecordingAstRule()
    text_rule = RecordingTextRule()
    engine = AnalysisEngine([ast_rule, text_rule])

    def unexpected_parse(
        *args: Any,
        **kwargs: Any,
    ) -> ast.AST:
        raise AssertionError(
            "AnalysisEngine must not parse the source again."
        )

    monkeypatch.setattr(ast, "parse", unexpected_parse)

    engine.analyze(source_file)

    assert len(ast_rule.calls) == 1
    assert len(text_rule.calls) == 1


def test_each_mixed_rule_runs_once(
    tmp_path: Path,
) -> None:
    """Every AST and text rule should run once."""

    source_file = _create_source_file(tmp_path / "example.py")
    first_ast_rule = RecordingAstRule()
    text_rule = RecordingTextRule()
    second_ast_rule = RecordingAstRule()

    engine = AnalysisEngine(
        [
            first_ast_rule,
            text_rule,
            second_ast_rule,
        ]
    )

    engine.analyze(source_file)

    assert len(first_ast_rule.calls) == 1
    assert len(text_rule.calls) == 1
    assert len(second_ast_rule.calls) == 1


def test_text_rule_exception_is_not_hidden(
    tmp_path: Path,
) -> None:
    """Unexpected text rule errors should reach the caller."""

    source_file = _create_source_file(tmp_path / "example.py")
    rule = RecordingTextRule(
        error=RuntimeError("Text rule execution failed.")
    )
    engine = AnalysisEngine([rule])

    with pytest.raises(
        RuntimeError,
        match="Text rule execution failed",
    ):
        engine.analyze(source_file)