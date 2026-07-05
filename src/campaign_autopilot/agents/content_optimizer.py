"""Agente de Otimização de Conteúdo — analisa artigos e sugere melhorias SEO."""

from __future__ import annotations

import re
from typing import Any
from collections import Counter

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class ContentOptimizerAgent(AgentBase):
    """Analisa conteúdo gerado e sugere melhorias para SEO, legibilidade e conversão.

    Verifica:
    - Densidade de palavras-chave
    - Estrutura de headings
    - Meta description
    - Comprimento do conteúdo
    - Links internos e externos
    - Disclosure de afiliado
    - Call to action
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("content_optimizer", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Get articles
        gen = context.step_results.get("content_generator", {})
        gen_out = gen.get("output", {}) if isinstance(gen, dict) else {}
        articles = gen_out.get("articles", [])

        # Get repurposed content
        rp = context.step_results.get("content_repurposer", {})
        rp_out = rp.get("output", {}) if isinstance(rp, dict) else {}
        repurposed = rp_out.get("repurposed_content", [])

        # Get keywords from SEO
        seo_scraper = context.step_results.get("seo_scraper", {})
        seo_out = seo_scraper.get("output", {}) if isinstance(seo_scraper, dict) else {}
        results = seo_out.get("results", [])
        target_keywords = [r.get("keyword", "") for r in results if "error" not in r]

        # Analyze each article
        analyzed = []
        total_score = 0

        for article in articles:
            analysis = self._analyze_article(article, target_keywords, niche)
            analyzed.append(analysis)
            total_score += analysis.get("seo_score", 0)

        # Analyze repurposed content
        for item in repurposed:
            src = item.get("source_article", {})
            if src.get("title") and not any(
                a.get("title") == src["title"] for a in analyzed
            ):
                analysis = self._analyze_article(
                    {
                        "title": src.get("title", ""),
                        "body": "",
                        "meta_description": "",
                        "word_count": src.get("word_count", 0),
                        "keyword": src.get("keyword", ""),
                    },
                    target_keywords,
                    niche,
                    is_repurposed=True,
                )
                analyzed.append(analysis)
                total_score += analysis.get("seo_score", 0)

        avg_score = round(total_score / max(1, len(analyzed)), 1)

        # Overall recommendations
        global_issues = self._find_global_issues(analyzed)
        improvements = self._generate_improvements(
            avg_score, global_issues, len(analyzed)
        )

        output = {
            "niche": niche,
            "articles_analyzed": len(analyzed),
            "average_seo_score": avg_score,
            "analyses": analyzed[:5],
            "global_issues": global_issues[:5],
            "improvement_suggestions": improvements,
            "recommendation": self._generate_recommendation(avg_score, global_issues),
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="content_optimization",
                input_state={"articles": len(analyzed)},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={"avg_score": avg_score, "issues": len(global_issues)},
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="content_optimizer",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Analisou {len(analyzed)} peças de conteúdo, score médio {avg_score}"
            ],
            metadata={"analyzed": len(analyzed), "avg_score": avg_score},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _analyze_article(
        article: dict,
        keywords: list[str],
        niche: str,
        is_repurposed: bool = False,
    ) -> dict[str, Any]:
        """Analyze a single piece of content."""
        title = article.get("title", "")
        body = article.get("body", "")
        meta = article.get("meta_description", "")
        word_count = article.get("word_count", 0) or len(body.split())
        keyword = article.get("keyword", "")
        content_type = article.get("content_type", "article")
        body_lower = body.lower()

        issues = []
        score = 70  # Start at 70, deduct for issues

        # 1. Title analysis
        title_words = len(title.split())
        if title_words < 5:
            issues.append("Título muito curto (<5 palavras)")
            score -= 5
        elif title_words > 15:
            issues.append("Título muito longo (>15 palavras)")
            score -= 3

        # 2. Meta description
        if meta:
            meta_len = len(meta.split())
            if meta_len < 10:
                issues.append("Meta description muito curta (<10 palavras)")
                score -= 5
            elif meta_len > 25:
                issues.append("Meta description muito longa (>25 palavras)")
                score -= 2
        else:
            issues.append("Meta description ausente")
            score -= 10

        # 3. Word count
        if content_type == "article":
            if word_count < 300:
                issues.append(f"Conteúdo curto ({word_count} palavras, mínimo 300)")
                score -= 10
            elif word_count >= 1000:
                score += 5  # Bonus for long content
        elif content_type in ("review", "tutorial"):
            if word_count < 200:
                issues.append(f"Conteúdo curto ({word_count} palavras)")
                score -= 8

        # 4. Keyword usage
        if keyword:
            kw_count = body_lower.count(keyword.lower())
            if kw_count == 0:
                issues.append(f"Keyword '{keyword}' não encontrada no corpo")
                score -= 10
            elif kw_count < 2:
                issues.append(f"Keyword '{keyword}' aparece apenas {kw_count}x")
                score -= 5
            elif kw_count > 20:
                issues.append(
                    f"Excesso de keyword '{keyword}' ({kw_count}x) — risco de keyword stuffing"
                )
                score -= 5
            else:
                score += 3  # Good keyword density
        else:
            issues.append("Keyword alvo não definida")
            score -= 5

        # 5. Heading structure
        h2_count = len(re.findall(r"^##\s", body, re.MULTILINE))
        h3_count = len(re.findall(r"^###\s", body, re.MULTILINE))
        total_headings = h2_count + h3_count
        if total_headings == 0 and word_count > 200:
            issues.append("Nenhum heading (H2/H3) encontrado")
            score -= 8
        elif total_headings < 2 and word_count > 400:
            issues.append("Poucos headings para o tamanho do conteúdo")
            score -= 4

        # 6. Affiliate disclosure
        has_disclosure = any(
            x in body_lower for x in ["afiliado", "comissão", "disclosure", "afiliados"]
        )
        if not has_disclosure and not is_repurposed:
            issues.append("Disclosure de afiliado não encontrado")
            score -= 10

        # 7. Call to action
        has_cta = any(
            x in body_lower
            for x in [
                "comece",
                "compre",
                "acesse",
                "clique",
                "inscreva",
                "baixe",
                "saiba mais",
            ]
        )
        if not has_cta:
            issues.append("Call to action não encontrado")
            score -= 5

        # 8. External links
        has_links = "http" in body_lower or "https://" in body_lower
        if not has_links and not is_repurposed:
            issues.append("Nenhum link encontrado")
            score -= 8

        # 9. Readability (sentence length)
        sentences = re.split(r"[.!?]+", body)
        if sentences:
            long_sentences = sum(1 for s in sentences if len(s.split()) > 30)
            if long_sentences > len(sentences) * 0.3:
                issues.append("Muitas frases longas (>30 palavras) — dificulta leitura")
                score -= 4

        score = max(0, min(100, score))

        return {
            "title": title,
            "content_type": content_type,
            "word_count": word_count,
            "seo_score": score,
            "issues": issues,
            "issue_count": len(issues),
            "keyword": keyword or "não definida",
            "headings": {"h2": h2_count, "h3": h3_count, "total": total_headings},
            "has_disclosure": has_disclosure,
            "has_cta": has_cta,
            "has_links": has_links,
        }

    @staticmethod
    def _find_global_issues(analyses: list) -> list[str]:
        """Find issues that appear across multiple articles."""
        all_issues = []
        for a in analyses:
            all_issues.extend(a.get("issues", []))
        counter = Counter(all_issues)
        return [f"{issue} ({count}x)" for issue, count in counter.most_common(10)]

    @staticmethod
    def _generate_improvements(avg_score: float, issues: list, count: int) -> list[str]:
        """Generate actionable improvements."""
        suggestions = []
        if avg_score < 60:
            suggestions.append(
                "Revisar estrutura dos artigos: headings, keyword density e meta descriptions"
            )
        if any("Disclosure" in i for i in issues):
            suggestions.append("Adicionar disclosure de afiliado em todos os artigos")
        if any("Keyword" in i and "não encontrada" in i for i in issues):
            suggestions.append(
                "Incluir keyword alvo no corpo do artigo (especialmente no primeiro parágrafo)"
            )
        if any("Call to action" in i for i in issues):
            suggestions.append(
                "Adicionar CTA claro em cada artigo (ex: 'Clique aqui para saber mais')"
            )
        if any("Heading" in i for i in issues):
            suggestions.append("Adicionar headings H2/H3 para estruturar o conteúdo")
        if any("curto" in i for i in issues):
            suggestions.append(
                "Expandir conteúdo para mínimo 500-1000 palavras por artigo"
            )
        if not suggestions:
            suggestions.append(
                f"Score médio {avg_score} — conteúdo bem otimizado. Foco em links e consistência."
            )
        return suggestions

    @staticmethod
    def _generate_recommendation(avg_score: float, issues: list) -> str:
        if avg_score >= 80:
            return f"Score SEO médio: {avg_score}/100. Conteúdo bem otimizado! Mantenha a qualidade."
        elif avg_score >= 60:
            return f"Score SEO médio: {avg_score}/100. {len(issues)} issues encontradas. Revisar antes de publicar."
        else:
            return f"Score SEO médio: {avg_score}/100. {len(issues)} issues críticas. Precisa de revisão antes de publicar."
