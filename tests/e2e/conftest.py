"""
Playwright E2E test fixtures.

Starts the Flask dev server before tests, tears it down after.
Run: pytest tests/e2e/ -v --headed  (to see the browser)
"""

import os
import time
import subprocess
import signal
import pytest


BASE_URL = "http://localhost:5051"
SERVER_PORT = 5051


@pytest.fixture(scope="session")
def flask_server():
    """Start Flask dev server for E2E tests."""
    env = os.environ.copy()
    env["PORT"] = str(SERVER_PORT)

    proc = subprocess.Popen(
        ["python3", "app.py"],
        cwd=os.path.join(os.path.dirname(__file__), "..", ".."),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready
    for _ in range(30):
        try:
            import urllib.request
            urllib.request.urlopen(BASE_URL)
            break
        except Exception:
            time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError("Flask server failed to start")

    yield BASE_URL

    # Teardown
    os.kill(proc.pid, signal.SIGTERM)
    proc.wait(timeout=5)


@pytest.fixture
def page(flask_server, browser):
    """Create a new page, navigate to the app, and dismiss the welcome modal."""
    pg = browser.new_page()
    pg.goto(flask_server)

    # Dismiss welcome modal if it appears (target exact button ID)
    skip_btn = pg.locator("#welcomeSkip")
    try:
        if skip_btn.is_visible(timeout=3000):
            skip_btn.click()
            pg.wait_for_timeout(500)
    except Exception:
        pass  # Modal might not appear (already dismissed via localStorage)

    yield pg
    pg.close()
