"""Detect except blocks that contain only pass statements."""

from __future__ import annotations

import ast

from static_analyzer.models import Finding, Severity
from static_analyzer.rules.base import BaseRule


class EmptyExceptRule(BaseRule):
    """Detect exception handlers that silently ignore errors."""

    rule_id = "SA004"
    name = "Empty Except Block"
    description = (
        "Detect except blocks that contain only pass statements."
    )

    def check(
        self,
        tree: ast.AST,
        file_path: str,
    ) -> list[Finding]:
        """Return findings for pass-only exception handlers."""

        handlers = sorted(
            (
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.ExceptHandler)
            ),
            key=lambda handler: (
                handler.lineno,
                handler.col_offset,
            ),
        )

        findings: list[Finding] = []

        for handler in handlers:
            if not handler.body:
                continue

            if not all(
                isinstance(statement, ast.Pass)
                for statement in handler.body
            ):
                continue

            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    message="Empty except block found.",
                    file_path=file_path,
                    line_number=handler.lineno,
                    severity=Severity.WARNING,
                    column_number=handler.col_offset + 1,
                )
            )

        return findings