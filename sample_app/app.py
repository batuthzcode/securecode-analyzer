"""Create and configure the sample Flask application."""

from __future__ import annotations

from collections.abc import Mapping

from flask import (
    Flask,
    Response,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)

from sample_app.models import Task
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
    app.add_url_rule(
        "/tasks/<int:task_id>/edit",
        endpoint="edit_task",
        view_func=_edit_task,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/tasks/<int:task_id>/delete",
        endpoint="delete_task_form",
        view_func=_delete_task_form,
        methods=["POST"],
    )


def _index() -> str:
    """Render the browser task workspace."""

    return _render_index()


def _list_tasks() -> dict[str, object]:
    """Return all tasks in store order."""

    return {
        "tasks": _serialize_tasks(
            _get_task_store()
        )
    }


def _create_task(
) -> Response | tuple[dict[str, object], int] | tuple[str, int]:
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
        return _create_task_error_response(error)
    except ValueError as error:
        return _create_task_error_response(
            TaskRequestError(
                code="invalid_task",
                message=str(error),
            )
        )

    if _wants_html_response():
        return redirect(
            url_for("index"),
            code=303,
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


def _edit_task(
    task_id: int,
) -> Response | str | tuple[str, int]:
    """Render or process the browser task edit form."""

    task_store = _get_task_store()

    try:
        current_task = task_store.get_task(task_id)
    except ValueError:
        return _html_task_not_found_response(task_id)

    if current_task is None:
        return _html_task_not_found_response(task_id)

    if request.method == "GET":
        return _render_edit(current_task)

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
        return _render_edit_error(
            current_task,
            error,
        )
    except ValueError as error:
        return _render_edit_error(
            current_task,
            TaskRequestError(
                code="invalid_task",
                message=str(error),
            ),
        )

    if updated_task is None:
        return _html_task_not_found_response(task_id)

    return redirect(
        url_for("index"),
        code=303,
    )


def _delete_task_form(
    task_id: int,
) -> Response | tuple[str, int]:
    """Process one browser delete form."""

    try:
        deleted_task = _get_task_store().delete_task(
            task_id
        )
    except ValueError:
        return _html_task_not_found_response(task_id)

    if deleted_task is None:
        return _html_task_not_found_response(task_id)

    return redirect(
        url_for("index"),
        code=303,
    )


def _serialize_tasks(
    task_store: InMemoryTaskStore,
) -> list[dict[str, object]]:
    """Return JSON-compatible task snapshots."""

    return [
        task.to_dict()
        for task in task_store.list_tasks()
    ]


def _render_index(
    *,
    error: str | None = None,
    form_values: Mapping[str, str] | None = None,
) -> str:
    """Render the task list, counts, and create form."""

    tasks = _get_task_store().list_tasks()
    completed_count = sum(
        task.completed
        for task in tasks
    )

    return render_template(
        "index.html",
        application_name=_APPLICATION_NAME,
        tasks=tasks,
        task_counts={
            "total": len(tasks),
            "completed": completed_count,
            "pending": len(tasks) - completed_count,
        },
        error=error,
        form_values=(
            form_values
            if form_values is not None
            else {
                "title": "",
                "description": "",
            }
        ),
    )


def _render_edit(
    task: Task,
    *,
    error: str | None = None,
    form_values: Mapping[str, str] | None = None,
) -> str:
    """Render one task edit form."""

    return render_template(
        "edit.html",
        application_name=_APPLICATION_NAME,
        task=task,
        error=error,
        form_values=(
            form_values
            if form_values is not None
            else {
                "title": task.title,
                "description": task.description,
                "completed": (
                    "true"
                    if task.completed
                    else "false"
                ),
            }
        ),
    )


def _create_task_error_response(
    error: TaskRequestError,
) -> tuple[dict[str, object], int] | tuple[str, int]:
    """Return a JSON or browser create error."""

    if not _wants_html_response():
        return _task_error_response(error)

    return _render_index(
        error=str(error),
        form_values={
            "title": request.form.get("title", ""),
            "description": request.form.get(
                "description",
                "",
            ),
        },
    ), error.status_code


def _render_edit_error(
    task: Task,
    error: TaskRequestError,
) -> tuple[str, int]:
    """Render a controlled browser edit error."""

    return _render_edit(
        task,
        error=str(error),
        form_values={
            "title": request.form.get(
                "title",
                task.title,
            ),
            "description": request.form.get(
                "description",
                task.description,
            ),
            "completed": request.form.get(
                "completed",
                (
                    "true"
                    if task.completed
                    else "false"
                ),
            ),
        },
    ), error.status_code


def _html_task_not_found_response(
    task_id: int,
) -> tuple[str, int]:
    """Render the missing-task error in the workspace."""

    return _render_index(
        error=f"Task {task_id} was not found."
    ), 404


def _wants_html_response() -> bool:
    """Return whether one non-JSON client prefers HTML."""

    return (
        not request.is_json
        and request.accept_mimetypes["text/html"]
        > request.accept_mimetypes["application/json"]
    )


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
