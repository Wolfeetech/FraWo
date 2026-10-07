#!/usr/bin/env python3
"""Regression checks for the FraWo Funk beta view."""
from pathlib import Path
import unittest


VIEW = Path(__file__).resolve().parents[1] / "addons/frawo_agent/views/radio_page.xml"
FOOTER_PLAYER = Path(__file__).resolve().parents[1] / "Codex/website/frawo_custom_footer_player.html"


class RadioBetaViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xml = VIEW.read_text(encoding="utf-8")
        cls.footer_player = FOOTER_PLAYER.read_text(encoding="utf-8") if FOOTER_PLAYER.exists() else ""

    def test_page_player_prefers_global_persistent_audio(self):
        marker = "window.ffTogglePlay = function() {"
        start = self.xml.index(marker)
        block = self.xml[start : start + 500]
        self.assertIn("window.fwAudio.togglePlay()", block)

    def test_page_player_syncs_ui_without_delaying_user_play_action(self):
        self.assertIn("function syncPersistentPlayerState()", self.xml)
        marker = "window.ffTogglePlay = function() {"
        start = self.xml.index(marker)
        end = self.xml.index("window.ffSetVolume = function(val) {", start)
        block = self.xml[start:end]
        self.assertEqual(block.count("window.fwAudio.togglePlay()"), 1)
        self.assertIn("syncPersistentPlayerState", block)
        self.assertNotIn("setTimeout(function()", block)

    def test_page_player_never_creates_a_local_fallback_audio(self):
        marker = "window.ffTogglePlay = function() {"
        start = self.xml.index(marker)
        end = self.xml.index("window.ffSetVolume = function(val) {", start)
        block = self.xml[start:end]
        self.assertNotIn("new Audio()", block)
        self.assertIn("PLAYER LÄDT", block)

    def test_volume_prefers_global_persistent_audio(self):
        marker = "window.ffSetVolume = function(val) {"
        start = self.xml.index(marker)
        block = self.xml[start : start + 300]
        self.assertIn("window.fwAudio.setVolume(val)", block)
        self.assertNotIn("setTimeout", block)

    def test_quality_control_is_not_a_false_toggle_with_global_player(self):
        self.assertIn('id="ff-quality-btn" disabled="disabled"', self.xml)
        self.assertIn("Beta-Stream: 320 kbit/s", self.xml)

    def test_anonymous_rating_gets_immediate_login_feedback(self):
        marker = "window.ffRate = function (stars) {"
        start = self.xml.index(marker)
        block = self.xml[start : start + 500]
        self.assertIn("if (!ffIsLoggedIn())", block)
        self.assertIn("Zum Bewerten bitte im Portal anmelden", block)

    def test_mobile_footer_uses_responsive_grid_class(self):
        self.assertIn('class="fw-footer-grid"', self.xml)
        self.assertIn("@media (max-width: 760px)", self.xml)
        self.assertIn(".fw-footer-grid { grid-template-columns: 1fr;", self.xml)

    def test_subtle_3d_is_css_only_and_respects_reduced_motion(self):
        self.assertIn("perspective: 1200px", self.xml)
        self.assertIn("transform-style: preserve-3d", self.xml)
        self.assertIn("@media (hover: hover) and (pointer: fine)", self.xml)
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.xml)
        self.assertNotIn("WebGLRenderingContext", self.xml)

    def test_radio_page_uses_only_approved_ci_colors(self):
        """Die Radioseite darf keine abgelösten Farben mehr enthalten (CI v3.0)."""
        import json
        tokens = json.loads((Path(__file__).resolve().parents[1] / "SSOT/ci_tokens.json")
                            .read_text(encoding="utf-8"))
        lowered = self.xml.lower()
        gefunden = {
            farbe: lowered.count(farbe)
            for farbe in tokens["abgeloest"]
            if not farbe.startswith("_") and farbe in lowered
        }
        self.assertEqual(gefunden, {}, f"abgelöste Farben in radio_page.xml: {gefunden}")
        self.assertIn("#a050f0", lowered, "CI-Akzent #a050f0 fehlt")

    def test_primary_audio_controls_have_accessible_labels(self):
        self.assertIn('id="ff-play-btn" type="button" aria-label="FraWo Funk abspielen oder pausieren"', self.xml)
        self.assertIn('id="ff-vol-slider" aria-label="Lautstärke"', self.xml)


class RadioMobileLayoutTests(unittest.TestCase):
    """Am 07.10.2026 war die Seite auf dem Handy nach rechts verschoben, mit
    schwarzem Rand und abgeschnittenem Inhalt: Die 850px breite Aurora ragte
    aus dem Bildschirm. Diese Tests halten die Seite schmal."""

    @classmethod
    def setUpClass(cls):
        cls.xml = VIEW.read_text(encoding="utf-8")

    def test_seite_kann_nicht_querscrollen(self):
        self.assertIn("overflow-x: hidden", self.xml)
        self.assertIn(".ff-container {\n  overflow-x: clip;", self.xml)

    def test_aurora_ist_nie_breiter_als_die_seite(self):
        start = self.xml.index(".ff-ambient-light {")
        block = self.xml[start : start + 400]
        self.assertIn("width: min(850px, 100%)", block)
        self.assertIn("max-width: 100%", block)

    def test_keine_festen_breiten_ueber_400px_ausser_begrenzter_aurora(self):
        import re
        treffer = [
            m.group(0)
            for m in re.finditer(r"(?:^|[;{\s])width:\s*(\d{3,5})px", self.xml)
            if int(m.group(1)) > 400
        ]
        self.assertEqual(treffer, [], f"feste Breiten ueber 400px: {treffer}")


if __name__ == "__main__":
    unittest.main()


