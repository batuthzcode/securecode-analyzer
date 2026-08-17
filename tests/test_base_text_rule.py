"""Tests for the base text analysis rule interface."""

import pytest

from static_analyzer.models import Finding
from static_analyzer.rules import BaseTextRule


def test_base_text_rule_cannot_be_instantiated() -> None:
    """BaseTextRule must remain abstract."""

    with pytest.raises(TypeError):
        BaseTextRule()


def test_concrete_text_rule_can_implement_check_contract() -> None:
    """A concrete text rule can implement the shared interface."""

    class ExampleTextRule(BaseTextRule):
        rule_id = "TEXT000"
        name = "Example Text Rule"
        description = "Rule used only for testing."

        def check(
            self,
            source: str,
            file_path: str,
        ) -> list[Finding]:
            return []

    rule = ExampleTextRule()

    assert rule.rule_id == "TEXT000"
    assert rule.name == "Example Text Rule"
    assert rule.check("value = 1\n", "example.py") == []