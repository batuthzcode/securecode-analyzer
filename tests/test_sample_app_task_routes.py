"""Integration tests for sample application task routes."""

from __future__ import annotations

import pytest

from flask import Response
from flask.testing import FlaskClient

from sample_app import (
    InMemoryTaskStore,
    Task,
    create_app,
)


def create_client(
    tasks: tuple[Task, ...] = (),
) -> tuple[FlaskClient, InMemoryTaskStore]:
    """Create a test client with an isolated task store."""

    store = InMemoryTaskStore(tasks)
    app = create_app(
        {"TESTING": True},
        task_store=store,
    )
    return app.test_client(), store


def assert_error(
    response: Response,
    *,
    status_code: int,
    code: str,
    message: str,
) -> None:
    """Assert the task API error response contract."""

    assert response.status_code == status_code
    assert response.is_json
    assert response.get_json() == {
        "error": {
            "code": code,
            "message": message,
        }
    }


def test_list_tasks_returns_tasks_in_store_order() -> None:
    """GET /tasks serializes the ordered store snapshot."""

    second = Task(id=2, title="Second")
    first = Task(id=1, title="First")
    client, _ = create_client((second, first))

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.get_json() == {
        "tasks": [
            second.to_dict(),
            first.to_dict(),
        ]
    }


def test_list_tasks_returns_empty_list() -> None:
    """An empty store is a successful list response."""

    client, _ = create_client()

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.get_json() == {"tasks": []}


def test_create_task_accepts_json() -> None:
    """POST /tasks creates one task from JSON data."""

    client, store = create_client(
        (Task(id=4, title="Existing"),)
    )

    response = client.post(
        "/tasks",
        json={
            "title": "Prepare release notes",
            "description": "Summarize changes.",
        },
    )

    expected_task = Task(
        id=5,
        title="Prepare release notes",
        description="Summarize changes.",
    )
    assert response.status_code == 201
    assert response.get_json() == {
        "task": expected_task.to_dict()
    }
    assert store.get_task(5) == expected_task


def test_create_task_accepts_urlencoded_form() -> None:
    """POST /tasks accepts standard HTML form data."""

    client, store = create_client()

    response = client.post(
        "/tasks",
        data={
            "title": "Prepare demo",
            "description": "Review the output.",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["task"][
        "title"
    ] == "Prepare demo"
    assert store.get_task(1) is not None


def test_create_task_accepts_multipart_form() -> None:
    """POST /tasks accepts multipart form fields."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        data={"title": "Prepare demo"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    assert response.get_json()["task"][
        "title"
    ] == "Prepare demo"


def test_create_task_defaults_description() -> None:
    """An omitted description becomes an empty string."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        json={"title": "Prepare demo"},
    )

    assert response.status_code == 201
    assert response.get_json()["task"][
        "description"
    ] == ""


def test_create_task_normalizes_text_fields() -> None:
    """Task model normalization applies to HTTP input."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        json={
            "title": "  Prepare demo  ",
            "description": "  Review output.  ",
        },
    )

    assert response.get_json()["task"] == {
        "id": 1,
        "title": "Prepare demo",
        "description": "Review output.",
        "completed": False,
    }


def test_created_task_appears_in_list_and_home() -> None:
    """Created state is visible through API and HTML reads."""

    client, _ = create_client()

    create_response = client.post(
        "/tasks",
        json={"title": "Prepare demo"},
    )
    created_task = create_response.get_json()["task"]

    assert client.get("/tasks").get_json() == {
        "tasks": [created_task]
    }
    assert "Prepare demo" in client.get(
        "/"
    ).get_data(as_text=True)


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        ({}, "title is required."),
        (
            {"title": ""},
            "title must not be empty.",
        ),
        (
            {"title": "   "},
            "title must not be empty.",
        ),
        (
            {"title": 42},
            "title must be a string.",
        ),
    ],
)
def test_create_task_rejects_invalid_title(
    payload: dict[str, object],
    expected_message: str,
) -> None:
    """Task creation requires one non-empty string title."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        json=payload,
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_task",
        message=expected_message,
    )


@pytest.mark.parametrize(
    "description",
    [
        None,
        42,
        ["description"],
    ],
)
def test_create_task_rejects_invalid_description(
    description: object,
) -> None:
    """A present description must be a string."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        json={
            "title": "Prepare demo",
            "description": description,
        },
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_task",
        message="description must be a string.",
    )


@pytest.mark.parametrize(
    "raw_body",
    [
        "[]",
        '"task"',
        "1",
        "null",
    ],
)
def test_create_task_rejects_non_object_json(
    raw_body: str,
) -> None:
    """JSON task requests must contain an object."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        data=raw_body,
        content_type="application/json",
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_request",
        message=(
            "Request body must contain a valid "
            "JSON object."
        ),
    )


def test_create_task_rejects_malformed_json() -> None:
    """Malformed JSON returns the controlled error contract."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        data='{"title":',
        content_type="application/json",
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_request",
        message=(
            "Request body must contain a valid "
            "JSON object."
        ),
    )


@pytest.mark.parametrize(
    ("data", "content_type"),
    [
        ("title=Prepare+demo", "text/plain"),
        (None, None),
    ],
)
def test_create_task_rejects_unsupported_media_type(
    data: str | None,
    content_type: str | None,
) -> None:
    """Unsupported or missing content types return HTTP 415."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        data=data,
        content_type=content_type,
    )

    assert_error(
        response,
        status_code=415,
        code="unsupported_media_type",
        message=(
            "Content-Type must be application/json "
            "or form data."
        ),
    )


@pytest.mark.parametrize(
    ("extra_fields", "expected_message"),
    [
        (
            {"id": 99},
            "Unexpected fields: id.",
        ),
        (
            {"completed": True},
            "Unexpected fields: completed.",
        ),
        (
            {"zeta": 1, "alpha": 2},
            "Unexpected fields: alpha, zeta.",
        ),
    ],
)
def test_create_task_rejects_unexpected_fields(
    extra_fields: dict[str, object],
    expected_message: str,
) -> None:
    """Clients cannot mass-assign task-managed fields."""

    client, _ = create_client()
    payload = {
        "title": "Prepare demo",
        **extra_fields,
    }

    response = client.post(
        "/tasks",
        json=payload,
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_request",
        message=expected_message,
    )


def test_invalid_request_does_not_consume_task_id() -> None:
    """Rejected creation leaves the store and ID sequence unchanged."""

    client, store = create_client()

    invalid_response = client.post(
        "/tasks",
        json={"title": "   "},
    )
    valid_response = client.post(
        "/tasks",
        json={"title": "Prepare demo"},
    )

    assert invalid_response.status_code == 400
    assert valid_response.get_json()["task"][
        "id"
    ] == 1
    assert len(store.list_tasks()) == 1


def test_tasks_route_rejects_unimplemented_method() -> None:
    """Update methods remain unavailable in this phase."""

    client, _ = create_client()

    response = client.put(
        "/tasks",
        json={"title": "Prepare demo"},
    )

    assert response.status_code == 405
