"""Agente de Rank Tracker — monitora posições de keywords no Google via scraping."""

from __future__ import annotations

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


class RankParser(HTMLParser):
    """Parse Google results to find target domain positions."""

    def __init__(self, target_domain: str = ""):
        super().__init__()
        self.results: list[dict[str, Any]] = []
        self._current: dict[str, Any] = {}
        self._capture_text = False
        self._text_buffer = ""
        self._in_link = False
        self._position = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = dict(attrs)
        if tag == "a" and "href" in attr_dict:
            href = attr_dict["href"]
            if "/url?q=" in str(href) and "google.com" not in str(href):
                self._in_link = True
                parsed = urllib.parse.urlparse(str(href))
                qs = urllib.parse.parse_qs(parsed.query)
                url = qs.get("q", [""])[0]
                self._current = {"url": url, "position": 0}
        if tag in ("h3",) and self._in_link:
            self._capture_text = True
            self._text_buffer = ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_link:
            self._in_link = False
            if self._current.get("url"):
                self._position += 1
                self._current["position"] = self._position
                self.results.append(dict(self._current))
                self._current = {}
        if self._capture_text and tag == "h3":
            self._capture_text = False
            if self._in_link:
                self._current["title"] = self._text_buffer.strip()

    def handle_data(self, data: str) -> None:
        if self._capture_text:
            self._text_buffer += data


class RankTrackerAgent(AgentBase):
    """Monitora posições de keywords no Google.

    Faz scraping periódico para verificar em que posição
    seu domínio (ou concorrentes) aparece para cada keyword.
    """

    def __init__(self, rate_limit: float = 3.0, **kwargs) -> None:
        super().__init__("rank_tracker", **kwargs)
        self.rate_limit = rate_limit
        self._last_request: float = 0.0

    def _check_rank(self, keyword: str, target_domain: str = "") -> dict[str, Any]:
        """Check Google rank for a keyword."""
        self._rate_limit()
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9",
        }
        url = f"https://www.google.com/search?q={urllib.parse.quote(keyword)}&num=20&hl=pt-BR"
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            return {
                "keyword": keyword,
                "error": str(exc),
                "position": None,
                "ranked": False,
            }

        parser = RankParser(target_domain)
        parser.feed(html)

        # Find position for target domain
        my_position = None
        top_urls = []
        for r in parser.results:
            top_urls.append(
                {"pos": r["position"], "url": r["url"], "title": r.get("title", "")}
            )
            if target_domain and target_domain in r.get("url", ""):
                my_position = r["position"]

        return {
            "keyword": keyword,
            "position": my_position,
            "ranked": my_position is not None,
            "top_10_count": min(10, len(parser.results)),
            "top_results": top_urls[:10],
            "estimated_traffic_share": self._estimate_traffic_share(my_position)
            if my_position
            else 0,
        }

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request = time.time()

    @staticmethod
    def _estimate_traffic_share(position: int) -> float:
        """Estimate % of traffic for a given position (first page only)."""
        shares = {
            1: 0.32,
            2: 0.18,
            3: 0.11,
            4: 0.08,
            5: 0.06,
            6: 0.04,
            7: 0.03,
            8: 0.02,
            9: 0.015,
            10: 0.01,
        }
        return shares.get(position, 0.0)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        target_domain = context.artifacts.get("target_domain", "")

        # Get keywords from SEO agents
        seo_scraper = context.step_results.get("seo_scraper", {})
        seo_out = seo_scraper.get("output", {}) if isinstance(seo_scraper, dict) else {}

        seo_research = context.step_results.get("seo_research", {})
        seo_research_out = (
            seo_research.get("output", {}) if isinstance(seo_research, dict) else {}
        )

        # Collect keywords
        keywords = []
        for result in seo_out.get("results", []):
            kw = result.get("keyword", "")
            if kw and kw not in keywords:
                keywords.append(kw)
            for sug in result.get("related_searches", [])[:2]:
                if sug not in keywords:
                    keywords.append(sug)

        for opp in seo_research_out.get("top_opportunities", []):
            kw = opp.get("keyword", "")
            if kw and kw not in keywords:
                keywords.append(kw)

        if not keywords:
            keywords = [niche, f"{niche} para iniciantes", f"como fazer {niche}"]

        keywords = keywords[:5]  # Max 5 per cycle (rate limited)

        # Check rank for each keyword
        rankings = []
        ranked_count = 0
        top10_count = 0
        for kw in keywords:
            result = self._check_rank(kw, target_domain)
            if result["ranked"]:
                ranked_count += 1
                if result["position"] and result["position"] <= 10:
                    top10_count += 1
            rankings.append(result)

        output = {
            "niche": niche,
            "keywords_tracked": len(keywords),
            "ranked_keywords": ranked_count,
            "top_10_keywords": top10_count,
            "rankings": rankings,
            "target_domain": target_domain or "não configurado",
            "data_source": "google_serp_scraping",
            "recommendation": self._generate_report(rankings, ranked_count),
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="rank_tracking",
                input_state={"keywords": len(keywords), "domain": target_domain},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={"ranked": ranked_count, "top10": top10_count},
            )

        # Semantic memory
        if self.semantic_memory:
            for r in rankings[:3]:
                if r.get("position"):
                    r_concept = self.semantic_memory.register_concept(
                        f"rank_{r['keyword'][:15]}",
                        "revenue",
                        f"Posição {r['position']} para '{r['keyword']}'",
                    )
                    self.semantic_memory.register_observer(
                        self.name, "AGENT", self.name, 0.8
                    )
                    self.semantic_memory.assert_claim(
                        subject=f"kw_{r['keyword'][:15]}",
                        predicate="ranks_at_position",
                        object=r_concept,
                        confidence=min(0.9, 1.0 - (r.get("position", 10) / 20)),
                        evidence_type="DIRECT_OBSERVATION",
                        epistemic_status="VERIFIED",
                        supporting_data={
                            "position": r["position"],
                            "share": r["estimated_traffic_share"],
                        },
                        source_cycle_id=context.run_id,
                        asserted_by=self.name,
                        observer_id=self.name,
                    )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="rank_tracker",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Trackeou {len(keywords)} keywords, {ranked_count} ranqueadas, {top10_count} no top 10"
            ],
            metadata={
                "tracked": len(keywords),
                "ranked": ranked_count,
                "top10": top10_count,
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _generate_report(rankings: list[dict], ranked_count: int) -> str:
        """Generate rank tracking report."""
        ranked = [r for r in rankings if r.get("position")]
        if not ranked:
            return "Nenhuma keyword ranqueada ainda. Publique conteúdo e acompanhe nos próximos ciclos."

        best = min(ranked, key=lambda r: r["position"])
        return (
            f"{ranked_count} keywords ranqueadas. "
            f"Melhor posição: '{best['keyword']}' na posição {best['position']} "
            f"(~{best['estimated_traffic_share'] * 100:.0f}% do tráfego). "
            f"Produza mais conteúdo para as keywords não ranqueadas."
        )
