"""Contract tests for the GitHub Actions CI foundation."""

from __future__ import annotations

import re
from pathlib import Path


_REPOSITORY_ROOT = Path(__file__).parents[1]
_WORKFLOW_PATH = (
    _REPOSITORY_ROOT / ".github" / "workflows" / "ci.yml"
)
_ACTION_PATTERN = re.compile(
    r"uses: "
    r"(?P<action>actions/(?:checkout|setup-python))"
    r"@(?P<sha>[0-9a-f]{40})"
    r" # (?P<version>v[0-9]+\.[0-9]+\.[0-9]+)"
)


def _workflow_text() -> str:
    """Return the checked-in workflow document."""

    return _WORKFLOW_PATH.read_text(encoding="utf-8")


def test_workflow_runs_for_pull_requests_and_main_pushes() -> None:
    """CI should cover review changes and merged main commits."""

    workflow = _workflow_text()

    assert (
        "on:\n"
        "  pull_request:\n"
        "  push:\n"
        "    branches:\n"
        "      - main\n"
    ) in workflow
    assert "pull_request_target" not in workflow


def test_workflow_uses_read_only_repository_permissions() -> None:
    """The default token should not receive write permissions."""

    workflow = _workflow_text()

    assert "permissions:\n  contents: read\n" in workflow
    assert not re.search(
        r"(?m)^\s+[a-z-]+: write\s*$",
        workflow,
    )
    assert "persist-credentials: false" in workflow


def test_workflow_cancels_superseded_branch_runs() -> None:
    """New commits should replace obsolete work on the same ref."""

    workflow = _workflow_text()

    assert (
        "group: ci-${{ github.workflow }}-${{ github.ref }}"
        in workflow
    )
    assert "cancel-in-progress: true" in workflow


def test_official_actions_are_pinned_to_expected_commits() -> None:
    """Third-party execution should use reviewed immutable SHAs."""

    matches = {
        match.group("action"): (
            match.group("sha"),
            match.group("version"),
        )
        for match in _ACTION_PATTERN.finditer(
            _workflow_text()
        )
    }

    assert matches == {
        "actions/checkout": (
            "3d3c42e5aac5ba805825da76410c181273ba90b1",
            "v7.0.1",
        ),
        "actions/setup-python": (
            "5fda3b95a4ea91299a34e894583c3862153e4b97",
            "v7.0.0",
        ),
    }


def test_python_environment_is_explicit_and_cached() -> None:
    """CI should reproduce the supported Python setup efficiently."""

    workflow = _workflow_text()

    assert 'python-version: "3.11"' in workflow
    assert "cache: pip" in workflow
    assert "cache-dependency-path: pyproject.toml" in workflow


def test_dependency_install_and_test_commands_are_ordered() -> None:
    """The job should prepare pip, install dev extras, then test."""

    workflow = _workflow_text()
    commands = (
        "python -m pip install --upgrade pip",
        'python -m pip install -e ".[dev]"',
        "python -m pytest -q",
    )
    positions = tuple(
        workflow.index(command)
        for command in commands
    )

    assert positions == tuple(sorted(positions))


def test_test_job_has_bounded_ubuntu_execution() -> None:
    """A stuck test run should not consume an unbounded runner."""

    workflow = _workflow_text()

    assert "runs-on: ubuntu-latest" in workflow
    assert "timeout-minutes: 10" in workflow


def test_static_analysis_job_waits_for_tests() -> None:
    """Security analysis should run only after the test gate passes."""

    workflow = _workflow_text()

    assert (
        "  static-analysis:\n"
        "    name: Static analysis\n"
        "    needs: test\n"
        "    runs-on: ubuntu-latest\n"
        "    timeout-minutes: 10\n"
    ) in workflow
    assert workflow.count("persist-credentials: false") == 2
    assert workflow.count('python-version: "3.11"') == 2
    assert workflow.count("actions/checkout@") == 2
    assert workflow.count("actions/setup-python@") == 2


def test_static_analysis_job_writes_project_json_reports() -> None:
    """Project sources should produce separate machine-readable reports."""

    workflow = _workflow_text()

    assert "mkdir -p reports/ci" in workflow
    assert (
        "securecode-analyzer src --format json"
        in workflow
    )
    assert (
        "> reports/ci/static-analysis-src.json"
        in workflow
    )
    assert (
        "securecode-analyzer tools --format json"
        in workflow
    )
    assert (
        "> reports/ci/static-analysis-tools.json"
        in workflow
    )


def test_static_analysis_job_validates_controlled_demo() -> None:
    """Known demo findings should be reported without breaking the gate."""

    workflow = _workflow_text()

    assert (
        "securecode-analyzer sample_app --format json"
        in workflow
    )
    assert (
        "> reports/ci/static-analysis-sample-app.json"
        in workflow
    )
    assert 'if [ "$status" -ne 1 ]; then' in workflow
    assert (
        "reports/ci/static-analysis-sample-app.json"
        in workflow
    )
    assert (
        "reports/sample-app/static-analysis.json"
        in workflow
    )
    assert (
        "python -m pytest "
        "tests/test_sample_app_security_demo.py -q"
        in workflow
    )
