"""Agente de Growth Hacking Orgânico — analisa todos os canais e maximiza resultados com estratégias de crescimento viral, SEO avançado e cross-pollination."""

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


# ── Estratégias de Growth Hacking Orgânico ─────────────────────────

_GROWTH_STRATEGIES: dict[str, dict[str, Any]] = {
    "pillar_cluster": {
        "name": "Pillar Page + Topic Cluster",
        "effort": "medium",
        "impact": "very_high",
        "time_to_result": "2-4 meses",
        "description": (
            "Criar uma página piloto (guia completo) sobre o tema central do nicho "
            "e 5-10 artigos cluster que linkam para a piloto. O Google reconhece "
            "a autoridade temática e rankeia melhor todos os artigos."
        ),
        "implementation": [
            "Identificar o tema central do nicho (ex: 'marketing de afiliados')",
            "Criar guia completo de 3000+ palavras como página piloto",
            "Criar 5-10 artigos cluster linkando para a piloto",
            "A piloto linka para todos os clusters",
            "Usar anchor text variados e naturais",
        ],
        "kpi": "Aumento de 30-50% no tráfego orgânico em 3 meses",
    },
    "skyscraper": {
        "name": "Skyscraper Technique (Backlinks)",
        "effort": "high",
        "impact": "very_high",
        "time_to_result": "3-6 meses",
        "description": (
            "Encontrar conteúdo bem-linkado no nicho, criar uma versão superior "
            "(mais completa, atualizada, visual) e contactar quem linkou o original "
            "para linkar o seu."
        ),
        "implementation": [
            "Encontrar artigos populares com muitos backlinks no nicho",
            "Criar versão 2x melhor (mais dados, infográficos, exemplos)",
            "Identificar sites que linkaram o original",
            "Contactar sugerindo substituição pelo conteúdo superior",
            "Oferecer valor adicional (infográfico para embed)",
        ],
        "kpi": "10-20 novos backlinks de autoridade em 3 meses",
    },
    "featured_snippet": {
        "name": "Featured Snippet Optimization",
        "effort": "low",
        "impact": "high",
        "time_to_result": "1-2 meses",
        "description": (
            "Otimizar conteúdo para aparecer nos featured snippets do Google "
            "(position zero). Isso aumenta significativamente o CTR e a autoridade."
        ),
        "implementation": [
            "Pesquisar perguntas frequentes do nicho (PAA - People Also Ask)",
            "Criar seções de resposta direta (definition, list, table, step-by-step)",
            "Usar formato pergunta-resposta com <h2> ou <h3>",
            "Incluir listas ordenadas e tabelas quando relevante",
            "Manter respostas concisas (40-50 palavras) seguidas de aprofundamento",
        ],
        "kpi": "5-10 featured snippets em 2 meses",
    },
    "internal_linking": {
        "name": "Internal Linking Optimization",
        "effort": "low",
        "impact": "high",
        "time_to_result": "1-2 meses",
        "description": (
            "Estruturar links internos para distribuir link juice e ajudar o Google "
            "a entender a hierarquia do conteúdo. Artigos âncora linkam para artigos "
            "de conversão."
        ),
        "implementation": [
            "Mapear todos os artigos por tema e autoridade",
            "Artigos informacionais linkam para artigos de conversão (comerciais)",
            "Usar anchor text ricos em keywords",
            "Mínimo 3-5 links internos por artigo",
            "Links contextuais (não apenas no final do artigo)",
        ],
        "kpi": "Aumento de 15-25% nas páginas por sessão",
    },
    "cross_channel_syndication": {
        "name": "Cross-Channel Syndication",
        "effort": "medium",
        "impact": "high",
        "time_to_result": "1-2 meses",
        "description": (
            "Distribuir cada conteúdo em múltiplos formatos e canais, "
            "criando uma rede de backlinks e exposição máxima."
        ),
        "implementation": [
            "Artigo do blog → YouTube vídeo → Pinterest pins → Twitter thread",
            "YouTube vídeo → Blog post (transcrição) → LinkedIn article",
            "Twitter thread → Blog post expandido → Email newsletter",
            "Adicionar links entre todas as versões do mesmo conteúdo",
            "Usar UTM parameters para tracking cross-channel",
        ],
        "kpi": "3-5x mais exposição por peça de conteúdo",
    },
    "content_upgrade": {
        "name": "Content Upgrades para Email List",
        "effort": "medium",
        "impact": "high",
        "time_to_result": "Imediato",
        "description": (
            "Oferecer um bônus baixável em cada artigo em troca do email. "
            "Checklists, templates, planilhas e ebooks têm alta conversão."
        ),
        "implementation": [
            "Identificar artigos com maior tráfego orgânico",
            "Criar upgrade de conteúdo específico para cada artigo",
            "Inserir call-to-action no meio e no final do artigo",
            "Entregar automaticamente por email após cadastro",
            "Medir taxa de conversão de cada upgrade",
        ],
        "kpi": "5-15% de taxa de conversão de visitante para lead",
    },
    "evergreen_refresh": {
        "name": "Evergreen Content Refresh",
        "effort": "low",
        "impact": "medium",
        "time_to_result": "1-2 meses",
        "description": (
            "Atualizar conteúdo perene (evergreen) regularmente para manter "
            "relevância e sinalizar frescor para o Google."
        ),
        "implementation": [
            "Identificar artigos evergreen com tráfego em declínio",
            "Atualizar dados, estatísticas e exemplos",
            "Adicionar novas seções com tendências atuais",
            "Atualizar ano no título e no conteúdo",
            "Republicar com data atualizada",
        ],
        "kpi": "Aumento de 20-40% no tráfego de artigos atualizados",
    },
    "social_proof_boost": {
        "name": "Social Proof Boost",
        "effort": "low",
        "impact": "medium",
        "time_to_result": "Imediato",
        "description": (
            "Adicionar elementos de prova social nos artigos e landing pages "
            "para aumentar confiança e conversão."
        ),
        "implementation": [
            "Adicionar contador de compartilhamentos nos artigos",
            "Mostrar número de comentários ou avaliações",
            "Incluir depoimentos de leitores/clientes",
            "Badges de autoridade (featured in, as seen on)",
            "Número de inscritos/seguidores nas redes",
        ],
        "kpi": "Aumento de 10-20% no tempo na página e conversão",
    },
    "faq_schema": {
        "name": "FAQ Schema & Rich Results",
        "effort": "low",
        "impact": "high",
        "time_to_result": "1-2 meses",
        "description": (
            "Adicionar marcação FAQ schema nos artigos para aparecer "
            "como rich results no Google, ocupando mais espaço nos resultados."
        ),
        "implementation": [
            "Adicionar seção de FAQ em cada artigo",
            "Implementar FAQ schema (JSON-LD)",
            "Perguntas devem ser baseadas em PAA (People Also Ask)",
            "Incluir pelo menos 3-5 perguntas por artigo",
            "Manter respostas concisas e diretas",
        ],
        "kpi": "Aumento de 5-15% no CTR orgânico",
    },
    "broken_link_building": {
        "name": "Broken Link Building",
        "effort": "high",
        "impact": "high",
        "time_to_result": "2-4 meses",
        "description": (
            "Encontrar links quebrados em sites do nicho e sugerir seu "
            "conteúdo como substituto. Ganha backlinks e ajuda webmasters."
        ),
        "implementation": [
            "Usar ferramentas (Check My Links, Ahrefs) para achar links quebrados",
            "Identificar páginas com autoridade no nicho",
            "Criar conteúdo substituto (ou verificar se já tem conteúdo relevante)",
            "Contactar webmaster informando o link quebrado",
            "Sugerir seu conteúdo como substituto de valor",
        ],
        "kpi": "5-15 backlinks de qualidade em 3 meses",
    },
    "video_seo_boost": {
        "name": "YouTube Video SEO Boost",
        "effort": "medium",
        "impact": "high",
        "time_to_result": "1-3 meses",
        "description": (
            "Otimizar vídeos do YouTube para busca, incluindo transcrições "
            "e embeds nos artigos do blog para aumentar sinais de engajamento."
        ),
        "implementation": [
            "Embedar vídeos do YouTube nos artigos relacionados do blog",
            "Adicionar transcrição completa do vídeo abaixo do vídeo no YouTube",
            "Links do vídeo na descrição apontando para o artigo completo",
            "Cards e end screens para aumentar tempo de exibição",
            "OTIMIZAR: título, descrição, tags, thumbnail",
        ],
        "kpi": "Aumento de 50-100% nas visualizações do YouTube",
    },
}

# ── Estratégias de Marketing Viral ────────────────────────────────

_VIRAL_STRATEGIES: list[dict[str, Any]] = [
    {
        "name": "Share Triggers",
        "description": "Adicionar gatilhos de compartilhamento no conteúdo.",
        "tactics": [
            "Citações destacadas com botão de compartilhar (Click to Tweet)",
            "Infográficos com embed code para outros sites",
            "Estatísticas impressionantes formatadas para compartilhamento",
            "Checklists imprimíveis que as pessoas compartilham",
            "Frases de efeito no final de cada seção",
        ],
        "expected_boost": "2-3x mais compartilhamentos",
    },
    {
        "name": "Viral Loop Mechanics",
        "description": "Criar ciclos onde o usuário traz mais usuários.",
        "tactics": [
            "Conteúdo interativo (calculadoras, quizzes) com compartilhamento obrigatório para ver resultado",
            "Desafios e competições com premiação por indicação",
            "Conteúdo colaborativo onde leitores contribuem e compartilham",
            "Email marketing com incentivo para forward (ex: 'encaminhe para um amigo')",
        ],
        "expected_boost": "Crescimento exponencial da base",
    },
    {
        "name": "Social Proof Triggers",
        "description": "Usar psicologia social para aumentar engajamento.",
        "tactics": [
            "Mostrar contadores de 'pessoas lendo agora'",
            "Notificações de compras recentes (fake social proof para urgência)",
            "Badges de 'mais compartilhado' nos artigos populares",
            "Seção de comentários com destaque para os mais engajados",
        ],
        "expected_boost": "Aumento de 15-30% no engajamento",
    },
    {
        "name": "Reciprocity Marketing",
        "description": "Oferecer valor antes de pedir algo em troca.",
        "tactics": [
            "Ferramentas gratuitas (calculadoras, geradores, templates)",
            "Guias completos resolvendo um problema específico",
            "Consultoria gratuita limitada (estratégia de escassez)",
            "Amostras grátis de produtos digitais",
        ],
        "expected_boost": "Alta taxa de conversão de lead para cliente",
    },
]

# ── Estratégias de SEO Avançado ───────────────────────────────────

_ADVANCED_SEO: list[dict[str, Any]] = [
    {
        "name": "Entity SEO",
        "description": "Otimizar para entidades (pessoas, marcas, lugares) em vez de apenas keywords.",
        "tactics": [
            "Mapear entidades relevantes do nicho",
            "Criar conteúdo sobre cada entidade",
            "Usar schema.org markup para entidades (Person, Organization, Product)",
            "Construir autoridade temática (Topic Authority)",
            "Links para fontes autoritativas (Wikipedia, gov, edu)",
        ],
    },
    {
        "name": "Search Intent Optimization",
        "description": "Alinhar conteúdo com a intenção de busca exata.",
        "tactics": [
            "Mapear intenção de cada keyword (informational, commercial, transactional, navigational)",
            "Criar formato de conteúdo adequado para cada intenção",
            "Informational: guias, tutoriais, listas",
            "Commercial: reviews, comparativos, melhores",
            "Transactional: landing pages, preços, CTAs",
        ],
    },
    {
        "name": "HARO / Source Building",
        "description": "Conseguir backlinks de autoridade respondendo a consultas de jornalistas.",
        "tactics": [
            "Cadastrar em plataformas como HARO, SourceBottle, Qwoted",
            "Responder consultas relacionadas ao nicho",
            "Oferecer dados exclusivos ou opinião de especialista",
            "Incluir link para seu conteúdo na resposta",
        ],
    },
]


class OrganicTrafficGrowthHackerAgent(AgentBase):
    """Agente de Growth Hacking especializado em tráfego orgânico.

    Analisa todos os canais e outputs do ciclo e gera recomendações
    estratégicas para maximizar o crescimento orgânico usando:
    - SEO avançado (pillar clusters, featured snippets, entity SEO)
    - Viral growth loops (share triggers, social proof)
    - Cross-channel syndication
    - Content upgrades e email list growth
    - Backlink building (skyscraper, broken links, HARO)
    - Evergreen content refresh
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("organic_growth", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        step_results = context.step_results

        # Coletar outputs dos agentes
        contents = self._collect_content(step_results, campaign)

        # Gerar recomendações
        recommendations = self._generate_recommendations(contents, niche, step_results)

        # Identificar estratégias aplicáveis
        applicable_strategies = self._find_applicable_strategies(contents, niche)

        # Identificar táticas virais aplicáveis
        viral_opportunities = self._find_viral_opportunities(contents, niche)

        # SEO avançado recomendado
        seo_recommendations = self._recommend_advanced_seo(contents, niche)

        # Estimar impacto
        impact_estimate = self._estimate_impact(applicable_strategies)

        output = {
            "status": "success",
            "niche": niche,
            "recommended_strategies": applicable_strategies,
            "viral_opportunities": viral_opportunities,
            "advanced_seo": seo_recommendations,
            "actionable_recommendations": recommendations,
            "impact_estimate": impact_estimate,
            "total_recommendations": len(recommendations),
            "priority_actions": [
                r for r in recommendations if r.get("priority") in ("critical", "high")
            ][:5],
            "summary": self._generate_summary(len(recommendations), impact_estimate),
        }

        # Explanation store
        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="organic_growth_analysis",
                input_state={"niche": niche, "contents": len(contents)},
            )
            self.explanation_store.update_decision_output(
                did,
                output_decision={"recommendations": len(recommendations)},
            )

        # Semantic memory
        if self.semantic_memory:
            niche_concept = self.semantic_memory.find_concept(niche, "niche")
            for rec in recommendations[:3]:
                rec_cid = self.semantic_memory.register_concept(
                    f"growth_{rec['type'][:15]}",
                    "growth_strategy",
                    rec["action"][:100],
                )
                if niche_concept:
                    self.semantic_memory.assert_claim(
                        subject=niche_concept["concept_id"],
                        predicate="has_growth_strategy",
                        object=rec_cid,
                        confidence=0.8,
                        evidence_type="EXPERT_OPINION",
                        epistemic_status="INFERRED",
                        supporting_data={"priority": rec.get("priority")},
                        source_cycle_id=context.run_id,
                        asserted_by=self.name,
                        observer_id=self.name,
                    )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="organic_growth",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(recommendations)} recomendações de growth para nicho '{niche}'. "
                f"{len(applicable_strategies)} estratégias aplicáveis identificadas."
            ],
            metadata={
                "recommendations": len(recommendations),
                "strategies": len(applicable_strategies),
                "viral_ops": len(viral_opportunities),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    # ── Coleta de Conteúdo ──────────────────────────────────────

    def _collect_content(self, step_results: dict, campaign: dict) -> dict[str, Any]:
        """Coleta todo o conteúdo gerado no ciclo para análise."""
        collected: dict[str, Any] = {}
        collected["articles"] = []
        collected["keywords"] = []
        collected["channels"] = list(campaign.get("channels", ["seo"]))

        def _get(step_id: str) -> dict:
            s = step_results.get(step_id, {})
            o = s.get("output", {}) if isinstance(s, dict) else {}
            return o if isinstance(o, dict) else {}

        # Content Generator
        cg = _get("content_generator")
        if cg:
            articles = cg.get("articles", []) or cg.get("generated_articles", [])
            if isinstance(articles, list):
                collected["articles"] = articles

        # SEO Research
        sr = _get("seo_research")
        if sr:
            collected["keywords"] = sr.get("top_opportunities", []) or sr.get(
                "keywords", []
            )

        # SEO Scraper
        ss = _get("seo_scraper")
        if ss:
            collected["seo_data"] = ss

        # Count content across channels
        channel_counts = {}
        for ch in [
            "youtube_marketing",
            "instagram_marketing",
            "tiktok_marketing",
            "twitter_marketing",
            "pinterest_marketing",
            "whatsapp_marketing",
            "email_marketing",
            "lead_capture",
        ]:
            out = _get(ch)
            if out:
                videos = (
                    out.get("videos", [])
                    or out.get("posts", [])
                    or out.get("threads", [])
                    or out.get("pins", [])
                    or out.get("messages", [])
                    or out.get("sequences", [])
                )
                channel_counts[ch.replace("_marketing", "")] = (
                    len(videos) if isinstance(videos, list) else 0
                )
        collected["channel_counts"] = channel_counts

        # Campaign info
        collected["niche"] = str(campaign.get("objective", campaign.get("niche", "")))

        return collected

    # ── Geração de Recomendações ────────────────────────────────

    def _generate_recommendations(
        self, contents: dict, niche: str, step_results: dict
    ) -> list[dict[str, Any]]:
        """Generate actionable growth recommendations."""
        recs: list[dict[str, Any]] = []

        # 1. Pillar Page Strategy
        articles = contents.get("articles", [])
        if len(articles) >= 2:
            recs.append(
                {
                    "type": "pillar_cluster",
                    "priority": "high",
                    "action": f"Criar página piloto sobre '{niche}' e interlinkar com {len(articles)} artigos existentes",
                    "rationale": "Topic clusters aumentam autoridade temática e melhoram ranking de todos os artigos",
                    "effort": "medium",
                    "impact": "very_high",
                    "timeframe": "2-4 meses",
                }
            )

        # 2. Internal Linking
        if len(articles) >= 2:
            recs.append(
                {
                    "type": "internal_linking",
                    "priority": "high",
                    "action": f"Criar malha de links internos entre os {len(articles)} artigos",
                    "rationale": "Links internos distribuem link juice e ajudam o Google a entender hierarquia",
                    "effort": "low",
                    "impact": "high",
                    "timeframe": "1-2 meses",
                    "specifics": [
                        "Artigo 1 → link para artigo 2 com anchor text rico",
                        "Artigos informacionais → link para artigos de conversão",
                        "Mínimo 3 links internos por artigo",
                    ],
                }
            )

        # 3. Content Upgrades
        if articles:
            recs.append(
                {
                    "type": "content_upgrade",
                    "priority": "high",
                    "action": "Criar conteúdo upgrade (checklist/template/PDF) para cada artigo",
                    "rationale": "Content upgrades convertem 5-15% dos visitantes em leads de email",
                    "effort": "medium",
                    "impact": "high",
                    "timeframe": "Imediato",
                }
            )

        # 4. Featured Snippet
        keyword_count = len(contents.get("keywords", []))
        if keyword_count > 0:
            recs.append(
                {
                    "type": "featured_snippet",
                    "priority": "high",
                    "action": f"Otimizar {min(keyword_count, 5)} artigos para featured snippets do Google",
                    "rationale": "Position zero aumenta CTR significativamente e gera tráfego adicional",
                    "effort": "low",
                    "impact": "high",
                    "timeframe": "1-2 meses",
                    "specifics": [
                        "Adicionar seção de FAQ no final de cada artigo",
                        "Usar formato pergunta → resposta direta (40-50 palavras)",
                        "Implementar FAQ Schema (JSON-LD)",
                    ],
                }
            )

        # 5. Cross-Channel
        channel_counts = contents.get("channel_counts", {})
        active_channels = [ch for ch, cnt in channel_counts.items() if cnt > 0]
        if len(active_channels) >= 2:
            recs.append(
                {
                    "type": "cross_channel_syndication",
                    "priority": "medium",
                    "action": f"Cross-syndicate conteúdo entre {len(active_channels)} canais ativos",
                    "rationale": "Cada conteúdo em múltiplos formatos gera 3-5x mais exposição",
                    "effort": "medium",
                    "impact": "high",
                    "timeframe": "1-2 meses",
                    "channels": active_channels,
                }
            )

        # 6. Social Sharing
        recs.append(
            {
                "type": "share_triggers",
                "priority": "medium",
                "action": "Adicionar share triggers no conteúdo (Click to Tweet, infográficos, quotes)",
                "rationale": "Facilitar o compartilhamento aumenta exposição orgânica e backlinks",
                "effort": "low",
                "impact": "medium",
                "timeframe": "Imediato",
            }
        )

        # 7. FAQ Schema
        recs.append(
            {
                "type": "faq_schema",
                "priority": "medium",
                "action": "Implementar FAQ schema em todos os artigos",
                "rationale": "Rich results ocupam mais espaço no Google e aumentam CTR em 5-15%",
                "effort": "low",
                "impact": "high",
                "timeframe": "1-2 meses",
            }
        )

        # 8. Video SEO
        yt_videos = channel_counts.get("youtube", 0)
        if yt_videos > 0:
            recs.append(
                {
                    "type": "video_seo_boost",
                    "priority": "high",
                    "action": f"Embedar {yt_videos} vídeos do YouTube nos artigos do blog e adicionar transcrições",
                    "rationale": "Vídeos embedados aumentam tempo na página e sinais de engajamento",
                    "effort": "medium",
                    "impact": "high",
                    "timeframe": "1-3 meses",
                }
            )

        # 9. Broken Link Building
        recs.append(
            {
                "type": "broken_link_building",
                "priority": "medium",
                "action": f"Identificar links quebrados em sites do nicho '{niche}' e oferecer conteúdo substituto",
                "rationale": "Backlinks de qualidade aumentam autoridade de domínio e rankings",
                "effort": "high",
                "impact": "high",
                "timeframe": "2-4 meses",
            }
        )

        # 10. Evergreen Refresh
        if articles:
            recs.append(
                {
                    "type": "evergreen_refresh",
                    "priority": "medium",
                    "action": "Agendar refresh trimestral de artigos evergreen com dados atualizados",
                    "rationale": "Conteúdo atualizado sinaliza frescor para o Google e recupera tráfego",
                    "effort": "low",
                    "impact": "medium",
                    "timeframe": "1-2 meses",
                }
            )

        # 11. Email Lead Magnets
        recs.append(
            {
                "type": "lead_magnet",
                "priority": "critical",
                "action": f"Criar lead magnet específico para '{niche}' e capturar emails em todos os artigos",
                "rationale": "Lista de email é o ativo mais valioso para monetização a longo prazo",
                "effort": "medium",
                "impact": "very_high",
                "timeframe": "Imediato",
            }
        )

        # 12. Entity SEO
        recs.append(
            {
                "type": "entity_seo",
                "priority": "medium",
                "action": "Mapear entidades do nicho e criar conteúdo sobre cada uma",
                "rationale": "Entity SEO é o futuro da busca no Google (Knowledge Graph)",
                "effort": "medium",
                "impact": "high",
                "timeframe": "3-6 meses",
            }
        )

        return recs

    # ── Estratégias Aplicáveis ──────────────────────────────────

    def _find_applicable_strategies(
        self, contents: dict, niche: str
    ) -> list[dict[str, Any]]:
        """Find which growth strategies are applicable to this cycle."""
        applicable = []
        articles = contents.get("articles", [])

        for key, strategy in _GROWTH_STRATEGIES.items():
            strategy_info = {
                "key": key,
                "name": strategy["name"],
                "effort": strategy["effort"],
                "impact": strategy["impact"],
                "timeframe": strategy["time_to_result"],
                "description": strategy["description"],
                "implementation": strategy["implementation"],
            }
            applicable.append(strategy_info)

        return applicable

    # ── Oportunidades Virais ────────────────────────────────────

    def _find_viral_opportunities(
        self, contents: dict, niche: str
    ) -> list[dict[str, Any]]:
        """Identify viral growth opportunities."""
        return [
            {
                "name": v["name"],
                "description": v["description"],
                "tactics": v["tactics"],
                "expected_boost": v["expected_boost"],
            }
            for v in _VIRAL_STRATEGIES
        ]

    # ── SEO Avançado ────────────────────────────────────────────

    def _recommend_advanced_seo(
        self, contents: dict, niche: str
    ) -> list[dict[str, Any]]:
        """Recommend advanced SEO strategies."""
        return [
            {
                "name": seo["name"],
                "description": seo["description"],
                "tactics": seo["tactics"],
            }
            for seo in _ADVANCED_SEO
        ]

    # ── Estimativa de Impacto ───────────────────────────────────

    def _estimate_impact(self, strategies: list[dict]) -> dict[str, Any]:
        """Estimate combined impact of recommended strategies."""
        high_impact = sum(1 for s in strategies if s.get("impact") == "very_high")
        medium_impact = sum(1 for s in strategies if s.get("impact") == "high")

        return {
            "very_high_impact_strategies": high_impact,
            "high_impact_strategies": medium_impact,
            "estimated_traffic_increase_3_months": f"{high_impact * 30 + medium_impact * 15}%+",
            "estimated_lead_increase": "5-15% com content upgrades",
            "estimated_backlinks": "10-35 novos backlinks em 3 meses",
            "note": "Resultados reais dependem de execução consistente e qualidade do conteúdo.",
        }

    # ── Sumário ─────────────────────────────────────────────────

    @staticmethod
    def _generate_summary(rec_count: int, impact: dict) -> str:
        return (
            f"📈 **Growth Hacking Analysis Complete**\n\n"
            f"Foram geradas **{rec_count} recomendações** estratégicas para maximizar o tráfego orgânico.\n\n"
            f"**Estratégias de alto impacto:** {impact.get('very_high_impact_strategies', 0)} very high, "
            f"{impact.get('high_impact_strategies', 0)} high\n"
            f"**Estimativa de crescimento:** {impact.get('estimated_traffic_increase_3_months', '30%+')} em 3 meses\n"
            f"**Backlinks estimados:** {impact.get('estimated_backlinks', '10-35')}\n\n"
            f"**Prioridade imediata:** Implementar content upgrades para capturar leads + "
            f"otimizar featured snippets + criar pillar cluster.\n"
            f"Crescimento orgânico sustentável é construído com consistência e valor real."
        )
