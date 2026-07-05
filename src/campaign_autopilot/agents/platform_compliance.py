"""Agente de Compliance Multi-Plataforma — valida conteúdo contra regras específicas de cada plataforma para minimizar bloqueios, bans e penalidades."""

from __future__ import annotations

from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


# ── Regras Específicas por Plataforma ───────────────────────────────────

_PLATFORM_RULES: dict[str, dict[str, Any]] = {
    "youtube": {
        "name": "YouTube",
        "policy_url": "https://www.youtube.com/howyoutubeworks/policies/",
        "forbidden_practices": [
            "conteúdo enganoso (clickbait)",
            "keyword stuffing no título",
            "comprar visualizações",
            "comprar inscritos",
            "engajamento artificial",
            "uso de bots",
            "reaplicar conteúdo de terceiros sem transformação significativa",
            "links externos enganosos",
        ],
        "restricted_content": [
            "nudez",
            "sexual",
            "violência explícita",
            "discurso de ódio",
            "assédio",
            "spam",
            "conteúdo enganoso",
            "informação médica falsa",
            "venda de produtos ilegais",
            "armas de fogo",
            "terrorismo",
            "conteúdo chocante",
            "desafios perigosos",
        ],
        "restricted_terms_pt": [
            "garantido",
            "dinheiro fácil",
            "enriqueça rápido",
            "milagroso",
            "cura",
            "emagreça sem esforço",
            "fique rico",
        ],
        "copyright_rules": [
            "Usar apenas músicas livres de direitos autorais",
            "Incluir atribuição quando necessário",
            "Não usar clipes de terceiros sem permissão",
            "Conteúdo original ou devidamente licenciado",
        ],
        "affiliate_rules": [
            "Incluir disclosure de afiliado na descrição",
            "Link de afiliado permitido na descrição",
            "Não colocar links de afiliado no vídeo (overlay)",
            "Descrição deve ter valor informativo, não apenas links",
        ],
        "allowed_categories": [
            "educação",
            "entretenimento",
            "tecnologia",
            "finanças",
            "saúde (informativo)",
            "negócios",
            "marketing",
        ],
        "max_keywords_title": 5,
        "max_hashtags_description": 15,
        "requires_disclosure_in_description": True,
    },
    "instagram": {
        "name": "Instagram",
        "policy_url": "https://help.instagram.com/477434105621119",
        "restricted_content": [
            "nudez",
            "sexual explícito",
            "discurso de ódio",
            "assédio",
            "bullying",
            "violência",
            "automutilação",
            "transtorno alimentar",
            "conteúdo enganoso",
            "desinformação",
            "spam",
            "venda de drogas",
            "armas de fogo",
            "produtos ilegais",
        ],
        "restricted_terms_pt": [
            "garantido",
            "milagroso",
            "cura definitiva",
            "resultado garantido",
            "dinheiro fácil",
            "emagreça rápido",
        ],
        "copyright_rules": [
            "Usar músicas da biblioteca do Instagram",
            "Conteúdo original é priorizado pelo algoritmo",
            "Dar crédito quando usar conteúdo de terceiros",
            "Não repostar sem permissão",
        ],
        "affiliate_rules": [
            "Incluir #publi ou #ad em posts pagos",
            "Link de afiliado permitido apenas na bio ou stories",
            "Não colocar links clicáveis na legenda",
            "Disclosure obrigatório em parcerias pagas",
        ],
        "link_policy": "apenas_bio_ou_stories",
        "max_hashtags": 30,
        "max_hashtags_recommended": 15,
        "recommended_posts_per_day": 3,
        "forbidden_practices": [
            "seguir/desseguir em massa",
            "comentários automáticos",
            "curtidas em massa",
            "uso de bots",
            "comprar seguidores",
        ],
    },
    "tiktok": {
        "name": "TikTok",
        "policy_url": "https://www.tiktok.com/community-guidelines",
        "restricted_content": [
            "nudez",
            "atividade sexual",
            "discurso de ódio",
            "assédio",
            "bullying",
            "violência explícita",
            "desafios perigosos",
            "automutilação",
            "transtorno alimentar",
            "conteúdo enganoso",
            "desinformação",
            "spam",
            "golpes financeiros",
            "venda de produtos regulamentados",
        ],
        "restricted_terms_pt": [
            "garantido",
            "dinheiro fácil",
            "esquema",
            "pirâmide",
            "milagroso",
            "cura",
            "resultado imediato",
        ],
        "copyright_rules": [
            "Usar músicas da biblioteca do TikTok",
            "Conteúdo original tem prioridade",
            "Não usar clipes de TV/filmes sem permissão",
            "Atribuição não substitui permissão de uso",
        ],
        "affiliate_rules": [
            "Disclosure obrigatório na legenda ou vídeo",
            "Link de afiliado permitido na bio",
            "Não colocar links nos comentários",
            "#ad ou #publi obrigatório para conteúdo pago",
        ],
        "max_duration_recommended": 60,  # segundos para melhor alcance
        "forbidden_practices": [
            "comprar visualizações",
            "comprar seguidores",
            "engajamento artificial",
            "uso de bots",
            "cross-post automático sem adaptação",
        ],
        "age_restricted_categories": ["suplementos", "emagrecimento", "investimentos"],
    },
    "twitter": {
        "name": "Twitter/X",
        "policy_url": "https://help.twitter.com/rules-and-policies",
        "restricted_content": [
            "discurso de ódio",
            "assédio",
            "violência",
            "terrorismo",
            "conteúdo sexual não consensual",
            "spam",
            "manipulação de plataforma",
            "desinformação",
            "golpes",
            "conteúdo enganoso",
        ],
        "restricted_terms_pt": [
            "garantido",
            "dinheiro fácil",
            "esquema",
            "pirâmide",
        ],
        "affiliate_rules": [
            "Disclosure obrigatório em posts com link de afiliado",
            "Links de afiliado permitidos",
            "Transparência sobre parcerias pagas",
        ],
        "max_tweets_per_day": 50,
        "max_hashtags": 10,
        "recommended_hashtags": 2,
        "forbidden_practices": [
            "spam em menções",
            "seguir/desseguir em massa",
            "tweets duplicados",
            "engajamento artificial",
            "uso de bots",
        ],
    },
    "pinterest": {
        "name": "Pinterest",
        "policy_url": "https://policy.pinterest.com/pt/community-guidelines",
        "restricted_content": [
            "spam",
            "conteúdo enganoso",
            "nudez",
            "violência",
            "discurso de ódio",
            "desinformação",
            "produtos regulamentados",
        ],
        "restricted_terms_pt": [
            "garantido",
            "milagroso",
            "emagreça rápido",
        ],
        "copyright_rules": [
            "Usar imagens originais ou licenciadas",
            "Links devem levar a conteúdo relevante",
            "Pins devem descrever com precisão o destino do link",
        ],
        "affiliate_rules": [
            "Disclosure no título ou descrição",
            "Links de afiliado permitidos",
            "Não usar link shorteners que escondem destino",
        ],
        "max_pins_per_day": 25,
        "max_hashtags": 20,
        "recommended_pin_aspect_ratio": "2:3 (1000x1500px)",
        "forbidden_practices": [
            "pins duplicados",
            "links quebrados",
            "redirecionamentos múltiplos",
            "pins com texto excessivo na imagem",
        ],
    },
    "whatsapp": {
        "name": "WhatsApp Business",
        "policy_url": "https://www.whatsapp.com/legal/commerce-policy",
        "restricted_content": [
            "spam em massa",
            "conteúdo enganoso",
            "golpes",
            "produtos ilegais",
            "conteúdo adulto",
            "violência",
        ],
        "affiliate_rules": [
            "Opt-in explícito obrigatório",
            "Disclosure obrigatório",
            "Links de afiliado permitidos apenas com consentimento",
            "Oferecer opt-out a qualquer momento",
            "Não enviar mensagens em massa sem autorização",
        ],
        "max_messages_per_day": 1000,  # limite do WhatsApp Business
        "restricted_terms_pt": [
            "garantido",
            "milagroso",
            "promessa",
            "dinheiro fácil",
            "renda garantida",
            "esquema",
            "pirâmide",
        ],
        "requires_opt_in": True,
        "requires_opt_out": True,
        "forbidden_practices": [
            "mensagens em massa sem opt-in",
            "compartilhar número de usuários",
            "enviar mensagens fora do horário comercial (8-18h)",
            "usar listas compradas de terceiros",
        ],
        "brazil_lgpd_required": True,
    },
    "email": {
        "name": "Email Marketing",
        "policy_url": "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
        "restricted_terms_pt": [
            "garantido",
            "milagroso",
            "dinheiro fácil",
            "clique aqui",
            "última chance",
            "oferta imperdível",
        ],
        "restricted_content": [
            "conteúdo enganoso",
            "spam",
            "golpes",
            "phishing",
        ],
        "affiliate_rules": [
            "Disclosure obrigatório em cada email",
            "Link de afiliado permitido com disclosure",
            "Não enganar sobre a natureza do conteúdo",
            "Incluir endereço físico do remetente",
        ],
        "required_elements": [
            "linha de assunto não enganosa",
            "identificação clara do remetente",
            "endereço físico",
            "link de descadastro (opt-out)",
            "disclosure se conteúdo pago",
        ],
        "lgpd_requirements": [
            "consentimento explícito para coleta de dados",
            "finalidade clara do tratamento de dados",
            "direito de exclusão dos dados",
            "política de privacidade acessível",
        ],
        "forbidden_practices": [
            "comprar listas de emails",
            "enviar sem consentimento",
            "ocultar identidade do remetente",
            "linha de assunto enganosa",
            "sem link de descadastro",
        ],
    },
    "site": {
        "name": "Site/Blog",
        "policy_url": "https://www.gov.br/secretariageral/pt-br/lgpd",
        "restricted_terms_pt": [
            "garantido",
            "milagroso",
            "dinheiro fácil",
            "enriqueça rápido",
            "cura milagrosa",
            "resultado garantido",
        ],
        "restricted_content": [
            "conteúdo enganoso",
            "golpes",
            "plágio",
        ],
        "affiliate_rules": [
            "Disclosure de afiliado em TODAS as páginas com links",
            "Página de política de privacidade obrigatória",
            "Página de disclosure de afiliados obrigatória",
            "Termos de uso recomendado",
            "LGPD: aviso de cookies obrigatório",
            "LGPD: política de privacidade detalhada",
        ],
        "required_pages": [
            "privacidade",
            "disclosure",
            "termos de uso",
        ],
        "seo_guidelines": [
            "Conteúdo original e de valor",
            "Sem keyword stuffing",
            "Meta descriptions únicas por página",
            "Links internos relevantes",
            "Velocidade de carregamento (Core Web Vitals)",
        ],
        "forbidden_practices": [
            "plágio de conteúdo",
            "copiar conteúdo de concorrentes",
            "keyword stuffing",
            "cloaking",
            "conteúdo gerado automaticamente sem revisão",
        ],
    },
}

# ── Análise ─────────────────────────────────────────────────────────────


def _normalize(value: Any) -> str:
    return str(value).lower() if value is not None else ""


def _find_restricted(text: str, terms: list[str]) -> list[dict[str, Any]]:
    hits = []
    text_lower = text.lower()
    for term in terms:
        if term.lower() in text_lower:
            hits.append({"term": term, "severity": "high"})
    return hits


class PlatformComplianceAgent(AgentBase):
    """Valida conteúdo contra regras específicas de cada plataforma.

    Para cada plataforma (YouTube, Instagram, TikTok, Twitter, Pinterest,
    WhatsApp, Email, Site), verifica:
    - Termos restritos por plataforma
    - Regras de disclosure de afiliado
    - Práticas proibidas
    - LGPD/CAN-SPAM compliance
    - Copyright rules
    - Gera relatório de riscos com sugestões de correção.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("platform_compliance", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        policy = context.policy

        # Coletar conteúdo de todos os step_results
        step_results = context.step_results

        # Determinar quais plataformas verificar
        channels = list(campaign.get("channels", [])) or [
            "seo",
            "newsletter",
            "youtube",
            "instagram",
            "tiktok",
            "twitter",
            "pinterest",
            "whatsapp",
        ]

        all_content = self._collect_content(step_results, campaign)
        platform_reports: dict[str, Any] = {}
        total_issues = 0
        total_critical = 0

        for ch in channels:
            platform_key = self._platform_key(ch)
            if platform_key not in _PLATFORM_RULES:
                continue

            rules = _PLATFORM_RULES[platform_key]
            content = all_content.get(platform_key, {})

            report = self._check_platform(rules, content, campaign, policy)
            platform_reports[platform_key] = report
            total_issues += len(report.get("issues", []))
            total_critical += sum(
                1 for i in report.get("issues", []) if i.get("severity") == "critical"
            )

        # Determinar status geral
        if total_critical > 0:
            overall_status = "block"
        elif total_issues > 0:
            overall_status = "warn"
        else:
            overall_status = "pass"

        output = {
            "status": overall_status,
            "platforms_checked": list(platform_reports.keys()),
            "total_issues": total_issues,
            "total_critical": total_critical,
            "platform_reports": platform_reports,
            "recommendation": self._generate_recommendation(
                overall_status, total_issues
            ),
        }

        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="platform_compliance",
                input_state={"channels": channels, "total_issues": total_issues},
            )
            self.explanation_store.update_decision_output(
                did,
                output_decision={"status": overall_status, "issues": total_issues},
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="platform_compliance",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Verificou {len(platform_reports)} plataformas. "
                f"{total_issues} issues encontradas ({total_critical} críticas)."
            ],
            metadata={"platforms": len(platform_reports), "issues": total_issues},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    # ── Coleção de Conteúdo ──────────────────────────────────────────

    def _collect_content(self, step_results: dict, campaign: dict) -> dict[str, Any]:
        """Coleta conteúdo gerado por cada agente para verificação."""
        collected: dict[str, Any] = {}

        def _get(step_id: str) -> dict:
            s = step_results.get(step_id, {})
            o = s.get("output", {}) if isinstance(s, dict) else {}
            return o if isinstance(o, dict) else {}

        # YouTube
        yt = _get("youtube_marketing")
        if yt:
            videos = yt.get("videos", [])
            collected["youtube"] = {
                "videos": videos,
                "all_text": " ".join(
                    str(v.get("title", "")) + " " + str(v.get("description", ""))
                    for v in videos
                ),
            }

        # Instagram
        ig = _get("instagram_marketing")
        if ig:
            posts = ig.get("posts", [])
            collected["instagram"] = {
                "posts": posts,
                "all_text": " ".join(
                    str(p.get("title", "")) + " " + str(p.get("caption", ""))
                    for p in posts
                ),
            }

        # TikTok
        tt = _get("tiktok_marketing")
        if tt:
            videos = tt.get("videos", [])
            collected["tiktok"] = {
                "videos": videos,
                "all_text": " ".join(
                    str(v.get("hook", "")) + " " + str(v.get("script", ""))
                    for v in videos
                ),
            }

        # Twitter
        tw = _get("twitter_marketing")
        if tw:
            threads = tw.get("threads", [])
            posts = tw.get("posts", [])
            all_text = (
                " ".join(
                    str(t.get("first_tweet", ""))
                    + " "
                    + " ".join(t.get("middle_tweets", []))
                    for t in threads
                )
                + " "
                + " ".join(str(p.get("content", "")) for p in posts)
            )
            collected["twitter"] = {
                "threads": threads,
                "posts": posts,
                "all_text": all_text,
            }

        # Pinterest
        pin = _get("pinterest_marketing")
        if pin:
            pins = pin.get("pins", [])
            collected["pinterest"] = {
                "pins": pins,
                "all_text": " ".join(
                    str(p.get("title", "")) + " " + str(p.get("description", ""))
                    for p in pins
                ),
            }

        # WhatsApp
        wa = _get("whatsapp_marketing")
        if wa:
            msgs = wa.get("messages", [])
            collected["whatsapp"] = {
                "messages": msgs,
                "all_text": " ".join(str(m.get("content", "")) for m in msgs),
            }

        # Email
        em = _get("email_marketing")
        if em:
            sequences = em.get("sequences", [])
            collected["email"] = {
                "sequences": sequences,
                "all_text": " ".join(
                    str(s.get("subject", "")) + " " + str(s.get("body", ""))
                    for s in sequences
                ),
            }

        # Site / Blog
        wpp = _get("wp_publisher")
        cg = _get("content_generator")
        site_text = ""
        articles = []
        if cg:
            articles = cg.get("articles", []) or cg.get("generated_articles", [])
            if not isinstance(articles, list):
                articles = []
            site_text = " ".join(str(a.get("content", "")) for a in articles)
        collected["site"] = {
            "articles": articles,
            "all_text": site_text,
        }

        # Fallback para conteúdo do campaign
        campaign_text = " ".join(
            _normalize(campaign.get(f, ""))
            for f in ("headline", "description", "copy", "cta", "objective")
        )
        if not collected:
            collected["site"] = {"all_text": campaign_text, "articles": []}

        return collected

    # ── Verificação por Plataforma ───────────────────────────────────

    def _check_platform(
        self, rules: dict, content: dict, campaign: dict, policy: dict
    ) -> dict[str, Any]:
        issues: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        details: dict[str, Any] = {}

        all_text = content.get("all_text", _normalize(campaign.get("objective", "")))
        required_disclosures = list(policy.get("required_disclosures", []))

        # 1. Verificar termos restritos
        restricted = rules.get("restricted_terms_pt", [])
        hits = _find_restricted(all_text, restricted)
        for h in hits:
            issues.append(
                {
                    "platform": rules["name"],
                    "type": "restricted_term",
                    "detail": f"Termo restrito encontrado: '{h['term']}'",
                    "severity": h["severity"],
                    "fix": f"Remova ou substitua o termo '{h['term']}' por uma versão mais neutra.",
                }
            )

        # 2. Verificar disclosure de afiliado
        aff_rules = rules.get("affiliate_rules", [])
        has_disclosure = any(
            term.lower() in all_text.lower()
            for term in [
                "disclosure",
                "publi",
                "ad",
                "afiliado",
                "parceria",
                "publicidade",
            ]
        )
        if "requires_disclosure_in_description" in rules:
            if not has_disclosure and aff_rules:
                warnings.append(
                    {
                        "platform": rules["name"],
                        "type": "missing_disclosure",
                        "detail": "Disclosure de afiliado não encontrada no conteúdo.",
                        "severity": "high",
                        "fix": "Adicione disclosure: 'Este post contém links de afiliado...'",
                    }
                )

        # 3. Verificar práticas proibidas
        forbidden = rules.get("forbidden_practices", [])
        for fb in forbidden:
            warnings.append(
                {
                    "platform": rules["name"],
                    "type": "forbidden_practice_reminder",
                    "detail": f"Prática proibida: {fb}",
                    "severity": "medium",
                    "fix": f"Evite {fb}. Isso pode resultar em banimento.",
                }
            )

        # 4. Verificar LGPD/CAN-SPAM
        if rules.get("brazil_lgpd_required"):
            warnings.append(
                {
                    "platform": rules["name"],
                    "type": "lgpd",
                    "detail": "LGPD brasileira exige consentimento explícito para coleta de dados.",
                    "severity": "high",
                    "fix": "Implemente opt-in duplo e política de privacidade clara.",
                }
            )

        lgpd = rules.get("lgpd_requirements", [])
        for req in lgpd:
            details.setdefault("lgpd_checks", []).append(
                {
                    "requirement": req,
                    "status": "check_required",
                }
            )

        # 5. Verificar elementos obrigatórios (email marketing)
        required_el = rules.get("required_elements", [])
        for el in required_el:
            el_ok = any(e_keyword in all_text.lower() for e_keyword in el.split())
            if not el_ok:
                warnings.append(
                    {
                        "platform": rules["name"],
                        "type": "missing_required_element",
                        "detail": f"Elemento obrigatório ausente: {el}",
                        "severity": "medium",
                        "fix": f"Inclua {el} no conteúdo.",
                    }
                )

        return {
            "platform": rules["name"],
            "issues": issues,
            "warnings": warnings,
            "total_issues": len(issues) + len(warnings),
            "details": details,
        }

    @staticmethod
    def _platform_key(channel: str) -> str:
        mapping = {
            "seo": "site",
            "blog": "site",
            "newsletter": "email",
            "youtube": "youtube",
            "instagram": "instagram",
            "tiktok": "tiktok",
            "twitter": "twitter",
            "pinterest": "pinterest",
            "whatsapp": "whatsapp",
            "email": "email",
            "site": "site",
        }
        return mapping.get(channel.lower(), channel.lower())

    @staticmethod
    def _generate_recommendation(status: str, total: int) -> str:
        if status == "block":
            return (
                f"🚫 {total} issues críticas encontradas. "
                "Corrija os problemas antes de publicar em qualquer plataforma. "
                "Risco de banimento ou penalidade grave."
            )
        elif status == "warn":
            return (
                f"⚠️ {total} issues não-críticas encontradas. "
                "Recomendado corrigir antes de publicar para evitar riscos futuros."
            )
        return (
            "✅ Nenhuma issue de compliance encontrada. "
            "Conteúdo apto para publicação em todas as plataformas verificadas."
        )
