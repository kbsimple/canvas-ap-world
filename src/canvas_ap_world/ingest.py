"""Pull course materials from Canvas into a local data directory."""

import json
import os
from typing import Any, Dict, List

from canvas_ap_world.canvas_client import CanvasClient


def pull_course_materials(
    client: CanvasClient, course_id: str, data_dir: str = "data"
) -> Dict[str, Any]:
    """Download a course's modules, pages, and assignments to data_dir.

    Returns a manifest describing what was saved. Materials are written
    as JSON so later stages can re-read them without hitting the API.
    """
    course_dir = os.path.join(data_dir, f"course_{course_id}")
    os.makedirs(course_dir, exist_ok=True)

    modules = client.list_modules(course_id)
    _write_json(os.path.join(course_dir, "modules.json"), modules)

    assignments = client.list_assignments(course_id)
    _write_json(os.path.join(course_dir, "assignments.json"), assignments)

    pages = _pull_pages(client, course_id, modules, course_dir)

    manifest = {
        "course_id": course_id,
        "module_count": len(modules),
        "page_count": len(pages),
        "assignment_count": len(assignments),
        "page_slugs": sorted(pages),
    }
    _write_json(os.path.join(course_dir, "manifest.json"), manifest)
    return manifest


def _pull_pages(
    client: CanvasClient,
    course_id: str,
    modules: List[Dict[str, Any]],
    course_dir: str,
) -> List[str]:
    """Fetch every page referenced by module items; return their slugs."""
    slugs = []
    for module in modules:
        for item in module.get("items", []):
            if item.get("type") != "Page":
                continue
            # Page-type module items carry the page's slug in page_url;
            # html_url points at the module item, not the page.
            slug = item.get("page_url") or ""
            if not slug or slug in slugs:
                continue
            slugs.append(slug)
            page = client.get_page(course_id, slug)
            _write_json(
                os.path.join(course_dir, "pages", f"{slug}.json"), page
            )
    return slugs


def _write_json(path: str, payload: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)