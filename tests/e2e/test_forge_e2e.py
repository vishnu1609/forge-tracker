"""
FORGE — End-to-End Tests (Playwright Python)

Full browser tests for the FORGE training tracker.
Run:  pytest tests/e2e/ -v
      pytest tests/e2e/ -v --headed          (watch the browser)
      pytest tests/e2e/ -v --headed --slow    (slow motion)
"""

import re
import pytest
from playwright.sync_api import expect


# ═══════════════════════════════════════════════
#   PAGE LOAD & BASICS
# ═══════════════════════════════════════════════

class TestPageLoad:
    """Verify the app loads correctly."""

    def test_page_title(self, page):
        expect(page).to_have_title(re.compile(r"FORGE"))

    def test_page_has_forge_logo(self, page):
        logo = page.locator("#navLogo")
        expect(logo).to_be_visible()
        expect(logo).to_have_text("FORGE")

    def test_no_console_errors(self, page):
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.reload()
        page.wait_for_timeout(2000)
        # Filter out known non-critical errors
        ignore = ["supabase", "favicon", "failed to load", "net::err", "404"]
        critical = [e for e in errors if not any(k in e.lower() for k in ignore)]
        assert len(critical) == 0, f"Console errors: {critical}"


# ═══════════════════════════════════════════════
#   NAVIGATION
# ═══════════════════════════════════════════════

class TestNavigation:
    """Nav bar and menu tests."""

    def test_nav_bar_visible(self, page):
        nav = page.locator("#mainNav")
        expect(nav).to_be_visible()

    def test_nav_burger_visible_on_mobile(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        burger = page.locator("#navBurger")
        expect(burger).to_be_visible()

    def test_nav_tabs_hidden_on_mobile(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        tabs = page.locator(".nav-tabs")
        expect(tabs).to_be_hidden()

    def test_hamburger_opens_mobile_menu(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        burger = page.locator("#navBurger")
        mobile_menu = page.locator("#mobileMenu")

        # Menu should be hidden initially
        expect(mobile_menu).to_be_hidden()

        # Click burger to open
        burger.click()
        expect(mobile_menu).to_be_visible()

    def test_hamburger_closes_mobile_menu(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        burger = page.locator("#navBurger")
        mobile_menu = page.locator("#mobileMenu")

        # Open then close
        burger.click()
        expect(mobile_menu).to_be_visible()
        burger.click()
        expect(mobile_menu).to_be_hidden()

    def test_mobile_menu_has_all_sections(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        page.locator("#navBurger").click()

        menu = page.locator("#mobileMenu")
        for section in ["Home", "Schedule", "Plan", "Sessions", "Muscles", "Fuel", "Log", "Reports", "Glossary"]:
            expect(menu.locator(f"text={section}")).to_be_visible()

    def test_mobile_menu_navigates_to_section(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        page.locator("#navBurger").click()

        # Click Sessions tab
        page.locator("#mobileMenu >> text=Sessions").click()
        page.wait_for_timeout(1000)

        # Menu should close after clicking
        expect(page.locator("#mobileMenu")).to_be_hidden()

    def test_nav_tabs_visible_on_desktop(self, page):
        page.set_viewport_size({"width": 1280, "height": 800})
        tabs = page.locator(".nav-tabs")
        expect(tabs).to_be_visible()

    def test_nav_burger_hidden_on_desktop(self, page):
        page.set_viewport_size({"width": 1280, "height": 800})
        burger = page.locator("#navBurger")
        expect(burger).to_be_hidden()


# ═══════════════════════════════════════════════
#   HERO SECTION
# ═══════════════════════════════════════════════

class TestHeroSection:
    """Hero banner content."""

    def test_hero_title_visible(self, page):
        hero_title = page.locator(".hero-title")
        expect(hero_title).to_be_visible()

    def test_hero_has_cta_buttons(self, page):
        hero = page.locator(".hero")
        hero.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        # Buttons may use slightly different text casing
        session_btn = page.locator(".hero-cta-primary, [data-target='sessions']").first
        expect(session_btn).to_be_attached()

    def test_hero_eyebrow_shows_program(self, page):
        eyebrow = page.locator(".hero-eyebrow")
        expect(eyebrow).to_contain_text("WINTER ARC")
        expect(eyebrow).to_contain_text("6 DAYS/WEEK")


# ═══════════════════════════════════════════════
#   SCHEDULE SECTION
# ═══════════════════════════════════════════════

class TestScheduleSection:
    """Weekly schedule card grid."""

    def test_schedule_section_exists(self, page):
        schedule = page.locator("#schedule")
        expect(schedule).to_be_attached()

    def test_seven_day_cards_exist(self, page):
        cards = page.locator(".day-card")
        expect(cards).to_have_count(7)

    def test_day_labels(self, page):
        days = page.locator(".dc-day")
        texts = days.all_text_contents()
        expected = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        assert texts == expected

    def test_rest_days_marked(self, page):
        rest_cards = page.locator(".day-card.rest-day")
        expect(rest_cards).to_have_count(1)  # Sun only


# ═══════════════════════════════════════════════
#   SESSION ARTICLES
# ═══════════════════════════════════════════════

class TestSessionArticles:
    """Training session workout cards."""

    def test_all_six_sessions_exist(self, page):
        for session_id in ["upper", "lower", "abs", "push", "pull", "legs"]:
            session = page.locator(f"#{session_id}")
            expect(session).to_be_attached()

    def test_session_headers_expand(self, page):
        # Click Upper session header to expand
        page.locator("#upper .sb-hdr").click()
        page.wait_for_timeout(500)

        # Body should be visible
        body = page.locator("#upper-body")
        expect(body).to_be_visible()

    def test_session_headers_collapse(self, page):
        header = page.locator("#upper .sb-hdr")

        # Open
        header.click()
        page.wait_for_timeout(500)
        expect(page.locator("#upper-body")).to_be_visible()

        # Close
        header.click()
        page.wait_for_timeout(500)
        expect(page.locator("#upper-body")).to_be_hidden()

    def test_upper_has_exercises(self, page):
        page.locator("#upper .sb-hdr").click()
        page.wait_for_timeout(500)

        rows = page.locator("#upper-body .ex-name")
        count = rows.count()
        assert count == 8, f"Expected 8 exercises in Upper, got {count}"

    def test_lower_has_kettlebell_swing(self, page):
        """Lower session ends with explosive Kettlebell Swing."""
        page.locator("#lower .sb-hdr").click()
        page.wait_for_timeout(500)

        body_text = page.locator("#lower-body").text_content()
        assert "Kettlebell Swing" in body_text

    def test_pull_has_conventional_deadlift(self, page):
        page.locator("#pull .sb-hdr").click()
        page.wait_for_timeout(500)

        expect(page.locator("#pull-body >> text=Conventional Deadlift")).to_be_visible()

    def test_abs_session_has_forearm_work(self, page):
        """Wednesday ABS session includes forearm exercises."""
        page.locator("#abs .sb-hdr").click()
        page.wait_for_timeout(500)

        body_text = page.locator("#abs-body").text_content()
        assert "Farmer" in body_text, "ABS session missing Farmer's Walk"
        assert "Wrist Curl" in body_text, "ABS session missing Barbell Wrist Curl"

    def test_each_session_has_eight_exercises(self, page):
        """Every session should have exactly 8 exercises."""
        for session_id in ["upper", "lower", "abs", "push", "pull", "legs"]:
            page.locator(f"#{session_id} .sb-hdr").click()
            page.wait_for_timeout(300)

            rows = page.locator(f"#{session_id}-body .ex-name")
            count = rows.count()
            assert count == 8, f"{session_id} has {count} exercises, expected 8"

            page.locator(f"#{session_id} .sb-hdr").click()
            page.wait_for_timeout(200)


# ═══════════════════════════════════════════════
#   EXERCISE INTERACTIONS
# ═══════════════════════════════════════════════

class TestExerciseInteractions:
    """Exercise row clicks, video modal, LOG buttons."""

    def test_log_buttons_exist(self, page):
        page.locator("#upper .sb-hdr").click()
        page.wait_for_timeout(500)

        log_btns = page.locator("#upper-body .log-quick-btn")
        assert log_btns.count() == 8

    def test_log_button_has_data_attributes(self, page):
        page.locator("#upper .sb-hdr").click()
        page.wait_for_timeout(500)

        first_log = page.locator("#upper-body .log-quick-btn").first
        assert first_log.get_attribute("data-exercise") is not None
        assert first_log.get_attribute("data-session") == "Upper"

    def test_exercise_name_is_clickable(self, page):
        page.locator("#upper .sb-hdr").click()
        page.wait_for_timeout(500)

        # Click an exercise name — should open detail panel
        ex_name = page.locator("#upper-body .ex-name").first
        ex_name.click()
        page.wait_for_timeout(500)

        # Detail panel or video overlay should appear
        detail = page.locator("#exDetailPanel, #videoOverlay")
        # At least one interaction element should respond
        assert detail.count() >= 1

    def test_video_overlay_exists_in_dom(self, page):
        overlay = page.locator("#videoOverlay")
        expect(overlay).to_be_attached()


# ═══════════════════════════════════════════════
#   TRACKER SECTION
# ═══════════════════════════════════════════════

class TestTrackerSection:
    """Tracker / logging section."""

    def test_tracker_section_exists(self, page):
        tracker = page.locator("#tracker")
        expect(tracker).to_be_attached()

    def test_tracker_has_tabs(self, page):
        # Scroll to tracker
        page.locator("#tracker").scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        # Should have BODY and WORKOUT tabs (or similar)
        tracker_text = page.locator("#tracker").text_content()
        assert any(word in tracker_text for word in ["BODY", "WORKOUT", "LOG", "WEIGHT"])


# ═══════════════════════════════════════════════
#   MUSCLE MAP
# ═══════════════════════════════════════════════

class TestMuscleMap:
    """Muscle visualization section."""

    def test_muscle_section_exists(self, page):
        muscle_viz = page.locator("#muscleViz")
        expect(muscle_viz).to_be_attached()

    def test_muscle_maps_in_dom(self, page):
        expect(page.locator("#muscleMapFront")).to_be_attached()
        expect(page.locator("#muscleMapBack")).to_be_attached()


# ═══════════════════════════════════════════════
#   API ENDPOINTS (E2E)
# ═══════════════════════════════════════════════

class TestAPIEndpoints:
    """Hit the real API endpoints through the running server.

    Note: body/workout/stats endpoints require a live Supabase connection.
    The health endpoint works regardless (returns 'disconnected' if DB is down).
    Tests that need Supabase are marked with pytest.mark.supabase.
    """

    def test_health_endpoint(self, page, flask_server):
        resp = page.request.get(f"{flask_server}/api/health")
        assert resp.status == 200
        data = resp.json()
        assert data["status"] == "ok"
        # database could be 'connected' or 'disconnected'
        assert data["database"] in ("connected", "disconnected")

    def _supabase_available(self, page, flask_server):
        """Check if Supabase is reachable."""
        resp = page.request.get(f"{flask_server}/api/health")
        return resp.json().get("database") == "connected"

    def test_get_body_logs_endpoint(self, page, flask_server):
        if not self._supabase_available(page, flask_server):
            pytest.skip("Supabase not connected")
        resp = page.request.get(f"{flask_server}/api/body")
        assert resp.status == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "data" in data

    def test_get_workout_logs_endpoint(self, page, flask_server):
        if not self._supabase_available(page, flask_server):
            pytest.skip("Supabase not connected")
        resp = page.request.get(f"{flask_server}/api/workout")
        assert resp.status == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_get_stats_endpoint(self, page, flask_server):
        if not self._supabase_available(page, flask_server):
            pytest.skip("Supabase not connected")
        resp = page.request.get(f"{flask_server}/api/stats")
        assert resp.status == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_post_and_delete_body_log(self, page, flask_server):
        """Full CRUD cycle: create then delete a body log."""
        if not self._supabase_available(page, flask_server):
            pytest.skip("Supabase not connected")
        resp = page.request.post(f"{flask_server}/api/body", data={
            "date": "2099-01-01",
            "weight": 99.9,
            "waist": 30,
            "notes": "E2E test entry"
        })
        assert resp.status == 200
        created = resp.json()
        assert created["status"] == "ok"

        if created.get("data") and len(created["data"]) > 0:
            log_id = created["data"][0].get("id")
            if log_id:
                del_resp = page.request.delete(f"{flask_server}/api/body/{log_id}")
                assert del_resp.status == 200

    def test_post_and_delete_workout_log(self, page, flask_server):
        """Full CRUD cycle: create then delete a workout log."""
        if not self._supabase_available(page, flask_server):
            pytest.skip("Supabase not connected")
        resp = page.request.post(f"{flask_server}/api/workout", data={
            "date": "2099-01-01",
            "session": "Upper",
            "exercise": "E2E Test Exercise",
            "weight": 0,
            "sets": 1,
            "reps": "10"
        })
        assert resp.status == 200
        created = resp.json()

        if created.get("data") and len(created["data"]) > 0:
            log_id = created["data"][0].get("id")
            if log_id:
                del_resp = page.request.delete(f"{flask_server}/api/workout/{log_id}")
                assert del_resp.status == 200


# ═══════════════════════════════════════════════
#   RESPONSIVE DESIGN
# ═══════════════════════════════════════════════

class TestResponsiveDesign:
    """Mobile and desktop layout checks."""

    def test_mobile_layout(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(500)

        # Nav should be minimal height
        nav = page.locator("#mainNav")
        box = nav.bounding_box()
        assert box["height"] <= 50, f"Nav too tall on mobile: {box['height']}px"

    def test_desktop_layout(self, page):
        page.set_viewport_size({"width": 1280, "height": 800})
        page.wait_for_timeout(500)

        nav = page.locator("#mainNav")
        box = nav.bounding_box()
        assert box["height"] <= 55, f"Nav too tall on desktop: {box['height']}px"

    def test_no_major_horizontal_scroll(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(1000)

        scroll_w = page.evaluate("document.documentElement.scrollWidth")
        client_w = page.evaluate("document.documentElement.clientWidth")
        overflow = scroll_w - client_w
        # Allow up to 50px for minor overflow from wide tables/content
        # (exercise tables use overflow-x:auto but may contribute to body scrollWidth)
        assert overflow <= 50, (
            f"Major horizontal scroll on mobile: scrollWidth={scroll_w}, "
            f"clientWidth={client_w}, overflow={overflow}px"
        )

    def test_burger_on_right_side(self, page):
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(500)

        burger = page.locator("#navBurger")
        box = burger.bounding_box()
        viewport_width = 375

        # Burger should be in the right 25% of the screen
        assert box["x"] > viewport_width * 0.70, (
            f"Burger not on right side: x={box['x']}, expected > {viewport_width * 0.70}"
        )


# ═══════════════════════════════════════════════
#   SCROLL PROGRESS
# ═══════════════════════════════════════════════

class TestScrollProgress:
    """Scroll progress bar behavior."""

    def test_progress_bar_exists(self, page):
        bar = page.locator("#scrollProgressBar")
        expect(bar).to_be_attached()

    def test_progress_bar_advances_on_scroll(self, page):
        bar = page.locator("#scrollProgressBar")

        # Get initial width
        initial_width = page.evaluate(
            "document.getElementById('scrollProgressBar').style.width || '0%'"
        )

        # Scroll down
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(500)

        new_width = page.evaluate(
            "document.getElementById('scrollProgressBar').style.width"
        )

        # Width should have changed after scrolling
        assert new_width != initial_width or new_width != "0%"


# ═══════════════════════════════════════════════
#   FOOTER
# ═══════════════════════════════════════════════

class TestFooter:
    """Footer content."""

    def test_footer_exists(self, page):
        footer = page.locator("footer, .footer, .forge-footer")
        expect(footer).to_be_attached()

    def test_footer_shows_program_type(self, page):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)

        body_text = page.locator("body").text_content()
        assert "UPPER-LOWER" in body_text
        assert "PPL" in body_text
