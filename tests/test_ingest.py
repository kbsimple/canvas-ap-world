"""Tests for ingesting course materials."""

import json
import os
from typing import Any, Dict, List

import pytest

from canvas_ap_world.canvas_client import CanvasClient
from canvas_ap_world.ingest import pull_course_materials


class FakeCanvasClient:
    """Stand-in for CanvasClient that returns canned API payloads."""

    def __init__(self, modules: List[Dict[str, Any]],
                 assignments: List[Dict[str, Any]],
                 pages: Dict[str, Dict[str, Any]]) -> None:
        self._modules = modules
        self._assignments = assignments
        self._pages = pages

    def list_modules(self, course_id: str) -> List[Dict[str, Any]]:
        return self._modules

    def list_assignments(self, course_id: str) -> List[Dict[str, Any]]:
        return self._assignments

    def get_page(self, course_id: str, page_slug: str) -> Dict[str, Any]:
        return self._pages[page_slug]


def test_pull_writes_manifest_and_pages(tmp_path: Any) -> None:
    client: Any = FakeCanvasClient(
        modules=[
            {
                "id": 1,
                "name": "Unit 3",
                "items": [
                    {
                        "type": "Page",
                        "title": "Unit 3",
                        "page_url": "unit-3",
                        "html_url":
                            "https://canvas.example.com/c/1/modules/items/7",
                    },
                    {"type": "Assignment"},
                ],
            }
        ],
        assignments=[{"id": 9, "name": "DBQ: Empires"}],
        pages={"unit-3": {"title": "Unit 3", "body": "<p>Empires.</p>"}},
    )
    manifest = pull_course_materials(client, "1", data_dir=str(tmp_path))

    assert manifest["module_count"] == 1
    assert manifest["page_count"] == 1
    assert manifest["assignment_count"] == 1
    assert manifest["page_slugs"] == ["unit-3"]

    course_dir = os.path.join(str(tmp_path), "course_1")
    with open(os.path.join(course_dir, "manifest.json")) as handle:
        assert json.load(handle)["page_slugs"] == ["unit-3"]
    with open(os.path.join(course_dir, "pages", "unit-3.json")) as handle:
        assert json.load(handle)["title"] == "Unit 3"


def test_canvas_client_sends_bearer_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CANVAS_API_URL", "https://canvas.example.com")
    monkeypatch.setenv("CANVAS_API_TOKEN", "secret")
    client = CanvasClient.__new__(CanvasClient)
    import requests

    client._base = "https://canvas.example.com/api/v1"
    client._timeout = 1.0
    client._session = requests.Session()
    client._session.headers.update(
        {"Authorization": "Bearer secret"}
    )
    assert (
        client._session.headers["Authorization"] == "Bearer secret"
    )