"""Tests for the hardcoded secret analysis rule."""

import ast

from static_analyzer.models import Severity
from static_analyzer.rules import BaseRule, HardcodedSecretRule


def _parse(source: str) -> ast.AST:
    """Parse source code for rule tests."""

    return ast.parse(source)


def test_rule_uses_expected_metadata() -> None:
    """The rule should expose stable public metadata."""

    rule = HardcodedSecretRule()

    assert rule.rule_id == "SA005"
    assert rule.name == "Hardcoded Secret"
    assert rule.description == (
        "Detect string literals assigned to sensitive variable names."
    )


def test_rule_implements_base_rule() -> None:
    """The rule should implement the AST rule contract."""

    rule = HardcodedSecretRule()

    assert isinstance(rule, BaseRule)


def test_empty_source_returns_no_findings() -> None:
    """An empty module should not produce findings."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse(""),
        "example.py",
    )

    assert findings == []


def test_password_assignment_is_detected() -> None:
    """A hardcoded password should produce a finding."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('password = "admin123"\n'),
        "example.py",
    )

    assert len(findings) == 1


def test_api_key_assignment_is_detected() -> None:
    """A hardcoded API key should produce a finding."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('api_key = "abc123"\n'),
        "example.py",
    )

    assert len(findings) == 1


def test_sensitive_name_detection_is_case_insensitive() -> None:
    """Sensitive names should be matched case-insensitively."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('API_KEY = "abc123"\n'),
        "example.py",
    )

    assert len(findings) == 1


def test_sensitive_snake_case_name_is_detected() -> None:
    """Sensitive words inside snake_case names should be detected."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('database_password = "admin123"\n'),
        "example.py",
    )

    assert len(findings) == 1


def test_annotated_assignment_is_detected() -> None:
    """An annotated hardcoded secret should be detected."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('client_secret: str = "secret-value"\n'),
        "example.py",
    )

    assert len(findings) == 1


def test_attribute_assignment_is_detected() -> None:
    """A sensitive attribute assignment should be detected."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('config.password = "admin123"\n'),
        "example.py",
    )

    assert len(findings) == 1


def test_multiple_sensitive_targets_produce_multiple_findings() -> None:
    """Every sensitive target should produce a finding."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse(
            'password = backup_password = "admin123"\n'
        ),
        "example.py",
    )

    assert len(findings) == 2


def test_empty_string_is_ignored() -> None:
    """An empty string should not be reported."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('password = ""\n'),
        "example.py",
    )

    assert findings == []


def test_whitespace_only_string_is_ignored() -> None:
    """A whitespace-only string should not be reported."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('token = "   "\n'),
        "example.py",
    )

    assert findings == []


def test_environment_variable_call_is_ignored() -> None:
    """Environment variable lookups should not be reported."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('api_key = os.getenv("API_KEY")\n'),
        "example.py",
    )

    assert findings == []


def test_function_call_is_ignored() -> None:
    """Secrets returned by functions should not be reported."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse("secret = load_secret()\n"),
        "example.py",
    )

    assert findings == []


def test_non_string_values_are_ignored() -> None:
    """Numeric and None values should not be reported."""

    source = (
        "password = None\n"
        "token = 12345\n"
    )
    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_non_sensitive_variable_is_ignored() -> None:
    """A normal variable should not produce a finding."""

    source = (
        'username = "admin"\n'
        'message = "secret"\n'
    )
    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings == []


def test_finding_uses_real_file_path() -> None:
    """The provided file path should be copied into the finding."""

    file_path = "src/nested/settings.py"
    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('password = "admin123"\n'),
        file_path,
    )

    assert findings[0].file_path == file_path


def test_finding_uses_target_line_and_column() -> None:
    """The finding should point to the sensitive target."""

    source = (
        "def configure() -> None:\n"
        '    password = "admin123"\n'
    )
    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert findings[0].line_number == 2
    assert findings[0].column_number == 5


def test_finding_uses_expected_payload() -> None:
    """The finding should contain the expected public data."""

    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse('password = "admin123"\n'),
        "example.py",
    )

    finding = findings[0]

    assert finding.rule_id == "SA005"
    assert finding.message == "Possible hardcoded secret found."
    assert finding.severity is Severity.WARNING


def test_findings_preserve_source_order() -> None:
    """Findings should follow their natural source order."""

    source = (
        'password = "first"\n'
        'api_key = "second"\n'
        'client_secret = "third"\n'
    )
    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse(source),
        "example.py",
    )

    assert [finding.line_number for finding in findings] == [
        1,
        2,
        3,
    ]


def test_secret_value_is_not_exposed_in_message() -> None:
    """The actual secret should not appear in the finding message."""

    secret_value = "super-secret-value"
    rule = HardcodedSecretRule()

    findings = rule.check(
        _parse(f'password = "{secret_value}"\n'),
        "example.py",
    )

    assert secret_value not in findings[0].message


def test_rule_does_not_modify_existing_ast() -> None:
    """Analysis should not mutate the provided AST object."""

    tree = _parse('password = "admin123"\n')
    tree_before = ast.dump(
        tree,
        include_attributes=True,
    )
    rule = HardcodedSecretRule()

    rule.check(tree, "example.py")

    tree_after = ast.dump(
        tree,
        include_attributes=True,
    )

    assert tree_after == tree_before