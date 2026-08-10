"""Tests for the base analysis rule interface."""

import ast

import pytest

from static_analyzer.models import Finding
from static_analyzer.rules import BaseRule


def test_base_rule_cannot_be_instantiated() -> None:
    """BaseRule must remain abstract."""

    with pytest.raises(TypeError):
        BaseRule()


def test_concrete_rule_can_implement_check_contract() -> None:
    """A concrete rule can implement the shared interface."""

    class ExampleRule(BaseRule):
        rule_id = "SA000"
        name = "Example rule"
        description = "Rule used only for testing."

        def check(self, tree: ast.AST, file_path: str) -> list[Finding]:
            return []

    rule = ExampleRule()

    assert rule.rule_id == "SA000"
    assert rule.name == "Example rule"
    assert rule.check(ast.parse("value = 1"), "example.py") == []
