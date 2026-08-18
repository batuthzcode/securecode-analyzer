"""Create and configure the sample Flask application."""

from __future__ import annotations

from collections.abc import Mapping

from flask import Flask, current_app, request

from sample_app.store import (
    InMemoryTaskStore,
    create_demo_tasks,
)
from sample_app.task_requests import (
    TaskRequestError,
    parse_create_task_request,
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
