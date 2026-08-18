"""Serve one recorded OSV query without network access."""

from __future__ import annotations

import json
from pathlib import Path

from dependency_scanner.osv_client import OsvQueryError
from dependency_scanner.osv_models import OsvQueryResponse
from dependency_scanner.osv_parser import (
    OsvResponseParseError,
    parse_osv_query_response,
)
from dependency_scanner.package_normalizer import (
    normalize_package_name,
)


class OsvFixtureError(ValueError):
    """Represent an invalid offline OSV fixture."""


class FixtureOsvQueryClient:
    """Return one checked-in OSV response for its recorded query."""

    def __init__(self, fixture_path: str | Path) -> None:
        """Load and validate one fixture document."""

        self._fixture_path = Path(fixture_path)
        payload = self._load_payload()
        self._package_name, self._version = (
            _parse_fixture_query(payload)
        )

        try:
            self._response = parse_osv_query_response(
                payload
            )
        except OsvResponseParseError as error:
            raise OsvFixtureError(
                f"Invalid OSV response fixture: {error}"
            ) from error

    @property
    def fixture_path(self) -> Path:
        """Return the configured fixture path."""

        return self._fixture_path

    @property
    def expected_query(self) -> tuple[str, str, None]:
        """Return the single package query recorded by the fixture."""

        return (self._package_name, self._version, None)

    def query_package(
        self,
        package_name: str,
        version: str,
        page_token: str | None = None,
    ) -> OsvQueryResponse:
        """Return the response only for the fixture's exact query."""

        try:
            normalized_name = normalize_package_name(
                package_name
            )
        except ValueError as error:
            raise OsvQueryError(
                f"Invalid fixture package query: {error}"
            ) from error

        query = (
            normalized_name,
            version,
            page_token,
        )

        if query != self.expected_query:
            raise OsvQueryError(
                "OSV fixture query does not match its "
                f"recorded input: {query!r}"
            )

        return self._response

    def _load_payload(self) -> dict[str, object]:
        """Read the fixture as one JSON object."""

        try:
            payload = json.loads(
                self._fixture_path.read_text(
                    encoding="utf-8"
                )
            )
        except json.JSONDecodeError as error:
            raise OsvFixtureError(
                f"Invalid OSV fixture JSON: {error.msg}"
            ) from error

        if not isinstance(payload, dict):
            raise OsvFixtureError(
                "OSV fixture root must be an object."
            )

        return payload


def _parse_fixture_query(
    payload: dict[str, object],
) -> tuple[str, str]:
    """Return the normalized package and version from metadata."""

    fixture = _require_mapping(
        payload.get("_fixture"),
        "_fixture",
    )
    query = _require_mapping(
        fixture.get("query"),
        "_fixture.query",
    )
    package = _require_mapping(
        query.get("package"),
        "_fixture.query.package",
    )
    ecosystem = _require_string(
        package.get("ecosystem"),
        "_fixture.query.package.ecosystem",
    )

    if ecosystem != "PyPI":
        raise OsvFixtureError(
            "OSV fixture ecosystem must be PyPI."
        )

    package_name = _require_string(
        package.get("name"),
        "_fixture.query.package.name",
    )
    version = _require_string(
        query.get("version"),
        "_fixture.query.version",
    )

    try:
        normalized_name = normalize_package_name(
            package_name
        )
    except ValueError as error:
        raise OsvFixtureError(
            f"Invalid OSV fixture package name: {error}"
        ) from error

    return normalized_name, version


def _require_mapping(
    value: object,
    path: str,
) -> dict[str, object]:
    """Require one metadata mapping."""

    if not isinstance(value, dict):
        raise OsvFixtureError(
            f"{path} must be an object."
        )

    return value


def _require_string(
    value: object,
    path: str,
) -> str:
    """Require one non-empty metadata string."""

    if not isinstance(value, str) or not value.strip():
        raise OsvFixtureError(
            f"{path} must be a non-empty string."
        )

    return value.strip()
