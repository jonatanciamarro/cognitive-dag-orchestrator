"""Agente de Marketing no TikTok — gera scripts de vídeos curtos, trends e estratégia orgânica."""

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


_VIDEO_TEMPLATES: dict[str, dict[str, Any]] = {
    "educational": {
        "hook_template": "Você sabia que {keyword} pode {benefit}? 🚀",
        "script_template": (
            "[HOOK — 0-3s]\n"
            "Você sabia que {keyword} pode {benefit}?\n\n"
            "[PROBLEMA — 3-10s]\n"
            "A maioria das pessoas em {niche} erra porque {mistake}.\n\n"
            "[SOLUÇÃO — 10-25s]\n"
            "O segredo está em {solution}. Deixa eu te mostrar:\n"
            "🔥 {tip_1}\n"
            "🔥 {tip_2}\n"
            "🔥 {tip_3}\n\n"
            "[CTA — 25-30s]\n"
            "Salva esse vídeo para não esquecer e segue para mais dicas de {niche}! "
            "Comenta qual dessas dicas você já aplica 👇"
        ),
    },
    "review": {
        "hook_template": "{product_name} — vale a pena ou é furada? 🤔",
        "script_template": (
            "[HOOK — 0-3s]\n"
            "{product_name} — vale a pena ou é furada?\n\n"
            "[CONTEXTO — 3-8s]\n"
            "Testei {product_name} por {days} dias para dar minha opinião honesta.\n\n"
            "[PRÓS — 8-18s]\n"
            "O que EU ACHEI incrível:\n"
            "✅ {pro_1}\n"
            "✅ {pro_2}\n\n"
            "[CONTRAS — 18-25s]\n"
            "O que poderia melhorar:\n"
            "⚠️ {con_1}\n"
            "⚠️ {con_2}\n\n"
            "[VEREDITO — 25-30s]\n"
            "Veredito final: {veredito}. Link na bio para mais informações! 🎯"
        ),
    },
    "tip": {
        "hook_template": "3 dicas de {keyword} que ninguém te conta 🤫",
        "script_template": (
            "[HOOK — 0-3s]\n"
            "3 dicas de {keyword} que ninguém te conta:\n\n"
            "[DICA 1 — 3-10s]\n"
            "Número 1: {tip_1}\n"
            "Isso faz toda a diferença porque {reason_1}.\n\n"
            "[DICA 2 — 10-20s]\n"
            "Número 2: {tip_2}\n"
            "A maioria ignora, mas {reason_2}.\n\n"
            "[DICA 3 — 20-27s]\n"
            "Número 3: {tip_3}\n"
            "Essa é a dica mais importante! {reason_3}.\n\n"
            "[CTA — 27-30s]\n"
            "Segue para mais dicas de {niche} e salva esse vídeo! 🚀"
        ),
    },
}


class TikTokMarketingAgent(AgentBase):
    """Gera scripts de vídeos curtos, trends e estratégia para TikTok."""

    def __init__(self, **kwargs) -> None:
        super().__init__("tiktok_marketing", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        seo = context.step_results.get("seo_research", {})
        seo_out = seo.get("output", {}) if isinstance(seo, dict) else {}
        opportunities = seo_out.get("top_opportunities", [])

        offers_step = context.step_results.get("offer_lookup", {})
        offers_out = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        available_offers = offers_out.get("available_offers", [])

        if not opportunities:
            opportunities = [
                {
                    "keyword": str(campaign.get("objective", "marketing digital")),
                    "volume": 1000,
                    "difficulty": 0.3,
                    "intent": "informational",
                }
            ]

        videos = []
        for i, opp in enumerate(opportunities[:5]):
            keyword = opp.get("keyword", "")
            intent = opp.get("intent", "informational")

            if intent == "commercial" and available_offers:
                video_type = "review"
            elif i < 2:
                video_type = "educational"
            else:
                video_type = "tip"

            template = _VIDEO_TEMPLATES[video_type]
            product = available_offers[0] if available_offers else {}

            vars_map = {
                "keyword": keyword,
                "niche": niche,
                "product_name": product.get("product_name", ""),
                "benefit": "transformar seus resultados",
                "mistake": "tenta fazer tudo sozinho sem as ferramentas certas",
                "solution": "usar a estratégia correta com as ferramentas certas",
                "tip_1": "Comece com um planejamento estratégico",
                "tip_2": "Use ferramentas que automatizam o processo",
                "tip_3": "Mantenha consistência por pelo menos 3 meses",
                "reason_1": "planejamento evita retrabalho",
                "reason_2": "automação libera seu tempo para o que importa",
                "reason_3": "consistência é o verdadeiro segredo do sucesso",
                "days": "30",
                "pro_1": "Interface intuitiva e fácil de usar",
                "pro_2": "Suporte ao cliente excepcional",
                "con_1": "Poderia ter mais integrações",
                "con_2": "Preço um pouco salgado para iniciantes",
                "veredito": "RECOMENDO para quem já tem uma base",
            }

            hook = template["hook_template"]
            for k, v in vars_map.items():
                hook = hook.replace(f"{{{k}}}", str(v))

            script = template["script_template"]
            for k, v in vars_map.items():
                script = script.replace(f"{{{k}}}", str(v))

            hashtags = self._generate_hashtags(keyword, niche)

            videos.append(
                {
                    "hook": hook,
                    "script": script,
                    "video_type": video_type,
                    "hashtags": hashtags[:10],
                    "keyword": keyword,
                    "duration_seconds": 30,
                    "best_time_to_post": "19:00-22:00 (horário de pico no Brasil)",
                    "strategy_note": "Vídeos educativos e de dicas geram mais salvamentos e engajamento.",
                    "trend_suggestion": "Usar som trending + texto na tela + legenda automática para acessibilidade.",
                }
            )

        output = {
            "videos": videos,
            "total_videos": len(videos),
            "niche": niche,
            "recommendation": (
                f"Criar {len(videos)} vídeos para TikTok. Postar 1 vídeo por dia. "
                f"TikTok tem o melhor alcance orgânico entre todas as redes sociais. "
                f"Usar link na bio para direcionar para lead capture ou afiliado."
            ),
        }

        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="tiktok_marketing",
                input_state={"opportunities": len(opportunities), "niche": niche},
            )
            self.explanation_store.update_decision_output(did, {"videos": len(videos)})

        if self.semantic_memory:
            for v in videos:
                vc = self.semantic_memory.register_concept(
                    f"tt_{v['keyword'][:15]}",
                    "content",
                    v["hook"][:100],
                )
                nc = self.semantic_memory.find_concept(niche, "niche")
                if nc:
                    self.semantic_memory.assert_claim(
                        subject=nc["concept_id"],
                        predicate="has_tiktok_video",
                        object=vc,
                        confidence=0.7,
                        evidence_type="DIRECT_OBSERVATION",
                        epistemic_status="INFERRED",
                        supporting_data={"type": v["video_type"]},
                        source_cycle_id=context.run_id,
                        asserted_by=self.name,
                        observer_id=self.name,
                    )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="tiktok_marketing",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Gerou {len(videos)} scripts TikTok para nicho '{niche}'"],
            metadata={"videos": len(videos), "niche": niche},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _generate_hashtags(keyword: str, niche: str) -> list[str]:
        tags = set()
        for w in keyword.lower().split() + niche.lower().split():
            if len(w) > 2:
                tags.add(f"#{w}")
        extra = {
            "marketing": [
                "#marketingdigital",
                "#afiliados",
                "#rendaextra",
                "#empreendedorismo",
            ],
            "financas": ["#financaspessoais", "#investimentos", "#educacaofinanceira"],
            "tecnologia": ["#tecnologia", "#ferramentas", "#produtividade"],
        }
        for key, ext in extra.items():
            if key in keyword.lower() or key in niche.lower():
                tags.update(ext)
        return list(tags)[:12]
