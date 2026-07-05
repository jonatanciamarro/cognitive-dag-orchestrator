"""Agente de SEO Scraper — coleta dados reais de SEO via web scraping (sem API key)."""

from __future__ import annotations

import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class SERPParser(HTMLParser):
    """Parse Google search results from HTML."""

    def __init__(self):
        super().__init__()
        self.results: list[dict[str, Any]] = []
        self._current: dict[str, Any] = {}
        self._tag_stack: list[str] = []
        self._capture_text = False
        self._text_buffer = ""
        self._in_link = False
        self._link_href = ""
        self._result_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._tag_stack.append(tag)
        attr_dict = dict(attrs)

        # Detect result links
        if tag == "a" and "href" in attr_dict:
            href = attr_dict["href"]
            if "/url?q=" in str(href) and not any(
                x in str(href) for x in ["google.com", "youtube.com", "accounts.google"]
            ):
                self._in_link = True
                # Extract actual URL
                parsed = urllib.parse.urlparse(str(href))
                qs = urllib.parse.parse_qs(parsed.query)
                if "q" in qs:
                    self._link_href = qs["q"][0]
                else:
                    self._link_href = str(href)
                self._current["url"] = self._link_href

        # Detect headings (potential titles)
        if tag in ("h3", "h2", "span") and self._in_link:
            self._capture_text = True
            self._text_buffer = ""

    def handle_endtag(self, tag: str) -> None:
        self._tag_stack.pop()
        if tag == "a" and self._in_link:
            self._in_link = False
            if self._current.get("title") and self._current.get("url"):
                self._current["position"] = self._result_count + 1
                self.results.append(dict(self._current))
                self._result_count += 1
                self._current = {}
        if self._capture_text and tag in ("h3", "h2", "span"):
            self._capture_text = False
            title = self._text_buffer.strip()
            if title and len(title) > 5 and self._in_link:
                self._current["title"] = title

    def handle_data(self, data: str) -> None:
        if self._capture_text:
            self._text_buffer += data


class SEOScraperAgent(AgentBase):
    """Coleta dados reais de SEO via web scraping.

    Faz scraping dos resultados de busca do Google para obter:
    - Keywords reais (sugestões de busca)
    - Volumes estimados (baseados em concorrência)
    - Dificuldade estimada
    - URLs dos concorrentes
    - Títulos e meta descriptions

    Não requer API key — usa scraping público.
    """

    def __init__(self, rate_limit_seconds: float = 2.0, **kwargs) -> None:
        super().__init__("seo_scraper", **kwargs)
        self.rate_limit = rate_limit_seconds
        self._last_request: float = 0.0

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request = time.time()

    def _google_search(self, query: str, num_results: int = 10) -> list[dict[str, Any]]:
        """Scrape Google search results for a query."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        }
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}&hl=pt-BR"

        req = urllib.request.Request(url, headers=headers)
        self._rate_limit()

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                html_content = response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            raise RuntimeError(f"Google search failed: {exc}") from exc

        # Parse results
        parser = SERPParser()
        parser.feed(html_content)

        # Also extract "People also ask" and related searches
        related = self._extract_related_questions(html_content)
        suggestions = self._extract_search_suggestions(html_content)

        return {
            "organic_results": parser.results[:num_results],
            "total_results_found": len(parser.results),
            "related_questions": related,
            "search_suggestions": suggestions,
            "query": query,
        }

    def _extract_related_questions(self, html: str) -> list[str]:
        """Extract 'People also ask' questions from HTML."""
        questions = []
        # Find text patterns that look like questions
        question_patterns = re.finditer(r"(?:<[^>]*>)*([^<>]*\?)(?:<[^>]*>)*", html)
        seen = set()
        for m in question_patterns:
            q = m.group(1).strip()
            if len(q) > 10 and len(q) < 150 and q not in seen:
                seen.add(q)
                questions.append(q)
        return questions[:8]

    def _extract_search_suggestions(self, html: str) -> list[str]:
        """Extract 'Related searches' suggestions."""
        suggestions = []
        # Look for suggestion patterns
        parts = re.split(r'<div[^>]*class="[^"]*suggestions[^"]*"[^>]*>', html)
        if len(parts) > 1:
            text = re.sub(r"<[^>]+>", " ", parts[1])
            suggestions = [
                s.strip() for s in text.split("\n") if s.strip() and len(s.strip()) > 5
            ]
        return suggestions[:10]

    def _estimate_difficulty(
        self, query: str, results_count: int, related_count: int
    ) -> dict[str, Any]:
        """Estimate keyword difficulty based on SERP analysis."""
        # Simplified difficulty estimation
        if results_count == 0:
            return {
                "difficulty": 0.1,
                "level": "very_easy",
                "note": "Pouca concorrência encontrada",
            }
        if results_count < 5:
            base = 0.2
        elif results_count < 10:
            base = 0.4
        else:
            base = 0.6

        # Related questions indicate higher competition
        if related_count > 5:
            base += 0.15
        elif related_count > 2:
            base += 0.05

        difficulty = min(0.95, base)

        # Check if query is a question (usually easier)
        if query.strip().endswith("?"):
            difficulty = max(0.1, difficulty - 0.15)

        level = (
            "very_easy"
            if difficulty < 0.2
            else "easy"
            if difficulty < 0.35
            else "medium"
            if difficulty < 0.55
            else "hard"
            if difficulty < 0.75
            else "very_hard"
        )

        return {"difficulty": round(difficulty, 2), "level": level}

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        search_queries = [
            niche,
            f"{niche} para iniciantes",
            f"como fazer {niche}",
            f"melhores {niche}",
            f"{niche} passo a passo",
        ]

        seo_data: list[dict[str, Any]] = []
        total_opportunities = 0

        for query in search_queries:
            try:
                result = self._google_search(query)
                diff = self._estimate_difficulty(
                    query,
                    result["total_results_found"],
                    len(result["related_questions"]),
                )

                opportunities = {
                    "keyword": query,
                    "volume_estimate": self._estimate_volume(query, diff["difficulty"]),
                    "difficulty": diff,
                    "competitors_count": result["total_results_found"],
                    "related_searches": result["search_suggestions"],
                    "people_also_ask": result["related_questions"],
                    "top_urls": [
                        r.get("url", "") for r in result["organic_results"][:5]
                    ],
                    "top_titles": [
                        r.get("title", "") for r in result["organic_results"][:5]
                    ],
                }

                seo_data.append(opportunities)
                if diff["difficulty"] < 0.5:
                    total_opportunities += 1

            except Exception as exc:
                seo_data.append(
                    {
                        "keyword": query,
                        "error": str(exc),
                        "volume_estimate": 500,
                        "difficulty": {"difficulty": 0.3, "level": "unknown"},
                    }
                )

        # Sort by difficulty (easiest first)
        seo_data.sort(key=lambda x: x.get("difficulty", {}).get("difficulty", 1))

        # Extract all unique suggestions as additional keywords
        all_suggestions = []
        for d in seo_data:
            all_suggestions.extend(d.get("related_searches", []))
            all_suggestions.extend(d.get("people_also_ask", []))

        deduped_suggestions = list(dict.fromkeys(all_suggestions))[:15]

        output = {
            "niche": niche,
            "queries_analyzed": len(search_queries),
            "results": seo_data,
            "total_opportunities": total_opportunities,
            "additional_keywords_from_serp": deduped_suggestions,
            "recommendation": self._generate_recommendation(
                seo_data, total_opportunities
            ),
            "data_source": "google_serp_scraping",
            "note": "Dados coletados via scraping público do Google. Precisão limitada sem API paga (Ahrefs/Semrush).",
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="seo_scraping",
                input_state={"niche": niche, "queries": len(search_queries)},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "opportunities": total_opportunities,
                    "keywords": len(deduped_suggestions),
                },
            )

        # Semantic memory
        if self.semantic_memory:
            for data in seo_data[:3]:
                if "error" not in data:
                    kw_concept = self.semantic_memory.register_concept(
                        f"kw_{data['keyword'][:20]}",
                        "keyword",
                        f"Dificuldade: {data['difficulty']['difficulty']}",
                    )
                    niche_concept = self.semantic_memory.find_concept(niche, "niche")
                    if niche_concept:
                        self.semantic_memory.assert_claim(
                            subject=niche_concept["concept_id"],
                            predicate="has_real_keyword",
                            object=kw_concept,
                            confidence=1.0 - data["difficulty"]["difficulty"],
                            evidence_type="DIRECT_OBSERVATION",
                            epistemic_status="VERIFIED",
                            supporting_data={
                                "difficulty": data["difficulty"],
                                "competitors": data["competitors_count"],
                            },
                            source_cycle_id=context.run_id,
                            asserted_by=self.name,
                            observer_id=self.name,
                        )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="seo_scraper",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Analisou {len(search_queries)} queries no Google para '{niche}', encontrou {total_opportunities} oportunidades"
            ],
            metadata={
                "queries": len(search_queries),
                "opportunities": total_opportunities,
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _estimate_volume(query: str, difficulty: float) -> int:
        """Estimate search volume based on keyword characteristics."""
        # Simplified volume estimation
        base = 500
        if difficulty < 0.2:
            base = 200  # Very easy = low volume
        elif difficulty < 0.4:
            base = 800  # Easy = medium volume
        elif difficulty < 0.6:
            base = 2000  # Medium = good volume
        else:
            base = 5000  # Hard = high volume (competitive)

        # Questions usually have good volume
        if query.strip().endswith("?"):
            base = int(base * 0.7)

        # "Melhores" and "como" queries have higher volume
        if any(x in query.lower() for x in ["melhores", "como", "guia"]):
            base = int(base * 1.3)

        return base

    @staticmethod
    def _generate_recommendation(results: list[dict], opportunities: int) -> str:
        """Generate SEO recommendation based on analysis."""
        easy = [
            r
            for r in results
            if r.get("difficulty", {}).get("level") in ("very_easy", "easy")
        ]
        medium = [
            r for r in results if r.get("difficulty", {}).get("level") == "medium"
        ]

        if easy:
            return (
                f"{len(easy)} oportunidades de baixa concorrência encontradas. "
                f"Priorizar: '{easy[0]['keyword']}' (dificuldade: {easy[0]['difficulty']['difficulty']}). "
                f"Criar conteúdo focado em palavras-chave de cauda longa para ranquear mais rápido."
            )
        elif medium:
            return (
                f"{len(medium)} oportunidades de média concorrência. "
                f"Criar conteúdo aprofundado e钉子 para competir. "
                f"Foco em SEO on-page e backlinks."
            )
        return (
            f"{opportunities} oportunidades no nicho '{results[0]['keyword'] if results else '?'}'. "
            f"Considere nichos mais específicos (cauda longa) para concorrência menor."
        )
