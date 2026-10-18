"""Tests for the generation stage."""

from canvas_ap_world.generate import _slugify, render_study_guide


def test_render_study_guide_includes_sections() -> None:
    lesson = {
        "title": "Unit 3: Land Empires",
        "url": "https://canvas.example.com/courses/1/pages/unit-3",
        "headings": ["Ottoman Empire"],
        "key_terms": ["Ottoman Empire", "Safavid Empire"],
        "text": "",
    }
    guide = render_study_guide(lesson)
    assert "# Unit 3: Land Empires" in guide
    assert "- Ottoman Empire" in guide
    assert "- **Safavid Empire**" in guide
    assert "## Exercises" in guide
    assert "Source: https://canvas.example.com" in guide


def test_slugify_handles_punctuation_and_spaces() -> None:
    assert _slugify("Unit 3: Land-Based Empires!") == "unit-3-land-based-empires"
    assert _slugify("   ") == "lesson"


def test_render_study_guide_without_terms_still_has_exercises() -> None:
    guide = render_study_guide({"title": "Bare", "url": "", "headings": [],
                                "key_terms": [], "text": ""})
    assert "## Exercises" in guide