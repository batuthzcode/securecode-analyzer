"""Coordinate static analysis across all Python files in a project."""

from __future__ import annotations

from pathlib import Path

from static_analyzer.analysis_engine import AnalysisEngine
from static_analyzer.file_scanner import FileScanner
from static_analyzer.models import Finding
from static_analyzer.source_reader import SourceReader


class ProjectAnalyzer:
    """Analyze every Python file discovered in a target directory."""

    def __init__(
        self,
        scanner: FileScanner,
        reader: SourceReader,
        engine: AnalysisEngine,
    ) -> None:
        """Initialize the analyzer with its required dependencies."""

        self.scanner = scanner
        self.reader = reader
        self.engine = engine

    def analyze(
        self,
        target: str | Path,
    ) -> list[Finding]:
        """Analyze all discovered Python files and return sorted findings."""

        python_files = self.scanner.scan(target)
        findings: list[Finding] = []

        for file_path in python_files:
            source_file = self.reader.read(file_path)
            file_findings = self.engine.analyze(source_file)
            findings.extend(file_findings)

        return sorted(
            findings,
            key=self._finding_sort_key,
        )

    @staticmethod
    def _finding_sort_key(
        finding: Finding,
    ) -> tuple[str, int, int, str]:
        """Return a stable ordering key for a finding."""

        return (
            finding.file_path.casefold(),
            finding.line_number,
            finding.column_number or 0,
            finding.rule_id,
        )