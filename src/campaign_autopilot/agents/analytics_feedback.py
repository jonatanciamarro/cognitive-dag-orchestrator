"""Agente de Feedback Analítico — coleta métricas, avalia resultados e alimenta o ciclo de aprendizado."""

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


class AnalyticsFeedbackAgent(AgentBase):
    """Avalia os resultados de um ciclo e alimenta o sistema de aprendizado.

    Este agente fecha o loop: pega o output de todos os agentes do ciclo,
    avalia o que funcionou, extrai lições, e alimenta a memória semântica
    com insights que os próximos ciclos podem usar.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("analytics_feedback", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(campaign.get("niche", campaign.get("objective", "")))
        all_steps = context.step_results

        # Coletar outputs de todos os agentes
        agent_outputs: dict[str, dict[str, Any]] = {}
        for step_id, result in all_steps.items():
            if isinstance(result, dict):
                out = result.get("output", {})
                if isinstance(out, dict):
                    agent_outputs[step_id] = out

        # Métricas agregadas do ciclo
        total_words = 0
        total_pins = 0
        total_videos = 0
        total_emails = 0
        total_articles = 0
        total_publications = 0

        for step_id, out in agent_outputs.items():
            if step_id == "content_generator":
                articles = out.get("articles", [])
                total_articles = len(articles)
                total_words += sum(a.get("word_count", 0) for a in articles)
            elif step_id == "youtube_marketing":
                videos = out.get("videos", [])
                total_videos = len(videos)
            elif step_id == "email_marketing":
                total_emails = out.get("total_emails", 0)
            elif step_id == "pinterest_marketing":
                pins = out.get("pins", [])
                total_pins = len(pins)
            elif step_id == "wp_publisher":
                pubs = out.get("publications", [])
                total_publications = len(pubs)
                for p in pubs:
                    total_words += (
                        p.get("word_count", 0)
                        if isinstance(p.get("word_count"), (int, float))
                        else 0
                    )

        # Métricas de SEO (se disponíveis)
        seo = agent_outputs.get("seo_research", {})
        total_keywords = seo.get("total_keywords_found", 0)
        opportunities = seo.get("opportunities_count", 0)

        # Métricas de compliance
        compliance = agent_outputs.get("compliance", {})
        compliance_status = compliance.get("status", "pass")

        # Gerar score de qualidade do ciclo
        cycle_score = self._calculate_cycle_score(
            total_articles=total_articles,
            total_videos=total_videos,
            total_emails=total_emails,
            total_pins=total_pins,
            total_words=total_words,
            compliance_ok=(compliance_status != "block"),
        )

        # Extrair lições
        lessons = self._extract_lessons(
            agent_outputs=agent_outputs,
            total_articles=total_articles,
            total_videos=total_videos,
            total_emails=total_emails,
            total_pins=total_pins,
            cycle_score=cycle_score,
        )

        # Sugestões para próximo ciclo
        suggestions = self._generate_suggestions(
            total_articles=total_articles,
            total_videos=total_videos,
            total_emails=total_emails,
            total_pins=total_pins,
            cycle_score=cycle_score,
        )

        output = {
            "cycle_summary": {
                "total_articles": total_articles,
                "total_videos": total_videos,
                "total_emails": total_emails,
                "total_pins": total_pins,
                "total_words_generated": total_words,
                "total_publications": total_publications,
                "total_keywords_found": total_keywords,
                "opportunities_found": opportunities,
                "compliance_status": compliance_status,
                "cycle_quality_score": cycle_score,
            },
            "lessons": lessons,
            "suggestions": suggestions,
            "niche": niche,
        }

        # Registrar explicação
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="analytics_feedback",
                input_state={"steps": list(agent_outputs.keys())},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "cycle_score": cycle_score,
                    "lessons_count": len(lessons),
                    "suggestions_count": len(suggestions),
                },
            )

        # Alimentar memória semântica com lições
        if self.semantic_memory:
            lessons_concept = self.semantic_memory.find_concept(
                "cycle_lessons", "knowledge"
            )
            if not lessons_concept:
                lessons_concept_id = self.semantic_memory.register_concept(
                    "cycle_lessons",
                    "knowledge",
                    "Lessons extracted from campaign cycles",
                )
            else:
                lessons_concept_id = lessons_concept["concept_id"]

            for i, lesson in enumerate(lessons):
                lesson_concept_id = self.semantic_memory.register_concept(
                    f"lesson_{context.run_id[:8]}_{i}",
                    "knowledge",
                    lesson[:200],
                )
                self.semantic_memory.assert_claim(
                    subject=lessons_concept_id,
                    predicate="includes",
                    object=lesson_concept_id,
                    confidence=cycle_score / 100.0,
                    evidence_type="STATISTICAL_INFERENCE",
                    epistemic_status="INFERRED",
                    supporting_data={"cycle_id": context.run_id, "score": cycle_score},
                    source_cycle_id=context.run_id,
                    asserted_by=self.name,
                    observer_id=self.name,
                )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="analytics_feedback",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Analisou ciclo: score {cycle_score}, {len(lessons)} lições, {len(suggestions)} sugestões"
            ],
            metadata={
                "cycle_score": cycle_score,
                "lessons": len(lessons),
                "suggestions": len(suggestions),
                "articles": total_articles,
                "videos": total_videos,
                "emails": total_emails,
                "pins": total_pins,
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _calculate_cycle_score(
        total_articles: int,
        total_videos: int,
        total_emails: int,
        total_pins: int,
        total_words: int,
        compliance_ok: bool,
    ) -> float:
        """Calculate a quality score for the cycle (0-100)."""
        score = 0.0

        # Content volume (max 30 points)
        if total_articles >= 3:
            score += 15
        elif total_articles >= 1:
            score += 8
        if total_videos >= 3:
            score += 10
        elif total_videos >= 1:
            score += 5
        if total_emails >= 5:
            score += 10
        elif total_emails >= 1:
            score += 4
        if total_pins >= 3:
            score += 10
        elif total_pins >= 1:
            score += 4

        # Multi-channel bonus (max 20)
        channels = sum(
            1
            for v in [
                total_articles > 0,
                total_videos > 0,
                total_emails > 0,
                total_pins > 0,
            ]
            if v
        )
        score += channels * 5

        # Word count quality (max 20)
        if total_words >= 3000:
            score += 20
        elif total_words >= 1000:
            score += 12
        elif total_words >= 300:
            score += 6

        # Compliance (penalty if blocked)
        if not compliance_ok:
            score *= 0.5

        return min(100, round(score, 1))

    @staticmethod
    def _extract_lessons(
        agent_outputs: dict[str, Any],
        total_articles: int,
        total_videos: int,
        total_emails: int,
        total_pins: int,
        cycle_score: float,
    ) -> list[str]:
        """Extract lessons from the cycle."""
        lessons = []

        if total_articles > 0:
            lessons.append(
                f"Ciclo gerou {total_articles} artigos para blog — conteúdo informacional que atrai tráfego orgânico."
            )
        if total_videos > 0:
            lessons.append(
                f"Ciclo gerou {total_videos} roteiros de vídeo para YouTube — conteúdo de alto engajamento."
            )
        if total_emails > 0:
            lessons.append(
                f"Ciclo gerou {total_emails} emails em sequências de nutrição — construção de relacionamento com leads."
            )
        if total_pins > 0:
            lessons.append(
                f"Ciclo gerou {total_pins} pins para Pinterest — tráfego evergreen de longo prazo."
            )

        channels_count = sum(
            1
            for v in [
                total_articles > 0,
                total_videos > 0,
                total_emails > 0,
                total_pins > 0,
            ]
            if v
        )
        if channels_count >= 3:
            lessons.append(
                f"Distribuição multi-canal ativa ({channels_count} canais) — aumenta resiliência do tráfego."
            )
        elif channels_count <= 1:
            lessons.append(
                "Concentração em único canal — diversificar para reduzir risco."
            )

        if cycle_score >= 80:
            lessons.append("Alta qualidade de ciclo — manter estratégia atual.")
        elif cycle_score < 40:
            lessons.append(
                "Baixa pontuação de ciclo — aumentar volume e diversificar canais."
            )

        # Insights from SEO
        seo = agent_outputs.get("seo_research", {})
        opps = seo.get("opportunities_count", 0)
        if opps > 5:
            lessons.append(
                f"Bom volume de oportunidades SEO ({opps}) — priorizar keywords de baixa dificuldade."
            )

        return lessons

    @staticmethod
    def _generate_suggestions(
        total_articles: int,
        total_videos: int,
        total_emails: int,
        total_pins: int,
        cycle_score: float,
    ) -> list[str]:
        """Generate suggestions for the next cycle."""
        suggestions = []

        if total_articles < 3:
            suggestions.append(
                "Aumentar produção de artigos para 3+ por ciclo — blog é base do tráfego orgânico."
            )
        if total_videos < 1:
            suggestions.append(
                "Adicionar produção de vídeos para YouTube — conteúdo de alto valor e tráfego consistente."
            )
        if total_emails < 3:
            suggestions.append(
                "Expandir sequências de email para nutrição e conversão de leads."
            )
        if total_pins < 3:
            suggestions.append(
                "Aumentar produção de pins para Pinterest — tráfego evergreen de longo prazo."
            )

        if cycle_score < 50:
            suggestions.append(
                "Revisar estratégia: foco em 1-2 canais de maior retorno antes de escalar."
            )

        return suggestions[:5]
