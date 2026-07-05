"""Tests for SiteDeployAgent and SiteGenerator."""

from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.site_deploy import SiteDeployAgent


class TestSiteDeploy(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.agent = SiteDeployAgent(
            output_dir=str(self.tmpdir), site_url="https://test.com"
        )

    def test_generates_site(self):
        c = CampaignContext(
            campaign={"campaign_id": "sd_test", "niche": "marketing digital"}
        )
        c.run_id = "sd_run"
        c.step_results["content_generator"] = {
            "output": {
                "articles": [
                    {
                        "title": "Guia de Marketing Digital",
                        "slug": "guia-marketing-digital",
                        "body": "**Marketing digital** é essencial hoje em dia.\n\n## Por que é importante\n\nPorque traz resultados.\n\n- Primeiro item\n- Segundo item",
                        "meta_description": "Guia completo de marketing digital.",
                        "word_count": 300,
                        "keyword": "marketing digital",
                        "content_type": "article",
                    }
                ]
            }
        }
        result = self.agent.run(c)
        self.assertEqual(result.status, "success")
        self.assertGreater(result.output.get("files_generated", 0), 0)
        self.assertIn("site_url", result.output)

    def test_site_files_exist(self):
        c = CampaignContext(campaign={"campaign_id": "sd_test2", "niche": "mkt"})
        c.run_id = "sd_run2"
        c.step_results["content_generator"] = {
            "output": {
                "articles": [
                    {
                        "title": "Test",
                        "slug": "test",
                        "body": "Content.",
                        "meta_description": "Desc.",
                        "word_count": 100,
                        "keyword": "test",
                        "content_type": "article",
                    }
                ]
            }
        }
        self.agent.run(c)
        self.assertTrue((self.tmpdir / "index.html").exists())
        self.assertTrue((self.tmpdir / "sitemap.xml").exists())
        self.assertTrue((self.tmpdir / "robots.txt").exists())
        self.assertTrue((self.tmpdir / "rss.xml").exists())
        self.assertTrue((self.tmpdir / "blog/test.html").exists())
        self.assertTrue((self.tmpdir / "assets/css/style.css").exists())

    def test_article_has_html_structure(self):
        c = CampaignContext(campaign={"campaign_id": "sd_test3", "niche": "mkt"})
        c.run_id = "sd_run3"
        c.step_results["content_generator"] = {
            "output": {
                "articles": [
                    {
                        "title": "Guia SEO",
                        "slug": "guia-seo",
                        "body": "Conteúdo sobre SEO. ## Tópico Importante - Item",
                        "meta_description": "Guia SEO completo.",
                        "word_count": 200,
                        "keyword": "seo",
                        "content_type": "article",
                    }
                ]
            }
        }
        self.agent.run(c)
        html = (self.tmpdir / "blog/guia-seo.html").read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Guia SEO", html)
        self.assertIn("afiliados", html.lower())


if __name__ == "__main__":
    unittest.main()
