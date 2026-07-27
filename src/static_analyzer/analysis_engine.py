"""Coordinate execution of static analysis rules."""

from __future__ import annotations

from collections.abc import Iterable

from static_analyzer.models import Finding
from static_analyzer.rules.base import BaseRule
from static_analyzer.source_reader import SourceFile


class AnalysisEngine:
    """Run registered analysis rules against a parsed source file."""

    def __init__(
        self,
        rules: Iterable[BaseRule],
    ) -> None:
        """Initialize the engine with an immutable rule collection."""

        self.rules = tuple(rules)

    def analyze(
        self,
        source_file: SourceFile,
    ) -> list[Finding]:
        """Run every rule and return their combined findings."""

        findings: list[Finding] = []

        for rule in self.rules:
            rule_findings = rule.check(
                source_file.tree,
                str(source_file.file_path),
            )
            findings.extend(rule_findings)

        return findings