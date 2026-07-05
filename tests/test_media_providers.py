"""Tests for media_providers module."""

from __future__ import annotations
import unittest
from campaign_autopilot.media_providers import (
    check_provider,
    get_best_image_provider,
    get_provider_report,
    PillowImageProvider,
)


class TestMediaProviders(unittest.TestCase):
    def test_check_provider_pillow(self):
        """Pillow should be available (stdlib fallback)."""
        self.assertTrue(check_provider("pillow"))

    def test_best_image_fallback(self):
        """Should return PillowProvider when no AI providers available."""
        provider = get_best_image_provider()
        self.assertIn(provider.name(), ["pillow", "replicate", "diffusers", "fiapi"])

    def test_pillow_generates_image(self):
        """PillowImageProvider should generate valid PNG bytes."""
        provider = PillowImageProvider()
        result = provider.generate("Test prompt", width=100, height=100)
        self.assertGreater(len(result), 50)
        # Check PNG header
        self.assertEqual(result[:8], b"\x89PNG\r\n\x1a\n")

    def test_pillow_different_sizes(self):
        provider = PillowImageProvider()
        for w, h in [(200, 100), (100, 200), (300, 300)]:
            result = provider.generate("Test", width=w, height=h)
            self.assertGreater(len(result), 50, f"Failed at {w}x{h}")

    def test_get_provider_report_structure(self):
        report = get_provider_report()
        self.assertIn("image", report)
        self.assertIn("audio_tts", report)
        self.assertIn("music", report)
        self.assertIn("video", report)
        for category in report.values():
            self.assertIn("available", category)
            self.assertIn("active", category)


if __name__ == "__main__":
    unittest.main()
