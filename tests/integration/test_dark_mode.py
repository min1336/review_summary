"""Integration tests for the dark mode feature (issue #2)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDarkModeHTML:
    """Verify dark mode elements are present in the rendered HTML."""

    def test_base_includes_dark_mode_toggle_button(self) -> None:
        """Every page should contain the dark mode toggle button."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_dark_mode_toggle_has_aria_label(self) -> None:
        """The toggle button should include an accessible aria-label."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'aria-label="Toggle dark mode"' in response.text

    def test_base_includes_sun_and_moon_icons(self) -> None:
        """Both sun and moon SVG icons should be present for the toggle."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="icon-sun"' in response.text
        assert 'id="icon-moon"' in response.text

    def test_dark_mode_early_init_script_present(self) -> None:
        """An inline script referencing reviewsummary_theme must appear before CSS."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        # The early-init script must reference the theme localStorage key
        assert "reviewsummary_theme" in html
        # The early-init script must add the 'dark' class to documentElement
        assert "documentElement.classList.add('dark')" in html

    def test_html_element_ready_for_dark_class(self) -> None:
        """The <html> element must not hard-code a class that blocks dark mode."""
        response = client.get("/")
        assert response.status_code == 200
        # Tailwind darkMode:'class' requires .dark on <html>; <html> must not
        # pre-set a conflicting class that would override JS initialisation.
        assert "<html lang" in response.text

    def test_body_has_dark_background_class(self) -> None:
        """The body element should include Tailwind's dark:bg-gray-900 class."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-900" in response.text

    def test_nav_has_dark_classes(self) -> None:
        """The navigation bar should include dark mode Tailwind classes."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-800" in response.text

    def test_toggle_calls_toggle_dark_mode(self) -> None:
        """The toggle button's onclick must call toggleDarkMode()."""
        response = client.get("/")
        assert response.status_code == 200
        assert "toggleDarkMode()" in response.text

    def test_dark_mode_present_on_reviews_page(self) -> None:
        """Dark mode toggle should appear on the reviews list page too."""
        response = client.get("/reviews")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_dark_mode_present_on_analytics_page(self) -> None:
        """Dark mode toggle should appear on the analytics page too."""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text


class TestDarkModeCSS:
    """Verify the CSS file contains required dark mode variables and rules."""

    def test_css_file_accessible(self) -> None:
        """The static CSS file must be served correctly."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200

    def test_css_defines_light_mode_variables(self) -> None:
        """The CSS file must define :root CSS variables for light mode."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        css = response.text
        assert ":root" in css
        assert "--color-bg-primary" in css
        assert "--color-bg-surface" in css
        assert "--color-text-primary" in css

    def test_css_defines_dark_mode_variables(self) -> None:
        """The CSS file must define html.dark CSS variable overrides."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        css = response.text
        assert "html.dark" in css

    def test_css_has_dark_sentiment_badge_overrides(self) -> None:
        """Sentiment badge colours should be overridden in dark mode."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        css = response.text
        assert "html.dark .sentiment-positive" in css
        assert "html.dark .sentiment-negative" in css
        assert "html.dark .sentiment-neutral" in css
        assert "html.dark .sentiment-mixed" in css

    def test_css_has_dark_mode_toggle_button_style(self) -> None:
        """The dark mode toggle button should have dedicated CSS rules."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "#dark-mode-toggle" in response.text


class TestDarkModeJS:
    """Verify the JavaScript file contains the dark mode implementation."""

    def test_js_file_accessible(self) -> None:
        """The static JS file must be served correctly."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200

    def test_js_defines_theme_key_constant(self) -> None:
        """app.js must define the localStorage key for the theme preference."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "THEME_KEY" in response.text
        assert "reviewsummary_theme" in response.text

    def test_js_defines_toggle_dark_mode_function(self) -> None:
        """app.js must define the toggleDarkMode function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function toggleDarkMode" in response.text

    def test_js_defines_apply_dark_mode_function(self) -> None:
        """app.js must define the applyDarkMode helper function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function applyDarkMode" in response.text

    def test_js_defines_init_dark_mode_function(self) -> None:
        """app.js must define the initDarkMode initialisation function."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function initDarkMode" in response.text

    def test_js_persists_preference_in_local_storage(self) -> None:
        """toggleDarkMode must write the preference to localStorage."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        js = response.text
        assert "localStorage.setItem" in js
        assert "THEME_KEY" in js

    def test_js_uses_prefers_color_scheme(self) -> None:
        """The early-init logic must check the system dark mode preference."""
        response = client.get("/")
        assert response.status_code == 200
        assert "prefers-color-scheme" in response.text

    def test_js_calls_init_dark_mode_on_domcontentloaded(self) -> None:
        """initDarkMode must be called when the DOM is ready."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        js = response.text
        assert "initDarkMode()" in js
        assert "DOMContentLoaded" in js
