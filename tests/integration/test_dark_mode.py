"""Integration tests for dark mode functionality."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_base_template_has_dark_mode_toggle(client: TestClient) -> None:
    """Test that the base template includes the dark mode toggle button."""
    response = client.get("/")
    assert response.status_code == 200

    # Check for theme toggle button
    assert 'id="theme-toggle"' in response.text
    assert 'onclick="toggleTheme()"' in response.text
    assert 'aria-label="Toggle dark mode"' in response.text


def test_base_template_has_tailwind_dark_mode_config(client: TestClient) -> None:
    """Test that Tailwind is configured for dark mode."""
    response = client.get("/")
    assert response.status_code == 200

    # Check for dark mode configuration
    assert 'darkMode:' in response.text
    assert '[data-theme="dark"]' in response.text


def test_base_template_has_dark_mode_classes(client: TestClient) -> None:
    """Test that base template elements have dark mode classes."""
    response = client.get("/")
    assert response.status_code == 200

    # Check body has dark mode class
    assert 'dark:bg-gray-900' in response.text

    # Check navigation has dark mode class
    assert 'dark:bg-gray-800' in response.text

    # Check footer has dark mode class
    assert 'dark:border-gray-700' in response.text


def test_base_template_loads_theme_script(client: TestClient) -> None:
    """Test that the theme management JavaScript is loaded."""
    response = client.get("/")
    assert response.status_code == 200

    # Check for theme-related functions
    assert 'function getTheme()' in response.text or 'getTheme()' in response.text
    assert 'function setTheme(' in response.text or 'setTheme(' in response.text
    assert 'function toggleTheme()' in response.text or 'toggleTheme()' in response.text
    assert 'function initTheme()' in response.text or 'initTheme()' in response.text


def test_home_page_has_dark_mode_classes(client: TestClient) -> None:
    """Test that home page elements have dark mode classes."""
    response = client.get("/")
    assert response.status_code == 200

    # Check feature cards have dark mode classes
    assert 'dark:bg-gray-800' in response.text

    # Check stats section has dark mode classes
    assert 'dark:text-white' in response.text or 'dark:text-gray' in response.text


def test_reviews_page_has_dark_mode_classes(client: TestClient) -> None:
    """Test that reviews page elements have dark mode classes."""
    response = client.get("/reviews")
    assert response.status_code == 200

    # Check page header has dark mode classes
    assert 'dark:text-white' in response.text

    # Check filter bar has dark mode classes
    assert 'dark:bg-gray-800' in response.text or 'dark:bg-gray-700' in response.text


def test_create_review_page_has_dark_mode_classes(client: TestClient) -> None:
    """Test that create review page has dark mode classes."""
    response = client.get("/reviews/new")
    assert response.status_code == 200

    # Check form container has dark mode classes
    assert 'dark:bg-gray-800' in response.text

    # Check form inputs have dark mode classes
    assert 'dark:border-gray-600' in response.text
    assert 'dark:text-white' in response.text or 'dark:text-gray' in response.text


def test_css_has_dark_mode_variables(client: TestClient) -> None:
    """Test that CSS file contains dark mode variables."""
    response = client.get("/static/css/style.css")
    assert response.status_code == 200

    # Check for CSS variables
    assert ':root' in response.text
    assert '[data-theme="dark"]' in response.text

    # Check for specific dark mode variables
    assert '--bg-primary' in response.text
    assert '--text-primary' in response.text
    assert '--border-color' in response.text


def test_js_has_theme_management(client: TestClient) -> None:
    """Test that JavaScript file contains theme management code."""
    response = client.get("/static/js/app.js")
    assert response.status_code == 200

    # Check for theme key constant
    assert 'THEME_KEY' in response.text

    # Check for theme functions
    assert 'getTheme' in response.text
    assert 'setTheme' in response.text
    assert 'toggleTheme' in response.text
    assert 'applyTheme' in response.text

    # Check for localStorage usage
    assert 'localStorage.getItem' in response.text
    assert 'localStorage.setItem' in response.text

    # Check for system preference detection
    assert 'prefers-color-scheme' in response.text
