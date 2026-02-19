"""Integration tests for dark mode feature."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDarkModeHTML:
    """Tests that all pages contain the dark mode toggle and required markup."""

    def test_base_contains_dark_mode_toggle(self) -> None:
        """The base layout should include the dark mode toggle button."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_base_contains_sun_icon(self) -> None:
        """The base layout should include a sun icon for the toggle."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="dark-mode-sun"' in response.text

    def test_base_contains_moon_icon(self) -> None:
        """The base layout should include a moon icon for the toggle."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'id="dark-mode-moon"' in response.text

    def test_base_contains_fouc_prevention_script(self) -> None:
        """The base layout should include the FOUC-prevention inline script."""
        response = client.get("/")
        assert response.status_code == 200
        assert "reviewsummary_darkmode" in response.text

    def test_base_contains_prefers_color_scheme_check(self) -> None:
        """The base layout should detect the system colour-scheme preference."""
        response = client.get("/")
        assert response.status_code == 200
        assert "prefers-color-scheme" in response.text

    def test_base_contains_dark_mode_tailwind_config(self) -> None:
        """Tailwind should be configured for class-based dark mode."""
        response = client.get("/")
        assert response.status_code == 200
        assert "darkMode" in response.text
        assert "'class'" in response.text or '"class"' in response.text

    def test_body_has_dark_bg_class(self) -> None:
        """The body element should include a dark-mode background class."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-900" in response.text

    def test_toggle_button_has_aria_label(self) -> None:
        """The dark mode toggle button should have an accessible aria-label."""
        response = client.get("/")
        assert response.status_code == 200
        assert 'aria-label="Toggle dark mode"' in response.text

    def test_toggle_calls_toggle_function(self) -> None:
        """The toggle button should call toggleDarkMode() on click."""
        response = client.get("/")
        assert response.status_code == 200
        assert "toggleDarkMode" in response.text

    def test_reviews_page_has_dark_mode_toggle(self) -> None:
        """The reviews list page should also contain the dark mode toggle."""
        response = client.get("/reviews")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_analytics_page_has_dark_mode_toggle(self) -> None:
        """The analytics page should also contain the dark mode toggle."""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text

    def test_create_review_page_has_dark_mode_toggle(self) -> None:
        """The create review page should also contain the dark mode toggle."""
        response = client.get("/reviews/new")
        assert response.status_code == 200
        assert 'id="dark-mode-toggle"' in response.text


class TestDarkModeStaticAssets:
    """Tests that the CSS and JS files contain dark mode functionality."""

    def test_css_file_loads_successfully(self) -> None:
        """The custom CSS file should be accessible."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200

    def test_css_contains_dark_sentiment_positive(self) -> None:
        """The CSS file should have dark mode overrides for positive sentiment badge."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "html.dark .sentiment-positive" in response.text

    def test_css_contains_dark_sentiment_negative(self) -> None:
        """The CSS file should have dark mode overrides for negative sentiment badge."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "html.dark .sentiment-negative" in response.text

    def test_css_contains_dark_scrollbar(self) -> None:
        """The CSS file should include dark mode scrollbar styles."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "html.dark ::-webkit-scrollbar" in response.text

    def test_css_contains_dark_loading_spinner(self) -> None:
        """The CSS file should include dark mode loading spinner styles."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "html.dark .loading-spinner" in response.text

    def test_js_file_loads_successfully(self) -> None:
        """The app JS file should be accessible."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200

    def test_js_contains_toggle_dark_mode_function(self) -> None:
        """The JS file should define toggleDarkMode()."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function toggleDarkMode" in response.text

    def test_js_contains_init_dark_mode_function(self) -> None:
        """The JS file should define initDarkMode()."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function initDarkMode" in response.text

    def test_js_contains_update_dark_mode_toggle_function(self) -> None:
        """The JS file should define updateDarkModeToggle()."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "function updateDarkModeToggle" in response.text

    def test_js_contains_dark_mode_key_constant(self) -> None:
        """The JS file should define the localStorage key constant."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "DARK_MODE_KEY" in response.text

    def test_js_persists_to_local_storage(self) -> None:
        """The JS file should save the preference to localStorage."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "localStorage.setItem" in response.text
        assert "reviewsummary_darkmode" in response.text

    def test_js_reads_from_local_storage(self) -> None:
        """The JS file should read the preference from localStorage."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "localStorage.getItem" in response.text

    def test_js_toggles_dark_class_on_html(self) -> None:
        """The JS file should toggle the 'dark' class on the HTML element."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert "document.documentElement.classList.toggle" in response.text


class TestDarkModePageContent:
    """Tests that page templates include dark mode Tailwind classes."""

    def test_home_page_feature_cards_have_dark_bg(self) -> None:
        """The home page feature cards should have dark mode background classes."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-800" in response.text

    def test_home_page_has_dark_text_class(self) -> None:
        """The home page should have dark mode text classes."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:text-white" in response.text

    def test_reviews_page_has_dark_border_class(self) -> None:
        """The reviews page filter bar should have dark mode border classes."""
        response = client.get("/reviews")
        assert response.status_code == 200
        assert "dark:border-gray-700" in response.text

    def test_create_review_page_has_dark_input_class(self) -> None:
        """The create review page form inputs should have dark mode classes."""
        response = client.get("/reviews/new")
        assert response.status_code == 200
        assert "dark:bg-gray-700" in response.text

    def test_analytics_page_has_dark_card_classes(self) -> None:
        """The analytics page stat cards should have dark mode classes."""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert "dark:bg-gray-800" in response.text
        assert "dark:border-gray-700" in response.text

    def test_nav_has_dark_mode_classes(self) -> None:
        """The navigation bar should have dark mode background and border classes."""
        response = client.get("/")
        assert response.status_code == 200
        assert "dark:bg-gray-800" in response.text
        assert "dark:border-gray-700" in response.text
