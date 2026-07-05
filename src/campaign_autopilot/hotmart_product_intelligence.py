"""Hotmart Product Intelligence — Memoria e modelo de dados do protocolo.

Schema completo para o Product Intelligence Package:
  discovery → triage → scoring → diligence → affiliation → assets → normalization → ingestion → enrichment → activation

Ponytail: stdlib-only, sqlite3 WAL, dataclasses.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


# ═══════════════════════════════════════════════════════════════
# ENUMS / CONSTANTS
# ═══════════════════════════════════════════════════════════════

class ProductStatus(Enum):
    DISCOVERED = "discovered"
    TRIAGED = "triaged"
    SCORED = "scored"
    DILIGENCED = "diligenced"
    AFFILIATED = "affiliated"
    ASSETS_COLLECTED = "assets_collected"
    NORMALIZED = "normalized"
    INGESTED = "ingested"
    ENRICHED = "enriched"
    ACTIVATED = "activated"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class TriageVerdict(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"  # needs human review


class OpportunityTier(Enum):
    DIAMOND = "diamond"       # 85-100
    GOLD = "gold"             # 70-84
    SILVER = "silver"         # 50-69
    BRONZE = "bronze"         # 30-49
    LOW = "low"               # 0-29


# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

@dataclass
class HotmartProduct:
    """Produto do marketplace Hotmart coletado na Fase 1."""
    product_id: str
    name: str
    category: str = ""
    subcategory: str = ""
    producer: str = ""
    producer_id: str = ""
    price: float = 0.0
    commission_value: float = 0.0
    commission_pct: float = 0.0
    cookie_days: int = 7
    language: str = "pt"
    country: str = "BR"
    temperature: str = ""  # frio/morno/quente
    description: str = ""
    sales_page_url: str = ""
    last_updated: str = ""
    affiliate_link: str = ""
    checkout_url: str = ""
    vsl_url: str = ""
    upsell_url: str = ""
    discovered_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TriageResult:
    """Resultado da triagem inicial (Fase 2)."""
    product_id: str
    verdict: str  # TriageVerdict value
    issues: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    triaged_at: str = ""


@dataclass
class OpportunityScore:
    """Score de oportunidade (Fase 3)."""
    product_id: str
    total_score: float = 0.0
    market_potential: float = 0.0     # peso 25%
    commission_score: float = 0.0      # peso 15%
    conversion_score: float = 0.0      # peso 20%
    materials_score: float = 0.0       # peso 20%
    compatibility_score: float = 0.0   # peso 20%
    tier: str = ""  # OpportunityTier value
    scored_at: str = ""


@dataclass
class DueDiligenceReport:
    """Due diligence (Fase 4)."""
    product_id: str
    sales_page_score: float = 0.0
    sales_page_issues: list[str] = field(default_factory=list)
    digital_presence_score: float = 0.0
    digital_presence_notes: list[str] = field(default_factory=list)
    producer_score: float = 0.0
    producer_notes: list[str] = field(default_factory=list)
    overall_verdict: str = ""
    diligenced_at: str = ""


@dataclass
class AffiliationRecord:
    """Registro de afiliacao (Fase 5)."""
    product_id: str
    affiliate_id: str = ""
    affiliate_link: str = ""
    approved: bool = False
    approval_date: str = ""
    commission_terms: str = ""
    affiliated_at: str = ""


@dataclass
class ProductAssetCollection:
    """Ativos coletados (Fase 6)."""
    product_id: str
    images: list[str] = field(default_factory=list)
    banners: list[str] = field(default_factory=list)
    videos: list[str] = field(default_factory=list)
    logos: list[str] = field(default_factory=list)
    mockups: list[str] = field(default_factory=list)
    emails: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    copies: list[str] = field(default_factory=list)
    ads: list[str] = field(default_factory=list)
    faq: list[dict] = field(default_factory=list)
    links: dict[str, str] = field(default_factory=dict)  # affiliate, checkout, sales_page, vsl, upsell
    collected_at: str = ""


@dataclass
class ProductNormalized:
    """Produto normalizado (Fase 7)."""
    product_id: str
    name: str
    category: str
    price: float
    commission: float
    affiliate_link: str
    sales_page: str
    target_audience: str = ""
    pain_points: list[str] = field(default_factory=list)
    benefits: list[str] = field(default_factory=list)
    objections: list[str] = field(default_factory=list)
    normalized_at: str = ""


@dataclass
class ProductIntelligence:
    """Conhecimento extraido (Fase 8-9)."""
    product_id: str
    avatar: dict = field(default_factory=dict)       # quem compra, idade, objetivos, dores
    offer: dict = field(default_factory=dict)         # promessa, mecanismo, transformacao, urgencia
    language: dict = field(default_factory=dict)      # tom, vocabulario, argumentacao
    buyer_personas: list[dict] = field(default_factory=list)
    market_map: dict = field(default_factory=dict)
    competitor_map: list[dict] = field(default_factory=list)
    pain_map: list[dict] = field(default_factory=list)
    objection_map: list[dict] = field(default_factory=list)
    offer_map: dict = field(default_factory=dict)
    enriched_at: str = ""


@dataclass
class HotmartProductDossier:
    """Dossie operacional completo — output final do protocolo."""
    product: HotmartProduct | None = None
    triage: TriageResult | None = None
    score: OpportunityScore | None = None
    diligence: DueDiligenceReport | None = None
    affiliation: AffiliationRecord | None = None
    assets: ProductAssetCollection | None = None
    normalized: ProductNormalized | None = None
    intelligence: ProductIntelligence | None = None
    dossier_created_at: str = ""
    status: str = ""


# ═══════════════════════════════════════════════════════════════
# PRODUCT INTELLIGENCE STORE (SQLite WAL)
# ═══════════════════════════════════════════════════════════════

class ProductIntelligenceStore:
    """SQLite WAL store para todo o pipeline Hotmart.

    Schema unificado que armazena cada fase como tabela separada.
    Thread-safe via Lock.
    """

    def __init__(self, path: str | Path = ":memory:"):
        self.path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._lock:
            cur = self._conn.cursor()
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT DEFAULT '',
                    subcategory TEXT DEFAULT '',
                    producer TEXT DEFAULT '',
                    producer_id TEXT DEFAULT '',
                    price REAL DEFAULT 0,
                    commission_value REAL DEFAULT 0,
                    commission_pct REAL DEFAULT 0,
                    cookie_days INTEGER DEFAULT 7,
                    language TEXT DEFAULT 'pt',
                    country TEXT DEFAULT 'BR',
                    temperature TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    sales_page_url TEXT DEFAULT '',
                    affiliate_link TEXT DEFAULT '',
                    checkout_url TEXT DEFAULT '',
                    vsl_url TEXT DEFAULT '',
                    upsell_url TEXT DEFAULT '',
                    status TEXT DEFAULT 'discovered',
                    discovered_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS triage_results (
                    product_id TEXT PRIMARY KEY,
                    verdict TEXT NOT NULL,
                    issues TEXT DEFAULT '[]',
                    reasons TEXT DEFAULT '[]',
                    triaged_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS opportunity_scores (
                    product_id TEXT PRIMARY KEY,
                    total_score REAL DEFAULT 0,
                    market_potential REAL DEFAULT 0,
                    commission_score REAL DEFAULT 0,
                    conversion_score REAL DEFAULT 0,
                    materials_score REAL DEFAULT 0,
                    compatibility_score REAL DEFAULT 0,
                    tier TEXT DEFAULT '',
                    scored_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS due_diligence (
                    product_id TEXT PRIMARY KEY,
                    sales_page_score REAL DEFAULT 0,
                    sales_page_issues TEXT DEFAULT '[]',
                    digital_presence_score REAL DEFAULT 0,
                    digital_presence_notes TEXT DEFAULT '[]',
                    producer_score REAL DEFAULT 0,
                    producer_notes TEXT DEFAULT '[]',
                    overall_verdict TEXT DEFAULT '',
                    diligenced_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS affiliations (
                    product_id TEXT PRIMARY KEY,
                    affiliate_id TEXT DEFAULT '',
                    affiliate_link TEXT DEFAULT '',
                    approved INTEGER DEFAULT 0,
                    approval_date TEXT DEFAULT '',
                    commission_terms TEXT DEFAULT '',
                    affiliated_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS assets (
                    product_id TEXT PRIMARY KEY,
                    images TEXT DEFAULT '[]',
                    banners TEXT DEFAULT '[]',
                    videos TEXT DEFAULT '[]',
                    logos TEXT DEFAULT '[]',
                    mockups TEXT DEFAULT '[]',
                    emails TEXT DEFAULT '[]',
                    scripts TEXT DEFAULT '[]',
                    copies TEXT DEFAULT '[]',
                    ads TEXT DEFAULT '[]',
                    faq TEXT DEFAULT '[]',
                    links TEXT DEFAULT '{}',
                    collected_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS normalized_products (
                    product_id TEXT PRIMARY KEY,
                    name TEXT DEFAULT '',
                    category TEXT DEFAULT '',
                    price REAL DEFAULT 0,
                    commission REAL DEFAULT 0,
                    affiliate_link TEXT DEFAULT '',
                    sales_page TEXT DEFAULT '',
                    target_audience TEXT DEFAULT '',
                    pain_points TEXT DEFAULT '[]',
                    benefits TEXT DEFAULT '[]',
                    objections TEXT DEFAULT '[]',
                    normalized_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS product_intelligence (
                    product_id TEXT PRIMARY KEY,
                    avatar TEXT DEFAULT '{}',
                    offer TEXT DEFAULT '{}',
                    language TEXT DEFAULT '{}',
                    buyer_personas TEXT DEFAULT '[]',
                    market_map TEXT DEFAULT '{}',
                    competitor_map TEXT DEFAULT '[]',
                    pain_map TEXT DEFAULT '[]',
                    objection_map TEXT DEFAULT '[]',
                    offer_map TEXT DEFAULT '{}',
                    enriched_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS dossiers (
                    product_id TEXT PRIMARY KEY,
                    dossier TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT (datetime('now'))
                );
            """)
            self._conn.commit()

    # ── Product CRUD ──
    def upsert_product(self, p: HotmartProduct) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT INTO products (product_id, name, category, subcategory, producer,
                    producer_id, price, commission_value, commission_pct, cookie_days,
                    language, country, temperature, description, sales_page_url,
                    affiliate_link, checkout_url, vsl_url, upsell_url, status, discovered_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'discovered',datetime('now'))
                ON CONFLICT(product_id) DO UPDATE SET
                    name=excluded.name, price=excluded.price, commission_value=excluded.commission_value,
                    temperature=excluded.temperature, updated_at=datetime('now')
            """, (p.product_id, p.name, p.category, p.subcategory, p.producer,
                  p.producer_id, p.price, p.commission_value, p.commission_pct, p.cookie_days,
                  p.language, p.country, p.temperature, p.description, p.sales_page_url,
                  p.affiliate_link, p.checkout_url, p.vsl_url, p.upsell_url))
            self._conn.commit()

    def get_product(self, product_id: str) -> HotmartProduct | None:
        row = self._conn.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone()
        if not row:
            return None
        return HotmartProduct(
            product_id=row[0], name=row[1], category=row[2], subcategory=row[3],
            producer=row[4], producer_id=row[5], price=row[6], commission_value=row[7],
            commission_pct=row[8], cookie_days=row[9], language=row[10], country=row[11],
            temperature=row[12], description=row[13], sales_page_url=row[14],
            affiliate_link=row[15], checkout_url=row[16], vsl_url=row[17], upsell_url=row[18],
            discovered_at=row[20] if len(row) > 20 else "",
        )

    def list_products(self, status: str | None = None) -> list[HotmartProduct]:
        if status:
            rows = self._conn.execute("SELECT * FROM products WHERE status=?", (status,)).fetchall()
        else:
            rows = self._conn.execute("SELECT * FROM products ORDER BY discovered_at DESC").fetchall()
        return [HotmartProduct(
            product_id=r[0], name=r[1], category=r[2], subcategory=r[3],
            producer=r[4], producer_id=r[5], price=r[6], commission_value=r[7],
            commission_pct=r[8], cookie_days=r[9], language=r[10], country=r[11],
            temperature=r[12], description=r[13], sales_page_url=r[14],
            affiliate_link=r[15], checkout_url=r[16], vsl_url=r[17], upsell_url=r[18],
        ) for r in rows]

    def update_status(self, product_id: str, status: str) -> None:
        with self._lock:
            self._conn.execute("UPDATE products SET status=?, updated_at=datetime('now') WHERE product_id=?",
                             (status, product_id))
            self._conn.commit()

    # ── Phase storage ──
    def save_triage(self, t: TriageResult) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT INTO triage_results (product_id, verdict, issues, reasons, triaged_at)
                VALUES (?,?,?,?,datetime('now'))
                ON CONFLICT(product_id) DO UPDATE SET verdict=excluded.verdict, triaged_at=datetime('now')
            """, (t.product_id, t.verdict, json.dumps(t.issues), json.dumps(t.reasons)))
            self._conn.commit()

    def save_score(self, s: OpportunityScore) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT INTO opportunity_scores (product_id, total_score, market_potential,
                    commission_score, conversion_score, materials_score, compatibility_score, tier, scored_at)
                VALUES (?,?,?,?,?,?,?,?,datetime('now'))
                ON CONFLICT(product_id) DO UPDATE SET total_score=excluded.total_score, tier=excluded.tier
            """, (s.product_id, s.total_score, s.market_potential, s.commission_score,
                  s.conversion_score, s.materials_score, s.compatibility_score, s.tier))
            self._conn.commit()

    def save_diligence(self, d: DueDiligenceReport) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT INTO due_diligence (product_id, sales_page_score, sales_page_issues,
                    digital_presence_score, digital_presence_notes, producer_score,
                    producer_notes, overall_verdict, diligenced_at)
                VALUES (?,?,?,?,?,?,?,?,datetime('now'))
                ON CONFLICT(product_id) DO UPDATE SET overall_verdict=excluded.overall_verdict
            """, (d.product_id, d.sales_page_score, json.dumps(d.sales_page_issues),
                  d.digital_presence_score, json.dumps(d.digital_presence_notes),
                  d.producer_score, json.dumps(d.producer_notes), d.overall_verdict))
            self._conn.commit()

    def save_affiliation(self, a: AffiliationRecord) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT INTO affiliations (product_id, affiliate_id, affiliate_link, approved, approval_date, commission_terms, affiliated_at)
                VALUES (?,?,?,?,?,?,datetime('now'))
                ON CONFLICT(product_id) DO UPDATE SET approved=excluded.approved
            """, (a.product_id, a.affiliate_id, a.affiliate_link, int(a.approved), a.approval_date, a.commission_terms))
            self._conn.commit()

    def save_assets(self, a: ProductAssetCollection) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT INTO assets (product_id, images, banners, videos, logos, mockups,
                    emails, scripts, copies, ads, faq, links, collected_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
                ON CONFLICT(product_id) DO UPDATE SET collected_at=datetime('now')
            """, (a.product_id, json.dumps(a.images), json.dumps(a.banners), json.dumps(a.videos),
                  json.dumps(a.logos), json.dumps(a.mockups), json.dumps(a.emails),
                  json.dumps(a.scripts), json.dumps(a.copies), json.dumps(a.ads),
                  json.dumps(a.faq), json.dumps(a.links)))
            self._conn.commit()

    def save_normalized(self, n: ProductNormalized) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT INTO normalized_products (product_id, name, category, price, commission,
                    affiliate_link, sales_page, target_audience, pain_points, benefits, objections, normalized_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
                ON CONFLICT(product_id) DO UPDATE SET normalized_at=datetime('now')
            """, (n.product_id, n.name, n.category, n.price, n.commission,
                  n.affiliate_link, n.sales_page, n.target_audience,
                  json.dumps(n.pain_points), json.dumps(n.benefits), json.dumps(n.objections)))
            self._conn.commit()

    def save_intelligence(self, i: ProductIntelligence) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT INTO product_intelligence (product_id, avatar, offer, language,
                    buyer_personas, market_map, competitor_map, pain_map, objection_map, offer_map, enriched_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,datetime('now'))
                ON CONFLICT(product_id) DO UPDATE SET enriched_at=datetime('now')
            """, (i.product_id, json.dumps(i.avatar), json.dumps(i.offer), json.dumps(i.language),
                  json.dumps(i.buyer_personas), json.dumps(i.market_map), json.dumps(i.competitor_map),
                  json.dumps(i.pain_map), json.dumps(i.objection_map), json.dumps(i.offer_map)))
            self._conn.commit()

    def save_dossier(self, product_id: str, dossier: dict) -> None:
        with self._lock:
            self._conn.execute("""
                INSERT INTO dossiers (product_id, dossier, created_at)
                VALUES (?,?,datetime('now'))
                ON CONFLICT(product_id) DO UPDATE SET dossier=excluded.dossier
            """, (product_id, json.dumps(dossier)))
            self._conn.commit()

    def get_dossier(self, product_id: str) -> dict | None:
        row = self._conn.execute("SELECT dossier FROM dossiers WHERE product_id=?", (product_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def stats(self) -> dict:
        """Estatisticas do pipeline."""
        cur = self._conn.cursor()
        total = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        by_status = dict(cur.execute(
            "SELECT status, COUNT(*) FROM products GROUP BY status"
        ).fetchall())
        return {
            "total_products": total,
            "by_status": by_status,
            "triaged": cur.execute("SELECT COUNT(*) FROM triage_results").fetchone()[0],
            "scored": cur.execute("SELECT COUNT(*) FROM opportunity_scores").fetchone()[0],
            "diligenced": cur.execute("SELECT COUNT(*) FROM due_diligence").fetchone()[0],
            "affiliated": cur.execute("SELECT COUNT(*) FROM affiliations").fetchone()[0],
            "normalized": cur.execute("SELECT COUNT(*) FROM normalized_products").fetchone()[0],
            "enriched": cur.execute("SELECT COUNT(*) FROM product_intelligence").fetchone()[0],
            "dossiers": cur.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0],
        }

    def close(self) -> None:
        self._conn.close()
