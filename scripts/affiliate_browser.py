#!/usr/bin/env python3
"""CLI para o AffiliateBrowserAgent.

Uso:
  python scripts/affiliate_browser.py login hotmart          # Login manual (abre navegador)
  python scripts/affiliate_browser.py scan hotmart --niche "marketing digital"
  python scripts/affiliate_browser.py full-scan
  python scripts/affiliate_browser.py status
"""

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ['CAMPAIGN_BOT_REQUIRE_OPT_IN'] = 'false'

from campaign_autopilot.agents.affiliate_browser.browser_agent import (
    AffiliateBrowserAgent, PLATFORM_CONFIGS, SessionManager, main
)

if __name__ == "__main__":
    main()
