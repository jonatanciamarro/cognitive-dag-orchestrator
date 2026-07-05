"""Social Media Publishers — Publicação automática em todas as plataformas.

Cada publisher segue o padrão:
1. Se configurado (API key/token) → posta via API real
2. Se não configurado → gera arquivo pronto para postar manualmente
3. Fallback: salva em output/ para você copiar e colar

Plataformas suportadas:
- YouTube → YouTube Data API v3
- Twitter/X → Twitter API v2 (OAuth 2.0)
- Instagram → Instagram Graph API + browser fallback
- TikTok → TikTok API + browser fallback
- Pinterest → Pinterest API v5
- LinkedIn → LinkedIn API
- Telegram → Telegram Bot API (mais fácil de configurar!)
- Medium → Medium API
- Facebook → Facebook Graph API
"""

from .orchestrator import SocialPublishingOrchestratorAgent
from .youtube_publisher import YouTubePublisherAgent
from .twitter_publisher import TwitterPublisherAgent
from .instagram_publisher import InstagramPublisherAgent
from .tiktok_publisher import TikTokPublisherAgent
from .pinterest_publisher import PinterestPublisherAgent
from .linkedin_publisher import LinkedInPublisherAgent
from .telegram_publisher import TelegramPublisherAgent
from .facebook_publisher import FacebookPublisherAgent
from .browser_automation import BrowserAutomationAgent

__all__ = [
    "SocialPublishingOrchestratorAgent",
    "YouTubePublisherAgent",
    "TwitterPublisherAgent",
    "InstagramPublisherAgent",
    "TikTokPublisherAgent",
    "PinterestPublisherAgent",
    "LinkedInPublisherAgent",
    "TelegramPublisherAgent",
    "FacebookPublisherAgent",
    "BrowserAutomationAgent",
]
