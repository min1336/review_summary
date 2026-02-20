"""Integration tests for dark mode feature (issue #2)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDarkModeHTML:
    """Verify that the dark mode UI elements are present in rendered pages."""

    def test_root_page_has_dark_mode_toggle(self) -> None:
        """The landing page should include the dark mode toggle button."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="theme-toggle"' in response.text

    def test_root_page_has_theme_icons(self) -> None:
        """The landing page should include both sun and moon theme icons."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="theme-icon-sun"' in response.text
        assert 'id="theme-icon-moon"' in response.text

    def test_reviews_page_has_dark_mode_toggle(self) -> None:
        """The reviews page should include the dark mode toggle button."""
        response = client.get("/reviews")
        assert response.status_code == 200
        assert 'id="theme-toggle"' in response.text

    def test_analytics_page_has_dark_mode_toggle(self) -> None:
        """The analytics dashboard should include the dark mode toggle button."""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert 'id="theme-toggle"' in response.text


class TestDarkModeCSS:
    """Verify that dark mode CSS and Tailwind configuration are present."""

    def test_base_has_tailwind_dark_mode_class_config(self) -> None:
        """The base template should configure Tailwind's darkMode: 'class'."""
        response = client.get("/")
        assert response.status_code == 200
        assert "darkMode: 'class'" in response.text

    def test_body_has_dark_background_class(self) -> None:
        """The body element should have the dark mode background Tailwind class."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-900" in response.text

    def test_nav_has_dark_background_class(self) -> None:
        """The nav element should have a dark mode background class."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-800" in response.text


class TestDarkModeJS:
    """Verify that dark mode JavaScript is included in rendered pages."""

    def test_page_includes_theme_key_constant(self) -> None:
        """The rendered page should reference the localStorage theme key."""
        response = client.get("/")
        assert response.status_code == 200
        assert "reviewsummary_theme" in response.text

    def test_page_includes_toggle_theme_function(self) -> None:
        """The rendered page should reference the toggleTheme JS function."""
        response = client.get("/")
        assert response.status_code == 200
        assert "toggleTheme" in response.text

    def test_page_includes_flash_prevention_script(self) -> None:
        """The <head> should contain an early script to prevent theme flash."""
        response = client.get("/")
        assert response.status_code == 200
        assert "prefers-color-scheme" in response.text
