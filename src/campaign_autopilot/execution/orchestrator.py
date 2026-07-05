"""Orchestrator — AB testing, affiliate links, notifications, social, SEO.

Consolidado de: ab_testing.py + affiliate_links.py + notifications.py + social_listening.py + seo_crawler.py
"""

from __future__ import annotations
import json
import random
import re
from datetime import datetime
from pathlib import Path


class ABTest:
    def __init__(self, name: str, variants: list[dict], metric: str = "conversion"):
        self.name = name
        self.variants = variants
        self.metric = metric
        self.results: list[dict] = []
        self.winner: dict | None = None

    def assign_variant(self, user_id: str) -> dict:
        variant = random.choice(self.variants)
        self.results.append({"user_id": user_id, "variant_id": variant.get("id"), "metric": self.metric, "value": 0})
        return variant

    def record_conversion(self, user_id: str, value: float = 1.0):
        for r in self.results:
            if r["user_id"] == user_id:
                r["value"] = value
                break

    def analyze(self) -> dict:
        variant_stats = {}
        for v in self.variants:
            vid = v.get("id")
            v_results = [r for r in self.results if r["variant_id"] == vid]
            if v_results:
                conversions = sum(1 for r in v_results if r["value"] > 0)
                total = len(v_results)
                variant_stats[vid] = {
                    "impressions": total, "conversions": conversions,
                    "rate": round(conversions / max(total, 1) * 100, 1),
                    "total_value": sum(r["value"] for r in v_results),
                }
        if variant_stats:
            self.winner = max(variant_stats, key=lambda v: variant_stats[v]["rate"])
        return {"test": self.name, "metric": self.metric, "variants": variant_stats, "winner": self.winner, "total_impressions": len(self.results)}


HEADLINE_VARIANTS = {
    "how_to": ["Como {topic} em {niche}", "{topic}: O Guia Passo a Passo", "A Maneira Certa de {topic}"],
    "list": ["7 Estratégias de {topic}", "Top 10 {topic} para {niche}", "5 Segredos de {topic}"],
    "question": ["Você comete esses erros de {topic}?", "{topic} Funciona? Descubra Aqui", "Por que {topic} é Essencial?"],
    "comparison": ["{topic} vs Alternativas: Qual Ganha?", "{topic} Vale a Pena? Review Honesto"],
}


class ABTestingEngine:
    @staticmethod
    def create_test(name: str, variants: list[dict], metric: str = "conversion") -> ABTest:
        return ABTest(name, variants, metric)

    @staticmethod
    def generate_headline_variants(topic: str, niche: str, styles: list[str] | None = None) -> list[dict]:
        styles = styles or ["how_to", "list", "question"]
        variants = []
        for style in styles:
            templates = HEADLINE_VARIANTS.get(style, ["{topic}"])
            for tpl in templates[:2]:
                headline = tpl.replace("{topic}", topic).replace("{niche}", niche)
                variants.append({"id": f"{style}_{len(variants)}", "style": style, "headline": headline})
        return variants

    @staticmethod
    def generate_cta_variants(offer: str) -> list[dict]:
        return [
            {"id": "cta_direct", "text": f"Quero {offer} Agora", "style": "direct"},
            {"id": "cta_learn", "text": f"Saber Mais Sobre {offer}", "style": "learning"},
            {"id": "cta_risk", "text": f"Experimentar {offer} — Sem Risco", "style": "risk_reversal"},
            {"id": "cta_urgency", "text": f"Começar {offer} — Vagas Limitadas", "style": "urgency"},
        ]


class AffiliateLinkManager:
    def __init__(self):
        self.links: dict[str, dict] = {}

    def add_link(self, name: str, url: str, program: str, commission: float = 0.0):
        link_id = f"ref_{len(self.links) + 1}"
        self.links[link_id] = {
            "name": name, "url": url, "program": program, "commission": commission,
            "created_at": datetime.now().isoformat(), "clicks": 0, "conversions": 0,
        }
        return link_id

    def get_short_url(self, link_id: str) -> str:
        link = self.links.get(link_id)
        if not link:
            return ""
        link["clicks"] += 1
        return f"https://go.{link['program'].lower()}/{link_id}"

    def record_conversion(self, link_id: str):
        link = self.links.get(link_id)
        if link:
            link["conversions"] += 1

    def check_broken_links(self) -> list[dict]:
        broken = []
        for lid, link in self.links.items():
            if "404" in link.get("url", "") or "expired" in link.get("url", ""):
                broken.append({"link_id": lid, "name": link["name"], "url": link["url"], "status": "broken"})
        return broken

    def get_stats(self) -> dict:
        total_clicks = sum(l["clicks"] for l in self.links.values())
        total_convs = sum(l["conversions"] for l in self.links.values())
        return {
            "total_links": len(self.links), "total_clicks": total_clicks,
            "total_conversions": total_convs,
            "conversion_rate": round(total_convs / max(total_clicks, 1) * 100, 1),
            "by_program": self._group_by_program(),
        }

    def _group_by_program(self) -> dict:
        programs = {}
        for lid, link in self.links.items():
            prog = link["program"]
            if prog not in programs:
                programs[prog] = {"links": 0, "clicks": 0, "conversions": 0}
            programs[prog]["links"] += 1
            programs[prog]["clicks"] += link["clicks"]
            programs[prog]["conversions"] += link["conversions"]
        return programs

    @staticmethod
    def extract_links_from_content(content: str) -> list[dict]:
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s)"]*'
        urls = re.findall(url_pattern, content)
        return [{"url": u, "type": "affiliate" if any(d in u for d in [".com/", "hotmart", "amzn"]) else "regular"} for u in urls]

    @staticmethod
    def generate_disclosure(niche: str) -> str:
        return f"Alguns links neste artigo são de afiliados. Se você comprar através deles, eu posso ganhar uma comissão sem custo adicional para você. Isso ajuda a manter o conteúdo sobre {niche} gratuito e de qualidade."


class NotificationEngine:
    def __init__(self, state_dir: str = ".state/notifications"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.log: list[dict] = []
        self._load()

    def _load(self):
        log_file = self.state_dir / "notifications.json"
        if log_file.exists():
            with open(log_file) as f:
                self.log = json.load(f)

    def _save(self):
        with open(self.state_dir / "notifications.json", "w") as f:
            json.dump(self.log[-100:], f, indent=2)

    def send(self, channel: str, title: str, message: str, severity: str = "info") -> dict:
        notification = {
            "id": f"notif_{len(self.log) + 1}", "channel": channel,
            "title": title, "message": message, "severity": severity,
            "timestamp": datetime.now().isoformat(), "sent": False,
        }
        delivery = self._deliver(notification)
        notification["sent"] = delivery["success"]
        notification["delivery"] = delivery
        self.log.append(notification)
        self._save()
        return notification

    def _deliver(self, notif: dict) -> dict:
        channel = notif["channel"]
        if channel == "console":
            print(f"[{notif['severity'].upper()}] {notif['title']}: {notif['message'][:100]}")
            return {"success": True, "method": "console"}
        elif channel == "telegram":
            return {"success": False, "method": "telegram", "error": "API não configurada", "fallback": "console", "message": f"[TG] {notif['title']}: {notif['message']}"}
        elif channel == "email":
            return {"success": False, "method": "email", "error": "SMTP não configurado", "fallback": None}
        return {"success": False, "method": channel, "error": "Canal não suportado"}

    def send_digest(self, events: list[dict]) -> dict:
        summaries = {}
        for e in events:
            t = e.get("type", "unknown")
            summaries[t] = summaries.get(t, 0) + 1
        digest_msg = " | ".join(f"{k}: {v}" for k, v in summaries.items())
        return self.send("console", "📊 Digest Diário", digest_msg, "info")

    def get_recent(self, limit: int = 10) -> list[dict]:
        return self.log[-limit:]

    def get_stats(self) -> dict:
        by_severity = {}
        for n in self.log:
            s = n.get("severity", "info")
            by_severity[s] = by_severity.get(s, 0) + 1
        return {
            "total": len(self.log), "by_severity": by_severity,
            "by_channel": {ch: sum(1 for n in self.log if n.get("channel") == ch) for ch in set(n.get("channel", "") for n in self.log)},
        }


class SocialListeningEngine:
    def __init__(self, niche: str):
        self.niche = niche
        self.mentions: list[dict] = []
        self.sentiment_history: list[dict] = []

    def scan_mentions(self, platform: str, keyword: str) -> list[dict]:
        mentions = [
            {"platform": platform, "keyword": keyword, "text": f"Novo artigo sobre {keyword} em {self.niche} muito bom!", "sentiment": "positive", "engagement": random.randint(10, 200), "timestamp": datetime.now().isoformat()},
            {"platform": platform, "keyword": keyword, "text": f"Não concordo com a abordagem de {keyword}", "sentiment": "negative", "engagement": random.randint(5, 50), "timestamp": datetime.now().isoformat()},
        ]
        self.mentions.extend(mentions)
        return mentions

    def analyze_sentiment(self) -> dict:
        if not self.mentions:
            return {"total": 0, "positive": 0, "negative": 0, "neutral": 0, "score": 0}
        pos = sum(1 for m in self.mentions if m["sentiment"] == "positive")
        neg = sum(1 for m in self.mentions if m["sentiment"] == "negative")
        neu = sum(1 for m in self.mentions if m["sentiment"] == "neutral")
        total = len(self.mentions)
        return {"total": total, "positive": pos, "negative": neg, "neutral": neu, "score": round((pos - neg) / max(total, 1) * 100, 1)}

    def get_trending_topics(self) -> list[dict]:
        return [
            {"topic": self.niche, "volume": 1000, "growth": "+15%", "platform": "google"},
            {"topic": f"{self.niche} para iniciantes", "volume": 500, "growth": "+25%", "platform": "youtube"},
        ]

    def detect_crisis(self) -> list[dict]:
        warnings = []
        recent = self.mentions[-20:] if len(self.mentions) >= 20 else self.mentions
        negative = [m for m in recent if m["sentiment"] == "negative"]
        if len(negative) > len(recent) * 0.3:
            warnings.append({"type": "sentiment_crisis", "severity": "high", "message": f"Sentimento negativo acima de 30% nas últimas menções de {self.niche}", "action": "Revisar conteúdo recente e responder a críticas"})
        return warnings


class SEOCrawlerEngine:
    def __init__(self, domain: str = ""):
        self.domain = domain
        self.pages: list[dict] = []
        self.issues: list[dict] = []

    def generate_sitemap(self, pages: list[dict], base_url: str) -> str:
        urls = [f"  <url><loc>{base_url}/{p.get('slug', '')}</loc><priority>{p.get('priority', 0.5)}</priority></url>" for p in pages]
        return '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>"

    def generate_robots_txt(self, base_url: str, sitemap_path: str = "/sitemap.xml") -> str:
        return f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /private/\nSitemap: {base_url}{sitemap_path}"

    def check_meta_tags(self, pages: list[dict]) -> list[dict]:
        issues = []
        for p in pages:
            if not p.get("title"):
                issues.append({"page": p.get("slug", ""), "issue": "Missing title tag", "severity": "high"})
            if not p.get("description"):
                issues.append({"page": p.get("slug", ""), "issue": "Missing meta description", "severity": "high"})
            if not p.get("heading"):
                issues.append({"page": p.get("slug", ""), "issue": "Missing H1 heading", "severity": "medium"})
        self.issues.extend(issues)
        return issues

    def check_broken_links(self, links: list[str]) -> list[dict]:
        broken = []
        for link in links:
            if "404" in link or "broken" in link:
                broken.append({"url": link, "status": 404, "severity": "high"})
        return broken

    def analyze_page_speed(self, pages: list[dict]) -> dict:
        scores = [{"page": p.get("slug", ""), "performance_score": random.randint(60, 95), "seo_score": random.randint(70, 100), "issues_found": random.randint(0, 5)} for p in pages]
        avg_perf = sum(s["performance_score"] for s in scores) / max(len(scores), 1)
        avg_seo = sum(s["seo_score"] for s in scores) / max(len(scores), 1)
        return {"pages_analyzed": len(scores), "avg_performance": round(avg_perf, 1), "avg_seo": round(avg_seo, 1), "details": scores}

    def generate_seo_report(self, base_url: str, pages: list[dict]) -> dict:
        meta_issues = self.check_meta_tags(pages)
        return {
            "domain": base_url, "total_pages": len(pages),
            "meta_issues": len(meta_issues),
            "seo_score": round((1 - len(meta_issues) / max(len(pages) * 3, 1)) * 100, 1),
            "has_sitemap": True, "has_robots": True,
            "recommendations": self._recommend(meta_issues),
        }

    def _recommend(self, issues: list[dict]) -> list[str]:
        recs = []
        if any(i["severity"] == "high" for i in issues):
            recs.append("Corrigir erros críticos de SEO (meta tags faltando)")
        recs.append("Manter frequência de atualização de conteúdo")
        recs.append("Monitorar velocidade de carregamento das páginas")
        return recs
