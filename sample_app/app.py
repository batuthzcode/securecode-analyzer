"""Create and configure the sample Flask application."""

from __future__ import annotations

from collections.abc import Mapping

from flask import Flask, Response, current_app, request

from sample_app.store import (
    InMemoryTaskStore,
    create_demo_tasks,
)
from sample_app.task_requests import (
    TaskRequestError,
    parse_create_task_request,
    parse_update_task_request,
)


_APPLICATION_NAME = "SecureCode Analyzer Sample App"
_STORE_EXTENSION_KEY = "sample_app.task_store"


def create_app(
    test_config: Mapping[str, object] | None = None,
    *,
    task_store: InMemoryTaskStore | None = None,
) -> Flask:
    """Create one isolated sample application instance."""

    app = Flask(__name__)

    if test_config is not None:
        app.config.from_mapping(test_config)

    app.extensions[_STORE_EXTENSION_KEY] = (
        _select_task_store(task_store)
    )

    _register_routes(app)
    return app


def _select_task_store(
    task_store: InMemoryTaskStore | None,
) -> InMemoryTaskStore:
    """Return an injected store or a fresh demo store."""

    if task_store is None:
        return InMemoryTaskStore(
            create_demo_tasks()
        )

    if not isinstance(
        task_store,
        InMemoryTaskStore,
    ):
        raise ValueError(
            "task_store must be an "
            "InMemoryTaskStore instance."
        )

    return task_store


def _get_task_store() -> InMemoryTaskStore:
    """Return the store bound to the current application."""

    task_store = current_app.extensions.get(
        _STORE_EXTENSION_KEY
    )

    if not isinstance(
        task_store,
        InMemoryTaskStore,
    ):
        raise RuntimeError(
            "Sample app task store is not configured."
        )

    return task_store


def _register_routes(app: Flask) -> None:
    """Register task routes on one application."""

    app.add_url_rule(
        "/",
        endpoint="index",
        view_func=_index,
        methods=["GET"],
    )
    app.add_url_rule(
        "/tasks",
        endpoint="list_tasks",
        view_func=_list_tasks,
        methods=["GET"],
    )
    app.add_url_rule(
        "/tasks",
        endpoint="create_task",
        view_func=_create_task,
        methods=["POST"],
    )
    app.add_url_rule(
        "/tasks/<int:task_id>",
        endpoint="update_task",
        view_func=_update_task,
        methods=["PUT"],
    )
    app.add_url_rule(
        "/tasks/<int:task_id>",
        endpoint="delete_task",
        view_func=_delete_task,
        methods=["DELETE"],
    )


def _index() -> dict[str, object]:
    """Return application details and current tasks."""

    return {
        "application": _APPLICATION_NAME,
        "tasks": _serialize_tasks(
            _get_task_store()
        ),
    }


def _list_tasks() -> dict[str, object]:
    """Return all tasks in store order."""

    return {
        "tasks": _serialize_tasks(
            _get_task_store()
        )
    }


def _create_task() -> tuple[dict[str, object], int]:
    """Validate one request and create an incomplete task."""

    try:
        task_request = parse_create_task_request(
            request
        )
        task = _get_task_store().create_task(
            task_request.title,
            task_request.description,
        )
    except TaskRequestError as error:
        return _task_error_response(error)
    except ValueError as error:
        return _task_error_response(
            TaskRequestError(
                code="invalid_task",
                message=str(error),
            )
        )

    return {"task": task.to_dict()}, 201


def _update_task(
    task_id: int,
) -> tuple[dict[str, object], int]:
    """Validate and apply one partial task update."""

    task_store = _get_task_store()

    try:
        current_task = task_store.get_task(task_id)
    except ValueError:
        return _task_not_found_response(task_id)

    if current_task is None:
        return _task_not_found_response(task_id)

    try:
        task_request = parse_update_task_request(
            request
        )
        updated_task = task_store.update_task(
            task_id,
            title=task_request.title,
            description=task_request.description,
            completed=task_request.completed,
        )
    except TaskRequestError as error:
        return _task_error_response(error)
    except ValueError as error:
        return _task_error_response(
            TaskRequestError(
                code="invalid_task",
                message=str(error),
            )
        )

    if updated_task is None:
        return _task_not_found_response(task_id)

    return {"task": updated_task.to_dict()}, 200


def _delete_task(
    task_id: int,
) -> Response | tuple[dict[str, object], int]:
    """Delete one task and return an empty response."""

    task_store = _get_task_store()

    try:
        deleted_task = task_store.delete_task(
            task_id
        )
    except ValueError:
        return _task_not_found_response(task_id)

    if deleted_task is None:
        return _task_not_found_response(task_id)

    return current_app.response_class(status=204)


def _serialize_tasks(
    task_store: InMemoryTaskStore,
) -> list[dict[str, object]]:
    """Return JSON-compatible task snapshots."""

    return [
        task.to_dict()
        for task in task_store.list_tasks()
    ]


def _task_error_response(
    error: TaskRequestError,
) -> tuple[dict[str, object], int]:
    """Convert an expected request error to JSON."""

    return {
        "error": {
            "code": error.code,
            "message": str(error),
        }
    }, error.status_code


def _task_not_found_response(
    task_id: int,
) -> tuple[dict[str, object], int]:
    """Return the shared missing-task response."""

    return _task_error_response(
        TaskRequestError(
            code="task_not_found",
            message=f"Task {task_id} was not found.",
            status_code=404,
        )
    )
