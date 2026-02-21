"""Integration tests for dark mode feature."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDarkModeUI:
    """Tests that dark mode elements are present in rendered pages."""

    def test_dark_mode_toggle_present_in_navbar(self) -> None:
        """The navigation should contain a dark mode toggle button."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_dark_mode_toggle_has_aria_label(self) -> None:
        """The dark mode toggle should have an accessible aria-label."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'aria-label="Toggle dark mode"' in response.text

    def test_dark_mode_tailwind_config_enabled(self) -> None:
        """The Tailwind config should declare class-based dark mode."""
        response = client.get("/")
        assert response.status_code == 200
        assert "darkMode" in response.text
        assert "'class'" in response.text or '"class"' in response.text

    def test_dark_mode_css_classes_present(self) -> None:
        """The base template should include dark: variant Tailwind classes."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:" in response.text

    def test_dark_mode_toggle_function_referenced(self) -> None:
        """The toggle button should reference the toggleDarkMode JS function."""
        response = client.get("/")
        assert response.status_code == 200
        assert "toggleDarkMode" in response.text

    def test_dark_mode_flash_prevention_script_in_head(self) -> None:
        """An inline script should apply dark class early to prevent flash."""
        response = client.get("/")
        assert response.status_code == 200
        assert "reviewsummary_darkmode" in response.text
        # Script must appear before stylesheet link to prevent FOUC
        dark_init_pos = response.text.find("reviewsummary_darkmode")
        stylesheet_pos = response.text.find("/static/css/style.css")
        assert dark_init_pos < stylesheet_pos

    def test_dark_mode_toggle_on_reviews_page(self) -> None:
        """The dark mode toggle should be present on the reviews page too."""
        response = client.get("/reviews")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_dark_mode_toggle_on_analytics_page(self) -> None:
        """The dark mode toggle should be present on the analytics page."""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_dark_mode_body_has_dark_variant(self) -> None:
        """The body element should include a dark mode background class."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-900" in response.text

    def test_dark_mode_nav_has_dark_variant(self) -> None:
        """The navigation should include dark mode background and border classes."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-800" in response.text
        assert "dark:border-gray-700" in response.text
