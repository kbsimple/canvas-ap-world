"""Tests for configuration loading."""

import pytest

from canvas_ap_world.config import Config, ConfigError


def test_config_requires_api_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CANVAS_API_URL", "")
    monkeypatch.setenv("CANVAS_API_TOKEN", "token")
    monkeypatch.setenv("CANVAS_COURSE_ID", "1")
    with pytest.raises(ConfigError, match="CANVAS_API_URL"):
        Config()


def test_config_requires_api_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CANVAS_API_URL", "https://canvas.example.com")
    monkeypatch.setenv("CANVAS_API_TOKEN", "")
    with pytest.raises(ConfigError, match="CANVAS_API_TOKEN"):
        Config()


def test_config_strips_trailing_slash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CANVAS_API_URL", "https://canvas.example.com/")
    monkeypatch.setenv("CANVAS_API_TOKEN", "token")
    monkeypatch.setenv("CANVAS_COURSE_ID", "1")
    config = Config()
    assert config.api_url == "https://canvas.example.com"
    assert config.ensure_course_id() == "1"


def test_ensure_course_id_raises_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CANVAS_API_URL", "https://canvas.example.com")
    monkeypatch.setenv("CANVAS_API_TOKEN", "token")
    monkeypatch.delenv("CANVAS_COURSE_ID", raising=False)
    with pytest.raises(ConfigError, match="CANVAS_COURSE_ID"):
        Config().ensure_course_id()