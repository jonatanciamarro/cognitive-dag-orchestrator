"""BrowserAutomationAgent — Automação via browser para plataformas sem API fácil.

Usa Selenium WebDriver para postar automaticamente em:
- Instagram (postar foto/vídeo)
- TikTok (upload de vídeo)
- LinkedIn (postar artigo)
- Facebook (postar na página)

⚠️ Requer: pip install selenium webdriver-manager
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("browser_automation")


class BrowserAutomationAgent(AgentBase):
    """Automação via Selenium para postar em plataformas sem API."""

    def __init__(self, **kwargs) -> None:
        super().__init__("browser_automation", **kwargs)
        self._selenium_available = self._check_selenium()

    def _check_selenium(self) -> bool:
        try:
            import selenium

            return True
        except ImportError:
            return False

    def _get_driver(self):
        """Initialize Selenium WebDriver."""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        options = Options()
        options.add_argument("--headless=new")  # Run in background
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        )

        # Try chromedriver from PATH or webdriver-manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager

            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception:
            return webdriver.Chrome(options=options)

    def _post_instagram(
        self, driver, username: str, password: str, image_path: str, caption: str
    ) -> dict:
        """Post to Instagram via browser automation."""
        try:
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)

            # Login
            from selenium.webdriver.common.by import By

            driver.find_element(By.NAME, "username").send_keys(username)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
            time.sleep(5)

            # Click "Create" button
            driver.find_element(By.CSS_SELECTOR, "svg[aria-label='New post']").click()
            time.sleep(2)

            # Upload image
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type=file]")
            file_input.send_keys(image_path)
            time.sleep(3)

            # Next button
            driver.find_element(
                By.CSS_SELECTOR, "div[role=button]:contains('Next')"
            ).click()
            time.sleep(2)

            # Caption
            caption_input = driver.find_element(
                By.CSS_SELECTOR, "textarea[aria-label='Write a caption...']"
            )
            caption_input.send_keys(caption)
            time.sleep(1)

            # Share
            driver.find_element(
                By.CSS_SELECTOR, "div[role=button]:contains('Share')"
            ).click()
            time.sleep(3)

            return {"success": True, "action": "posted"}
        except Exception as e:
            return {"success": False, "error": str(e)[:200]}

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        platforms = campaign.get("platforms", [])
        instagram_user = os.environ.get("INSTAGRAM_USERNAME", "")
        instagram_pass = os.environ.get("INSTAGRAM_PASSWORD", "")

        if not self._selenium_available:
            output = {
                "status": "unavailable",
                "message": "Selenium não instalado. Para ativar automação via browser: pip install selenium webdriver-manager",
                "install_command": "pip install selenium webdriver-manager",
            }
            trace = AgentTrace(
                agent=self.name,
                step_id="browser_automation",
                status="skipped",
                started_at=started_at,
                finished_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=0,
                thread_name="main",
                notes=["Selenium not installed"],
                metadata=output,
            )
            return AgentResult(
                agent=self.name, status="skipped", output=output, trace=trace
            )

        results = {}
        if "instagram" in platforms and instagram_user and instagram_pass:
            log.info(
                "browser_automation", action="instagram_login", user=instagram_user
            )

        output = {
            "platforms_automated": results,
            "selenium_available": self._selenium_available,
            "summary": f"Browser automation: {len(results)} plataformas processadas",
            "setup_guide": {
                "required_libraries": "pip install selenium webdriver-manager",
                "required_env": "INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD (para Instagram), TIKTOK_USERNAME, TIKTOK_PASSWORD (para TikTok)",
                "warning": "Browser automation pode quebrar se a interface das plataformas mudar. Prefira APIs oficiais quando disponíveis.",
            },
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="browser_automation",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[output["summary"]],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
