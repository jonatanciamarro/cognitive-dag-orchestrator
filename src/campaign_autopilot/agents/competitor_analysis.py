"""Agente de Análise de Concorrência — analisa concorrentes, encontra gaps de conteúdo e oportunidades."""

from __future__ import annotations

import re
from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class CompetitorAnalysisAgent(AgentBase):
    """Analisa concorrentes no nicho, encontra gaps de conteúdo e oportunidades de diferenciação.

    Funciona sem API key: faz scraping público do Google para identificar
    quem está ranqueando, o que estão publicando, e onde estão os gaps.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("competitor_analysis", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Get SEO data from other agents
        seo_scraper = context.step_results.get("seo_scraper", {})
        seo_scraper_out = (
            seo_scraper.get("output", {}) if isinstance(seo_scraper, dict) else {}
        )

        seo_research = context.step_results.get("seo_research", {})
        seo_research_out = (
            seo_research.get("output", {}) if isinstance(seo_research, dict) else {}
        )

        # Extract competitor info from SEO data
        competitors: dict[str, dict[str, Any]] = {}
        competitor_keywords: dict[str, list[str]] = {}

        # Process real scraping data
        for result in seo_scraper_out.get("results", []):
            for url in result.get("top_urls", []):
                domain = self._extract_domain(url)
                if domain:
                    if domain not in competitors:
                        competitors[domain] = {
                            "domain": domain,
                            "urls_found": [],
                            "keywords_found": [],
                            "titles_found": [],
                            "mentions": 0,
                        }
                    competitors[domain]["urls_found"].append(url)
                    competitors[domain]["keywords_found"].append(
                        result.get("keyword", "")
                    )
                    competitors[domain]["mentions"] += 1

            for title in result.get("top_titles", []):
                for domain, info in competitors.items():
                    if any(domain in url for url in info["urls_found"]):
                        info["titles_found"].append(title)

        # Process simulated SEO data as fallback
        opportunities = seo_research_out.get("top_opportunities", [])
        if not competitors and opportunities:
            # Create simulated competitors based on keywords
            for opp in opportunities[:5]:
                kw = opp.get("keyword", "")
                competitors[f"competitor_{kw[:10]}"] = {
                    "domain": f"exemplo-{kw[:10]}.com",
                    "urls_found": [
                        f"https://exemplo.com/{kw.lower().replace(' ', '-')}"
                    ],
                    "keywords_found": [kw],
                    "titles_found": [f"Guia de {kw}"],
                    "mentions": 2,
                    "note": "Dado simulado (sem acesso a scraping real)",
                }

        # Rank competitors by mentions
        ranked = sorted(competitors.values(), key=lambda x: -x["mentions"])

        # Find content gaps: keywords that few competitors cover
        keyword_counts: dict[str, int] = {}
        for info in competitors.values():
            for kw in info["keywords_found"]:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

        content_gaps = [
            {
                "keyword": kw,
                "competitors_covering": count,
                "gap_level": "high"
                if count <= 1
                else "medium"
                if count <= 2
                else "low",
            }
            for kw, count in sorted(keyword_counts.items(), key=lambda x: x[1])
        ]

        # Analyze competitor content patterns
        common_patterns = self._analyze_content_patterns(competitors)

        output = {
            "niche": niche,
            "competitors_found": len(competitors),
            "top_competitors": [
                {
                    "domain": c["domain"],
                    "pages_analyzed": len(c["urls_found"]),
                    "keywords_covered": len(set(c["keywords_found"])),
                    "sample_titles": list(set(c["titles_found"]))[:3],
                }
                for c in ranked[:10]
            ],
            "content_gaps": content_gaps[:10],
            "high_opportunity_gaps": [
                g for g in content_gaps if g["gap_level"] == "high"
            ][:5],
            "common_content_patterns": common_patterns,
            "data_source": "google_serp_scraping"
            if competitors
            and not any("simulado" in str(c) for c in competitors.values())
            else "simulated",
            "recommendation": self._generate_recommendation(
                competitors, content_gaps, common_patterns
            ),
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="competitor_analysis",
                input_state={"niche": niche, "competitors": len(competitors)},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "competitors": len(competitors),
                    "gaps": len(content_gaps),
                },
            )

        # Semantic memory
        if self.semantic_memory:
            for gap in content_gaps[:3]:
                gap_concept = self.semantic_memory.register_concept(
                    f"gap_{gap['keyword'][:20]}",
                    "knowledge",
                    f"Gap: {gap['keyword']} ({gap['competitors_covering']} concorrentes)",
                )
                self.semantic_memory.assert_claim(
                    subject=f"niche_{niche[:15]}",
                    predicate="has_content_gap",
                    object=gap_concept,
                    confidence=0.8 if gap["gap_level"] == "high" else 0.5,
                    evidence_type="STATISTICAL_INFERENCE",
                    epistemic_status="INFERRED",
                    supporting_data=gap,
                    source_cycle_id=context.run_id,
                    asserted_by=self.name,
                    observer_id=self.name,
                )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="competitor_analysis",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Analisou {len(competitors)} concorrentes, encontrou {len(content_gaps)} gaps de conteúdo"
            ],
            metadata={"competitors": len(competitors), "gaps": len(content_gaps)},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        match = re.match(r"https?://(?:www\.)?([^/]+)", url)
        return match.group(1) if match else ""

    @staticmethod
    def _analyze_content_patterns(competitors: dict) -> list[str]:
        """Analyze common patterns in competitor content."""
        patterns = []
        all_titles = []
        for info in competitors.values():
            all_titles.extend(info.get("titles_found", []))

        if not all_titles:
            return ["Sem dados suficientes para análise de padrões"]

        # Detect common title patterns
        title_text = " ".join(all_titles).lower()
        if "guia" in title_text or "guia" in title_text:
            patterns.append("Guias completos são comuns entre concorrentes")
        if (
            "review" in title_text
            or "review" in title_text
            or "vale a pena" in title_text
        ):
            patterns.append("Reviews de produtos são estratégia comum")
        if (
            "passo a passo" in title_text
            or "tutorial" in title_text
            or "como" in title_text
        ):
            patterns.append("Tutoriais passo a passo têm boa presença")
        if "melhores" in title_text or "top" in title_text:
            patterns.append("Listas e comparações são populares")

        if not patterns:
            patterns.append("Padrão não identificado — oportunidade de inovação")

        return patterns

    @staticmethod
    def _generate_recommendation(competitors: dict, gaps: list, patterns: list) -> str:
        """Generate competitive strategy recommendation."""
        top_gaps = [g for g in gaps if g["gap_level"] == "high"][:3]
        gap_keywords = ", ".join(g["keyword"] for g in top_gaps)

        if top_gaps:
            return (
                f"{len(competitors)} concorrentes identificados. "
                f"{len(gaps)} gaps de conteúdo encontrados. "
                f"Alta oportunidade em: {gap_keywords}. "
                f"Criar conteúdo aprofundado nestes tópicos com baixa concorrência."
            )
        else:
            return (
                f"{len(competitors)} concorrentes. "
                f"Concorrência estabelecida no nicho. "
                f"Foco em conteúdo de nicho específico (cauda longa) para se destacar."
            )
