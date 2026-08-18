"""Contract tests for the public installation and usage documentation."""

from pathlib import Path


_REPOSITORY_ROOT = Path(__file__).parents[1]
_README_PATH = _REPOSITORY_ROOT / "README.md"


def _readme() -> str:
    """Return the public README with insignificant whitespace normalized."""

    return " ".join(
        _README_PATH.read_text(encoding="utf-8").split()
    )


def test_readme_documents_cross_platform_installation() -> None:
    """Clone, virtual environment, activation, and install steps are public."""

    readme = _readme()
    required_commands = (
        "git clone https://github.com/batuthzcode/securecode-analyzer.git",
        "python -m venv .venv",
        ".venv\\Scripts\\activate.bat",
        ".\\.venv\\Scripts\\Activate.ps1",
        "source .venv/bin/activate",
        "python -m pip install -e .",
        'python -m pip install -e ".[dev]"',
    )

    assert all(command in readme for command in required_commands)


def test_readme_documents_static_analyzer_contract() -> None:
    """Static text, JSON, threshold, options, and exits are documented."""

    readme = _readme()

    assert "securecode-analyzer src" in readme
    assert "securecode-analyzer src --format json" in readme
    assert "securecode-analyzer src --fail-on warning" in readme
    assert "`any`, `info`, `warning` veya `error`" in readme
    assert "[WARNING] SA005 src/example.py:1:1" in readme
    assert "Hedef, dosya okuma, Unicode" in readme


def test_readme_documents_dependency_scanner_contract() -> None:
    """Dependency scan formats, options, OSV, output, and exits are public."""

    readme = _readme()

    assert "securecode-dependency-scan requirements.txt" in readme
    assert "--output reports\\local\\dependency-scan.json" in readme
    assert "--fail-on high" in readme
    assert "--source` | Hayır | `osv`" in readme
    assert "--timeout` | Hayır | `10.0`" in readme
    assert "https://api.osv.dev/v1/query" in readme
    assert "PYSEC-2024-38" in readme


def test_readme_distinguishes_live_and_local_osv_data() -> None:
    """The deterministic fixture should not be presented as a live database."""

    readme = _readme()

    assert "python -m tools.run_ci_dependency_scan" in readme
    assert "tests/fixtures/osv/fastapi-0.109.0.json" in readme
    assert "HTTP isteği göndermez" in readme
    assert "genel amaçlı offline vulnerability database değildir" in readme


def test_readme_documents_required_limitations() -> None:
    """Language, format, false-positive, API, and fix limits are explicit."""

    readme = _readme()

    assert "yalnızca Python `.py`" in readme
    assert "yalnızca `package==version`" in readme
    assert "false positive veya false negative" in readme
    assert "OSV API erişilebilirliğine" in readme
    assert "güvenli sürüm bilgisi `null` kalabilir" in readme


def test_readme_references_existing_project_documents() -> None:
    """Primary documentation links should resolve inside the repository."""

    documentation_paths = (
        "docs/README.md",
        "docs/scope.md",
        "docs/project-plan.md",
        "docs/self-analysis.md",
        "docs/ci.md",
        "docs/components/static-analyzer/README.md",
        "docs/components/dependency-scanner/README.md",
        "docs/components/sample-web-app/README.md",
    )

    assert all(
        (_REPOSITORY_ROOT / path).is_file()
        for path in documentation_paths
    )


def test_readme_lists_every_static_rule() -> None:
    """The public rule table should contain the complete default ruleset."""

    readme = _readme()

    assert all(
        f"`SA{rule_number:03d}`" in readme
        for rule_number in range(1, 7)
    )
