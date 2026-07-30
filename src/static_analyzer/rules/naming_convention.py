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

_Definition = (
    ast.FunctionDef
    | ast.AsyncFunctionDef
    | ast.ClassDef
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

        findings: list[Finding] = []

        for definition in self._find_definitions(tree):
            message = self._get_violation_message(definition)

            if message is None:
                continue

            findings.append(
                self._create_finding(
                    definition,
                    message,
                    file_path,
                )
            )

        return findings

    @staticmethod
    def _find_definitions(
        tree: ast.AST,
    ) -> list[_Definition]:
        """Return supported definitions in source order."""

        definitions = (
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
        )

        return sorted(
            definitions,
            key=lambda node: (
                node.lineno,
                node.col_offset,
            ),
        )

    @classmethod
    def _get_violation_message(
        cls,
        definition: _Definition,
    ) -> str | None:
        """Return the naming violation message when invalid."""

        if isinstance(definition, ast.ClassDef):
            if cls._is_valid_class_name(definition.name):
                return None

            return "Class name should use PascalCase."

        if cls._is_dunder_name(definition.name):
            return None

        if cls._is_valid_function_name(definition.name):
            return None

        return "Function name should use snake_case."

    def _create_finding(
        self,
        definition: _Definition,
        message: str,
        file_path: str,
    ) -> Finding:
        """Create one naming-convention finding."""

        return Finding(
            rule_id=self.rule_id,
            message=message,
            file_path=file_path,
            line_number=definition.lineno,
            severity=Severity.INFO,
            column_number=definition.col_offset + 1,
        )

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