"""Agente de Marketing no Twitter/X — gera threads, posts e estratégia de tráfego."""

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


_THREAD_TEMPLATES: dict[str, dict[str, Any]] = {
    "educational_thread": {
        "first_tweet_template": (
            "🧵 {keyword} — GUIA COMPLETO PARA INICIANTES\n\n"
            "Aprenda tudo que você precisa saber sobre {keyword} em {niche}.\n\n"
            "Vou explicar em {number} tweets. Vamos lá! 👇"
        ),
        "middle_tweets": [
            "1/ O que é {keyword}?\n\n{definition}",
            "2/ Por que {keyword} é importante para {niche}?\n\n{importance}",
            "3/ Como começar com {keyword}?\n\n{how_to_start}",
            "4/ Erros comuns em {keyword}:\n\n{mistakes}",
            "5/ Ferramentas recomendadas para {keyword}:\n\n{tools}",
            "6/ Dica bônus:\n\n{bonus_tip}",
        ],
        "last_tweet_template": (
            "7/ Conclusão\n\n{conclusion}\n\n"
            "Se esse thread te ajudou, dá um like 🫶, retweet 🔄 e segue para mais conteúdo sobre {niche}!\n\n"
            "Tem algum comentário? Deixa aqui embaixo 👇"
        ),
    },
    "tip_post": {
        "template": (
            "⚡ DICA RÁPIDA DE {niche}\n\n"
            "{tip}\n\n"
            "Isso funciona porque {reason}.\n\n"
            "Teste hoje e me conta nos comentários!\n\n"
            "{hashtags}"
        ),
    },
    "question": {
        "template": (
            "🤔 PERGUNTA PARA VOCÊ:\n\n"
            "{question}\n\n"
            "{context}\n\n"
            "Me conta nos comentários! 👇\n\n"
            "{hashtags}"
        ),
    },
}


class TwitterMarketingAgent(AgentBase):
    """Gera threads, posts e estratégia para Twitter/X."""

    def __init__(self, **kwargs) -> None:
        super().__init__("twitter_marketing", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        seo = context.step_results.get("seo_research", {})
        seo_out = seo.get("output", {}) if isinstance(seo, dict) else {}
        opportunities = seo_out.get("top_opportunities", [])

        if not opportunities:
            opportunities = [
                {
                    "keyword": str(campaign.get("objective", "marketing digital")),
                    "volume": 1000,
                    "difficulty": 0.3,
                    "intent": "informational",
                }
            ]

        threads = []
        posts = []
        for i, opp in enumerate(opportunities[:3]):
            keyword = opp.get("keyword", "")

            # Create a thread for each keyword
            tmpl = _THREAD_TEMPLATES["educational_thread"]
            number = "7"

            vars_map = {
                "keyword": keyword,
                "niche": niche,
                "number": number,
                "definition": f"É a estratégia de usar {keyword} para gerar resultados em {niche}.",
                "importance": f"Porque {niche} está cada vez mais competitivo e quem domina {keyword} sai na frente.",
                "how_to_start": "1. Estude o básico\n2. Escolha suas ferramentas\n3. Crie um plano\n4. Execute com consistência\n5. Acompanhe os resultados",
                "mistakes": "❌ Não ter um plano\n❌ Desistir cedo demais\n❌ Não medir resultados\n❌ Copiar sem adaptar",
                "tools": "🔹 Ferramenta A — para análise\n🔹 Ferramenta B — para execução\n🔹 Ferramenta C — para monitoramento",
                "bonus_tip": "Consistência sempre vence intensidade. 1% melhor a cada dia.",
                "conclusion": f"{keyword} é uma habilidade que qualquer pessoa em {niche} pode desenvolver com prática e as ferramentas certas.",
            }

            first = tmpl["first_tweet_template"]
            for k, v in vars_map.items():
                first = first.replace(f"{{{k}}}", str(v))

            middle = []
            for t in tmpl["middle_tweets"]:
                t2 = t
                for k, v in vars_map.items():
                    t2 = t2.replace(f"{{{k}}}", str(v))
                middle.append(t2)

            last = tmpl["last_tweet_template"]
            for k, v in vars_map.items():
                last = last.replace(f"{{{k}}}", str(v))

            hashtags = self._generate_hashtags(keyword, niche)

            threads.append(
                {
                    "keyword": keyword,
                    "first_tweet": first,
                    "middle_tweets": middle,
                    "last_tweet": last,
                    "total_tweets": len(middle) + 2,
                    "hashtags": hashtags[:10],
                    "best_time_to_post": "12:00-14:00 ou 19:00-21:00 (horário de pico no Brasil)",
                }
            )

            # Create a tip post
            tip_tmpl = _THREAD_TEMPLATES["tip_post"]["template"]
            tip_vars = {
                "niche": niche,
                "tip": f"Comece criando conteúdo sobre {keyword} consistentemente por 30 dias.",
                "reason": "o algoritmo do Twitter prioriza contas que postam regularmente",
                "hashtags": " ".join(hashtags[:5]),
            }
            tip_text = tip_tmpl
            for k, v in tip_vars.items():
                tip_text = tip_text.replace(f"{{{k}}}", str(v))
            posts.append(
                {
                    "type": "tip",
                    "content": tip_text,
                }
            )

            # Create a question post
            q_tmpl = _THREAD_TEMPLATES["question"]["template"]
            q_vars = {
                "question": f"Qual sua maior dificuldade com {keyword}?",
                "context": f"Estou preparando um conteúdo completo sobre {keyword} para {niche} e quero saber o que você mais precisa.",
                "hashtags": " ".join(hashtags[:5]),
            }
            q_text = q_tmpl
            for k, v in q_vars.items():
                q_text = q_text.replace(f"{{{k}}}", str(v))
            posts.append(
                {
                    "type": "question",
                    "content": q_text,
                }
            )

        output = {
            "threads": threads,
            "total_threads": len(threads),
            "posts": posts,
            "total_posts": len(posts),
            "niche": niche,
            "recommendation": (
                f"Criar {len(threads)} threads e {len(posts)} posts para Twitter. "
                f"Postar 1 thread por semana + 3 posts de dicas. "
                f"Twitter é excelente para construir autoridade e rede de contatos. "
                f"Incluir link do lead capture na bio."
            ),
        }

        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="twitter_marketing",
                input_state={"opportunities": len(opportunities), "niche": niche},
            )
            self.explanation_store.update_decision_output(
                did, {"threads": len(threads)}
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="twitter_marketing",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(threads)} threads + {len(posts)} posts para Twitter no nicho '{niche}'"
            ],
            metadata={"threads": len(threads), "posts": len(posts), "niche": niche},
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
            "marketing": ["#MarketingDigital", "#Afiliados", "#Empreendedorismo"],
            "financas": ["#FinancasPessoais", "#RendaExtra", "#Investimentos"],
            "tecnologia": ["#Tecnologia", "#Inovacao", "#Produtividade"],
        }
        for key, ext in extra.items():
            if key in keyword.lower() or key in niche.lower():
                tags.update(ext)
        return list(tags)[:12]
