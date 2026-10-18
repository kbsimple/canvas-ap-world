"""Command-line interface for canvas-ap-world."""

import argparse
import os
import sys
from typing import List, Optional

from canvas_ap_world.analyze import analyze_course
from canvas_ap_world.canvas_client import CanvasClient
from canvas_ap_world.config import Config, ConfigError
from canvas_ap_world.generate import generate_study_guides, write_lessons
from canvas_ap_world.ingest import pull_course_materials


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ap-world",
        description="Generate study material from AP World Canvas courses.",
    )
    parser.add_argument(
        "--data-dir", default="data", help="Directory for pulled materials."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "list-courses", help="List courses visible to the API token."
    )
    subparsers.add_parser("pull", help="Pull course materials from Canvas.")
    subparsers.add_parser(
        "generate", help="Analyze pulled materials and write study guides."
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "list-courses":
            return _list_courses()
        if args.command == "pull":
            return _pull(args.data_dir)
        if args.command == "generate":
            return _generate(args.data_dir)
    except ConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 1


def _list_courses() -> int:
    client = CanvasClient(Config())
    for course in client.list_courses():
        print(f"{course.get('id')}: {course.get('name', '(unnamed)')}")
    return 0


def _pull(data_dir: str) -> int:
    config = Config()
    course_id = config.ensure_course_id()
    manifest = pull_course_materials(
        CanvasClient(config), course_id, data_dir=data_dir
    )
    print(
        f"Pulled course {course_id}: {manifest['module_count']} modules, "
        f"{manifest['page_count']} pages, "
        f"{manifest['assignment_count']} assignments."
    )
    return 0


def _generate(data_dir: str) -> int:
    config = Config()
    course_id = config.ensure_course_id()
    course_dir = os.path.join(data_dir, f"course_{course_id}")
    if not os.path.isdir(course_dir):
        print(
            f"error: no pulled materials at {course_dir}. Run 'ap-world pull' "
            "first.",
            file=sys.stderr,
        )
        return 2
    lessons = analyze_course(course_dir)
    write_lessons(lessons, course_dir)
    paths = generate_study_guides(lessons, course_dir)
    print(f"Generated {len(paths)} study guides under {course_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())