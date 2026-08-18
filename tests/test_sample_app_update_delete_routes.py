"""Integration tests for task update and delete routes."""

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


def create_task(
    task_id: int = 1,
) -> Task:
    """Create a complete task used by route tests."""

    return Task(
        id=task_id,
        title="Review report",
        description="Inspect findings.",
        completed=True,
    )


def assert_error(
    response: Response,
    *,
    status_code: int,
    code: str,
    message: str,
) -> None:
    """Assert the shared task API error contract."""

    assert response.status_code == status_code
    assert response.is_json
    assert response.get_json() == {
        "error": {
            "code": code,
            "message": message,
        }
    }


def test_update_task_accepts_partial_json() -> None:
    """PUT replaces one field and preserves omitted values."""

    original = create_task()
    client, store = create_client((original,))

    response = client.put(
        "/tasks/1",
        json={"title": "  Updated report  "},
    )

    updated = store.get_task(1)
    assert response.status_code == 200
    assert response.get_json()["task"] == {
        "id": 1,
        "title": "Updated report",
        "description": "Inspect findings.",
        "completed": True,
    }
    assert updated is not original
    assert original.title == "Review report"


def test_update_task_accepts_form_text_fields() -> None:
    """PUT accepts title and description from form data."""

    client, _ = create_client((create_task(),))

    response = client.put(
        "/tasks/1",
        data={
            "title": "Updated report",
            "description": "Review final findings.",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["task"] == {
        "id": 1,
        "title": "Updated report",
        "description": "Review final findings.",
        "completed": True,
    }


@pytest.mark.parametrize(
    "completed",
    [
        True,
        False,
    ],
)
def test_update_task_accepts_json_boolean(
    completed: bool,
) -> None:
    """JSON completion requires and preserves a real boolean."""

    client, _ = create_client((create_task(),))

    response = client.put(
        "/tasks/1",
        json={"completed": completed},
    )

    assert response.status_code == 200
    assert response.get_json()["task"][
        "completed"
    ] is completed


@pytest.mark.parametrize(
    ("form_value", "expected_completed"),
    [
        ("true", True),
        ("1", True),
        ("on", True),
        ("yes", True),
        ("FALSE", False),
        ("0", False),
        ("off", False),
        ("No", False),
    ],
)
def test_update_task_parses_form_boolean_tokens(
    form_value: str,
    expected_completed: bool,
) -> None:
    """Form completion uses the documented token table."""

    client, _ = create_client((create_task(),))

    response = client.put(
        "/tasks/1",
        data={"completed": form_value},
    )

    assert response.status_code == 200
    assert response.get_json()["task"][
        "completed"
    ] is expected_completed


def test_update_task_accepts_all_fields_together() -> None:
    """PUT can replace every client-managed task field."""

    first = create_task(1)
    second = create_task(2)
    client, store = create_client((first, second))

    response = client.put(
        "/tasks/1",
        json={
            "title": "Final report",
            "description": "Publish findings.",
            "completed": False,
        },
    )

    updated = store.get_task(1)
    assert response.get_json()["task"] == (
        updated.to_dict()
    )
    assert store.list_tasks() == (
        updated,
        second,
    )


def test_updated_task_appears_in_list_and_home() -> None:
    """Updated state is visible through both read routes."""

    client, _ = create_client((create_task(),))

    update_response = client.put(
        "/tasks/1",
        json={"title": "Final report"},
    )
    updated_task = update_response.get_json()[
        "task"
    ]

    assert client.get("/tasks").get_json() == {
        "tasks": [updated_task]
    }
    assert client.get("/").get_json()[
        "tasks"
    ] == [updated_task]


@pytest.mark.parametrize(
    ("data", "content_type"),
    [
        ("{}", "application/json"),
        (
            "",
            "application/x-www-form-urlencoded",
        ),
    ],
)
def test_update_task_rejects_empty_payload(
    data: str,
    content_type: str,
) -> None:
    """PUT requires at least one supported field."""

    client, _ = create_client((create_task(),))

    response = client.put(
        "/tasks/1",
        data=data,
        content_type=content_type,
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_request",
        message="At least one task field is required.",
    )


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        (
            {"id": 2},
            "Unexpected fields: id.",
        ),
        (
            {"unknown": "value"},
            "Unexpected fields: unknown.",
        ),
    ],
)
def test_update_task_rejects_unexpected_fields(
    payload: dict[str, object],
    expected_message: str,
) -> None:
    """PUT rejects ID and fields outside the update contract."""

    client, _ = create_client((create_task(),))

    response = client.put(
        "/tasks/1",
        json=payload,
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_request",
        message=expected_message,
    )


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        (
            {"title": "   "},
            "title must not be empty.",
        ),
        (
            {"title": 42},
            "title must be a string.",
        ),
        (
            {"description": None},
            "description must be a string.",
        ),
        (
            {"description": ["value"]},
            "description must be a string.",
        ),
    ],
)
def test_update_task_rejects_invalid_text_fields(
    payload: dict[str, object],
    expected_message: str,
) -> None:
    """PUT applies strict Task text validation."""

    original = create_task()
    client, store = create_client((original,))

    response = client.put(
        "/tasks/1",
        json=payload,
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_task",
        message=expected_message,
    )
    assert store.get_task(1) is original


@pytest.mark.parametrize(
    "completed",
    [
        1,
        0,
        "true",
        None,
        [],
    ],
)
def test_update_task_rejects_non_boolean_json(
    completed: object,
) -> None:
    """JSON completion does not coerce truthy values."""

    client, _ = create_client((create_task(),))

    response = client.put(
        "/tasks/1",
        json={"completed": completed},
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_task",
        message="completed must be a boolean.",
    )


@pytest.mark.parametrize(
    "completed",
    [
        "",
        "maybe",
        "2",
    ],
)
def test_update_task_rejects_invalid_form_boolean(
    completed: str,
) -> None:
    """Form completion rejects values outside its token table."""

    client, _ = create_client((create_task(),))

    response = client.put(
        "/tasks/1",
        data={"completed": completed},
    )

    assert_error(
        response,
        status_code=400,
        code="invalid_task",
        message=(
            "completed must be one of: true, false, "
            "1, 0, on, off, yes, no."
        ),
    )


@pytest.mark.parametrize(
    "raw_body",
    [
        "[]",
        "null",
        '{"completed":',
    ],
)
def test_update_task_rejects_invalid_json_body(
    raw_body: str,
) -> None:
    """PUT uses the controlled JSON object error."""

    client, _ = create_client((create_task(),))

    response = client.put(
        "/tasks/1",
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


def test_update_task_rejects_unsupported_media_type() -> None:
    """PUT returns HTTP 415 for unsupported content types."""

    client, _ = create_client((create_task(),))

    response = client.put(
        "/tasks/1",
        data="title=Updated",
        content_type="text/plain",
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


def test_update_missing_task_returns_json_404() -> None:
    """PUT reports an unknown task without creating it."""

    existing = create_task()
    client, store = create_client((existing,))

    response = client.put(
        "/tasks/99",
        json={"title": "Missing"},
    )

    assert_error(
        response,
        status_code=404,
        code="task_not_found",
        message="Task 99 was not found.",
    )
    assert store.list_tasks() == (existing,)


def test_delete_task_returns_empty_204() -> None:
    """DELETE removes one task without a response body."""

    task = create_task()
    client, store = create_client((task,))

    response = client.delete("/tasks/1")

    assert response.status_code == 204
    assert response.data == b""
    assert store.get_task(1) is None


def test_deleted_task_disappears_from_read_routes() -> None:
    """Delete is visible through both task collections."""

    first = create_task(1)
    second = create_task(2)
    client, _ = create_client((first, second))

    client.delete("/tasks/1")

    assert client.get("/tasks").get_json() == {
        "tasks": [second.to_dict()]
    }
    assert client.get("/").get_json()[
        "tasks"
    ] == [second.to_dict()]


def test_delete_missing_task_returns_json_404() -> None:
    """DELETE reports an unknown task with the shared error."""

    client, _ = create_client((create_task(),))

    response = client.delete("/tasks/99")

    assert_error(
        response,
        status_code=404,
        code="task_not_found",
        message="Task 99 was not found.",
    )


def test_create_does_not_reuse_deleted_task_id() -> None:
    """HTTP create continues after a deleted highest ID."""

    client, _ = create_client(
        (
            create_task(1),
            create_task(2),
        )
    )

    client.delete("/tasks/2")
    create_response = client.post(
        "/tasks",
        json={"title": "Third"},
    )

    assert create_response.get_json()["task"][
        "id"
    ] == 3


@pytest.mark.parametrize(
    "task_path",
    [
        "/tasks/0",
        "/tasks/-1",
        "/tasks/not-an-integer",
    ],
)
def test_task_write_routes_reject_invalid_path_id(
    task_path: str,
) -> None:
    """Task write routes require a positive integer path ID."""

    client, _ = create_client((create_task(),))

    assert client.put(
        task_path,
        json={"title": "Invalid"},
    ).status_code == 404
    assert client.delete(task_path).status_code == 404


@pytest.mark.parametrize(
    "method",
    [
        "get",
        "post",
    ],
)
def test_task_item_route_rejects_unimplemented_method(
    method: str,
) -> None:
    """Task item routes expose only PUT and DELETE."""

    client, _ = create_client((create_task(),))

    response = getattr(client, method)(
        "/tasks/1"
    )

    assert response.status_code == 405
