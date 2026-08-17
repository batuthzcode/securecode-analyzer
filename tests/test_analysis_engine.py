"""Tests for coordinating static analysis rules."""

import ast
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from static_analyzer.analysis_engine import AnalysisEngine
from static_analyzer.models import Finding, Severity
from static_analyzer.rules.base import BaseRule
from static_analyzer.source_reader import SourceFile


class RecordingRule(BaseRule):
    """Record rule calls and return configured findings."""

    rule_id = "TEST"
    name = "Recording Rule"
    description = "A test rule that records analysis calls."

    def __init__(
        self,
        findings: Sequence[Finding] = (),
        error: Exception | None = None,
    ) -> None:
        """Initialize the rule with findings or an optional error."""

        self.findings = list(findings)
        self.error = error
        self.calls: list[tuple[ast.AST, str]] = []

    def check(
        self,
        tree: ast.AST,
        file_path: str,
    ) -> list[Finding]:
        """Record the call and return the configured findings."""

        self.calls.append((tree, file_path))

        if self.error is not None:
            raise self.error

        return list(self.findings)


def _create_source_file(
    file_path: Path,
    source: str = "value = 1\n",
) -> SourceFile:
    """Create a parsed source file for engine tests."""

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
    line_number: int = 1,
) -> Finding:
    """Create a finding for engine tests."""

    return Finding(
        rule_id=rule_id,
        message=f"Finding from {rule_id}",
        file_path="example.py",
        line_number=line_number,
        severity=Severity.WARNING,
    )


def test_rules_are_stored_as_tuple() -> None:
    """Rules supplied as an iterable should be stored as a tuple."""

    first_rule = RecordingRule()
    second_rule = RecordingRule()
    supplied_rules = (
        rule
        for rule in [first_rule, second_rule]
    )

    engine = AnalysisEngine(supplied_rules)

    assert isinstance(engine.rules, tuple)
    assert engine.rules == (first_rule, second_rule)


def test_empty_rule_collection_returns_empty_findings(
    tmp_path: Path,
) -> None:
    """An engine without rules should return an empty result."""

    source_file = _create_source_file(tmp_path / "example.py")
    engine = AnalysisEngine([])

    findings = engine.analyze(source_file)

    assert findings == []


def test_single_rule_is_called_once(
    tmp_path: Path,
) -> None:
    """A registered rule should run exactly once per analysis."""

    source_file = _create_source_file(tmp_path / "example.py")
    rule = RecordingRule()
    engine = AnalysisEngine([rule])

    engine.analyze(source_file)

    assert len(rule.calls) == 1


def test_multiple_rules_are_each_called_once(
    tmp_path: Path,
) -> None:
    """Every registered rule should run exactly once."""

    source_file = _create_source_file(tmp_path / "example.py")
    first_rule = RecordingRule()
    second_rule = RecordingRule()
    engine = AnalysisEngine([first_rule, second_rule])

    engine.analyze(source_file)

    assert len(first_rule.calls) == 1
    assert len(second_rule.calls) == 1


def test_same_ast_object_is_passed_to_every_rule(
    tmp_path: Path,
) -> None:
    """Every rule should receive the existing source AST."""

    source_file = _create_source_file(tmp_path / "example.py")
    first_rule = RecordingRule()
    second_rule = RecordingRule()
    engine = AnalysisEngine([first_rule, second_rule])

    engine.analyze(source_file)

    assert first_rule.calls[0][0] is source_file.tree
    assert second_rule.calls[0][0] is source_file.tree


def test_real_file_path_is_passed_as_string(
    tmp_path: Path,
) -> None:
    """Rules should receive the source file path as a string."""

    file_path = tmp_path / "nested" / "example.py"
    source_file = _create_source_file(file_path)
    rule = RecordingRule()
    engine = AnalysisEngine([rule])

    engine.analyze(source_file)

    assert rule.calls[0][1] == str(file_path)


def test_source_is_not_parsed_again(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The engine should reuse the AST stored in SourceFile."""

    source_file = _create_source_file(tmp_path / "example.py")
    rule = RecordingRule()
    engine = AnalysisEngine([rule])

    def unexpected_parse(
        *args: Any,
        **kwargs: Any,
    ) -> ast.AST:
        raise AssertionError(
            "AnalysisEngine must not parse the source again."
        )

    monkeypatch.setattr(ast, "parse", unexpected_parse)

    engine.analyze(source_file)

    assert len(rule.calls) == 1


def test_single_finding_is_returned(
    tmp_path: Path,
) -> None:
    """A finding produced by one rule should be returned."""

    source_file = _create_source_file(tmp_path / "example.py")
    expected_finding = _create_finding("TEST001")
    rule = RecordingRule([expected_finding])
    engine = AnalysisEngine([rule])

    findings = engine.analyze(source_file)

    assert findings == [expected_finding]


def test_multiple_findings_from_one_rule_are_preserved(
    tmp_path: Path,
) -> None:
    """All findings returned by one rule should be preserved."""

    source_file = _create_source_file(tmp_path / "example.py")
    first_finding = _create_finding("TEST001", line_number=1)
    second_finding = _create_finding("TEST001", line_number=2)
    rule = RecordingRule(
        [
            first_finding,
            second_finding,
        ]
    )
    engine = AnalysisEngine([rule])

    findings = engine.analyze(source_file)

    assert findings == [
        first_finding,
        second_finding,
    ]


def test_findings_keep_rule_and_internal_order(
    tmp_path: Path,
) -> None:
    """Findings should preserve rule order and internal result order."""

    source_file = _create_source_file(tmp_path / "example.py")
    first_finding = _create_finding("FIRST", line_number=1)
    second_finding = _create_finding("FIRST", line_number=2)
    third_finding = _create_finding("SECOND", line_number=3)

    first_rule = RecordingRule(
        [
            first_finding,
            second_finding,
        ]
    )
    second_rule = RecordingRule([third_finding])
    engine = AnalysisEngine([first_rule, second_rule])

    findings = engine.analyze(source_file)

    assert findings == [
        first_finding,
        second_finding,
        third_finding,
    ]


def test_rule_without_findings_returns_empty_list(
    tmp_path: Path,
) -> None:
    """A rule with no findings should produce an empty result."""

    source_file = _create_source_file(tmp_path / "example.py")
    rule = RecordingRule()
    engine = AnalysisEngine([rule])

    findings = engine.analyze(source_file)

    assert findings == []


def test_rule_exception_is_not_hidden(
    tmp_path: Path,
) -> None:
    """Unexpected rule errors should be propagated to the caller."""

    source_file = _create_source_file(tmp_path / "example.py")
    rule = RecordingRule(
        error=RuntimeError("Rule execution failed.")
    )
    engine = AnalysisEngine([rule])

    with pytest.raises(
        RuntimeError,
        match="Rule execution failed",
    ):
        engine.analyze(source_file)