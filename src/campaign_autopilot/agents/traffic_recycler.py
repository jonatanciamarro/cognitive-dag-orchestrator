"""TrafficRecyclerAgent - Reaproveita trafego em 8+ camadas de monetizacao.

Integrado ao SemanticMemoryStore para aprendizado persistente.
Gera HTML pronto para embed no site.
Tracking de performance por caminho de conversao.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from .base import AgentBase, AgentResult, AgentTrace
from ..logging_utils import StructuredLogger

log = StructuredLogger("traffic_recycler")
MEMORY_FILE = Path(".state/traffic_recycling_memory.json")

# RPV realista para cada caminho de conversao
CONVERSION_PATHS = {
    "email_lead_magnet": {
        "name": "Email c/ Lead Magnet",
        "desc": "PDF/checklist gratis por email",
        "pos": "top",
        "cost": "zero",
        "rpv": 0.025,
        "icon": "inbox",
    },
    "email_affiliate_seq": {
        "name": "Sequencia de Afiliados",
        "desc": "5 emails automatizados com ofertas",
        "pos": "middle",
        "cost": "zero",
        "rpv": 0.035,
        "icon": "mail",
    },
    "exit_intent_popup": {
        "name": "Popup Exit-Intent",
        "desc": "Oferta irresistivel ao sair do site",
        "pos": "bottom",
        "cost": "zero",
        "rpv": 0.060,
        "icon": "exit",
    },
    "content_upgrade": {
        "name": "Content Upgrade",
        "desc": "Material extra relacionado ao artigo",
        "pos": "top",
        "cost": "zero",
        "rpv": 0.015,
        "icon": "file",
    },
    "webinar_optin": {
        "name": "Webinar Gratuito",
        "desc": "Aula ao vivo sobre o tema",
        "pos": "middle",
        "cost": "zero",
        "rpv": 0.050,
        "icon": "video",
    },
    "interstitial": {
        "name": "Interstitial c/ Oferta",
        "desc": "Popup contextual apos 30s de leitura",
        "pos": "middle",
        "cost": "zero",
        "rpv": 0.025,
        "icon": "refresh",
    },
    "cross_niche": {
        "name": "Cross-Nichos",
        "desc": "Recomendacao de artigo de outro nicho",
        "pos": "top",
        "cost": "zero",
        "rpv": 0.012,
        "icon": "link",
    },
    "membership": {
        "name": "Upgrade Membros",
        "desc": "Plano de membros com conteudo exclusivo",
        "pos": "bottom",
        "cost": "low",
        "rpv": 0.135,
        "icon": "diamond",
    },
    "digital_product": {
        "name": "Produto Digital",
        "desc": "Curso/ebook proprios ou afiliados",
        "pos": "bottom",
        "cost": "medium",
        "rpv": 0.376,
        "icon": "package",
    },
    "retargeting": {
        "name": "Pixel Retargeting",
        "desc": "Pixel para anuncios futuros",
        "pos": "top",
        "cost": "zero",
        "rpv": 0.010,
        "icon": "target",
    },
    "whatsapp": {
        "name": "WhatsApp",
        "desc": "Grupo exclusivo no WhatsApp",
        "pos": "middle",
        "cost": "zero",
        "rpv": 0.045,
        "icon": "chat",
    },
    "telegram": {
        "name": "Canal Telegram",
        "desc": "Canal com dicas diarias",
        "pos": "middle",
        "cost": "zero",
        "rpv": 0.030,
        "icon": "send",
    },
    "social_follow": {
        "name": "Seguir Redes",
        "desc": "Instagram/Twitter/TikTok",
        "pos": "top",
        "cost": "zero",
        "rpv": 0.002,
        "icon": "smartphone",
    },
    "sampling": {
        "name": "Amostra Gratis",
        "desc": "Amostra de produto digital limitada",
        "pos": "bottom",
        "cost": "low",
        "rpv": 0.150,
        "icon": "gift",
    },
}

INTENT_MAP = {
    "informational": [
        "email_lead_magnet",
        "content_upgrade",
        "telegram",
        "social_follow",
        "cross_niche",
    ],
    "commercial": [
        "exit_intent_popup",
        "email_affiliate_seq",
        "interstitial",
        "whatsapp",
        "digital_product",
    ],
    "transactional": [
        "digital_product",
        "membership",
        "exit_intent_popup",
        "webinar_optin",
        "retargeting",
    ],
    "navigational": ["social_follow", "telegram", "email_lead_magnet", "cross_niche"],
}

NICHE_MAP = {
    "tecnologia": [
        "email_lead_magnet",
        "digital_product",
        "telegram",
        "exit_intent_popup",
        "interstitial",
    ],
    "financas": [
        "webinar_optin",
        "email_affiliate_seq",
        "digital_product",
        "retargeting",
        "membership",
    ],
    "saude": [
        "email_lead_magnet",
        "content_upgrade",
        "telegram",
        "membership",
        "whatsapp",
    ],
    "carreira": [
        "email_lead_magnet",
        "webinar_optin",
        "digital_product",
        "telegram",
        "whatsapp",
    ],
}

CROSS_NICHE_MAP = {
    "tecnologia": "financas",
    "financas": "carreira",
    "carreira": "saude",
    "saude": "tecnologia",
}

NICHE_COLORS = {
    "tecnologia": {"primary": "#2b6cb0", "bg": "#ebf4ff", "accent": "#3182ce"},
    "financas": {"primary": "#2f855a", "bg": "#f0fff4", "accent": "#38a169"},
    "saude": {"primary": "#c53030", "bg": "#fff5f5", "accent": "#e53e3e"},
    "carreira": {"primary": "#6b46c1", "bg": "#faf5ff", "accent": "#805ad5"},
}

DEFAULT_COLORS = {"primary": "#2b6cb0", "bg": "#ebf4ff", "accent": "#3182ce"}


class TrafficRecyclerAgent(AgentBase):
    """Reaproveita cada visitante em multiplas camadas de monetizacao.

    Funil de 8+ camadas:
    1. Conteudo (links de afiliado + AdSense) - ja ativo
    2. Lead Magnet (captura de email)
    3. Interstitial (oferta contextual)
    4. Exit-Intent (popup ao sair)
    5. Cross-Niche (recomendacao de outro nicho)
    6. Telegram/WhatsApp (canal exclusivo)
    7. Email (sequencia de afiliados)
    8. Produto Digital / Membresia
    """

    def __init__(self, semantic_memory=None, **kwargs):
        super().__init__("traffic_recycler", **kwargs)
        self._lock = threading.Lock()
        self.semantic_memory = semantic_memory
        self.memory = self._load()

    def _load(self):
        try:
            if MEMORY_FILE.exists():
                data = json.loads(MEMORY_FILE.read_text())
                for pid in CONVERSION_PATHS:
                    data.setdefault("paths", {}).setdefault(
                        pid,
                        {
                            "rpv": CONVERSION_PATHS[pid]["rpv"],
                            "times_used": 0,
                            "conversions": 0,
                        },
                    )
                return data
        except Exception as e:
            log.warning("Could not load memory", error=str(e))
        return {
            "paths": {
                k: {"rpv": v["rpv"], "times_used": 0, "conversions": 0}
                for k, v in CONVERSION_PATHS.items()
            },
            "total_recycled": 0.0,
            "total_conversions": 0,
            "cycle_count": 0,
        }

    def _save(self):
        with self._lock:
            MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.memory["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.memory["cycle_count"] = self.memory.get("cycle_count", 0) + 1
            MEMORY_FILE.write_text(json.dumps(self.memory, indent=2, default=str))

    def _sync_to_semantic_memory(self):
        if not self.semantic_memory:
            return
        try:
            for pid, data in self.memory.get("paths", {}).items():
                cfg = CONVERSION_PATHS.get(pid)
                if not cfg:
                    continue
                times_used = data.get("times_used", 0)
                conversions = data.get("conversions", 0)
                conv_rate = conversions / max(times_used, 1)
                confidence = min(1.0, times_used / 100)
                self.semantic_memory.store_claim(
                    concept=f"conversion_path:{pid}",
                    claim=f"rpv={data.get('rpv', cfg['rpv'])} conversion_rate={conv_rate:.4f} times_used={times_used} conversions={conversions}",
                    confidence=confidence,
                    evidence_type="empirical",
                    epistemic_status="INFERRED" if times_used > 10 else "ASSUMED",
                    observer="traffic_recycler",
                    provenance=f"traffic_recycling_memory:cycle_{self.memory.get('cycle_count', 0)}",
                )
        except Exception as e:
            log.warning("Could not sync to semantic memory", error=str(e))

    def _intent(self, content):
        intent = content.get("intent", content.get("keyword_intent", "informational"))
        t = str(content.get("title", "")).lower()
        s = str(content.get("snippet", "")).lower()
        if any(
            w in t or w in s
            for w in [
                "melhor",
                "review",
                "vale a pena",
                "comprar",
                "guia de compra",
                "preco",
            ]
        ):
            return "commercial"
        if any(
            w in t or w in s
            for w in ["como", "guia", "passo a passo", "tutorial", "aprender"]
        ):
            return "informational"
        if any(w in t or w in s for w in ["gratis", "baixar", "download", "acesso"]):
            return "navigational"
        return intent

    def get_paths(self, content, niche, visits):
        intent = self._intent(content)
        candidates = list(
            dict.fromkeys(INTENT_MAP.get(intent, []) + NICHE_MAP.get(niche, []))
        )
        scored = []
        mem_paths = self.memory["paths"]

        for pid in candidates:
            cfg = CONVERSION_PATHS.get(pid)
            m = mem_paths.get(pid, {})
            if not cfg:
                continue
            rpv = m.get("rpv", cfg["rpv"])
            times_used = m.get("times_used", 0)
            conversions = m.get("conversions", 0)
            conv_rate = conversions / max(times_used, 1)
            confidence = min(1.0, times_used / 100)
            intent_boost = 1.2 if pid in INTENT_MAP.get(intent, []) else 0.8
            niche_boost = 1.1 if pid in NICHE_MAP.get(niche, []) else 0.9
            learning_boost = 0.8 + (confidence * 0.4)
            score = rpv * learning_boost * intent_boost * niche_boost
            if conv_rate > 0.01:
                score *= 1.2
            scored.append(
                {
                    "path_id": pid,
                    "name": cfg["name"],
                    "desc": cfg["desc"],
                    "pos": cfg["pos"],
                    "cost": cfg["cost"],
                    "icon": cfg.get("icon", ""),
                    "rpv": rpv,
                    "score": round(score, 6),
                    "conv_rate": round(conv_rate, 4),
                    "times_used": times_used,
                    "estimated_revenue": round(visits * rpv, 2),
                }
            )
        return sorted(scored, key=lambda x: x["score"], reverse=True)

    def estimate(self, content, paths, visits):
        title = content.get("title", content.get("slug", "unknown"))
        active_paths = [p for p in paths if p["cost"] in ("zero", "low")]
        remaining = visits
        total_extra = 0.0
        path_breakdown = []
        for p in active_paths:
            layer_rev = remaining * p["rpv"]
            total_extra += layer_rev
            path_breakdown.append(
                {
                    "path_id": p["path_id"],
                    "name": p["name"],
                    "rpv": p["rpv"],
                    "remaining_visitors": remaining,
                    "revenue": round(layer_rev, 2),
                }
            )
            remaining = int(remaining * 0.7)
        return {
            "title": title,
            "visits": visits,
            "recycled": round(total_extra, 2),
            "multiplier": round(total_extra / max(visits * 0.01, 1), 2),
            "path_breakdown": path_breakdown,
        }

    def gen_html(self, path_id, article, all_articles=None):
        content = article.get("content", article)
        niche = content.get("section", "tecnologia")
        title = content.get("title", "")
        slug = content.get("slug", "artigo")
        colors = NICHE_COLORS.get(niche, DEFAULT_COLORS)

        cn_article = None
        target_niche = CROSS_NICHE_MAP.get(niche)
        if all_articles and target_niche:
            for a in all_articles:
                c = a.get("content", a)
                if c.get("section") == target_niche:
                    cn_article = c
                    break

        if path_id == "email_lead_magnet":
            html = (
                '<div class="rm-lead" style="background:linear-gradient(135deg,'
                + colors["bg"]
                + ","
                + colors["bg"]
                + "dd);border:2px solid "
                + colors["primary"]
                + '40;border-radius:16px;padding:30px;margin:40px 0;text-align:center;">'
                '<h3 style="color:'
                + colors["primary"]
                + ';margin:0 0 8px;font-size:22px;"><span style="margin-right:8px;">📥</span>Quer ir mais fundo?</h3>'
                '<p style="color:#4a5568;margin:0 0 20px;font-size:15px;">Baixe nosso <strong>guia completo em PDF</strong> sobre '
                + title.split(":")[0]
                + " - totalmente gratuito!</p>"
                '<form style="display:flex;gap:10px;max-width:450px;margin:0 auto;" action="/api/lead" method="POST">'
                '<input type="hidden" name="source" value="' + slug + '">'
                '<input type="email" name="email" placeholder="Seu melhor email" required style="flex:1;padding:12px 16px;border:2px solid #e2e8f0;border-radius:10px;font-size:15px;">'
                '<button type="submit" style="background:'
                + colors["accent"]
                + ';color:white;border:none;padding:12px 28px;border-radius:10px;font-weight:bold;font-size:15px;cursor:pointer;">Receber PDF</button>'
                "</form>"
                '<p style="color:#718096;font-size:12px;margin:12px 0 0;">🔒 Sem spam. Descadastre-se a qualquer momento.</p>'
                "</div>"
            )
            return html

        elif path_id == "exit_intent_popup":
            html = (
                '<div id="rm-exit-'
                + slug
                + '" class="rm-exit-popup" style="display:none;position:fixed;bottom:0;left:0;right:0;background:white;box-shadow:0 -8px 30px rgba(0,0,0,0.2);padding:30px;z-index:9999;text-align:center;border-radius:20px 20px 0 0;">'
                '<div style="max-width:450px;margin:0 auto;">'
                "<button onclick=\"document.getElementById('rm-exit-"
                + slug
                + "').style.display='none'\" style=\"float:right;background:none;border:none;font-size:24px;cursor:pointer;color:#a0aec0;\">×</button>"
                '<h3 style="color:'
                + colors["primary"]
                + ';margin:8px 0;"><span style="margin-right:8px;">🎁</span>Espere! Não va ainda...</h3>'
                '<p style="color:#4a5568;margin:0 0 20px;">Temos uma <strong>oferta especial</strong> para voce sobre '
                + title.split(":")[0]
                + ".</p>"
                '<a href="/produtos/" style="display:inline-block;background:'
                + colors["accent"]
                + ';color:white;padding:14px 32px;border-radius:50px;text-decoration:none;font-weight:bold;font-size:16px;">Quero Aproveitar</a>'
                "</div></div>"
                '<script>(function(){var shown=false;document.addEventListener("mouseout",function(e){if(e.clientY<10&&!shown){document.getElementById("rm-exit-'
                + slug
                + '").style.display="block";shown=true;}});})();</script>'
            )
            return html

        elif path_id == "telegram":
            return (
                '<div class="rm-tg" style="background:linear-gradient(135deg,#0088cc,#005f8a);color:white;border-radius:16px;padding:24px;margin:30px 0;text-align:center;">'
                '<h4 style="margin:0 0 5px;font-size:18px;"><span style="margin-right:8px;">✈️</span>Canal Telegram</h4>'
                '<p style="margin:5px 0 15px;opacity:0.9;">Dicas exclusivas sobre '
                + title.split(":")[0]
                + " toda semana!</p>"
                '<a href="https://t.me/seucanal" target="_blank" rel="noopener" style="display:inline-block;background:white;color:#0088cc;padding:12px 30px;border-radius:50px;text-decoration:none;font-weight:bold;">Entrar Gratuitamente</a>'
                "</div>"
            )

        elif path_id == "whatsapp":
            return (
                '<div class="rm-wa" style="background:linear-gradient(135deg,#25d366,#128c7e);color:white;border-radius:16px;padding:24px;margin:30px 0;text-align:center;">'
                '<h4 style="margin:0 0 5px;font-size:18px;"><span style="margin-right:8px;">💬</span>Grupo Exclusivo WhatsApp</h4>'
                '<p style="margin:5px 0 15px;opacity:0.9;">Conteudo premium sobre '
                + title.split(":")[0]
                + "!</p>"
                '<a href="https://chat.whatsapp.com/seugrupo" target="_blank" rel="noopener" style="display:inline-block;background:white;color:#128c7e;padding:12px 30px;border-radius:50px;text-decoration:none;font-weight:bold;">Entrar no Grupo</a>'
                "</div>"
            )

        elif path_id == "cross_niche" and cn_article:
            cn_title = cn_article.get("title", "Conteudo Relacionado")
            cn_slug = cn_article.get("slug", "")
            cn_niche = cn_article.get("section", "")
            cn_label = NICHE_COLORS.get(cn_niche, DEFAULT_COLORS)
            return (
                '<div class="rm-cross" style="background:linear-gradient(135deg,'
                + cn_label["bg"]
                + ","
                + cn_label["bg"]
                + "dd);border:1px solid "
                + cn_label["primary"]
                + '30;border-radius:14px;padding:20px;margin:30px 0;">'
                '<div style="display:flex;align-items:center;gap:15px;flex-wrap:wrap;">'
                '<div style="flex:1;">'
                '<p style="margin:0 0 4px;color:'
                + cn_label["primary"]
                + ';font-weight:bold;font-size:13px;text-transform:uppercase;"><span style="margin-right:4px;">🔗</span>Recomendado - '
                + cn_niche.title()
                + "</p>"
                '<h4 style="margin:0;font-size:17px;"><a href="/'
                + cn_niche
                + "/"
                + cn_slug
                + '/" style="color:#2d3748;text-decoration:none;">'
                + cn_title
                + "</a></h4>"
                "</div>"
                '<a href="/'
                + cn_niche
                + "/"
                + cn_slug
                + '/" style="background:'
                + cn_label["accent"]
                + ';color:white;padding:10px 24px;border-radius:50px;text-decoration:none;font-weight:bold;font-size:14px;white-space:nowrap;">Ler →</a>'
                "</div></div>"
            )

        elif path_id == "interstitial":
            return (
                '<div class="rm-offer" style="background:#fffbeb;border:2px solid #f6ad55;border-radius:14px;padding:24px;margin:35px 0;text-align:center;">'
                '<h4 style="color:#744210;margin:0 0 8px;font-size:18px;"><span style="margin-right:8px;">🔥</span>Recomendação do Editor</h4>'
                '<p style="color:#744210;margin:0 0 16px;">Produtos e cursos recomendados sobre '
                + title.split(":")[0]
                + ".</p>"
                '<a href="/produtos/?ref='
                + slug
                + '" style="display:inline-block;background:#dd6b20;color:white;padding:12px 32px;border-radius:50px;text-decoration:none;font-weight:bold;font-size:15px;">Ver Ofertas</a>'
                "</div>"
            )

        return ""

    def run(self, context):
        started_at = datetime.now(timezone.utc).isoformat()
        camp = context.campaign if hasattr(context, "campaign") else {}
        articles = camp.get("articles", [])
        visits_data = camp.get("visit_data", {})
        curr_rev = camp.get("current_revenue", 0)

        analyses = []
        all_paths = []
        htmls = []
        path_stats = {}

        for art in articles:
            c = art.get("content", art)
            slug = c.get("slug", "")
            niche = c.get("section", "tecnologia")
            v = visits_data.get(slug, 500)
            paths = self.get_paths(c, niche, v)
            all_paths.extend(paths)
            a = self.estimate(c, paths, v)
            analyses.append(a)

            generated = set()
            for p in paths[:5]:
                if p["path_id"] not in generated:
                    h = self.gen_html(p["path_id"], art, articles)
                    if h:
                        htmls.append(
                            {
                                "path_id": p["path_id"],
                                "name": p["name"],
                                "icon": p.get("icon", ""),
                                "html": h,
                            }
                        )
                        generated.add(p["path_id"])

            for p in paths:
                pid = p["path_id"]
                if pid not in path_stats:
                    path_stats[pid] = {
                        "name": p["name"],
                        "total_rev": 0,
                        "count": 0,
                        "icon": p.get("icon", ""),
                    }
                path_stats[pid]["total_rev"] += p["estimated_revenue"]
                path_stats[pid]["count"] += 1

        total_extra = sum(a["recycled"] for a in analyses)
        total_visits = sum(a["visits"] for a in analyses)

        with self._lock:
            for p in all_paths:
                pid = p["path_id"]
                if pid in self.memory["paths"]:
                    self.memory["paths"][pid]["times_used"] = (
                        self.memory["paths"][pid].get("times_used", 0) + 1
                    )
                    old_rpv = self.memory["paths"][pid].get(
                        "rpv", CONVERSION_PATHS[pid]["rpv"]
                    )
                    new_rpv = p["rpv"]
                    weight = min(0.3, self.memory["paths"][pid]["times_used"] / 500)
                    self.memory["paths"][pid]["rpv"] = round(
                        old_rpv * (1 - weight) + new_rpv * weight, 6
                    )
            self.memory["total_recycled"] = (
                self.memory.get("total_recycled", 0) + total_extra
            )

        self._save()
        self._sync_to_semantic_memory()

        base_value = max(curr_rev, total_visits * 0.005)
        multiplier = (
            round((base_value + total_extra) / max(base_value, 1), 2)
            if base_value > 0
            else round(total_extra / max(total_visits * 0.001, 1), 2)
        )

        output = {
            "articles_analyzed": len(articles),
            "total_visits": total_visits,
            "current_base_revenue": curr_rev,
            "total_additional_revenue_potential": round(total_extra, 2),
            "total_potential_with_recycling": round(curr_rev + total_extra, 2),
            "multiplier": multiplier,
            "article_analyses": analyses,
            "top_paths": sorted(all_paths, key=lambda x: x["score"], reverse=True)[:10],
            "path_stats": dict(
                sorted(
                    path_stats.items(), key=lambda x: x[1]["total_rev"], reverse=True
                )
            ),
            "interstitial_elements": htmls[:12],
            "funnel": {
                "1_conteudo_afiliado": "Links de afiliado + AdSense no conteudo (ja ativo)",
                "2_lead_magnet": "Captura de email com lead magnet (R$0.025/vis)",
                "3_interstitial": "Oferta contextual apos 30s (R$0.025/vis)",
                "4_exit_intent": "Popup de saida com oferta (R$0.06/vis)",
                "5_cross_niche": "Cross-sell entre nichos (R$0.012/vis)",
                "6_telegram_whatsapp": "Canal Telegram/Grupo WhatsApp (R$0.03-0.045/vis)",
                "7_email_seq": "Sequencia de emails automatizada (R$0.035/vis)",
                "8_upgrade_produto": "Produto Digital / Membresia (R$0.14-0.38/vis)",
            },
            "next_steps": [
                "1. Copie os elementos HTML de output/traffic_recycling/ para o template do site",
                "2. Crie conta gratuita no MailerLite/Brevo para capturar emails",
                "3. Adicione o pixel de retargeting (Meta/TikTok) no site",
                "4. Crie canal Telegram e grupo WhatsApp para cada nicho",
                "5. Configure sequencia de 5 emails de afiliados no MailerLite",
                "6. Ative o exit-intent popup (codigo JS ja incluso nos HTMLs)",
                "7. Quando tiver 500+ leads, lance um produto digital proprio",
            ],
            "memory_path": str(MEMORY_FILE),
        }

        trace = AgentTrace(
            agent=self.name,
            step_id="traffic_recycling",
            status="success",
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat(),
            duration_ms=0,
            thread_name="main",
            notes=[
                f"{len(articles)} artigos reciclados",
                f"+R${total_extra:.0f}/mes potencial",
                f"Multiplicador: {multiplier}x",
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
