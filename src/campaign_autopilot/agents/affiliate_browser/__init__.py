"""Affiliate Browser Automation — Navegacao automatizada em marketplaces de afiliados.

Permite que o sistema:
1. Navegue ate marketplaces (Hotmart, Kiwify, Eduzz, etc.)
2. Varredura de produtos por nicho
3. Extracao de links de afiliado REAIS
4. Registro automatico no ProductLinkRegistry
"""

from .browser_agent import AffiliateBrowserAgent

__all__ = ["AffiliateBrowserAgent"]
