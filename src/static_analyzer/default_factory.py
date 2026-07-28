"""Create the default static analyzer components."""

from __future__ import annotations

from static_analyzer.analysis_engine import (
    AnalysisEngine,
    AnalysisRule,
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


def create_default_rules() -> tuple[AnalysisRule, ...]:
    """Create a new collection of default analysis rules."""

    return (
        LongFunctionRule(),
        LongClassRule(),
        TodoFixmeRule(),
        EmptyExceptRule(),
        HardcodedSecretRule(),
        NamingConventionRule(),
    )


def create_default_analyzer() -> ProjectAnalyzer:
    """Create a project analyzer with all default components."""

    scanner = FileScanner()
    reader = SourceReader()
    engine = AnalysisEngine(
        rules=create_default_rules(),
    )

    return ProjectAnalyzer(
        scanner=scanner,
        reader=reader,
        engine=engine,
    )