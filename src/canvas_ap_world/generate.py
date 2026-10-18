"""Generate study material from analyzed lessons."""

import json
import os
from typing import Any, Dict, List


def render_study_guide(lesson: Dict[str, Any]) -> str:
    """Render one lesson as a markdown study guide with exercises."""
    lines: List[str] = [f"# {lesson['title'] or 'Untitled Lesson'}", ""]

    if lesson.get("headings"):
        lines.append("## Topics covered")
        lines.extend(f"- {heading}" for heading in lesson["headings"])
        lines.append("")

    if lesson.get("key_terms"):
        lines.append("## Key terms")
        lines.extend(f"- **{term}**" for term in lesson["key_terms"])
        lines.append("")

    lines.append("## Exercises")
    lines.extend(
        [
            "1. Define each key term in one sentence, in your own words.",
            "2. Explain how the topics above connect to each other.",
            "3. Write one 'compare/contrast' statement using two key terms.",
            "4. Write one possible AP-style short-answer question about "
            "this lesson, then answer it in a paragraph.",
            "",
        ]
    )

    if lesson.get("url"):
        lines.append(f"Source: {lesson['url']}")
        lines.append("")

    return "\n".join(lines)


def generate_study_guides(
    lessons: List[Dict[str, Any]], course_dir: str
) -> List[str]:
    """Write a study guide per lesson; return the output paths."""
    out_dir = os.path.join(course_dir, "study_guides")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for index, lesson in enumerate(lessons):
        name = _slugify(lesson.get("title") or f"lesson_{index:03d}")
        path = os.path.join(out_dir, f"{name}.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(render_study_guide(lesson))
        paths.append(path)
    return paths


def _slugify(title: str) -> str:
    slug = "".join(
        char if char.isalnum() else "-" for char in title.lower()
    ).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "lesson"


def write_lessons(lessons: List[Dict[str, Any]], course_dir: str) -> str:
    """Persist analyzed lessons for downstream stages; return the path."""
    path = os.path.join(course_dir, "lessons.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(lessons, handle, indent=2, ensure_ascii=False)
    return path