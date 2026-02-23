"""Integration tests for dark mode feature."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDarkModeToggleButton:
    """Tests that the dark mode toggle button is present on all pages."""

    def test_home_page_has_dark_mode_toggle(self) -> None:
        """The home page should contain the dark mode toggle button."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_reviews_page_has_dark_mode_toggle(self) -> None:
        """The reviews list page should contain the dark mode toggle button."""
        response = client.get("/reviews")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_create_review_page_has_dark_mode_toggle(self) -> None:
        """The create review page should contain the dark mode toggle button."""
        response = client.get("/reviews/new")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_analytics_page_has_dark_mode_toggle(self) -> None:
        """The analytics page should contain the dark mode toggle button."""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text


class TestDarkModeIcons:
    """Tests that dark mode icons (sun/moon) are present in the navbar."""

    def test_home_page_has_sun_icon(self) -> None:
        """The home page should include the sun icon for dark mode toggle."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="sun-icon"' in response.text

    def test_home_page_has_moon_icon(self) -> None:
        """The home page should include the moon icon for dark mode toggle."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="moon-icon"' in response.text


class TestDarkModeJavaScript:
    """Tests that the app.js file contains the required dark mode functions."""

    def test_static_js_has_toggle_function(self) -> None:
        """app.js should export the toggleDarkMode function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "toggleDarkMode" in response.text

    def test_static_js_has_init_function(self) -> None:
        """app.js should export the initDarkMode function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "initDarkMode" in response.text

    def test_static_js_has_apply_function(self) -> None:
        """app.js should export the applyDarkMode function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "applyDarkMode" in response.text

    def test_static_js_has_dark_mode_key(self) -> None:
        """app.js should define the DARK_MODE_KEY localStorage key."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "DARK_MODE_KEY" in response.text

    def test_static_js_has_localstorage_persistence(self) -> None:
        """app.js should use localStorage to persist the dark mode preference."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "localStorage.setItem" in response.text
        assert "localStorage.getItem" in response.text

    def test_pages_have_system_preference_detection(self) -> None:
        """Pages should detect the system color scheme preference via FOUC-prevention script."""
        response = client.get("/")
        assert response.status_code == 200
        assert "prefers-color-scheme" in response.text


class TestDarkModeCSS:
    """Tests that the CSS file contains the required dark mode variables."""

    def test_static_css_has_root_variables(self) -> None:
        """style.css should define CSS custom properties in :root."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "--color-bg-primary" in response.text
        assert "--color-bg-secondary" in response.text
        assert "--color-text-primary" in response.text

    def test_static_css_has_dark_class_overrides(self) -> None:
        """style.css should define dark mode overrides under the .dark selector."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert ".dark {" in response.text

    def test_static_css_has_dark_sentiment_overrides(self) -> None:
        """style.css should include dark mode overrides for sentiment badges."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert ".dark .sentiment-positive" in response.text
        assert ".dark .sentiment-negative" in response.text

    def test_static_css_has_transition_class(self) -> None:
        """style.css should include the dark mode transition class."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "dark-transitioning" in response.text


class TestDarkModeTailwindConfig:
    """Tests that the base template configures Tailwind for class-based dark mode."""

    def test_base_template_configures_dark_mode_class(self) -> None:
        """The base template should configure Tailwind darkMode as 'class'."""
        response = client.get("/")
        assert response.status_code == 200
        assert "darkMode: 'class'" in response.text

    def test_base_template_has_fouc_prevention_script(self) -> None:
        """The base template should have a script to prevent flash of unstyled content."""
        response = client.get("/")
        assert response.status_code == 200
        assert "reviewsummary_dark_mode" in response.text
        assert "document.documentElement.classList.add" in response.text
