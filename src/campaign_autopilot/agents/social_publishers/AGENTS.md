# social_publishers — Sub-agents Package

## Purpose
Publicacao em 8 plataformas sociais: YouTube, Instagram, TikTok, Twitter, Pinterest, LinkedIn, Telegram, Facebook

## Agents
- browser_automation
- facebook_publisher
- instagram_publisher
- linkedin_publisher
- orchestrator
- pinterest_publisher
- telegram_publisher
- tiktok_publisher
- twitter_publisher
- youtube_publisher

## Rules
- All agents extend AgentBase from agents/base.py
- Each agent implements run(context) -> AgentResult
- Zero external dependencies for core logic
- Thread-safe with RLock for shared state
