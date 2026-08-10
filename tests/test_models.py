

from static_analyzer.models import Finding, Severity


def test_finding_to_dict_returns_serializable_data() -> None:


    finding = Finding(
        rule_id="SA001",
        message="Example finding",
        file_path="example.py",
        line_number=10,
        column_number=4,
        severity=Severity.ERROR,
    )

    assert finding.to_dict() == {
        "rule_id": "SA001",
        "message": "Example finding",
        "file_path": "example.py",
        "line_number": 10,
        "severity": "error",
        "column_number": 4,
    }


def test_finding_uses_warning_as_default_severity() -> None:


    finding = Finding(
        rule_id="SA002",
        message="Default severity example",
        file_path="example.py",
        line_number=1,
    )

    assert finding.severity is Severity.WARNING
