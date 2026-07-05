"""Tests for money_printer module (MoneyPrinterTurbo integration)."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from campaign_autopilot.media_pipeline.money_printer import (
    EdgeTTSSynthesizer,
    TurboVideoProducer,
)


class TestMoneyPrinter(unittest.TestCase):
    def setUp(self) -> None:
        self.output_dir = Path("output/test_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.audio_path = self.output_dir / "test_narration.mp3"

    def tearDown(self) -> None:
        # Cleanup test files
        if self.audio_path.exists():
            try:
                self.audio_path.unlink()
            except Exception:
                pass
        for f in self.output_dir.glob("*.mp4"):
            try:
                f.unlink()
            except Exception:
                pass
        try:
            self.output_dir.rmdir()
        except Exception:
            pass

    def test_edge_tts_synthesis(self) -> None:
        """Verify EdgeTTS narration synthesis and timings generation."""
        text = "Olá! Isto é um teste rápido de narração."
        result = EdgeTTSSynthesizer.synthesize(text, self.audio_path)
        
        self.assertEqual(result["status"], "success")
        self.assertTrue(self.audio_path.exists())
        self.assertGreater(self.audio_path.stat().st_size, 100)
        
        # Check timings
        timings = result["timings"]
        self.assertIsInstance(timings, list)
        self.assertGreater(len(timings), 0)
        for t in timings:
            self.assertIn("text", t)
            self.assertIn("start", t)
            self.assertIn("end", t)

    def test_turbo_video_producer_fallback(self) -> None:
        """Verify TurboVideoProducer creates a video successfully (with fallback)."""
        script = "Dica um: Foco e determinação. Curtiu? Siga para mais!"
        producer = TurboVideoProducer(self.output_dir)
        
        result = producer.produce_viral_short(
            script_text=script,
            niche="teste",
            keyword="foco",
            filename="test_short.mp4",
        )
        
        self.assertEqual(result["status"], "success")
        self.assertTrue((self.output_dir / "test_short.mp4").exists())
        self.assertGreater((self.output_dir / "test_short.mp4").stat().st_size, 1000)
        self.assertEqual(result["width"], 720)
        self.assertEqual(result["height"], 1280)


if __name__ == "__main__":
    unittest.main()
