"""Integration tests for dark mode feature (issue #2)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDarkModeHTML:
    """Verify dark mode markup is present in every rendered page."""

    def _assert_dark_mode_elements(self, html: str, page: str) -> None:
        """Assert that all required dark-mode elements appear in *html*."""
        assert "reviewsummary_theme" in html, f"{page}: localStorage key missing"
        assert "dark-mode-toggle" in html, f"{page}: toggle button missing"
        assert "toggleDarkMode" in html, f"{page}: toggleDarkMode() call missing"
        assert "prefers-color-scheme" in html, f"{page}: system-preference detection missing"
        assert "darkMode" in html, f"{page}: Tailwind darkMode config missing"
        assert "document.documentElement.classList" in html, (
            f"{page}: classList manipulation missing"
        )

    def test_index_page_has_dark_mode(self) -> None:
        """Landing page should contain all dark mode markup."""
        response = client.get("/")
        assert response.status_code == 200
        self._assert_dark_mode_elements(response.text, "index")

    def test_reviews_page_has_dark_mode(self) -> None:
        """Reviews list page should contain all dark mode markup."""
        response = client.get("/reviews")
        assert response.status_code == 200
        self._assert_dark_mode_elements(response.text, "/reviews")

    def test_reviews_new_page_has_dark_mode(self) -> None:
        """Create review page should contain all dark mode markup."""
        response = client.get("/reviews/new")
        assert response.status_code == 200
        self._assert_dark_mode_elements(response.text, "/reviews/new")

    def test_analytics_page_has_dark_mode(self) -> None:
        """Analytics dashboard page should contain all dark mode markup."""
        response = client.get("/analytics")
        assert response.status_code == 200
        self._assert_dark_mode_elements(response.text, "/analytics")


class TestDarkModeToggleButton:
    """Verify the toggle button is rendered with correct attributes."""

    def test_toggle_button_has_aria_label(self) -> None:
        """The toggle button must have an accessible aria-label."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'aria-label="Toggle dark mode"' in response.text

    def test_toggle_button_contains_sun_and_moon_icons(self) -> None:
        """Both sun and moon SVG icons must be present for the toggle."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="icon-sun"' in response.text
        assert 'id="icon-moon"' in response.text

    def test_dark_mode_toggle_id_present(self) -> None:
        """The toggle button must have the correct id."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text


class TestDarkModeCSS:
    """Verify the static CSS file ships the required variables."""

    def test_css_file_returns_200(self) -> None:
        """The style.css file should be served successfully."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200

    def test_css_contains_light_mode_variables(self) -> None:
        """CSS must define :root custom properties for light mode."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        css = response.text
        assert ":root" in css
        assert "--color-bg" in css
        assert "--color-surface" in css
        assert "--color-text-primary" in css

    def test_css_contains_dark_mode_variables(self) -> None:
        """CSS must define html.dark custom properties for dark mode."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        css = response.text
        assert "html.dark" in css

    def test_css_contains_transition(self) -> None:
        """CSS should include a smooth transition for theme switching."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "transition" in response.text


class TestDarkModeJS:
    """Verify the static JS file ships the required dark mode functions."""

    def test_js_file_returns_200(self) -> None:
        """The app.js file should be served successfully."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200

    def test_js_contains_toggle_function(self) -> None:
        """app.js must export a toggleDarkMode function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function toggleDarkMode" in response.text

    def test_js_contains_init_function(self) -> None:
        """app.js must export an initDarkMode function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function initDarkMode" in response.text

    def test_js_uses_localstorage_theme_key(self) -> None:
        """app.js must persist the preference with the expected key."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "reviewsummary_theme" in response.text

    def test_js_updates_icons(self) -> None:
        """app.js must update sun/moon icons when theme changes."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function updateDarkModeIcons" in response.text
        assert "icon-sun" in response.text
        assert "icon-moon" in response.text
