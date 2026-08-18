"""Tests for the sample Flask application foundation."""

import pytest
import sample_app

from flask import Flask

from sample_app import (
    InMemoryTaskStore,
    Task,
    create_app,
)


def test_create_app_applies_test_configuration() -> None:
    """The factory accepts isolated test configuration."""

    app = create_app(
        {
            "TESTING": True,
            "SAMPLE_SETTING": "enabled",
        }
    )

    assert isinstance(app, Flask)
    assert app.testing
    assert app.config["SAMPLE_SETTING"] == "enabled"


def test_create_app_rejects_invalid_store() -> None:
    """The factory requires the supported store implementation."""

    with pytest.raises(
        ValueError,
        match="task_store must be an InMemoryTaskStore",
    ):
        create_app(
            task_store=object()  # type: ignore[arg-type]
        )


def test_home_page_uses_injected_store() -> None:
    """The root response serializes the injected task snapshot."""

    task = Task(
        id=10,
        title="Injected task",
        description="Used by the test app.",
    )
    store = InMemoryTaskStore((task,))
    app = create_app(
        {"TESTING": True},
        task_store=store,
    )

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "application": (
            "SecureCode Analyzer Sample App"
        ),
        "tasks": [task.to_dict()],
    }


def test_default_home_page_contains_demo_tasks() -> None:
    """A default app exposes its deterministic demo data."""

    app = create_app({"TESTING": True})

    response = app.test_client().get("/")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["application"] == (
        "SecureCode Analyzer Sample App"
    )
    assert [
        task["id"]
        for task in payload["tasks"]
    ] == [1, 2]


def test_default_app_instances_have_isolated_stores() -> None:
    """Separate factory calls do not share task mutations."""

    first_app = create_app({"TESTING": True})
    second_app = create_app({"TESTING": True})

    first_store = first_app.extensions[
        "sample_app.task_store"
    ]
    first_store.create_task("Only in first app")

    first_payload = (
        first_app.test_client().get("/").get_json()
    )
    second_payload = (
        second_app.test_client().get("/").get_json()
    )

    assert len(first_payload["tasks"]) == 3
    assert len(second_payload["tasks"]) == 2


def test_home_page_rejects_post_requests() -> None:
    """The foundation root route remains read-only."""

    app = create_app({"TESTING": True})

    response = app.test_client().post("/")

    assert response.status_code == 405


def test_package_exports_foundation_interface() -> None:
    """Factory and store are available from the package."""

    assert sample_app.create_app is create_app
    assert (
        sample_app.InMemoryTaskStore
        is InMemoryTaskStore
    )
