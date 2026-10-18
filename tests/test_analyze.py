"""Tests for the analysis stage."""

from canvas_ap_world.analyze import analyze_page, extract_text


def test_extract_text_strips_html_and_blank_lines() -> None:
    html = "<h2>Silk Roads</h2><p>The Silk Roads connected&nbsp;empires.</p>"
    assert extract_text(html) == "Silk Roads\nThe Silk Roads connected empires."


def test_analyze_page_structure() -> None:
    page = {
        "title": "Unit 3: Land Empires",
        "html_url": "https://canvas.example.com/courses/1/pages/unit-3",
        "body": (
            "<h2>Ottoman Empire</h2>"
            "<p>The Ottoman Empire expanded. The Safavid Empire rose too.</p>"
        ),
    }
    lesson = analyze_page(page)
    assert lesson["title"] == "Unit 3: Land Empires"
    assert lesson["headings"] == ["Ottoman Empire"]
    assert "Ottoman Empire" in lesson["key_terms"]
    assert "Safavid Empire" in lesson["key_terms"]
    assert "The Ottoman Empire expanded." in lesson["text"]


def test_analyze_page_empty_body() -> None:
    lesson = analyze_page({"title": "Empty", "body": None})
    assert lesson["text"] == ""
    assert lesson["headings"] == []
    assert lesson["key_terms"] == []