"""Analyze ingested Canvas material into structured lesson content."""

import glob
import json
import os
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

_TAG_RE = re.compile(r"<[^>]+>")


def extract_text(html: str) -> str:
    """Convert a page's HTML to plain, whitespace-normalized text."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n").replace(" ", " ")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def analyze_page(page: Dict[str, Any]) -> Dict[str, Any]:
    """Turn a raw Canvas page into structured content for generation."""
    html = page.get("body") or ""
    text = extract_text(html)
    soup = BeautifulSoup(html, "html.parser")
    headings = [
        tag.get_text(strip=True)
        for tag in soup.find_all(["h1", "h2", "h3"])
        if tag.get_text(strip=True)
    ]
    terms = sorted(set(_find_key_terms(text)))
    return {
        "title": page.get("title", ""),
        "url": page.get("html_url", ""),
        "headings": headings,
        "key_terms": terms,
        "text": text,
    }


def analyze_course(course_dir: str) -> List[Dict[str, Any]]:
    """Analyze every ingested page in a course data directory."""
    lessons = []
    for path in sorted(glob.glob(os.path.join(course_dir, "pages", "*.json"))):
        with open(path, encoding="utf-8") as handle:
            page = json.load(handle)
        lessons.append(analyze_page(page))
    return lessons


_LEADING_STOPWORDS = ("The", "A", "An", "In", "Of", "On")


def _find_key_terms(text: str) -> List[str]:
    """Yield capitalized multi-word phrases that likely name concepts.

    Leading stop words ("The Ottoman Empire") are stripped so the same
    concept is not captured twice. This is a deliberately simple
    heuristic; a later phase can swap in an LLM-based extractor behind
    the same interface.
    """
    seen: List[str] = []
    for match in re.finditer(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b", text):
        phrase = match.group(1)
        words = phrase.split(" ")
        while words and words[0] in _LEADING_STOPWORDS:
            words = words[1:]
        if len(words) < 2:
            continue
        phrase = " ".join(words)
        if phrase not in seen:
            seen.append(phrase)
    return seen[:40]