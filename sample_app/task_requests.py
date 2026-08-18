"""Parse task write data at the HTTP boundary."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from flask import Request


_CREATE_FIELDS = frozenset(
    {
        "description",
        "title",
    }
)
_UPDATE_FIELDS = frozenset(
    {
        "completed",
        "description",
        "title",
    }
)
_FORM_MIMETYPES = frozenset(
    {
        "application/x-www-form-urlencoded",
        "multipart/form-data",
    }
)
_TRUE_FORM_VALUES = frozenset(
    {
        "1",
        "on",
        "true",
        "yes",
    }
)
_FALSE_FORM_VALUES = frozenset(
    {
        "0",
        "false",
        "no",
        "off",
    }
)


@dataclass(frozen=True, slots=True)
class CreateTaskRequest:
    """Represent validated fields for one task creation."""

    title: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class UpdateTaskRequest:
    """Represent validated fields for one partial update."""

    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TaskRequestError(ValueError):
    """Represent one expected client request failure."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
    ) -> None:
        """Initialize a serializable request error."""

        super().__init__(message)
        self.code = code
        self.status_code = status_code


def parse_create_task_request(
    http_request: Request,
) -> CreateTaskRequest:
    """Parse and validate one JSON or form task request."""

    payload = _load_payload(http_request)
    _reject_unexpected_fields(
        payload,
        _CREATE_FIELDS,
    )

    if "title" not in payload:
        raise TaskRequestError(
            code="invalid_task",
            message="title is required.",
        )

    title = payload["title"]
    description = payload.get("description", "")

    if not isinstance(title, str):
        raise TaskRequestError(
            code="invalid_task",
            message="title must be a string.",
        )

    if not isinstance(description, str):
        raise TaskRequestError(
            code="invalid_task",
            message="description must be a string.",
        )

    return CreateTaskRequest(
        title=title,
        description=description,
    )


def parse_update_task_request(
    http_request: Request,
) -> UpdateTaskRequest:
    """Parse and validate one partial task update."""

    payload = _load_payload(http_request)
    _reject_unexpected_fields(
        payload,
        _UPDATE_FIELDS,
    )

    if not payload:
        raise TaskRequestError(
            code="invalid_request",
            message=(
                "At least one task field is required."
            ),
        )

    return UpdateTaskRequest(
        title=_read_optional_text(
            payload,
            "title",
        ),
        description=_read_optional_text(
            payload,
            "description",
        ),
        completed=_read_optional_completed(
            http_request,
            payload,
        ),
    )


def _load_payload(
    http_request: Request,
) -> Mapping[str, object]:
    """Load one supported request body as a mapping."""

    if http_request.is_json:
        payload = http_request.get_json(
            silent=True
        )

        if not isinstance(payload, dict):
            raise TaskRequestError(
                code="invalid_request",
                message=(
                    "Request body must contain a valid "
                    "JSON object."
                ),
            )

        return payload

    if http_request.mimetype in _FORM_MIMETYPES:
        return http_request.form.to_dict(
            flat=True
        )

    raise TaskRequestError(
        code="unsupported_media_type",
        message=(
            "Content-Type must be application/json "
            "or form data."
        ),
        status_code=415,
    )


def _reject_unexpected_fields(
    payload: Mapping[str, object],
    allowed_fields: frozenset[str],
) -> None:
    """Reject fields outside one write contract."""

    unexpected_fields = sorted(
        set(payload) - allowed_fields
    )

    if not unexpected_fields:
        return

    field_list = ", ".join(unexpected_fields)
    raise TaskRequestError(
        code="invalid_request",
        message=f"Unexpected fields: {field_list}.",
    )


def _read_optional_text(
    payload: Mapping[str, object],
    field_name: str,
) -> str | None:
    """Return one optional validated text field."""

    if field_name not in payload:
        return None

    value = payload[field_name]

    if not isinstance(value, str):
        raise TaskRequestError(
            code="invalid_task",
            message=f"{field_name} must be a string.",
        )

    return value


def _read_optional_completed(
    http_request: Request,
    payload: Mapping[str, object],
) -> bool | None:
    """Return one optional strict completion value."""

    if "completed" not in payload:
        return None

    value = payload["completed"]

    if http_request.is_json:
        if type(value) is not bool:
            raise TaskRequestError(
                code="invalid_task",
                message="completed must be a boolean.",
            )

        return value

    if not isinstance(value, str):
        raise TaskRequestError(
            code="invalid_task",
            message="completed must be a boolean.",
        )

    normalized_value = value.strip().lower()

    if normalized_value in _TRUE_FORM_VALUES:
        return True

    if normalized_value in _FALSE_FORM_VALUES:
        return False

    raise TaskRequestError(
        code="invalid_task",
        message=(
            "completed must be one of: true, false, "
            "1, 0, on, off, yes, no."
        ),
    )
