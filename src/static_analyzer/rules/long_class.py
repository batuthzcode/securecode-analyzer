"""Rule for detecting classes that exceed a configured line limit."""

from __future__ import annotations

import ast

from static_analyzer.models import Finding, Severity
from static_analyzer.rules.base import BaseRule


DEFAULT_MAX_CLASS_LINES = 200


class LongClassRule(BaseRule):
    """Detect classes that exceed the configured maximum line count."""

    rule_id = "SA002"
    name = "Long Class"
    description = "Detect classes that exceed the configured line limit."

    def __init__(
        self,
        max_lines: int = DEFAULT_MAX_CLASS_LINES,
    ) -> None:
        """Initialize the rule with a maximum allowed class length."""

        if (
            isinstance(max_lines, bool)
            or not isinstance(max_lines, int)
            or max_lines <= 0
        ):
            raise ValueError("max_lines must be greater than zero")

        self.max_lines = max_lines

    def check(
        self,
        tree: ast.AST,
        file_path: str,
    ) -> list[Finding]:
        """Return findings for classes exceeding the configured limit."""

        findings: list[Finding] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            end_line = node.end_lineno or node.lineno
            class_length = end_line - node.lineno + 1

            if class_length <= self.max_lines:
                continue

            message = (
                f"Class '{node.name}' has {class_length} lines, "
                f"exceeding the limit of {self.max_lines}."
            )

            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    message=message,
                    file_path=file_path,
                    line_number=node.lineno,
                    column_number=node.col_offset,
                    severity=Severity.WARNING,
                )
            )

        return findings