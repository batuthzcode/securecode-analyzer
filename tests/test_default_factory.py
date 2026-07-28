"""Tests for the default static analyzer factory."""

import ast
from pathlib import Path

import pytest

from static_analyzer.analysis_engine import AnalysisEngine
from static_analyzer.default_factory import (
    create_default_analyzer,
    create_default_rules,
)
from static_analyzer.file_scanner import FileScanner
from static_analyzer.project_analyzer import ProjectAnalyzer
from static_analyzer.rules import (
    EmptyExceptRule,
    HardcodedSecretRule,
    LongClassRule,
    LongFunctionRule,
    NamingConventionRule,
    TodoFixmeRule,
)
from static_analyzer.source_reader import SourceReader


def _function_source(total_lines: int) -> str:
    """Create a function containing the requested total line count."""

    body_line_count = total_lines - 1

    return (
        "def example_function() -> None:\n"
        + "".join(
            "    pass\n"
            for _ in range(body_line_count)
        )
    )


def _class_source(total_lines: int) -> str:
    """Create a class containing the requested total line count."""

    body_line_count = total_lines - 1

    return (
        "class ExampleClass:\n"
        + "".join(
            "    pass\n"
            for _ in range(body_line_count)
        )
    )


def test_default_rules_are_returned_as_tuple() -> None:
    """The default rule collection should be immutable."""

    rules = create_default_rules()

    assert isinstance(rules, tuple)


def test_default_rules_contain_exactly_six_rules() -> None:
    """The factory should create exactly six default rules."""

    rules = create_default_rules()

    assert len(rules) == 6


def test_default_rules_use_expected_classes() -> None:
    """Every supported rule class should be included in order."""

    rules = create_default_rules()

    assert tuple(type(rule) for rule in rules) == (
        LongFunctionRule,
        LongClassRule,
        TodoFixmeRule,
        EmptyExceptRule,
        HardcodedSecretRule,
        NamingConventionRule,
    )


def test_default_rule_ids_use_stable_order() -> None:
    """Default rule identifiers should follow their public order."""

    rules = create_default_rules()

    assert tuple(rule.rule_id for rule in rules) == (
        "SA001",
        "SA002",
        "SA003",
        "SA004",
        "SA005",
        "SA006",
    )


def test_each_rules_call_returns_new_tuple() -> None:
    """Factory calls should not share the same tuple object."""

    first_rules = create_default_rules()
    second_rules = create_default_rules()

    assert first_rules is not second_rules


def test_each_rules_call_returns_new_rule_objects() -> None:
    """Factory calls should create independent rule instances."""

    first_rules = create_default_rules()
    second_rules = create_default_rules()

    assert all(
        first_rule is not second_rule
        for first_rule, second_rule in zip(
            first_rules,
            second_rules,
            strict=True,
        )
    )


def test_long_function_rule_uses_default_threshold() -> None:
    """The long-function rule should retain its default limit."""

    long_function_rule = create_default_rules()[0]

    exact_limit_findings = long_function_rule.check(
        ast.parse(_function_source(50)),
        "example.py",
    )
    over_limit_findings = long_function_rule.check(
        ast.parse(_function_source(51)),
        "example.py",
    )

    assert exact_limit_findings == []
    assert len(over_limit_findings) == 1


def test_long_class_rule_uses_default_threshold() -> None:
    """The long-class rule should retain its default limit."""

    long_class_rule = create_default_rules()[1]

    exact_limit_findings = long_class_rule.check(
        ast.parse(_class_source(200)),
        "example.py",
    )
    over_limit_findings = long_class_rule.check(
        ast.parse(_class_source(201)),
        "example.py",
    )

    assert exact_limit_findings == []
    assert len(over_limit_findings) == 1


def test_default_analyzer_is_project_analyzer() -> None:
    """The factory should return a real ProjectAnalyzer."""

    analyzer = create_default_analyzer()

    assert isinstance(analyzer, ProjectAnalyzer)


def test_default_analyzer_uses_real_file_scanner() -> None:
    """The analyzer should contain a real FileScanner."""

    analyzer = create_default_analyzer()

    assert isinstance(analyzer.scanner, FileScanner)


def test_default_analyzer_uses_real_source_reader() -> None:
    """The analyzer should contain a real SourceReader."""

    analyzer = create_default_analyzer()

    assert isinstance(analyzer.reader, SourceReader)


def test_default_analyzer_uses_real_analysis_engine() -> None:
    """The analyzer should contain a real AnalysisEngine."""

    analyzer = create_default_analyzer()

    assert isinstance(analyzer.engine, AnalysisEngine)


def test_default_engine_contains_expected_rules() -> None:
    """The engine should contain all default rules in stable order."""

    analyzer = create_default_analyzer()

    assert tuple(
        rule.rule_id
        for rule in analyzer.engine.rules
    ) == (
        "SA001",
        "SA002",
        "SA003",
        "SA004",
        "SA005",
        "SA006",
    )


def test_default_analyzer_calls_are_independent() -> None:
    """Separate factory calls should not share mutable components."""

    first_analyzer = create_default_analyzer()
    second_analyzer = create_default_analyzer()

    assert first_analyzer is not second_analyzer
    assert first_analyzer.scanner is not second_analyzer.scanner
    assert first_analyzer.reader is not second_analyzer.reader
    assert first_analyzer.engine is not second_analyzer.engine

    assert all(
        first_rule is not second_rule
        for first_rule, second_rule in zip(
            first_analyzer.engine.rules,
            second_analyzer.engine.rules,
            strict=True,
        )
    )


def test_default_analyzer_runs_end_to_end(
    tmp_path: Path,
) -> None:
    """The factory result should analyze a real temporary project."""

    source_file = tmp_path / "example.py"
    source_file.write_text(
        (
            'password = "admin123"\n'
            "\n"
            "def BadFunction() -> None:\n"
            "    pass\n"
        ),
        encoding="utf-8",
    )

    analyzer = create_default_analyzer()

    findings = analyzer.analyze(tmp_path)
    rule_ids = {
        finding.rule_id
        for finding in findings
    }

    assert "SA005" in rule_ids
    assert "SA006" in rule_ids


def test_default_analyzer_propagates_missing_target_error(
    tmp_path: Path,
) -> None:
    """Missing-target errors should not be hidden by the factory."""

    missing_target = tmp_path / "missing"
    analyzer = create_default_analyzer()

    with pytest.raises(
        FileNotFoundError,
        match="Target path does not exist",
    ):
        analyzer.analyze(missing_target)