"""Integration tests for dark mode feature (issue #2)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDarkModeHTML:
    """Tests that HTML pages contain dark mode infrastructure."""

    def test_base_has_dark_mode_toggle_button(self) -> None:
        """The homepage must include the dark mode toggle button."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_toggle_has_aria_label(self) -> None:
        """The dark mode toggle button must have an accessible aria-label."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'aria-label="Toggle dark mode"' in response.text

    def test_toggle_references_toggle_function(self) -> None:
        """The toggle button should call toggleDarkMode on click."""
        response = client.get("/")
        assert response.status_code == 200
        assert "toggleDarkMode" in response.text

    def test_base_has_sun_and_moon_icons(self) -> None:
        """Both sun and moon SVG icons must be present for the toggle."""
        response = client.get("/")
        assert response.status_code == 200
        assert "sun-icon" in response.text
        assert "moon-icon" in response.text

    def test_base_has_early_init_script(self) -> None:
        """An early-init script must be present to prevent theme flash."""
        response = client.get("/")
        assert response.status_code == 200
        assert "reviewsummary_darkmode" in response.text

    def test_flash_prevention_script_before_stylesheet(self) -> None:
        """The early-init script must appear before the stylesheet to prevent FOUC."""
        response = client.get("/")
        assert response.status_code == 200
        dark_init_pos = response.text.find("reviewsummary_darkmode")
        stylesheet_pos = response.text.find("/static/css/style.css")
        assert dark_init_pos < stylesheet_pos

    def test_tailwind_darkmode_class_config(self) -> None:
        """Tailwind config must include darkMode: 'class'."""
        response = client.get("/")
        assert response.status_code == 200
        assert "darkMode: 'class'" in response.text

    def test_base_has_dark_variant_classes(self) -> None:
        """The base template must include Tailwind dark: variant classes."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:" in response.text

    def test_body_has_dark_background_class(self) -> None:
        """The body element must include a dark mode background class."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-900" in response.text

    def test_nav_has_dark_background_class(self) -> None:
        """The navigation must include dark mode background and border classes."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-800" in response.text
        assert "dark:border-gray-700" in response.text

    def test_dark_mode_toggle_present_on_reviews_page(self) -> None:
        """The reviews list page must also include the dark mode toggle."""
        response = client.get("/reviews")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_dark_mode_toggle_present_on_analytics_page(self) -> None:
        """The analytics page must also include the dark mode toggle."""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text


class TestDarkModeStaticAssets:
    """Tests that static assets for dark mode are served correctly."""

    def test_css_served(self) -> None:
        """The stylesheet must be served with 200 status."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200

    def test_css_contains_dark_sentiment_overrides(self) -> None:
        """style.css must define dark mode overrides for sentiment badges."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert ".dark .sentiment-positive" in response.text
        assert ".dark .sentiment-negative" in response.text

    def test_css_contains_dark_mode_transition(self) -> None:
        """style.css must include a smooth transition for theme switching."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "transition" in response.text
        assert "background-color" in response.text

    def test_js_served(self) -> None:
        """The JavaScript bundle must be served with 200 status."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200

    def test_js_contains_toggle_function(self) -> None:
        """app.js must define the toggleDarkMode function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function toggleDarkMode()" in response.text

    def test_js_contains_apply_theme_function(self) -> None:
        """app.js must define the applyTheme function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function applyTheme(" in response.text

    def test_js_contains_init_dark_mode_function(self) -> None:
        """app.js must define the initDarkMode function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function initDarkMode()" in response.text

    def test_js_uses_localstorage_for_persistence(self) -> None:
        """app.js must persist the theme preference in localStorage."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "localStorage.setItem(DARK_MODE_KEY" in response.text
        assert "localStorage.getItem(DARK_MODE_KEY)" in response.text

    def test_js_respects_system_preference(self) -> None:
        """app.js must query prefers-color-scheme media feature."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "prefers-color-scheme" in response.text

    def test_js_listens_for_system_preference_changes(self) -> None:
        """app.js must listen for system dark mode preference changes."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "addEventListener('change'" in response.text

    def test_js_dark_mode_key_constant(self) -> None:
        """app.js must define a DARK_MODE_KEY constant."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "DARK_MODE_KEY = 'reviewsummary_darkmode'" in response.text
