"""Detect invalid Python function and class names."""

from __future__ import annotations

import ast
import re

from static_analyzer.models import Finding, Severity
from static_analyzer.rules.base import BaseRule


_SNAKE_CASE_PATTERN = re.compile(
    r"^_*[a-z][a-z0-9]*(?:_[a-z0-9]+)*$"
)

_PASCAL_CASE_PATTERN = re.compile(
    r"^_*[A-Z][A-Za-z0-9]*$"
)


class NamingConventionRule(BaseRule):
    """Detect function and class naming convention violations."""

    rule_id = "SA006"
    name = "Naming Convention"
    description = (
        "Detect function and class names that violate naming conventions."
    )

    def check(
        self,
        tree: ast.AST,
        file_path: str,
    ) -> list[Finding]:
        """Return findings for invalid function and class names."""

        definitions = sorted(
            (
                node
                for node in ast.walk(tree)
                if isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                        ast.ClassDef,
                    ),
                )
            ),
            key=lambda node: (
                node.lineno,
                node.col_offset,
            ),
        )

        findings: list[Finding] = []

        for definition in definitions:
            if isinstance(definition, ast.ClassDef):
                if self._is_valid_class_name(definition.name):
                    continue

                message = "Class name should use PascalCase."

            else:
                if self._is_dunder_name(definition.name):
                    continue

                if self._is_valid_function_name(definition.name):
                    continue

                message = "Function name should use snake_case."

            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    message=message,
                    file_path=file_path,
                    line_number=definition.lineno,
                    severity=Severity.INFO,
                    column_number=definition.col_offset + 1,
                )
            )

        return findings

    @staticmethod
    def _is_dunder_name(name: str) -> bool:
        """Return whether a name represents a Python special method."""

        return (
            len(name) > 4
            and name.startswith("__")
            and name.endswith("__")
        )

    @staticmethod
    def _is_valid_function_name(name: str) -> bool:
        """Return whether a function name uses snake_case."""

        return _SNAKE_CASE_PATTERN.fullmatch(name) is not None

    @staticmethod
    def _is_valid_class_name(name: str) -> bool:
        """Return whether a class name uses PascalCase."""

        return _PASCAL_CASE_PATTERN.fullmatch(name) is not None