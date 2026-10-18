"""Thin client over the Canvas LMS API."""

from typing import Any, Dict, Iterator, List, Optional

import requests

from canvas_ap_world.config import Config


class CanvasClient:
    """Read-only client for course materials in a Canvas instance."""

    def __init__(self, config: Config, timeout: float = 30.0) -> None:
        self._base = f"{config.api_url}/api/v1"
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {"Authorization": f"Bearer {config.api_token}"}
        )

    def _get_paginated(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Iterator[Dict[str, Any]]:
        """Yield items from a paginated Canvas endpoint."""
        url: Optional[str] = f"{self._base}{path}"
        query: Optional[Dict[str, Any]] = dict(params or {})
        while url:
            response = self._session.get(
                url, params=query, timeout=self._timeout
            )
            response.raise_for_status()
            for item in response.json():
                yield item
            url = response.links.get("next", {}).get("url")
            query = None  # The next link already carries the params.

    def list_courses(self) -> List[Dict[str, Any]]:
        """List the courses visible to this token."""
        return list(self._get_paginated("/courses"))

    def list_modules(self, course_id: str) -> List[Dict[str, Any]]:
        """List modules for a course."""
        return list(
            self._get_paginated(f"/courses/{course_id}/modules",
                                {"include[]": ["items"]})
        )

    def list_assignments(self, course_id: str) -> List[Dict[str, Any]]:
        """List assignments for a course."""
        return list(self._get_paginated(f"/courses/{course_id}/assignments"))

    def get_page(self, course_id: str, page_slug: str) -> Dict[str, Any]:
        """Fetch a single course page by its slug."""
        response = self._session.get(
            f"{self._base}/courses/{course_id}/pages/{page_slug}",
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    def list_files(self, course_id: str) -> List[Dict[str, Any]]:
        """List files attached to a course."""
        return list(self._get_paginated(f"/courses/{course_id}/files"))

    def download_file(self, url: str, dest_path: str) -> str:
        """Download a Canvas file to dest_path and return the path."""
        response = self._session.get(url, timeout=self._timeout, stream=True)
        response.raise_for_status()
        with open(dest_path, "wb") as handle:
            for chunk in response.iter_content(chunk_size=65536):
                handle.write(chunk)
        return dest_path