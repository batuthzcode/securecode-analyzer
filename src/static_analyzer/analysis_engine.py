"""Coordinate execution of static analysis rules."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeAlias

from static_analyzer.models import Finding
from static_analyzer.rules.base import BaseRule
from static_analyzer.rules.base_text import BaseTextRule
from static_analyzer.source_reader import SourceFile


AnalysisRule: TypeAlias = BaseRule | BaseTextRule


class AnalysisEngine:
    """Run registered analysis rules against a parsed source file."""

    def __init__(
        self,
        rules: Iterable[AnalysisRule],
    ) -> None:
        """Initialize the engine with an immutable rule collection."""

        self.rules = tuple(rules)

    def analyze(
        self,
        source_file: SourceFile,
    ) -> list[Finding]:
        """Run every registered rule and combine their findings."""

        findings: list[Finding] = []
        file_path = str(source_file.file_path)

        for rule in self.rules:
            if isinstance(rule, BaseTextRule):
                rule_findings = rule.check(
                    source_file.source,
                    file_path,
                )
            else:
                rule_findings = rule.check(
                    source_file.tree,
                    file_path,
                )

            findings.extend(rule_findings)

        return findings
