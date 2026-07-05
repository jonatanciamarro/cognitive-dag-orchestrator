"""Módulo de afiliados — gestão de ofertas, links, tracking e redes."""

from __future__ import annotations
from pathlib import Path

import json
import threading
import sqlite3
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode, urlparse, urlunparse


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


# ── Modelos ───────────────────────────────────────────────────────────


@dataclass
class AffiliateOffer:
    """Uma oferta de afiliado disponível para promoção."""

    offer_id: str
    network: str  # amazon, hotmart, monetizze, awin, etc.
    product_name: str
    product_url: str
    commission_type: str  # percentage, fixed, tiered
    commission_value: float
    currency: str = "BRL"
    category: str = ""
    tags: list[str] = field(default_factory=list)
    description: str = ""
    merchant: str = ""
    cookie_days: int = 30
    is_active: bool = True
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AffiliateOffer":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AffiliateLink:
    """Link de afiliado com parâmetros de tracking."""

    link_id: str
    offer_id: str
    base_url: str
    tracked_url: str
    source: str = ""  # blog, youtube, newsletter, social
    content_id: str = ""  # id do artigo/vídeo/post
    campaign: str = ""
    created_at: str = field(default_factory=_utc_now)
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AffiliateLink":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ContentBrief:
    """Briefing de conteúdo gerado pelo planejador."""

    brief_id: str
    topic: str
    keyword: str
    content_type: str  # article, video, social_post, email
    target_audience: str = ""
    search_intent: str = ""
    offers: list[str] = field(default_factory=list)  # offer_ids
    outline: list[str] = field(default_factory=list)
    estimated_volume: int = 0
    difficulty: float = 0.0
    status: str = "draft"  # draft, approved, published
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContentBrief":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ── Rede de Afiliados Genérica ───────────────────────────────────────


class AffiliateNetwork:
    """Classe base para integração com redes de afiliados."""

    def __init__(self, name: str):
        self.name = name

    def build_link(self, offer: AffiliateOffer, **params: str) -> str:
        """Constroi URL de afiliado com parâmetros de tracking."""
        raise NotImplementedError


class AmazonAssociates(AffiliateNetwork):
    """Integração com Amazon Associates."""

    def __init__(self, tracking_id: str = ""):
        super().__init__("amazon")
        self.tracking_id = tracking_id

    def build_link(self, offer: AffiliateOffer, **params: str) -> str:
        tag = params.get("tag", self.tracking_id)
        url = offer.product_url
        parsed = urlparse(url)
        query = dict(
            pair.split("=", 1) for pair in parsed.query.split("&") if "=" in pair
        )
        if tag:
            query["tag"] = tag
        query["ref"] = "as_li_ss_tl"
        new_query = urlencode(query)
        return urlunparse(parsed._replace(query=new_query))


class Hotmart(AffiliateNetwork):
    """Integracao com Hotmart.

    NOTA: Hotmart nao tem ID fixo de afiliado.
    Cada produto gera um link UNICO contendo o parametro aff.
    O link completo (ja com ?aff=SEUCODIGO) deve vir da configuracao.
    """

    def __init__(self, affiliate_id: str = ""):
        super().__init__("hotmart")
        self.affiliate_id = affiliate_id

    def build_link(self, offer: AffiliateOffer, **params: str) -> str:
        """Retorna o URL completo com o parametro aff do afiliado."""
        from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

        url = offer.product_url or ""
        aff_id = params.get("affiliate_id", self.affiliate_id)

        if not url:
            if aff_id:
                return f"https://hotm.art/link?aff={aff_id}"
            return ""

        # Se a URL ja tem ?aff=..., retorna como esta
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "aff" in qs:
            return url

        # Adiciona o parametro aff a URL existente
        if aff_id:
            qs["aff"] = [aff_id]
            new_query = urlencode(qs, doseq=True)
            return urlunparse(parsed._replace(query=new_query))

        return url


class GenericAffiliate(AffiliateNetwork):
    """Rede genérica — usa parâmetros configuráveis."""

    def __init__(self, name: str = "generic", param_name: str = "ref"):
        super().__init__(name)
        self.param_name = param_name

    def build_link(self, offer: AffiliateOffer, **params: str) -> str:
        value = params.get(self.param_name, "")
        url = offer.product_url
        if value:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{self.param_name}={value}"
        return url


# ── Gerenciador de Ofertas ────────────────────────────────────────────


class OfferManager:
    """Gerencia o catálogo de ofertas de afiliados em SQLite."""

    def __init__(self, conn: Any):
        self._conn = conn
        self._lock = threading.Lock()
        self._ensure_schema()

    def _execute(self, sql: str, params=None):
        with self._lock:
            if params is not None:
                return self._conn.execute(sql, params)
            return self._conn.execute(sql)

    def _ensure_schema(self) -> None:
        self._execute("""CREATE TABLE IF NOT EXISTS affiliate_offers (
            offer_id TEXT PRIMARY KEY,
            network TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_url TEXT NOT NULL,
            commission_type TEXT NOT NULL DEFAULT 'percentage',
            commission_value REAL NOT NULL DEFAULT 0.0,
            currency TEXT NOT NULL DEFAULT 'BRL',
            category TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '[]',
            description TEXT NOT NULL DEFAULT '',
            merchant TEXT NOT NULL DEFAULT '',
            cookie_days INTEGER NOT NULL DEFAULT 30,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )""")
        self._execute(
            "CREATE INDEX IF NOT EXISTS idx_offers_network ON affiliate_offers(network)"
        )
        self._execute(
            "CREATE INDEX IF NOT EXISTS idx_offers_category ON affiliate_offers(category)"
        )
        self._execute("""CREATE TABLE IF NOT EXISTS affiliate_links (
            link_id TEXT PRIMARY KEY,
            offer_id TEXT NOT NULL REFERENCES affiliate_offers(offer_id),
            base_url TEXT NOT NULL,
            tracked_url TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT '',
            content_id TEXT NOT NULL DEFAULT '',
            campaign TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            clicks INTEGER NOT NULL DEFAULT 0,
            conversions INTEGER NOT NULL DEFAULT 0,
            revenue REAL NOT NULL DEFAULT 0.0
        )""")
        self._execute(
            "CREATE INDEX IF NOT EXISTS idx_links_offer ON affiliate_links(offer_id)"
        )
        self._execute(
            "CREATE INDEX IF NOT EXISTS idx_links_content ON affiliate_links(content_id)"
        )
        self._execute("""CREATE TABLE IF NOT EXISTS content_briefs (
            brief_id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            keyword TEXT NOT NULL,
            content_type TEXT NOT NULL DEFAULT 'article',
            target_audience TEXT NOT NULL DEFAULT '',
            search_intent TEXT NOT NULL DEFAULT '',
            offers TEXT NOT NULL DEFAULT '[]',
            outline TEXT NOT NULL DEFAULT '[]',
            estimated_volume INTEGER NOT NULL DEFAULT 0,
            difficulty REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TEXT NOT NULL
        )""")
        self._execute(
            "CREATE INDEX IF NOT EXISTS idx_briefs_status ON content_briefs(status)"
        )
        self._execute("""CREATE TABLE IF NOT EXISTS affiliate_events (
            event_id TEXT PRIMARY KEY,
            link_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            metadata TEXT NOT NULL DEFAULT '{}'
        )""")
        self._execute(
            "CREATE INDEX IF NOT EXISTS idx_events_link ON affiliate_events(link_id)"
        )

    # ── Ofertas ──────────────────────────────────────────────────────

    def register_offer(self, offer: AffiliateOffer) -> str:
        existing = self._execute(
            "SELECT offer_id FROM affiliate_offers WHERE offer_id = ?",
            (offer.offer_id,),
        ).fetchone()
        if existing:
            return existing[0]
        data = offer.to_dict()
        data["tags"] = json.dumps(data.get("tags", []))
        self._execute(
            """INSERT INTO affiliate_offers
               (offer_id, network, product_name, product_url, commission_type,
                commission_value, currency, category, tags, description,
                merchant, cookie_days, is_active, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["offer_id"],
                data["network"],
                data["product_name"],
                data["product_url"],
                data["commission_type"],
                data["commission_value"],
                data["currency"],
                data["category"],
                data["tags"],
                data["description"],
                data["merchant"],
                data["cookie_days"],
                int(data["is_active"]),
                data["created_at"],
            ),
        )
        self._conn.commit()
        return offer.offer_id

    def get_offer(self, offer_id: str) -> AffiliateOffer | None:
        row = self._execute(
            "SELECT * FROM affiliate_offers WHERE offer_id = ?", (offer_id,)
        ).fetchone()
        if row is None:
            return None
        data = dict(row)
        data["tags"] = json.loads(data["tags"])
        data["is_active"] = bool(data["is_active"])
        return AffiliateOffer.from_dict(data)

    def list_offers(
        self,
        network: str | None = None,
        category: str | None = None,
        active_only: bool = True,
    ) -> list[AffiliateOffer]:
        clauses: list[str] = []
        params: list[Any] = []
        if network:
            clauses.append("network = ?")
            params.append(network)
        if category:
            clauses.append("category = ?")
            params.append(category)
        if active_only:
            clauses.append("is_active = 1")
        where = " AND ".join(clauses) if clauses else "1=1"
        rows = self._execute(
            f"SELECT * FROM affiliate_offers WHERE {where} ORDER BY product_name",
            params,
        ).fetchall()
        results = []
        for r in rows:
            data = dict(r)
            data["tags"] = json.loads(data["tags"])
            data["is_active"] = bool(data["is_active"])
            results.append(AffiliateOffer.from_dict(data))
        return results

    # ── Links ────────────────────────────────────────────────────────

    def create_link(
        self,
        offer: AffiliateOffer,
        network: AffiliateNetwork,
        source: str = "",
        content_id: str = "",
        campaign: str = "",
        **tracking_params: str,
    ) -> AffiliateLink:
        tracked = network.build_link(offer, **tracking_params)
        link = AffiliateLink(
            link_id=_new_id(),
            offer_id=offer.offer_id,
            base_url=offer.product_url,
            tracked_url=tracked,
            source=source,
            content_id=content_id,
            campaign=campaign,
        )
        data = link.to_dict()
        self._execute(
            """INSERT INTO affiliate_links
               (link_id, offer_id, base_url, tracked_url, source, content_id,
                campaign, created_at, clicks, conversions, revenue)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["link_id"],
                data["offer_id"],
                data["base_url"],
                data["tracked_url"],
                data["source"],
                data["content_id"],
                data["campaign"],
                data["created_at"],
                data["clicks"],
                data["conversions"],
                data["revenue"],
            ),
        )
        self._conn.commit()
        return link

    def get_links_for_content(self, content_id: str) -> list[AffiliateLink]:
        rows = self._execute(
            "SELECT * FROM affiliate_links WHERE content_id = ? ORDER BY created_at",
            (content_id,),
        ).fetchall()
        return [AffiliateLink.from_dict(dict(r)) for r in rows]

    def track_click(self, link_id: str, metadata: dict[str, Any] | None = None) -> None:
        self._execute(
            "UPDATE affiliate_links SET clicks = clicks + 1 WHERE link_id = ?",
            (link_id,),
        )
        self._execute(
            "INSERT INTO affiliate_events (event_id, link_id, event_type, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
            (_new_id(), link_id, "click", _utc_now(), json.dumps(metadata or {})),
        )
        self._conn.commit()

    def track_conversion(
        self, link_id: str, revenue: float = 0.0, metadata: dict[str, Any] | None = None
    ) -> None:
        self._execute(
            "UPDATE affiliate_links SET conversions = conversions + 1, revenue = revenue + ? WHERE link_id = ?",
            (revenue, link_id),
        )
        self._execute(
            "INSERT INTO affiliate_events (event_id, link_id, event_type, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
            (_new_id(), link_id, "conversion", _utc_now(), json.dumps(metadata or {})),
        )
        self._conn.commit()

    # ── Briefings ────────────────────────────────────────────────────

    def save_brief(self, brief: ContentBrief) -> str:
        data = brief.to_dict()
        data["offers"] = json.dumps(data.get("offers", []))
        data["outline"] = json.dumps(data.get("outline", []))
        self._execute(
            """INSERT OR REPLACE INTO content_briefs
               (brief_id, topic, keyword, content_type, target_audience,
                search_intent, offers, outline, estimated_volume,
                difficulty, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["brief_id"],
                data["topic"],
                data["keyword"],
                data["content_type"],
                data["target_audience"],
                data["search_intent"],
                data["offers"],
                data["outline"],
                data["estimated_volume"],
                data["difficulty"],
                data["status"],
                data["created_at"],
            ),
        )
        self._conn.commit()
        return brief.brief_id

    def list_briefs(self, status: str | None = None) -> list[ContentBrief]:
        if status:
            rows = self._execute(
                "SELECT * FROM content_briefs WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = self._execute(
                "SELECT * FROM content_briefs ORDER BY created_at DESC"
            ).fetchall()
        results = []
        for r in rows:
            data = dict(r)
            data["offers"] = json.loads(data["offers"])
            data["outline"] = json.loads(data["outline"])
            results.append(ContentBrief.from_dict(data))
        return results

    # ── Métricas de afiliado ──────────────────────────────────────────

    def get_affiliate_metrics(self) -> dict[str, Any]:
        """Retorna métricas agregadas de performance de afiliados."""
        total_clicks = self._execute(
            "SELECT COALESCE(SUM(clicks), 0) AS total FROM affiliate_links"
        ).fetchone()["total"]
        total_conversions = self._execute(
            "SELECT COALESCE(SUM(conversions), 0) AS total FROM affiliate_links"
        ).fetchone()["total"]
        total_revenue = self._execute(
            "SELECT COALESCE(SUM(revenue), 0) AS total FROM affiliate_links"
        ).fetchone()["total"]
        conversion_rate = (
            (total_conversions / total_clicks * 100) if total_clicks > 0 else 0.0
        )
        top_offers = self._execute(
            """SELECT o.product_name, SUM(l.clicks) AS clicks, SUM(l.conversions) AS conversions,
                      SUM(l.revenue) AS revenue
               FROM affiliate_links l
               JOIN affiliate_offers o ON l.offer_id = o.offer_id
               GROUP BY l.offer_id
               ORDER BY revenue DESC LIMIT 5"""
        ).fetchall()
        return {
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_revenue": round(total_revenue, 2),
            "conversion_rate": round(conversion_rate, 2),
            "top_offers": [dict(r) for r in top_offers],
        }

# ── Product Link Registry ─────────────────────────────────────────────
# Resolve o problema: cada produto tem link de afiliado UNICO por usuario.
# Plataformas como Hotmart, Kiwify, Eduzz nao possuem ID fixo de afiliado.
# Cada produto gera um link individual contendo o codigo do afiliado.
# Exemplo: https://go.hotmart.com/PRODUTO?aff=SEUCODIGO
# Exemplo: https://pay.kiwify.com.br/PRODUTO?aff=SEUCODIGO
#
# O usuario registra manualmente o link real de cada produto que promove.
# O sistema prefere o link registrado ao link generico do config.


class ProductLinkRegistry:
    """Registro de links de afiliado REAIS por produto.

    Cada produto tem um link unico por usuario na maioria das plataformas
    (Hotmart, Kiwify, Eduzz, etc). Este registro armazena esses links
    para que o sistema use os links corretos em vez de placeholders.

    Para plataformas com tag unica (Amazon Associates), o sistema
    continua usando o metodo atual via AMAZON_ASSOCIATES_TAG.
    """

    _DB_PATH = Path(__file__).resolve().parent.parent.parent / ".state" / "product_links.db"
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._conn = sqlite3.connect(str(self._DB_PATH))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._init_db()

    def _init_db(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS product_links (
                link_id TEXT PRIMARY KEY,
                network TEXT NOT NULL,
                product_name TEXT NOT NULL,
                affiliate_link TEXT NOT NULL,
                category TEXT DEFAULT '',
                status TEXT DEFAULT 'active',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_pl_network ON product_links(network);
            CREATE INDEX IF NOT EXISTS idx_pl_status ON product_links(status);
        """)
        self._conn.commit()

    # ── CRUD ────────────────────────────────────────────────────────

    def register(self, network: str, product_name: str,
                 affiliate_link: str, category: str = "",
                 notes: str = "") -> str:
        """Registra um link de afiliado real para um produto."""
        link_id = _new_id()
        now = _utc_now()
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO product_links
                   (link_id, network, product_name, affiliate_link,
                    category, status, notes, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?)""",
                (link_id, network, product_name, affiliate_link,
                 category, notes, now, now),
            )
            self._conn.commit()
        return link_id

    def get_link(self, product_name: str, network: str = "") -> dict | None:
        """Busca link registrado pelo nome do produto."""
        with self._lock:
            if network:
                row = self._conn.execute(
                    "SELECT * FROM product_links WHERE product_name = ? AND network = ? AND status = 'active'",
                    (product_name, network),
                ).fetchone()
            else:
                row = self._conn.execute(
                    "SELECT * FROM product_links WHERE product_name = ? AND status = 'active'",
                    (product_name,),
                ).fetchone()
        return dict(row) if row else None

    def get_links_by_network(self, network: str) -> list[dict]:
        """Lista todos os links registrados para uma rede."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM product_links WHERE network = ? AND status = 'active' ORDER BY product_name",
                (network,),
            ).fetchall()
        return [dict(r) for r in rows]

    def list_all(self, status: str = "active") -> list[dict]:
        """Lista todos os links registrados."""
        with self._lock:
            if status == "all":
                rows = self._conn.execute(
                    "SELECT * FROM product_links ORDER BY network, product_name"
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT * FROM product_links WHERE status = ? ORDER BY network, product_name",
                    (status,),
                ).fetchall()
        return [dict(r) for r in rows]

    def unregister(self, link_id: str) -> bool:
        """Marca um link como inativo."""
        with self._lock:
            self._conn.execute(
                "UPDATE product_links SET status = 'inactive', updated_at = ? WHERE link_id = ?",
                (_utc_now(), link_id),
            )
            self._conn.commit()
        return True

    def update_link(self, link_id: str, affiliate_link: str) -> bool:
        """Atualiza o link de afiliado de um produto."""
        with self._lock:
            self._conn.execute(
                "UPDATE product_links SET affiliate_link = ?, updated_at = ? WHERE link_id = ?",
                (affiliate_link, _utc_now(), link_id),
            )
            self._conn.commit()
        return True

    def get_stats(self) -> dict:
        """Estatisticas do registro."""
        with self._lock:
            total = self._conn.execute(
                "SELECT COUNT(*) AS c FROM product_links WHERE status = 'active'"
            ).fetchone()["c"]
            by_network = self._conn.execute(
                "SELECT network, COUNT(*) AS c FROM product_links WHERE status = 'active' GROUP BY network"
            ).fetchall()
            last_added = self._conn.execute(
                "SELECT product_name, network, created_at FROM product_links ORDER BY created_at DESC LIMIT 5"
            ).fetchall()
        return {
            "total_active": total,
            "by_network": {r["network"]: r["c"] for r in by_network},
            "recently_added": [dict(r) for r in last_added],
        }

    # ── Integracao com OfferLookup ───────────────────────────────────

    def resolve_link(self, product_name: str, network: str,
                     default_url: str = "") -> str:
        """Resolve o melhor link para um produto.

        Prioridade:
        1. Link registrado manualmente no ProductLinkRegistry
        2. Link configurado no affiliate_offers.json (default_url)
        3. String vazia se nada disponivel
        """
        registered = self.get_link(product_name, network)
        if registered and registered.get("affiliate_link"):
            return registered["affiliate_link"]
        return default_url
