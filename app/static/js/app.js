/**
 * ReviewSummary Platform - Client-side JavaScript
 *
 * Provides:
 * - API helper functions (fetchJSON wrapper)
 * - Authentication token management (localStorage)
 * - Login/signup modal handling
 * - Utility functions (escapeHtml, etc.)
 */

/* ============================================================
   Token Management
   ============================================================ */

var TOKEN_KEY = 'reviewsummary_token';
var USER_KEY = 'reviewsummary_user';

/**
 * Store the authentication token and user info in localStorage.
 */
function setAuth(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    if (user) {
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
}

/**
 * Retrieve the stored authentication token.
 */
function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Retrieve the stored user info.
 */
function getUser() {
    var raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch (e) {
        return null;
    }
}

/**
 * Clear stored authentication data.
 */
function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
}

/* ============================================================
   API Helper
   ============================================================ */

/**
 * Fetch JSON from an API endpoint with automatic error handling.
 *
 * @param {string} url - The API endpoint URL
 * @param {Object} [options] - Fetch options (method, headers, body, etc.)
 * @returns {Promise<any>} Parsed JSON response
 * @throws {Error} If the response is not OK
 */
async function fetchJSON(url, options) {
    var defaults = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    // Merge headers
    if (options && options.headers) {
        var merged = Object.assign({}, defaults.headers, options.headers);
        options.headers = merged;
    }

    var finalOptions = Object.assign({}, defaults, options || {});

    // Auto-attach auth token if available and no Authorization header set
    var token = getToken();
    if (token && !finalOptions.headers['Authorization']) {
        finalOptions.headers['Authorization'] = 'Bearer ' + token;
    }

    var response = await fetch(url, finalOptions);

    if (!response.ok) {
        var errorBody;
        try {
            errorBody = await response.json();
        } catch (e) {
            errorBody = null;
        }
        var message = (errorBody && (errorBody.detail || errorBody.error)) || response.statusText;
        var err = new Error(message);
        err.status = response.status;
        err.body = errorBody;
        throw err;
    }

    // Handle 204 No Content
    if (response.status === 204) {
        return null;
    }

    return response.json();
}

/* ============================================================
   HTML Escaping
   ============================================================ */

/**
 * Escape HTML entities to prevent XSS when inserting user text into the DOM.
 */
function escapeHtml(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

/* ============================================================
   Auth Modal
   ============================================================ */

var isSignUpMode = false;

function showLoginModal() {
    isSignUpMode = false;
    updateModalMode();
    var modal = document.getElementById('login-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeLoginModal() {
    var modal = document.getElementById('login-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    // Reset form
    document.getElementById('auth-form').reset();
    var errorEl = document.getElementById('auth-error');
    if (errorEl) errorEl.classList.add('hidden');
}

function toggleAuthMode() {
    isSignUpMode = !isSignUpMode;
    updateModalMode();
}

function updateModalMode() {
    var title = document.getElementById('modal-title');
    var submitText = document.getElementById('auth-submit-text');
    var toggleText = document.getElementById('modal-toggle-text');
    var toggleBtn = document.getElementById('modal-toggle-btn');

    if (isSignUpMode) {
        if (title) title.textContent = 'Create Account';
        if (submitText) submitText.textContent = 'Sign Up';
        if (toggleText) toggleText.textContent = 'Already have an account?';
        if (toggleBtn) toggleBtn.textContent = 'Sign In';
    } else {
        if (title) title.textContent = 'Sign In';
        if (submitText) submitText.textContent = 'Sign In';
        if (toggleText) toggleText.textContent = "Don't have an account?";
        if (toggleBtn) toggleBtn.textContent = 'Sign Up';
    }
}

async function handleAuth(event) {
    event.preventDefault();

    var email = document.getElementById('auth-email').value.trim();
    var password = document.getElementById('auth-password').value;
    var errorEl = document.getElementById('auth-error');

    if (errorEl) errorEl.classList.add('hidden');

    var endpoint = isSignUpMode ? '/api/v1/auth/signup' : '/api/v1/auth/login';

    try {
        var data = await fetchJSON(endpoint, {
            method: 'POST',
            body: JSON.stringify({ email: email, password: password }),
        });

        setAuth(data.access_token, data.user);
        closeLoginModal();
        updateAuthUI();
    } catch (err) {
        if (errorEl) {
            errorEl.textContent = err.message || 'Authentication failed';
            errorEl.classList.remove('hidden');
        }
    }
}

async function handleLogout() {
    try {
        await fetchJSON('/api/v1/auth/logout', { method: 'POST' });
    } catch (e) {
        // Best-effort logout
    }
    clearAuth();
    updateAuthUI();
}

/**
 * Update the navigation bar to show logged-in or logged-out state.
 */
function updateAuthUI() {
    var authSection = document.getElementById('auth-section');
    if (!authSection) return;

    var user = getUser();
    authSection.textContent = '';

    if (user) {
        var container = document.createElement('div');
        container.className = 'flex items-center space-x-3';

        var emailSpan = document.createElement('span');
        emailSpan.className = 'text-sm text-gray-600 hidden sm:inline';
        emailSpan.textContent = user.email;

        var logoutBtn = document.createElement('button');
        logoutBtn.className = 'text-gray-500 hover:text-red-600 text-sm font-medium transition-colors';
        logoutBtn.textContent = 'Sign Out';
        logoutBtn.addEventListener('click', handleLogout);

        container.appendChild(emailSpan);
        container.appendChild(logoutBtn);
        authSection.appendChild(container);
    } else {
        var loginBtn = document.createElement('button');
        loginBtn.id = 'login-btn';
        loginBtn.className = 'text-gray-600 hover:text-brand-600 font-medium transition-colors';
        loginBtn.textContent = 'Sign In';
        loginBtn.addEventListener('click', showLoginModal);
        authSection.appendChild(loginBtn);
    }
}

/* ============================================================
   Dark Mode
   ============================================================ */

var THEME_KEY = 'reviewsummary_theme';

/**
 * Apply the given theme ('dark' or 'light') to the document root and update
 * the toggle button icon to match.
 *
 * @param {string} theme - 'dark' or 'light'
 */
function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    updateThemeToggle(theme);
}

/**
 * Initialise theme on page load.
 * Uses the stored localStorage preference, falling back to the OS preference.
 */
function initTheme() {
    var stored = localStorage.getItem(THEME_KEY);
    if (stored === 'dark' || stored === 'light') {
        applyTheme(stored);
    } else {
        var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark ? 'dark' : 'light');
    }
}

/**
 * Toggle between dark and light mode and persist the preference.
 */
function toggleTheme() {
    var isDark = document.documentElement.classList.contains('dark');
    var newTheme = isDark ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, newTheme);
    applyTheme(newTheme);
}

/**
 * Update the toggle button icons to reflect the active theme.
 * The sun icon is shown in dark mode (click to switch to light).
 * The moon icon is shown in light mode (click to switch to dark).
 *
 * @param {string} theme - 'dark' or 'light'
 */
function updateThemeToggle(theme) {
    var sunIcon = document.getElementById('theme-icon-sun');
    var moonIcon = document.getElementById('theme-icon-moon');
    if (!sunIcon || !moonIcon) return;

    if (theme === 'dark') {
        sunIcon.classList.remove('hidden');
        moonIcon.classList.add('hidden');
    } else {
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
    }
}

/* ============================================================
   Initialisation
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {
    updateAuthUI();
    initTheme();
});
