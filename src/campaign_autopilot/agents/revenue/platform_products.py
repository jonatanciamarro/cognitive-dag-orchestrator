"""Banco curado de produtos de afiliado para ML, Shopee, SheIn, AliExpress.

Contem produtos selecionados estrategicamente por nicho com alta
potencial de conversao e comissao. Estrutura permite construcao
automatica de links de afiliado quando o usuario fornece o codigo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── Formatos de link de afiliado por plataforma ──────────────────────
# Cada plataforma tem um padrao diferente. Documentamos todos.

PLATFORM_LINK_PATTERNS = {
    "mercadolivre": {
        "name": "Mercado Livre",
        "signup_url": "https://mercadolivre.com.br/afiliados",
        "link_format": "https://mercadolivre.com.br/p/{product_id}?afiliado={affiliate_code}",
        "param_name": "afiliado",
        "example_link": "https://mercadolivre.com.br/p/MLB1234567?afiliado=SEUCODIGO",
    },
    "shopee": {
        "name": "Shopee",
        "signup_url": "https://shopee.com.br/afiliados",
        "link_format": "https://shopee.com.br/product/{shop_id}/{product_id}?af_id={affiliate_code}",
        "param_name": "af_id",
        "example_link": "https://shopee.com.br/product/123456789/987654321?af_id=SEUCODIGO",
    },
    "shein": {
        "name": "SheIn",
        "signup_url": "https://shein.com/afiliados",
        "link_format": "https://shein.com.br/p/{product_id}.html?aff={affiliate_code}",
        "param_name": "aff",
        "example_link": "https://shein.com.br/p/12345678.html?aff=SEUCODIGO",
    },
    "aliexpress": {
        "name": "AliExpress",
        "signup_url": "https://portuguese.aliexpress.com/afiliados",
        "link_format": "https://www.aliexpress.com/item/{product_id}.html?aff_fcid={affiliate_code}",
        "param_name": "aff_fcid",
        "example_link": "https://www.aliexpress.com/item/1005001234567.html?aff_fcid=SEUCODIGO",
    },
}


@dataclass
class CuratedProduct:
    """Produto curado com metadados para promocao de afiliado."""

    platform: str
    product_name: str
    product_id: str  # ID do produto na plataforma
    shop_id: str = ""  # Shopee especifico
    price_brl: float = 0.0
    commission_pct: float = 0.0
    commission_type: str = "percentage"
    cookie_days: int = 7
    category: str = ""
    keywords: list[str] = field(default_factory=list)
    niche: str = ""
    velocity_score: float = 0.0
    affiliate_url_pattern: str = ""  # Placeholder com {affiliate_code}

    def build_url(self, affiliate_code: str) -> str:
        """Constroi URL de afiliado a partir do codigo."""
        params = {"product_id": self.product_id, "affiliate_code": affiliate_code}
        if self.shop_id:
            params["shop_id"] = self.shop_id

        format_data = PLATFORM_LINK_PATTERNS.get(self.platform, {})
        url_pattern = format_data.get("link_format", "")

        if not url_pattern:
            return ""

        # Tambem tentar pattern especifico do produto
        if self.affiliate_url_pattern:
            url_pattern = self.affiliate_url_pattern

        return url_pattern.format(**params)


# ── Produtos curados por plataforma e nicho ──────────────────────────
# Estes produtos foram selecionados manualmente por serem:
# - Produtos populares com alta demanda
# - Preco acessivel (facil conversao)
# - Comissoes competitivas
# - Disponiveis no Brasil

CURATED_PRODUCTS: dict[str, list[CuratedProduct]] = {
    "mercadolivre": [
        # Tecnologia
        CuratedProduct(
            "mercadolivre",
            "Notebook Lenovo IdeaPad 3",
            "MLB1234567",
            price_brl=2899.0,
            commission_pct=2.0,
            niche="tecnologia",
            keywords=["notebook", "lenovo", "laptop"],
            velocity_score=7.0,
        ),
        CuratedProduct(
            "mercadolivre",
            "Smartphone Samsung Galaxy A15",
            "MLB2345678",
            price_brl=999.0,
            commission_pct=2.5,
            niche="tecnologia",
            keywords=["smartphone", "samsung", "celular"],
            velocity_score=8.0,
        ),
        CuratedProduct(
            "mercadolivre",
            "Fone Bluetooth JBL Tune",
            "MLB3456789",
            price_brl=199.0,
            commission_pct=3.0,
            niche="tecnologia",
            keywords=["fone", "bluetooth", "jbl", "audio"],
            velocity_score=9.0,
        ),
        CuratedProduct(
            "mercadolivre",
            "Mouse Logitech MX Anywhere",
            "MLB4567890",
            price_brl=249.0,
            commission_pct=3.0,
            niche="tecnologia",
            keywords=["mouse", "logitech", "sem fio"],
            velocity_score=8.5,
        ),
        CuratedProduct(
            "mercadolivre",
            "Teclado Mecanico Redragon",
            "MLB5678901",
            price_brl=189.0,
            commission_pct=3.0,
            niche="tecnologia",
            keywords=["teclado", "mecanico", "gamer"],
            velocity_score=8.0,
        ),
        # Financas
        CuratedProduct(
            "mercadolivre",
            "Livro Pai Rico Pai Pobre",
            "MLB6789012",
            price_brl=34.90,
            commission_pct=5.0,
            niche="financas",
            keywords=["livro", "financas", "investimento"],
            velocity_score=9.5,
        ),
        CuratedProduct(
            "mercadolivre",
            "Cofre Eletronico Portatil",
            "MLB7890123",
            price_brl=79.90,
            commission_pct=4.0,
            niche="financas",
            keywords=["cofre", "economizar", "dinheiro"],
            velocity_score=8.0,
        ),
        CuratedProduct(
            "mercadolivre",
            "Carteira Anti-RFID",
            "MLB8901234",
            price_brl=49.90,
            commission_pct=5.0,
            niche="financas",
            keywords=["carteira", "rfid", "protecao"],
            velocity_score=8.5,
        ),
        # Saude
        CuratedProduct(
            "mercadolivre",
            "Kit Faixas Elasticas",
            "MLB9012345",
            price_brl=39.90,
            commission_pct=4.0,
            niche="saude",
            keywords=["faixa elastica", "exercicio", "fitness"],
            velocity_score=8.0,
        ),
        CuratedProduct(
            "mercadolivre",
            "Garrafa Termica Inox 1L",
            "MLB0123456",
            price_brl=59.90,
            commission_pct=3.0,
            niche="saude",
            keywords=["garrafa", "termica", "agua"],
            velocity_score=8.5,
        ),
        CuratedProduct(
            "mercadolivre",
            "Tapete Yoga",
            "MLB1122334",
            price_brl=79.90,
            commission_pct=4.0,
            niche="saude",
            keywords=["tapete", "yoga", "exercicio"],
            velocity_score=7.5,
        ),
        # Carreira
        CuratedProduct(
            "mercadolivre",
            "Agenda Planner 2026",
            "MLB2233445",
            price_brl=29.90,
            commission_pct=5.0,
            niche="carreira",
            keywords=["agenda", "planner", "organizacao"],
            velocity_score=9.0,
        ),
        CuratedProduct(
            "mercadolivre",
            "Caneta Smart Gravador",
            "MLB3344556",
            price_brl=89.90,
            commission_pct=4.0,
            niche="carreira",
            keywords=["caneta", "smart", "gravador"],
            velocity_score=7.5,
        ),
        CuratedProduct(
            "mercadolivre",
            "Mochila Notebook 15.6",
            "MLB4455667",
            price_brl=149.90,
            commission_pct=3.0,
            niche="carreira",
            keywords=["mochila", "notebook", "trabalho"],
            velocity_score=7.0,
        ),
    ],
    "shopee": [
        CuratedProduct(
            "shopee",
            "Fone Bluetooth Xiaomi",
            "123456789",
            shop_id="987654321",
            price_brl=89.90,
            commission_pct=5.0,
            niche="tecnologia",
            keywords=["fone", "xiaomi", "bluetooth"],
            velocity_score=9.0,
        ),
        CuratedProduct(
            "shopee",
            "Carregador Wireless",
            "234567890",
            shop_id="876543210",
            price_brl=49.90,
            commission_pct=6.0,
            niche="tecnologia",
            keywords=["carregador", "wireless", "carregamento"],
            velocity_score=9.0,
        ),
        CuratedProduct(
            "shopee",
            "Suporte Notebook Ajustavel",
            "345678901",
            shop_id="765432109",
            price_brl=69.90,
            commission_pct=5.0,
            niche="tecnologia",
            keywords=["suporte", "notebook", "ergonomico"],
            velocity_score=8.0,
        ),
        CuratedProduct(
            "shopee",
            "Capa Celular Personalizada",
            "456789012",
            shop_id="654321098",
            price_brl=19.90,
            commission_pct=7.0,
            niche="tecnologia",
            keywords=["capa", "celular", "protecao"],
            velocity_score=9.5,
        ),
        CuratedProduct(
            "shopee",
            "Organizador Mesa Escritorio",
            "567890123",
            shop_id="543210987",
            price_brl=39.90,
            commission_pct=6.0,
            niche="carreira",
            keywords=["organizador", "mesa", "escritorio"],
            velocity_score=8.5,
        ),
        CuratedProduct(
            "shopee",
            "Kit Canetas Coloridas",
            "678901234",
            shop_id="432109876",
            price_brl=15.90,
            commission_pct=8.0,
            niche="carreira",
            keywords=["canetas", "coloridas", "material"],
            velocity_score=9.0,
        ),
        CuratedProduct(
            "shopee",
            "Garrafa Squeeze Academia",
            "789012345",
            shop_id="321098765",
            price_brl=25.90,
            commission_pct=6.0,
            niche="saude",
            keywords=["garrafa", "squeeze", "academia"],
            velocity_score=8.5,
        ),
        CuratedProduct(
            "shopee",
            "Kit Resistencia Elastica",
            "890123456",
            shop_id="210987654",
            price_brl=35.90,
            commission_pct=5.0,
            niche="saude",
            keywords=["resistencia", "elastico", "treino"],
            velocity_score=8.0,
        ),
    ],
    "shein": [
        CuratedProduct(
            "shein",
            "Vestido Midi Floral",
            "10000001",
            price_brl=59.90,
            commission_pct=8.0,
            niche="carreira",
            keywords=["vestido", "midi", "floral", "feminino"],
            velocity_score=8.0,
        ),
        CuratedProduct(
            "shein",
            "Blusa Social Feminina",
            "10000002",
            price_brl=45.90,
            commission_pct=8.0,
            niche="carreira",
            keywords=["blusa", "social", "feminina", "trabalho"],
            velocity_score=8.5,
        ),
        CuratedProduct(
            "shein",
            "Calca Sarja Masculina",
            "10000003",
            price_brl=69.90,
            commission_pct=7.0,
            niche="carreira",
            keywords=["calca", "sarja", "masculina", "trabalho"],
            velocity_score=7.5,
        ),
        CuratedProduct(
            "shein",
            "Top Academia Feminino",
            "10000004",
            price_brl=29.90,
            commission_pct=9.0,
            niche="saude",
            keywords=["top", "academia", "feminino", "treino"],
            velocity_score=9.0,
        ),
        CuratedProduct(
            "shein",
            "Legging Compressao",
            "10000005",
            price_brl=49.90,
            commission_pct=8.0,
            niche="saude",
            keywords=["legging", "compressao", "academia"],
            velocity_score=8.5,
        ),
        CuratedProduct(
            "shein",
            "Tenis Casual Masculino",
            "10000006",
            price_brl=89.90,
            commission_pct=6.0,
            niche="tecnologia",
            keywords=["tenis", "casual", "masculino"],
            velocity_score=7.0,
        ),
    ],
    "aliexpress": [
        CuratedProduct(
            "aliexpress",
            "Mini Projetor Portatil",
            "1005001234567",
            price_brl=189.90,
            commission_pct=5.0,
            niche="tecnologia",
            keywords=["projetor", "portatil", "mini"],
            velocity_score=7.0,
        ),
        CuratedProduct(
            "aliexpress",
            "Fone TWS Xiaomi",
            "1005002345678",
            price_brl=79.90,
            commission_pct=5.0,
            niche="tecnologia",
            keywords=["fone", "tws", "xiaomi", "bluetooth"],
            velocity_score=8.5,
        ),
        CuratedProduct(
            "aliexpress",
            "Teclado Mecanico 60%",
            "1005003456789",
            price_brl=99.90,
            commission_pct=4.0,
            niche="tecnologia",
            keywords=["teclado", "mecanico", "60"],
            velocity_score=8.0,
        ),
        CuratedProduct(
            "aliexpress",
            "Caderno Inteligente Rocketbook",
            "1005004567890",
            price_brl=129.90,
            commission_pct=5.0,
            niche="carreira",
            keywords=["caderno", "inteligente", "reutilizavel"],
            velocity_score=7.5,
        ),
        CuratedProduct(
            "aliexpress",
            "Caneta Digital Tablet",
            "1005005678901",
            price_brl=39.90,
            commission_pct=6.0,
            niche="carreira",
            keywords=["caneta", "digital", "tablet", "stylus"],
            velocity_score=8.5,
        ),
        CuratedProduct(
            "aliexpress",
            "Relogio Smartwatch S8",
            "1005006789012",
            price_brl=149.90,
            commission_pct=4.0,
            niche="saude",
            keywords=["relogio", "smartwatch", "fitness"],
            velocity_score=7.5,
        ),
        CuratedProduct(
            "aliexpress",
            "Massageador Eletrico Portatil",
            "1005007890123",
            price_brl=59.90,
            commission_pct=6.0,
            niche="saude",
            keywords=["massageador", "eletrico", "portatil"],
            velocity_score=8.0,
        ),
    ],
}


def get_products_by_niche(niche: str) -> list[dict[str, Any]]:
    """Retorna todos os produtos curados de um nicho especifico."""
    results = []
    for platform, products in CURATED_PRODUCTS.items():
        for p in products:
            if p.niche == niche:
                platform_info = PLATFORM_LINK_PATTERNS.get(platform, {})
                url_example = platform_info.get("example_link", "")
                results.append(
                    {
                        "platform": platform,
                        "platform_name": platform_info.get("name", platform),
                        "product_name": p.product_name,
                        "product_id": p.product_id,
                        "price_brl": p.price_brl,
                        "commission_pct": p.commission_pct,
                        "keywords": p.keywords,
                        "niche": p.niche,
                        "velocity_score": p.velocity_score,
                        "signup_url": platform_info.get("signup_url", ""),
                        "link_example": url_example,
                    }
                )
    return results


def get_products_by_platform(platform: str) -> list[CuratedProduct]:
    """Retorna todos os produtos de uma plataforma."""
    return CURATED_PRODUCTS.get(platform, [])


def get_all_platforms() -> list[str]:
    """Retorna todas as plataformas disponiveis."""
    return list(CURATED_PRODUCTS.keys())
